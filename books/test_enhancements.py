from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .covers import prepare_cover
from .models import Author, Book, BookCopy, Category


def upload(name="test.png"):
    buffer = BytesIO()
    Image.new("RGB", (80, 120), "#517164").save(buffer, "PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="text/html")


class CatalogEnhancementTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.settings_override = override_settings(MEDIA_ROOT=self.directory.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    def test_cover_sanitized_stored_with_generated_name_and_served_as_image(self):
        book = Book.objects.create(title="Kapaklı", cover=upload("../../bad.png"))
        self.assertTrue(book.cover.name.startswith("covers/"))
        self.assertNotIn("bad", book.cover.name)
        with Image.open(book.cover.path) as saved:
            self.assertEqual(saved.format, "JPEG")
            self.assertFalse(saved.getexif())
        response = self.client.get(reverse("books:cover", args=[book.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertTrue(b"".join(response.streaming_content).startswith(b"\xff\xd8"))

    def test_untrusted_and_oversize_files_rejected_without_persisting(self):
        for content in (b"<svg onload='alert(1)'/>", b"x" * (4 * 1024 * 1024 + 1)):
            with self.assertRaises(ValidationError):
                Book.objects.create(title="Invalid", cover=SimpleUploadedFile("cover.png", content))
        self.assertEqual(Book.objects.count(), 0)
        buffer = BytesIO()
        Image.new("RGB", (4000, 4000)).save(buffer, "PNG")
        with self.assertRaises(ValidationError):
            prepare_cover(SimpleUploadedFile("large.png", buffer.getvalue()))

    def test_author_year_and_stock_filters_together_and_validation(self):
        author = Author.objects.create(name="Yazar")
        category = Category.objects.create(name="Tarih")
        for year in (1990, 2000, 2020):
            book = Book.objects.create(title=str(year), publication_year=year)
            book.authors.add(author)
            book.categories.add(category)
            BookCopy.objects.create(book=book, inventory_code=str(year))
        url = reverse("books:list")
        response = self.client.get(url, {"author": author.pk, "category": category.pk, "year_from": 2000, "year_to": 2020, "available": "1", "sort": "oldest"})
        self.assertEqual([b.publication_year for b in response.context["books"]], [2000, 2020])
        page = self.client.get(url, {"year_from": 2020, "year_to": 1900})
        self.assertContains(page, "Son yıl ilk yıldan önce olamaz.")
        self.assertEqual(page.context["paginator"].count, 0)

    def test_cover_upload_requires_catalog_permission_and_no_cover_is_404(self):
        user = get_user_model().objects.create_user("reader", is_staff=True)
        self.client.force_login(user)
        self.assertEqual(self.client.post(reverse("admin:books_book_add"), {"title": "X", "cover": upload()}).status_code, 403)
        book = Book.objects.create(title="Kapaksız")
        self.assertEqual(self.client.get(reverse("books:cover", args=[book.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("books:cover", args=[book.pk])).status_code, 405)
