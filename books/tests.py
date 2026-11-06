from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from .models import Author, Book, BookCopy, Category


class CatalogModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(title="Örnek Kitap", isbn="9780306406157")

    def test_book_supports_multiple_authors_and_categories(self):
        authors = [Author.objects.create(name=name) for name in ("Yazar A", "Yazar B")]
        categories = [Category.objects.create(name=name) for name in ("Bilim", "Tarih")]
        self.book.authors.add(*authors)
        self.book.categories.add(*categories)
        self.assertCountEqual(self.book.authors.all(), authors)
        self.assertCountEqual(self.book.categories.all(), categories)
        self.assertIn(self.book, authors[0].books.all())

    def test_different_authors_can_share_a_name(self):
        Author.objects.create(name="Aynı İsim")
        Author.objects.create(name="Aynı İsim")
        self.assertEqual(Author.objects.filter(name="Aynı İsim").count(), 2)

    def test_category_name_is_unique(self):
        Category.objects.create(name="Bilim")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(name="Bilim")

    def test_multiple_books_can_have_no_isbn(self):
        for title in ("ISBN'siz Kitap A", "ISBN'siz Kitap B"):
            book = Book(title=title)
            book.full_clean()
            book.save()
        self.assertEqual(Book.objects.filter(isbn="").count(), 2)

    def test_nonempty_isbn_is_unique_in_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Book.objects.create(title="Diğer Kitap", isbn=self.book.isbn)

    def test_valid_isbn_formats_and_check_digits(self):
        for isbn in ("0306406152", "080442957X", "9780140328721"):
            with self.subTest(isbn=isbn):
                Book(title="Geçerli ISBN", isbn=isbn).full_clean()

    def test_invalid_isbn_is_rejected(self):
        for isbn in (
            "9780306406158", "0306406153", "978-0306406157", "abc",
            "1234567890128", " 0306406152", "０３０６４０６１５２",
        ):
            with self.subTest(isbn=isbn), self.assertRaises(ValidationError):
                Book(title="Geçersiz ISBN", isbn=isbn).full_clean()

    def test_publication_year_is_optional(self):
        book = Book(title="Yılı bilinmeyen")
        book.full_clean()
        book.save()
        self.assertIsNone(book.publication_year)

    def test_invalid_publication_year_is_rejected_by_validation(self):
        for year in (0, 10000):
            with self.subTest(year=year), self.assertRaises(ValidationError):
                Book(title="Geçersiz yıl", publication_year=year).full_clean()

    def test_invalid_publication_year_is_rejected_by_database(self):
        for year in (0, 10000):
            with self.subTest(year=year):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Book.objects.create(title="Geçersiz yıl", publication_year=year)

    def test_copy_is_available_by_default(self):
        copy = BookCopy.objects.create(book=self.book, inventory_code="K-001")
        self.assertEqual(copy.status, BookCopy.Status.AVAILABLE)

    def test_inventory_code_is_unique_across_books(self):
        BookCopy.objects.create(book=self.book, inventory_code="K-001")
        other_book = Book.objects.create(title="Diğer Kitap")
        with self.assertRaises(IntegrityError), transaction.atomic():
            BookCopy.objects.create(book=other_book, inventory_code="K-001")

    def test_invalid_copy_status_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            BookCopy.objects.create(
                book=self.book, inventory_code="K-001", status="LOST",
            )

    def test_book_with_physical_copies_cannot_be_deleted(self):
        BookCopy.objects.create(book=self.book, inventory_code="K-001")
        with self.assertRaises(ProtectedError):
            self.book.delete()
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_availability_is_derived_from_copies_and_status_changes(self):
        self.assertEqual(self.book.available_copy_count, 0)
        copy = BookCopy.objects.create(book=self.book, inventory_code="K-001")
        BookCopy.objects.create(
            book=self.book, inventory_code="K-002", status=BookCopy.Status.ON_LOAN,
        )
        other_book = Book.objects.create(title="Diğer Kitap")
        BookCopy.objects.create(book=other_book, inventory_code="K-003")
        self.assertEqual(self.book.available_copy_count, 1)
        copy.status = BookCopy.Status.ON_LOAN
        copy.save(update_fields=["status", "updated_at"])
        self.assertEqual(self.book.available_copy_count, 0)
        copy.status = BookCopy.Status.AVAILABLE
        copy.save(update_fields=["status", "updated_at"])
        self.assertEqual(self.book.available_copy_count, 1)
        copy.delete()
        self.assertEqual(self.book.available_copy_count, 0)
