from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.roles import MEMBER
from books.models import Book, BookCopy
from circulation.models import Fine, Loan
from .statistics import library_statistics


class StatisticsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("reader")
        self.user.groups.add(Group.objects.get_or_create(name=MEMBER)[0])
        self.book = Book.objects.create(title="Gerçek hareket")
        self.copies = [BookCopy.objects.create(book=self.book, inventory_code=str(i)) for i in range(3)]
        now = timezone.now()
        old = now - timedelta(days=40)
        self.active = Loan.objects.create(member=self.user, copy=self.copies[0], issued_at=old, due_date=timezone.localdate() - timedelta(days=1))
        BookCopy.objects.filter(pk=self.copies[0].pk).update(status=BookCopy.Status.ON_LOAN)
        closed = Loan.objects.create(member=self.user, copy=self.copies[1], issued_at=now-timedelta(days=2), due_date=timezone.localdate(), returned_at=now)
        Fine.objects.create(loan=closed, amount=Decimal("15"), paid_at=now, paid_by=self.user)
        Fine.objects.create(loan=self.active, amount=Decimal("5"))

    def test_counts_periods_and_stock_are_database_derived(self):
        stats = library_statistics(7)
        self.assertEqual((stats["issued_total"], stats["returned_total"]), (1, 1))
        self.assertEqual(sum(row["issued"] for row in stats["activity"]), 1)
        self.assertEqual(sum(row["returned"] for row in stats["activity"]), 1)
        self.assertEqual(stats["paid_total"], Decimal("15"))
        self.assertEqual(stats["outstanding_total"], Decimal("5"))
        self.assertIn(("Gecikmiş ödünç", 1), stats["metrics"])
        self.assertEqual(stats["occupancy"], 33)
        self.assertEqual(list(stats["popular_books"])[0].loan_total, 2)

    def test_admin_only_and_empty_database(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("accounts:dashboard")).status_code, 403)
        admin = get_user_model().objects.create_superuser(username="admin")
        self.client.force_login(admin)
        page = self.client.get(reverse("accounts:dashboard"), {"days": "7"})
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.context["period_days"], 7)
        self.assertEqual(self.client.get(reverse("accounts:dashboard"), {"days": "bogus"}).context["period_days"], 30)
