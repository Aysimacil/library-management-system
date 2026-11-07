import os
import secrets
import subprocess
import sys
from pathlib import Path
from unittest import TestCase


class EnvironmentTests(TestCase):
    def run_django(self, args, **environment):
        # Start a fresh process for each profile; do not inherit deployment secrets.
        env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "TEMP", "TMP") if key in os.environ}
        return subprocess.run(
            [sys.executable, "manage.py", *args],
            cwd=Path(__file__).resolve().parents[1],
            env={**env, **environment},
            capture_output=True, text=True, timeout=20,
        )

    def production(self):
        return dict(DJANGO_ENV="production", SECRET_KEY=secrets.token_urlsafe(64),
                    ALLOWED_HOSTS="library.example.test", DB_NAME="library", DB_USER="library",
                    SMTP_HOST="smtp.example.test", MEDIA_ROOT="/srv/library-test-media", DEFAULT_FROM_EMAIL="library@example.test", MEDIA_VOLUME_ID="test-volume")

    def test_local_profile(self):
        result = self.run_django(["shell", "-c", """
from django.conf import settings as s
assert s.DEBUG and not s.SECURE_SSL_REDIRECT and not s.SESSION_COOKIE_SECURE
assert s.DATABASES['default']['ENGINE'].endswith('sqlite3')
assert s.MAILERS['default']['BACKEND'].endswith('console.EmailBackend')
"""])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_deployment_checks(self):
        env = self.production()
        result = self.run_django(["check", "--deploy"], **env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("security.W004", result.stderr)
        result = self.run_django(["check", "--deploy", "--fail-level", "WARNING"], **env,
                                 HSTS_SECONDS="31536000", HSTS_INCLUDE_SUBDOMAINS="true", HSTS_PRELOAD="true")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_security_and_connections(self):
        result = self.run_django(["shell", "-c", """
from django.conf import settings as s
assert not s.DEBUG and s.SECURE_SSL_REDIRECT and s.SECURE_HSTS_SECONDS == 0
assert s.CSRF_COOKIE_SECURE and s.SESSION_COOKIE_SECURE and s.SECURE_PROXY_SSL_HEADER is None
assert s.DATABASES['default']['ENGINE'].endswith('postgresql')
assert s.DATABASES['default']['OPTIONS']['sslmode'] == 'require'
assert s.MAILERS['default']['OPTIONS']['use_tls']
"""], **self.production())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_key_prevents_startup(self):
        env = self.production()
        del env["SECRET_KEY"]
        result = self.run_django(["check"], **env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY is required", result.stderr)

    def test_rejected_profile_settings(self):
        for key, value in (("DJANGO_ENV", "prodution"), ("DEBUG", "true"), ("DEBUG", "maybe"),
                           ("ALLOWED_HOSTS", "*"), ("SECRET_KEY", "example"),
                           ("EMAIL_MODE", "console"), ("CSRF_TRUSTED_ORIGINS", "http://unsafe.test")):
            with self.subTest(key=key, value=value):
                result = self.run_django(["check"], **{**self.production(), key: value})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ImproperlyConfigured", result.stderr)
