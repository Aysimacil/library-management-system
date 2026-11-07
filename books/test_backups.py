from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import skipUnless
import zipfile

from django.core.management import call_command
from django.db import connection
from django.test import SimpleTestCase, TransactionTestCase, override_settings

from .backup import create_backup, restore_backup
from .models import Book
from .test_enhancements import upload


class BackupArchiveTests(SimpleTestCase):
    def test_restore_rejects_traversal_and_checksum_corruption(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name, expected in (("../escape", sha256(b"bad").hexdigest()), ("database.sqlite3", "wrong")):
                archive = root / "malicious.zip"
                with zipfile.ZipFile(archive, "w") as bundle:
                    bundle.writestr(name, b"bad")
                    files = {name: expected}
                    bundle.writestr("manifest.json", json.dumps({"version": 1, "engine": "sqlite", "files": files}))
                with self.assertRaises(ValueError):
                    restore_backup(archive, root / "restored")
                self.assertFalse((root / "restored").exists())
                self.assertFalse((root / "escape").exists())

    def test_file_sqlite_roundtrip_and_no_overwrite(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "source.sqlite3"
            env = {**os.environ, "DEBUG": "true", "DJANGO_ENV": "development", "DB_ENGINE": "sqlite",
                   "DB_NAME": str(database), "MEDIA_ROOT": str(root / "media")}
            (root / "media").mkdir()
            for args in [
                ["migrate", "--noinput"],
                ["shell", "-c", "from books.models import Book; Book.objects.create(title='Backup örneği')"],
                ["backup_library", "--output", str(root / "backup.zip")],
            ]:
                subprocess.run([sys.executable, "manage.py", *args], env=env, check=True, capture_output=True, timeout=30)
            engine = restore_backup(root / "backup.zip", root / "restored")
            self.assertEqual(engine, "sqlite")
            with sqlite3.connect(root / "restored/database.sqlite3") as db:
                self.assertEqual(db.execute("SELECT title FROM books_book").fetchone()[0], "Backup örneği")
            with self.assertRaises(ValueError):
                restore_backup(root / "backup.zip", root / "restored")
            with self.assertRaises(ValueError):
                restore_backup(root / "backup.zip", root / "too-large", max_bytes=1)


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL and matching pg_dump client")
class PostgreSQLBackupTests(TransactionTestCase):
    def test_database_and_cover_bundle_can_be_verified_offline(self):
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=str(Path(directory) / "media")):
            root = Path(directory)
            (root / "media").mkdir()
            book = Book.objects.create(title="PostgreSQL backup", cover=upload())
            create_backup(root / "backup.zip")
            self.assertEqual(restore_backup(root / "backup.zip", root / "restored"), "postgresql")
            self.assertTrue((root / "restored/database.dump").read_bytes().startswith(b"PGDMP"))
            self.assertEqual((root / "media" / book.cover.name).read_bytes(), (root / "restored/media" / book.cover.name).read_bytes())
            with self.assertRaises(FileExistsError):
                create_backup(root / "backup.zip")
