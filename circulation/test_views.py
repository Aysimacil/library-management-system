from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from accounts.roles import LIBRARIAN, MEMBER
from books.models import Book, BookCopy
from .models import CheckoutRequest, Loan


class DeskTests(TestCase):
    def setUp(self):
        call_command("sync_library_roles")
        self.user = get_user_model().objects.create_user("reader")
        self.user.groups.add(Group.objects.get(name=MEMBER))
        self.staff = get_user_model().objects.create_user("staff", is_staff=True)
        self.staff.groups.add(Group.objects.get(name=LIBRARIAN))
        self.book = Book.objects.create(title="Kitap")
        self.copy = BookCopy.objects.create(book=self.book, inventory_code="TEST-1")

    def test_request_checkout_and_return_at_staff_desk(self):
        self.client.force_login(self.user)
        url = reverse("circulation:request", args=[self.book.pk])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(CheckoutRequest.objects.filter(status="PENDING").count(), 1)
        self.assertEqual(self.book.available_copy_count, 1)
        self.client.force_login(self.staff)
        form = {"username": self.user.username, "inventory_code": self.copy.inventory_code}
        self.assertRedirects(self.client.post(reverse("circulation:issue"), form), reverse("circulation:desk"))
        loan = Loan.objects.get()
        self.assertEqual(CheckoutRequest.objects.get().loan_id, loan.pk)
        self.assertEqual(self.book.available_copy_count, 0)
        self.assertContains(self.client.get(reverse("circulation:desk"), {"q": self.user.username}), self.copy.inventory_code)
        self.client.post(reverse("circulation:return", args=[loan.pk]))
        self.assertEqual(self.book.available_copy_count, 1)

    def test_csrf_and_invalid_metadata(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.staff)
        url = reverse("circulation:issue")
        self.assertEqual(client.post(url, {}).status_code, 403)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(url, {"username": "invalid", "inventory_code": "missing"}).status_code, 400)
        self.assertFalse(Loan.objects.exists())
