from django.db import DatabaseError
from django.core.management.base import BaseCommand, CommandError
from books.media_lifecycle import flush_media


class Command(BaseCommand):
    help = "Commit edilmiş kapak yazma ve silme işlemlerini yeniden dener."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        if not 1 <= options["limit"] <= 10000:
            raise CommandError("limit must be 1–10000")
        try:
            count = flush_media(limit=options["limit"])
        except (OSError, ValueError, DatabaseError):
            raise CommandError("Media operation failed; check storage and retry.") from None
        self.stdout.write(f"Tamamlanan işlem: {count}")
