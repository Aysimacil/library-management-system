from pathlib import Path
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from books.media_lifecycle import MANAGED_NAME, media_lock
from books.models import Book, CoverOperation


class Command(BaseCommand):
    help = "Dry-run orphan cover reconciliation. --apply deletes only aged, unreferenced managed files."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--older-than-hours", type=int, default=24)

    def handle(self, *args, **options):
        if options["older_than_hours"] < 1:
            raise CommandError("Grace period must be at least one hour.")
        cutoff = time.time() - options["older_than_hours"] * 3600
        count = 0
        with media_lock():
            root = Path(settings.MEDIA_ROOT).resolve()
            covers = root / "covers"
            if covers.is_symlink():
                raise CommandError("Symlink directories are unsupported.")
            if covers.is_dir():
                referenced = set(Book.objects.exclude(cover="").values_list("cover", flat=True))
                pending = set(CoverOperation.objects.values_list("name", flat=True))
                for path in covers.iterdir():
                    name = "covers/" + path.name
                    if not MANAGED_NAME.fullmatch(name) or path.is_symlink() or not path.is_file():
                        continue
                    if name in referenced or name in pending or path.stat().st_mtime >= cutoff:
                        continue
                    count += 1
                    if options["apply"]:
                        path.unlink()
        mode = "deleted" if options["apply"] else "eligible (dry-run)"
        self.stdout.write(f"{count} {mode}")
