from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from io import StringIO
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from books.models import Author, Book, BookCopy, Category
from .models import CheckoutRequest, Fine, Loan


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.sections = 0

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.urls.append(dict(attrs).get("href", ""))
        if tag == "section":
            self.sections += 1

    def handle_endtag(self, tag):
        if tag == "section":
            self.sections -= 1
            if self.sections < 0:
                raise AssertionError("Unmatched closing section")


class CatalogFixture:
    def setUp(self):
        call_command("sync_library_roles", stdout=StringIO())
        self.staff = get_user_model().objects.create_user("b04-staff", is_staff=True)
        self.staff.groups.add(Group.objects.get(name="Kütüphaneci"))
        self.reader = get_user_model().objects.create_user("b04-reader")
        self.other = get_user_model().objects.create_user("b04-other")
        for member in (self.reader, self.other):
            member.groups.add(Group.objects.get(name="Üye"))
        self.staff_client = Client()
        self.staff_client.force_login(self.staff)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
        author = Author.objects.create(name="İpek Çağrı")
        category = Category.objects.create(name="Mühendislik")
        response = self.staff_client.post(reverse("books:manage-create"), {
            "title": "B04 Gökyüzü ve Işık", "authors": [author.pk], "categories": [category.pk],
        })
        self.assertEqual(response.status_code, 302)
        self.book = Book.objects.get(title="B04 Gökyüzü ve Işık")
        for n in range(3):
            response = self.staff_client.post(reverse("books:manage-copy-create", args=[self.book.pk]), {
                "inventory_code": f"B04-{n}", "shelf_location": f"A-{n}",
            })
            self.assertEqual(response.status_code, 302)
        self.copy = self.book.copies.first()

    def issue(self, client=None, member=None):
        return (client or self.staff_client).post(reverse("circulation:issue"), {
            "username": (member or self.reader).username, "inventory_code": self.copy.inventory_code,
        })


class CatalogCirculationTests(CatalogFixture, TestCase):
    def assert_stock_across_screens(self, available):
        self.assertEqual(self.book.available_copy_count, available)
        for name, client in (("books:list", self.reader_client), ("books:manage", self.staff_client)):
            response = client.get(reverse(name), {"q": self.book.title})
            self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
            self.assertEqual((response.context["books"][0].total, response.context["books"][0].available), (3, available))
        for name, client in (("books:detail", self.reader_client), ("books:manage-detail", self.staff_client)):
            response = client.get(reverse(name, args=[self.book.pk]))
            self.assertEqual((response.context["book"].total, response.context["book"].available), (3, available))
        desk = self.staff_client.get(reverse("circulation:desk"), {"copy": self.copy.inventory_code})
        self.assertContains(desk, f"{available} / 3 kopya müsait")

    def test_three_copy_request_issue_profile_return_history_and_stock(self):
        self.assert_stock_across_screens(3)
        request_url = reverse("circulation:request", args=[self.book.pk])
        self.reader_client.post(request_url)
        self.reader_client.post(request_url)
        entry = CheckoutRequest.objects.get()
        self.assertEqual(entry.status, "PENDING")
        self.assert_stock_across_screens(3)
        params = {"q": self.book.title, "member": self.reader.username}
        desk = self.staff_client.get(reverse("circulation:desk"), params)
        self.assertEqual(desk.context["overview"]["pending"], 1)
        links = Links()
        links.feed(desk.content.decode())
        self.assertEqual(links.sections, 0)
        choice = next(link for link in links.urls if link.startswith("?copy=" + self.copy.inventory_code))
        selected = self.staff_client.get(reverse("circulation:desk") + choice)
        self.assertEqual(selected.context["form"].initial["username"], self.reader.username)
        self.assertEqual(selected.context["form"].initial["inventory_code"], self.copy.inventory_code)
        self.assertEqual(self.issue().status_code, 302)
        loan = Loan.objects.get()
        entry.refresh_from_db()
        self.assertEqual((entry.status, entry.loan_id), ("FULFILLED", loan.pk))
        self.assert_stock_across_screens(2)
        profile = self.reader_client.get(reverse("accounts:profile"))
        self.assertEqual([item.pk for item in profile.context["active"]], [loan.pk])
        desk = self.staff_client.get(reverse("circulation:desk"))
        self.assertEqual(desk.context["overview"], {"active": 1, "overdue": 0, "pending": 0})
        self.assertEqual(self.staff_client.post(reverse("circulation:return", args=[loan.pk])).status_code, 302)
        self.assert_stock_across_screens(3)
        profile = self.reader_client.get(reverse("accounts:profile"))
        self.assertEqual(profile.context["active_count"], 0)
        self.assertEqual(list(profile.context["history"].values_list("pk", flat=True)), [loan.pk])
        self.assertEqual(Loan.objects.count(), 1)
        self.assertEqual(self.staff_client.get(reverse("circulation:desk")).context["overview"]["active"], 0)

    def test_repeated_old_return_does_not_change_new_loan_or_stock(self):
        self.issue()
        old = Loan.objects.get()
        url = reverse("circulation:return", args=[old.pk])
        self.staff_client.post(url)
        old.refresh_from_db()
        returned_at = old.returned_at
        self.staff_client.post(url)
        self.assert_stock_across_screens(3)
        self.issue(member=self.other)
        self.staff_client.post(url)
        self.assert_stock_across_screens(2)
        old.refresh_from_db()
        self.assertEqual(old.returned_at, returned_at)
        self.assertEqual(Loan.objects.filter(returned_at=None).count(), 1)
        self.assertEqual(Fine.objects.count(), 0)

    def test_shelf_edit_and_unavailable_selection_do_not_override_active_loan(self):
        self.issue()
        self.staff_client.post(reverse("books:manage-shelf", args=[self.copy.pk]), {
            "shelf_location": "R-99", "status": "AVAILABLE", "inventory_code": "CHANGED",
        })
        self.copy.refresh_from_db()
        self.assertEqual((self.copy.status, self.copy.shelf_location), ("ON_LOAN", "R-99"))
        self.assert_stock_across_screens(2)
        response = self.staff_client.get(reverse("circulation:desk"), {"q": self.book.title, "member": self.other.username})
        links = Links()
        links.feed(response.content.decode())
        self.assertEqual(links.sections, 0)
        self.assertFalse(any(link.startswith("?copy=" + self.copy.inventory_code + "&") for link in links.urls))
        self.assertContains(response, "Teslime uygun değil")
        failed = self.issue(member=self.other)
        self.assertEqual(failed.status_code, 400)
        self.assertContains(failed, "zaten ödünçte", status_code=400)
        self.assertEqual(Loan.objects.count(), 1)
        self.assert_stock_across_screens(2)

    def test_copy_write_failure_rolls_back_loan_request_and_stock(self):
        self.reader_client.post(reverse("circulation:request", args=[self.book.pk]))
        with patch.object(BookCopy, "save", side_effect=RuntimeError("test-only failure")):
            with self.assertRaises(RuntimeError):
                self.issue()
        self.assertFalse(Loan.objects.exists())
        entry = CheckoutRequest.objects.get()
        self.assertEqual((entry.status, entry.loan_id), ("PENDING", None))
        self.assert_stock_across_screens(3)


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL row locks")
class CatalogCirculationRaceTests(CatalogFixture, TransactionTestCase):
    def race(self, *jobs):
        barrier = Barrier(len(jobs), timeout=10)

        def run(job):
            close_old_connections()
            try:
                barrier.wait()
                return job().status_code
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            return list(pool.map(run, jobs))

    def second_staff_client(self):
        client = Client()
        client.force_login(self.staff)
        return client

    def test_two_http_issues_of_same_copy_only_one_succeeds(self):
        second = self.second_staff_client()
        results = self.race(lambda: self.issue(), lambda: self.issue(second, self.other))
        self.assertCountEqual(results, [302, 400])
        self.assertEqual(Loan.objects.filter(copy=self.copy, returned_at=None).count(), 1)
        self.assertEqual(self.book.available_copy_count, 2)

    def test_http_shelf_update_and_issue_preserve_both_changes(self):
        second = self.second_staff_client()
        results = self.race(
            lambda: self.issue(),
            lambda: second.post(reverse("books:manage-shelf", args=[self.copy.pk]), {
                "shelf_location": "R-CONCURRENT", "status": "AVAILABLE",
            }),
        )
        self.assertEqual(results, [302, 302])
        self.copy.refresh_from_db()
        self.assertEqual((self.copy.status, self.copy.shelf_location), ("ON_LOAN", "R-CONCURRENT"))
        self.assertEqual(Loan.objects.filter(copy=self.copy, returned_at=None).count(), 1)
        self.assertEqual(self.book.available_copy_count, 2)
