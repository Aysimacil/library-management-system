from django.db import DatabaseError
from django.core.management.base import BaseCommand, CommandError
from books.backup import create_backup


class Command(BaseCommand):
    help = "Create a database + managed-cover backup; never overwrites an archive."

    def add_arguments(self, parser):
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            create_backup(options["output"])
        except (OSError, ValueError, TimeoutError, DatabaseError):
            raise CommandError("Backup failed. Check database tools, media and destination.") from None
        self.stdout.write("Backup created. Protect it as confidential application data.")
