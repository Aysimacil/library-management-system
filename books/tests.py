from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

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


class CatalogAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="Örnek Yazar")
        cls.category = Category.objects.create(name="Bilim")
        cls.book = Book.objects.create(title="Bilim Kitabı", isbn="9780306406157")
        cls.book.authors.add(cls.author)
        cls.book.categories.add(cls.category)
        cls.copy = BookCopy.objects.create(book=cls.book, inventory_code="K-001")
        cls.loaned_copy = BookCopy.objects.create(
            book=cls.book, inventory_code="K-002", status=BookCopy.Status.ON_LOAN,
        )
        cls.staff = get_user_model().objects.create_user(username="catalog_staff", is_staff=True)
        cls.staff.user_permissions.set(Permission.objects.filter(content_type__app_label="books"))
        cls.other_staff = get_user_model().objects.create_user(username="other_staff", is_staff=True)

    def setUp(self):
        self.client.force_login(self.staff)

    def test_all_catalog_changelists_render(self):
        for model in ("author", "category", "book", "bookcopy"):
            with self.subTest(model=model):
                response = self.client.get(reverse(f"admin:books_{model}_changelist"))
                self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("admin:books_book_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("admin:login")))

    def test_staff_without_model_permissions_cannot_manage_catalog(self):
        self.client.force_login(self.other_staff)
        for url in (
            reverse("admin:books_book_changelist"),
            reverse("admin:books_book_add"),
            reverse("admin:books_bookcopy_change", args=[self.copy.pk]),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
        response = self.client.post(reverse("admin:books_category_add"), {"name": "Yetkisiz"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Category.objects.filter(name="Yetkisiz").exists())

    def test_authorized_staff_can_create_book_and_copy(self):
        response = self.client.post(reverse("admin:books_book_add"), {
            "title": "Yeni Kitap", "isbn": "9780140328721", "publication_year": 1988,
            "authors": [self.author.pk], "categories": [self.category.pk], "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        book = Book.objects.get(isbn="9780140328721")
        self.assertIn(self.author, book.authors.all())
        response = self.client.post(reverse("admin:books_bookcopy_add"), {
            "book": book.pk, "inventory_code": "K-003", "shelf_location": "A-1",
            "status": BookCopy.Status.ON_LOAN, "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        copy = BookCopy.objects.get(inventory_code="K-003")
        self.assertEqual(copy.status, BookCopy.Status.AVAILABLE)

    def test_duplicate_inventory_code_shows_form_error(self):
        response = self.client.post(reverse("admin:books_bookcopy_add"), {
            "book": self.book.pk, "inventory_code": self.copy.inventory_code, "_save": "Save",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("inventory_code", response.context["adminform"].form.errors)
        self.assertEqual(BookCopy.objects.filter(inventory_code="K-001").count(), 1)

    def test_book_form_requires_an_author_and_valid_isbn(self):
        response = self.client.post(reverse("admin:books_book_add"), {
            "title": "Eksik Kitap", "isbn": "9780306406158", "_save": "Save",
        })
        self.assertEqual(response.status_code, 200)
        errors = response.context["adminform"].form.errors
        self.assertIn("authors", errors)
        self.assertIn("isbn", errors)
        self.assertFalse(Book.objects.filter(title="Eksik Kitap").exists())

    def test_copy_status_cannot_be_changed_through_catalog_form(self):
        response = self.client.post(reverse("admin:books_bookcopy_change", args=[self.copy.pk]), {
            "book": self.book.pk, "inventory_code": self.copy.inventory_code,
            "shelf_location": "B-2", "status": BookCopy.Status.ON_LOAN, "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        self.copy.refresh_from_db()
        self.assertEqual(self.copy.status, BookCopy.Status.AVAILABLE)
        self.assertEqual(self.copy.shelf_location, "B-2")

    def test_loaned_copy_identity_cannot_be_reassigned(self):
        other_book = Book.objects.create(title="Diğer Kitap")
        response = self.client.post(
            reverse("admin:books_bookcopy_change", args=[self.loaned_copy.pk]), {
                "book": other_book.pk, "inventory_code": "CHANGED", "shelf_location": "B-2",
                "status": BookCopy.Status.AVAILABLE, "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.loaned_copy.refresh_from_db()
        self.assertEqual(self.loaned_copy.book_id, self.book.pk)
        self.assertEqual(self.loaned_copy.inventory_code, "K-002")
        self.assertEqual(self.loaned_copy.status, BookCopy.Status.ON_LOAN)

    def test_loaned_copy_cannot_be_deleted_and_bulk_delete_is_disabled(self):
        response = self.client.post(reverse("admin:books_bookcopy_delete", args=[self.loaned_copy.pk]))
        self.assertEqual(response.status_code, 403)
        response = self.client.post(reverse("admin:books_bookcopy_changelist"), {
            "action": "delete_selected", "_selected_action": [self.loaned_copy.pk], "post": "yes",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(BookCopy.objects.filter(pk=self.loaned_copy.pk).exists())

    def test_available_copy_can_be_deleted(self):
        response = self.client.post(reverse("admin:books_bookcopy_delete", args=[self.copy.pk]), {
            "post": "yes",
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BookCopy.objects.filter(pk=self.copy.pk).exists())

    def test_search_and_category_filter_keep_counts_correct(self):
        second_author = Author.objects.create(name="İkinci Yazar")
        second_category = Category.objects.create(name="Tarih")
        self.book.authors.add(second_author)
        self.book.categories.add(second_category)
        Book.objects.create(title="Alakasız Kitap")
        response = self.client.get(reverse("admin:books_book_changelist"), {
            "q": self.author.name, "categories__id__exact": self.category.pk,
        })
        self.assertEqual(response.status_code, 200)
        results = list(response.context["cl"].result_list)
        self.assertEqual([book.pk for book in results], [self.book.pk])
        self.assertEqual(results[0]._copy_total, 2)
        self.assertEqual(results[0]._available_total, 1)
