from io import StringIO
import json
import logging
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import DatabaseError
from django.test import TestCase, override_settings
from django.urls import reverse

from .observability import SafeJSONFormatter


class HealthTests(TestCase):
    def test_liveness_is_not_a_database_test(self):
        with patch("library_system.health.connection.cursor", side_effect=DatabaseError):
            response = self.client.get(reverse("health-live"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_readiness_checks_media_and_database_without_paths_or_secrets(self):
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            response = self.client.get(reverse("health-ready"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Cache-Control"], "no-store")
            self.assertEqual(list(Path(directory).iterdir()), [])
            with patch("library_system.health.connection.cursor", side_effect=DatabaseError("password=secret")):
                with self.assertLogs("library.health"):
                    response = self.client.get(reverse("health-ready"))
            self.assertEqual(response.status_code, 503)
            self.assertNotContains(response, "secret", status_code=503)
            self.assertNotContains(response, directory, status_code=503)
        with override_settings(MEDIA_ROOT="/path/that/is/not/provisioned"), self.assertLogs("library.health"):
            self.assertEqual(self.client.get(reverse("health-ready")).status_code, 503)

    def test_log_formatter_omits_exception_message_and_request_body(self):
        try:
            raise ValueError("api_key=must-never-appear")
        except ValueError:
            record = logging.LogRecord("django.request", logging.ERROR, __file__, 1,
                                       "password=%s", ("never-print",), sys.exc_info())
        result = SafeJSONFormatter().format(record)
        self.assertNotIn("must-never-appear", result)
        self.assertNotIn("never-print", result)
        self.assertEqual(json.loads(result)["exception_type"], "ValueError")

    @override_settings(DATA_UPLOAD_MAX_MEMORY_SIZE=64)
    def test_oversized_non_file_post_is_rejected(self):
        from django.contrib.auth import get_user_model
        response = self.client.post(reverse("accounts:signup"), {"username": "x" * 200})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(get_user_model().objects.exists())
