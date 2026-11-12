from zipfile import BadZipFile
import sqlite3
from django.core.management.base import BaseCommand, CommandError
from books.backup import restore_backup


class Command(BaseCommand):
    help = "Verify and unpack into a NEW offline directory; never changes the configured database."

    def add_arguments(self, parser):
        parser.add_argument("--archive", required=True)
        parser.add_argument("--target", required=True)
        parser.add_argument("--max-bytes", type=int, default=2 * 1024**3)

    def handle(self, *args, **options):
        if options["max_bytes"] <= 0:
            raise CommandError("max-bytes must be positive.")
        try:
            engine = restore_backup(options["archive"], options["target"], options["max_bytes"])
        except (OSError, ValueError, TypeError, KeyError, BadZipFile, sqlite3.DatabaseError):
            raise CommandError("Restore verification failed. Target was not activated.") from None
        self.stdout.write(f"Verified offline restore ({engine}). Follow the documented cutover procedure.")
