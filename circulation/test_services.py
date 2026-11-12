from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.admin.sites import site
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, close_old_connections, connection, connections, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from accounts.roles import MEMBER
from books.models import Book, BookCopy
from .models import Fine, Loan
from .services import borrow_book, calculate_fine, open_day, pay_fine, renew_loan, return_book


def member(name):
    user = get_user_model().objects.create_user(username=name)
    user.groups.add(Group.objects.get_or_create(name=MEMBER)[0])
    return user


class LoanTests(TestCase):
    def setUp(self):
        self.member = member("okur")
        self.book = Book.objects.create(title="Örnek")
        self.copies = [BookCopy.objects.create(book=self.book, inventory_code=str(i)) for i in range(4)]

    def issue(self, index=0):
        return borrow_book(member_id=self.member.pk, copy_id=self.copies[index].pk)

    def test_stock_and_repeated_return(self):
        self.copies[3].delete()
        self.copies[2].delete()
        self.assertEqual(self.book.available_copy_count, 2)
        loan = self.issue()
        self.assertEqual(self.book.available_copy_count, 1)
        with self.assertRaises(ValidationError):
            self.issue()
        self.assertEqual(loan.due_date, open_day(timezone.localdate(loan.issued_at) + timedelta(days=14)))
        before = return_book(loan_id=loan.pk)
        after = return_book(loan_id=loan.pk)
        self.assertEqual(before.returned_at, after.returned_at)
        self.assertEqual(self.book.available_copy_count, 2)
        self.assertFalse(Fine.objects.exists())

    @override_settings(LIBRARY_CLOSED_DATES=["2026-11-09"])
    def test_calendar_and_renewal(self):
        self.assertEqual(open_day(date(2026, 11, 7)), date(2026, 11, 10))
        loan = self.issue()
        renewed = renew_loan(loan_id=loan.pk)
        self.assertEqual(renewed.previous_due_date, loan.due_date)
        self.assertEqual(renewed.due_date, open_day(loan.due_date + timedelta(days=7)))
        with self.assertRaises(ValidationError):
            renew_loan(loan_id=loan.pk)

    def test_limit_and_missing_copy(self):
        for index in range(3):
            self.issue(index)
        with self.assertRaises(ValidationError):
            self.issue(3)
        with self.assertRaises(BookCopy.DoesNotExist):
            borrow_book(member_id=self.member.pk, copy_id=999999)

    def test_fine_boundaries_repeated_payment_and_account_blocks(self):
        loan = self.issue()
        for days, expected in [(0, 0), (1, 5), (19, 95), (25, 100)]:
            self.assertEqual(calculate_fine(loan, loan.due_date + timedelta(days=days)), Decimal(expected))
        loan.due_date = timezone.localdate() - timedelta(days=2)
        loan.save(update_fields=["due_date"])
        with self.assertRaises(ValidationError):
            self.issue(1)
        with self.assertRaises(ValidationError):
            renew_loan(loan_id=loan.pk)
        return_book(loan_id=loan.pk)
        return_book(loan_id=loan.pk)
        fine = Fine.objects.get(loan=loan)
        self.assertEqual(fine.amount, Decimal("10"))
        with self.assertRaises(ValidationError):
            self.issue(1)
        staff = get_user_model().objects.create_superuser(username="supervisor")
        when = pay_fine(fine_id=fine.pk, actor=staff).paid_at
        self.assertEqual(pay_fine(fine_id=fine.pk, actor=staff).paid_at, when)
        self.issue(1)

    def test_rollback_if_copy_write_fails(self):
        with patch.object(BookCopy, "save", side_effect=RuntimeError), self.assertRaises(RuntimeError):
            self.issue()
        self.assertEqual(Loan.objects.count(), 0)
        self.assertEqual(self.book.available_copy_count, 4)

    def test_history_protected_after_return(self):
        loan = self.issue()
        return_book(loan_id=loan.pk)
        copy = self.copies[0]
        with self.assertRaises(ProtectedError):
            copy.delete()
        other = Book.objects.create(title="Başka")
        with self.assertRaises(IntegrityError), transaction.atomic():
            BookCopy.objects.filter(pk=copy.pk).update(book=other)
        self.assertIn("book", site._registry[BookCopy].get_readonly_fields(None, copy))

    def test_inactive_or_non_member_cannot_borrow(self):
        inactive_member = member("pasif-okur")
        inactive_member.is_active = False
        inactive_member.save(update_fields=["is_active"])
        with self.assertRaises(ValidationError):
            borrow_book(member_id=inactive_member.pk, copy_id=self.copies[0].pk)

        non_member = get_user_model().objects.create_user(username="rolsuz-kullanici")
        with self.assertRaises(ValidationError):
            borrow_book(member_id=non_member.pk, copy_id=self.copies[0].pk)

    def test_unauthorized_user_cannot_pay_fine_and_returned_loan_cannot_renew(self):
        loan = self.issue()
        loan.due_date = timezone.localdate() - timedelta(days=3)
        loan.save(update_fields=["due_date"])
        return_book(loan_id=loan.pk)

        with self.assertRaises(ValidationError):
            renew_loan(loan_id=loan.pk)

        fine = Fine.objects.get(loan=loan)
        with self.assertRaises(PermissionDenied):
            pay_fine(fine_id=fine.pk, actor=self.member)


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL row-level locks")
class ConcurrentLoanTests(TransactionTestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Eşzamanlı katalog")
        self.copy = BookCopy.objects.create(book=self.book, inventory_code="TEST-1")
        self.a = member("okur-a")
        self.b = member("okur-b")

    def race(self, jobs):
        barrier = Barrier(len(jobs), timeout=10)

        def attempt(job):
            close_old_connections()
            try:
                barrier.wait()
                job()
                return "ok"
            except ValidationError:
                return "denied"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            return list(pool.map(attempt, jobs))

    def test_double_issue(self):
        results = self.race([
            lambda: borrow_book(member_id=self.a.pk, copy_id=self.copy.pk),
            lambda: borrow_book(member_id=self.b.pk, copy_id=self.copy.pk),
        ])
        self.assertCountEqual(results, ["ok", "denied"])
        self.assertEqual(Loan.objects.filter(returned_at__isnull=True).count(), 1)
        self.copy.refresh_from_db()
        self.assertEqual(self.copy.status, BookCopy.Status.ON_LOAN)

    def test_member_limit_across_different_copies(self):
        copies = [BookCopy.objects.create(book=self.book, inventory_code=str(i)) for i in range(4)]
        for copy in copies[:2]:
            borrow_book(member_id=self.a.pk, copy_id=copy.pk)
        results = self.race([lambda c=c: borrow_book(member_id=self.a.pk, copy_id=c.pk) for c in copies[2:]])
        self.assertCountEqual(results, ["ok", "denied"])
        self.assertEqual(Loan.objects.filter(member=self.a, returned_at=None).count(), 3)

    def test_stale_admin_shelf_update_and_issue(self):
        class ShelfForm:
            changed_data = ["shelf_location"]

        self.copy.shelf_location = "R-7"

        def save_metadata():
            with transaction.atomic():
                site._registry[BookCopy].save_model(None, self.copy, ShelfForm(), True)

        self.assertEqual(self.race([
            save_metadata,
            lambda: borrow_book(member_id=self.a.pk, copy_id=self.copy.pk),
        ]), ["ok", "ok"])
        self.copy.refresh_from_db()
        self.assertEqual((self.copy.status, self.copy.shelf_location), (BookCopy.Status.ON_LOAN, "R-7"))