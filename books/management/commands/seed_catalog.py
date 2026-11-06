from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from books.models import Author, Book, BookCopy, Category


class Command(BaseCommand):
    help = "Örnek katalog kitaplarını ve fiziksel kopyalarını ekler."

    @transaction.atomic
    def handle(self, *args, **options):
        for number, (title, writer, genre) in enumerate([
            ("Rüzgâr Atlası", "D. Örnek", "Roman"),
            ("Kıyıda Yaşam", "A. Örnek", "Doğa"),
            ("Gökyüzü Notları", "B. Örnek", "Bilim"),
        ], start=1):
            code = f"DEMO-KAT-{number:02}"
            existing = BookCopy.objects.select_related("book").filter(inventory_code=code).first()
            if existing:
                if existing.book.title != title:
                    raise CommandError(f"{code} başka bir kitaba ait.")
                continue
            author, _ = Author.objects.get_or_create(name=writer, biography="Demo katalog yazarı.")
            category, _ = Category.objects.get_or_create(name=genre)
            book = Book.objects.create(title=title, publication_year=2020 + number)
            book.authors.add(author)
            book.categories.add(category)
            BookCopy.objects.create(book=book, inventory_code=code)
        self.stdout.write(self.style.SUCCESS("Demo kataloğu hazır."))
