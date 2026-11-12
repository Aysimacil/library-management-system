from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from books.models import Author, Book, BookCopy, Category


class AdminThemeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser("theme-admin", password="Test-admin-fixture-7392")
        cls.author = Author.objects.create(name="İpek Çağrı")
        cls.category = Category.objects.create(name="Bilim")
        cls.book = Book.objects.create(title="Gökyüzü ve Işık")
        cls.book.authors.add(cls.author)
        cls.copy = BookCopy.objects.create(book=cls.book, inventory_code="THEME-001")

    def assert_theme(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'css/admin-theme.css')
        self.assertNotContains(response, 'admin/js/theme.js')
        self.assertNotContains(response, 'admin/css/dark_mode.css')
        html = response.content.decode()
        self.assertGreater(html.index('css/admin-theme.css'), html.index('admin/css/responsive.css'))

    def test_all_admin_workflows_share_theme_and_keep_native_widgets(self):
        self.client.force_login(self.admin)
        pages = [
            reverse("admin:index"), reverse("admin:password_change"),
            *[reverse(f"admin:{model}_changelist") for model in (
                "books_book", "books_author", "books_category", "books_bookcopy",
                "auth_user", "auth_group", "circulation_loan", "circulation_fine",
            )],
            reverse("admin:books_book_add"),
            reverse("admin:books_book_change", args=[self.book.pk]),
            reverse("admin:books_bookcopy_change", args=[self.copy.pk]),
            reverse("admin:auth_user_change", args=[self.admin.pk]),
            reverse("admin:auth_group_add"),
        ]
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assert_theme(response)
                self.assertContains(response, "Kütüphane Yönetimi")
                self.assertContains(response, 'href="/">← Kütüphaneye dön')
        book_form = self.client.get(reverse("admin:books_book_add"))
        self.assertContains(book_form, 'multipart/form-data')
        self.assertContains(book_form, 'csrfmiddlewaretoken')
        self.assertContains(book_form, 'admin/js/autocomplete.js')
        self.assertContains(book_form, 'name="cover"')
        self.assertContains(self.client.get(reverse("admin:auth_group_add")), 'admin/js/SelectFilter2.js')

    def test_login_and_failed_login_use_same_theme_without_replacing_auth_form(self):
        url = reverse("admin:login")
        response = self.client.get(url)
        self.assert_theme(response)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'admin/css/login.css')
        response = self.client.post(url, {"username": self.admin.username, "password": "wrong", "next": reverse("admin:index")})
        self.assert_theme(response)
        self.assertTrue(response.context["form"].errors)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_invalid_form_and_related_popup_keep_theme_and_form_errors(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:books_book_add"), {"title": "Invalid", "isbn": "9780306406158"})
        self.assert_theme(response)
        self.assertIn("isbn", response.context["adminform"].form.errors)
        self.assertIn("authors", response.context["adminform"].form.errors)
        self.assertFalse(Book.objects.filter(title="Invalid").exists())
        popup = self.client.get(reverse("admin:books_author_add"), {"_popup": "1"})
        self.assert_theme(popup)
        self.assertContains(popup, 'name="_popup"')
        self.assertNotContains(popup, 'library-admin-brand')

    def test_anonymous_and_unprivileged_access_and_csrf_still_rejected(self):
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 302)
        staff = get_user_model().objects.create_user("theme-no-perms", is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse("admin:books_book_add")).status_code, 403)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        self.assertEqual(csrf_client.post(reverse("admin:books_book_add"), {"title": "Blocked"}).status_code, 403)
        self.assertFalse(Book.objects.filter(title="Blocked").exists())
