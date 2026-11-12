from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from .services import RecommendationUnavailable


class GeminiSmokeTests(TestCase):
    @override_settings(LLM_API_KEY="")
    @patch("recommendations.management.commands.smoke_gemini.recommend")
    def test_missing_key_skips_without_request(self, provider):
        output = StringIO()
        call_command("smoke_gemini", live=True, stdout=output)
        self.assertIn("SKIPPED", output.getvalue())
        provider.assert_not_called()

    @override_settings(LLM_API_KEY="unit-test-secret")
    @patch("recommendations.management.commands.smoke_gemini.recommend")
    def test_key_alone_is_not_opt_in(self, provider):
        output = StringIO()
        call_command("smoke_gemini", stdout=output)
        self.assertIn("SKIPPED", output.getvalue())
        provider.assert_not_called()

    @override_settings(LLM_API_KEY="unit-test-secret")
    @patch("recommendations.management.commands.smoke_gemini.recommend")
    def test_opt_in_uses_active_account_and_rejects_empty_or_failed_result(self, provider):
        user = get_user_model().objects.create_user("smoke")
        provider.return_value = []
        with self.assertRaises(CommandError):
            call_command("smoke_gemini", live=True, user_id=user.pk)
        provider.side_effect = RecommendationUnavailable("sensitive provider detail")
        with self.assertRaisesMessage(CommandError, "Live check failed"):
            call_command("smoke_gemini", live=True, user_id=user.pk)
        provider.side_effect = None
        provider.return_value = [(object(), "result")]
        output = StringIO()
        call_command("smoke_gemini", live=True, user_id=user.pk, stdout=output)
        self.assertIn("LIVE VERIFIED", output.getvalue())
        self.assertNotIn("unit-test-secret", output.getvalue())
