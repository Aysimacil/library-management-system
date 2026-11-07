from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Author, Book, BookCopy, Category
from .test_enhancements import upload
from circulation.services import borrow_book, return_book


class CatalogManagementTests(TestCase):
    def setUp(self):
        self.media = TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        override = override_settings(MEDIA_ROOT=self.media.name)
        override.enable()
        self.addCleanup(override.disable)
        call_command("sync_library_roles", verbosity=0)
        self.staff = get_user_model().objects.create_user("catalog-staff", is_staff=True)
        self.staff.groups.add(Group.objects.get(name="Kütüphaneci"))
        self.author = Author.objects.create(name="İpek Çağrı")
        self.second_author = Author.objects.create(name="Deniz Örnek")
        self.category = Category.objects.create(name="Mühendislik")
        self.second_category = Category.objects.create(name="Bilim")
        self.book = Book.objects.create(title="Gökyüzü ve Işık")
        self.book.authors.set([self.author, self.second_author])
        self.book.categories.set([self.category, self.second_category])
        self.copy = BookCopy.objects.create(book=self.book, inventory_code="S1-001", shelf_location="A-01")
        self.client.force_login(self.staff)

    def book_data(self, **changes):
        return {
            "title": "Yeni Kitap", "isbn": "9780306406157", "publication_year": "2001",
            "authors": [self.author.pk, self.second_author.pk],
            "categories": [self.category.pk, self.second_category.pk],
            "description": "Yapay katalog kaydı.", **changes,
        }

    def routes(self):
        return [
            (reverse("books:manage"), "view_book"),
            (reverse("books:manage-create"), "add_book"),
            (reverse("books:manage-edit", args=[self.book.pk]), "change_book"),
            (reverse("books:manage-detail", args=[self.book.pk]), "view_book"),
            (reverse("books:manage-copy-create", args=[self.book.pk]), "add_bookcopy"),
            (reverse("books:manage-shelf", args=[self.copy.pk]), "change_bookcopy"),
            (reverse("books:manage-taxonomy", args=["authors"]), "view_author"),
            (reverse("books:manage-taxonomy-create", args=["authors"]), "add_author"),
            (reverse("books:manage-taxonomy-edit", args=["authors", self.author.pk]), "change_author"),
            (reverse("books:manage-taxonomy", args=["categories"]), "view_category"),
            (reverse("books:manage-taxonomy-create", args=["categories"]), "add_category"),
            (reverse("books:manage-taxonomy-edit", args=["categories", self.category.pk]), "change_category"),
        ]

    def test_all_staff_screens_render_and_navigation_is_visible(self):
        for url, _ in self.routes():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertContains(self.client.get(reverse("books:list")), "Katalog Yönetimi")
        self.assertEqual(self.client.get(reverse("books:manage-taxonomy", args=["invalid"])).status_code, 404)

    def test_anonymous_member_and_unprivileged_staff_cannot_read_or_write(self):
        member = get_user_model().objects.create_user("member")
        staff = get_user_model().objects.create_user("no-permissions", is_staff=True)
        for user in (None, member, staff):
            if user:
                self.client.force_login(user)
            else:
                self.client.logout()
            for url, _ in self.routes():
                for method in (self.client.get, self.client.post):
                    with self.subTest(user=user, url=url, method=method.__name__):
                        self.assertEqual(method(url, {}).status_code, 302 if user is None else 403)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(BookCopy.objects.count(), 1)
        self.assertEqual(Author.objects.count(), 2)
        self.assertEqual(Category.objects.count(), 2)

    def test_each_screen_requires_its_specific_permission_and_staff_flag(self):
        for url, codename in self.routes():
            for is_staff in (False, True):
                user = get_user_model().objects.create_user(f"role-{codename}-{is_staff}-{len(url)}", is_staff=is_staff)
                user.user_permissions.add(Permission.objects.get(content_type__app_label="books", codename=codename))
                self.client.force_login(user)
                with self.subTest(url=url, staff=is_staff):
                    self.assertEqual(self.client.get(url).status_code, 200 if is_staff else 403)
                user.delete()
        viewer = get_user_model().objects.create_user("viewer", is_staff=True)
        viewer.user_permissions.add(Permission.objects.get(content_type__app_label="books", codename="view_book"))
        self.client.force_login(viewer)
        self.assertNotContains(self.client.get(reverse("books:manage")), "Yeni Kitap Ekle")
        self.assertEqual(self.client.post(reverse("books:manage-create"), self.book_data()).status_code, 403)

    def test_csrf_is_required_for_mutations(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.staff)
        for name, args in [("manage-create", []), ("manage-edit", [self.book.pk]), ("manage-copy-create", [self.book.pk]), ("manage-shelf", [self.copy.pk]), ("manage-taxonomy-create", ["authors"]), ("manage-taxonomy-create", ["categories"])]:
            self.assertEqual(client.post(reverse(f"books:{name}", args=args), {}).status_code, 403)

    def test_create_book_with_two_authors_categories_and_safe_cover(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("books:manage-create"), self.book_data(cover=upload()))
        book = Book.objects.get(title="Yeni Kitap")
        self.assertRedirects(response, reverse("books:manage-detail", args=[book.pk]))
        self.assertEqual(set(book.authors.values_list("pk", flat=True)), {self.author.pk, self.second_author.pk})
        self.assertEqual(book.categories.count(), 2)
        self.assertTrue(Path(book.cover.path).read_bytes().startswith(b"\xff\xd8"))
        self.assertEqual(book.available_copy_count, 0)

    def test_invalid_book_forms_do_not_persist(self):
        for changes in ({"isbn": "9780306406158"}, {"authors": []}, {"publication_year": "10000"}, {"cover": SimpleUploadedFile("fake.png", b"<svg/>", content_type="image/png")}):
            response = self.client.post(reverse("books:manage-create"), self.book_data(**changes))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
            self.assertEqual(Book.objects.count(), 1)
        self.assertFalse(list(Path(self.media.name).rglob("*.jpg")))

    def test_update_book_changes_metadata_and_cover_without_changing_copy_identity(self):
        member = get_user_model().objects.create_user("borrower")
        member.groups.add(Group.objects.get(name="Üye"))
        loan = borrow_book(member_id=member.pk, copy_id=self.copy.pk)
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("books:manage-edit", args=[self.book.pk]), self.book_data(cover=upload()))
        self.book.refresh_from_db()
        old_cover = self.book.cover.path
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("books:manage-edit", args=[self.book.pk]), self.book_data(description="Güncellendi", cover=upload()))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Path(old_cover).exists())
        self.copy.refresh_from_db()
        loan.refresh_from_db()
        self.assertEqual((self.copy.book_id, self.copy.inventory_code, self.copy.status), (self.book.pk, "S1-001", "ON_LOAN"))
        self.assertEqual(loan.copy_id, self.copy.pk)
        self.book.refresh_from_db()
        self.assertEqual(self.book.description, "Güncellendi")

    def test_copy_creation_duplicate_rejection_and_three_available_copies(self):
        for code, shelf in (("S1-002", "B-02"), ("S1-003", "C-03")):
            response = self.client.post(reverse("books:manage-copy-create", args=[self.book.pk]), {
                "inventory_code": code, "shelf_location": shelf, "status": "ON_LOAN", "book": "9999",
            })
            self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse("books:manage-copy-create", args=[self.book.pk]), {"inventory_code": "S1-001"})
        self.assertIn("inventory_code", response.context["form"].errors)
        self.assertEqual(self.book.available_copy_count, 3)
        detail = self.client.get(reverse("books:manage-detail", args=[self.book.pk]))
        self.assertEqual((detail.context["book"].total, detail.context["book"].available), (3, 3))
        self.assertContains(detail, "S1-003")

    def test_shelf_update_cannot_reassign_historical_copy_or_override_status(self):
        member = get_user_model().objects.create_user("loan-reader")
        member.groups.add(Group.objects.get(name="Üye"))
        loan = borrow_book(member_id=member.pk, copy_id=self.copy.pk)
        other = Book.objects.create(title="Başka kitap")
        for returned in (False, True):
            if returned:
                return_book(loan_id=loan.pk)
            self.client.post(reverse("books:manage-shelf", args=[self.copy.pk]), {
                "shelf_location": "A-99", "book": other.pk, "inventory_code": "CHANGED", "status": "ON_LOAN" if returned else "AVAILABLE",
            })
            self.copy.refresh_from_db()
            self.assertEqual((self.copy.book_id, self.copy.inventory_code, self.copy.shelf_location), (self.book.pk, "S1-001", "A-99"))
            self.assertEqual(self.copy.status, "AVAILABLE" if returned else "ON_LOAN")
        self.assertEqual(self.copy.loans.count(), 1)

    def test_authors_and_categories_can_be_created_and_edited_without_admin(self):
        for kind, model in (("authors", Author), ("categories", Category)):
            response = self.client.post(reverse("books:manage-taxonomy-create", args=[kind]), {"name": "Yeni Tanım"})
            entry = model.objects.get(name="Yeni Tanım")
            self.assertEqual(response.status_code, 302)
            self.client.post(reverse("books:manage-taxonomy-edit", args=[kind, entry.pk]), {"name": "Yeni Ad"})
            entry.refresh_from_db()
            self.assertEqual(entry.name, "Yeni Ad")
            self.assertContains(self.client.get(reverse("books:manage-taxonomy", args=[kind]), {"q": "YENİ"}), "Yeni Ad")
        duplicate = self.client.post(reverse("books:manage-taxonomy-create", args=["categories"]), {"name": "Bilim"})
        self.assertIn("name", duplicate.context["form"].errors)

    def test_management_uses_category_search_and_filters_without_count_inflation(self):
        response = self.client.get(reverse("books:manage"), {"q": "MÜHENDİSLİK", "author": self.author.pk, "category": self.second_category.pk})
        self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
        self.assertEqual((response.context["books"][0].total, response.context["books"][0].available), (1, 1))
