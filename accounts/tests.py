from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from books.models import Book, BookCopy
from circulation.services import borrow_book
from .roles import LIBRARIAN, MEMBER


class AccountsTests(TestCase):
    def test_public_signup_creates_only_member_even_with_tampered_role(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "okur", "password1": "UnitTest-fixture-73942", "password2": "UnitTest-fixture-73942",
            "is_staff": True, "is_superuser": True, "groups": LIBRARIAN,
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        user = get_user_model().objects.get(username="okur")
        self.assertFalse(user.is_staff or user.is_superuser)
        self.assertEqual(list(user.groups.values_list("name", flat=True)), [MEMBER])
        self.assertTrue(user.check_password("UnitTest-fixture-73942"))
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        self.client.post(reverse("accounts:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
        page = self.client.post(reverse("accounts:login"), {"username": "okur", "password": "wrong"})
        self.assertTrue(page.context["form"].errors)
        page = self.client.post(reverse("accounts:login"), {"username": "okur", "password": "UnitTest-fixture-73942"})
        self.assertRedirects(page, reverse("accounts:profile"))

    def test_invalid_password_rejected(self):
        response = self.client.post(reverse("accounts:signup"), {"username": "okur", "password1": "123", "password2": "123"})
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(get_user_model().objects.exists())

    def test_profile_and_renewal_are_scoped_to_self(self):
        owner = get_user_model().objects.create_user("owner")
        owner.groups.add(Group.objects.get_or_create(name=MEMBER)[0])
        book = Book.objects.create(title="Özel ödünç kaydı")
        copy = BookCopy.objects.create(book=book, inventory_code="AC-1")
        loan = borrow_book(member_id=owner.pk, copy_id=copy.pk)
        stranger = get_user_model().objects.create_user("other")
        self.client.force_login(stranger)
        self.assertNotContains(self.client.get(reverse("accounts:profile")), book.title)
        self.assertEqual(self.client.post(reverse("circulation:member-renew", args=[loan.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("circulation:desk")).status_code, 403)
        self.assertEqual(self.client.post(reverse("circulation:return", args=[loan.pk])).status_code, 403)
        self.client.force_login(owner)
        self.assertContains(self.client.get(reverse("accounts:profile")), book.title)
        self.client.post(reverse("circulation:member-renew", args=[loan.pk]))
        loan.refresh_from_db()
        self.assertEqual(loan.renewal_count, 1)

    def test_role_permissions_and_admin_stats(self):
        call_command("sync_library_roles")
        librarian = get_user_model().objects.create_user("librarian", is_staff=True)
        librarian.groups.add(Group.objects.get(name=LIBRARIAN))
        self.assertTrue(librarian.has_perm("circulation.issue_loan"))
        self.assertFalse(librarian.has_perm("auth.change_user"))
        self.client.force_login(librarian)
        self.assertEqual(self.client.get(reverse("circulation:desk")).status_code, 200)
        admin = get_user_model().objects.create_superuser(username="manager")
        self.client.force_login(admin)
        page = self.client.get(reverse("accounts:dashboard"))
        self.assertIn(("Fiziksel kopya", 0), page.context["metrics"])

    def test_demo_is_repeatable_and_does_not_grant_access_to_existing_user(self):
        from django.core.management.base import CommandError
        from circulation.models import Loan

        collision = get_user_model().objects.create_user("demo_gorevli")
        with self.assertRaises(CommandError):
            call_command("seed_library_demo")
        self.assertFalse(get_user_model().objects.filter(username="demo_okur").exists())
        self.assertFalse(collision.groups.exists())
        collision.delete()
        for _ in range(2):
            call_command("seed_library_demo")
        self.assertEqual(Loan.objects.count(), 2)
        self.assertEqual(Loan.objects.filter(returned_at=None).count(), 1)
        self.assertFalse(get_user_model().objects.get(username="demo_gorevli").has_usable_password())
