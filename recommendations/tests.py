import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from books.models import Book, BookCopy
from .models import UsageWindow
from .services import RecommendationUnavailable, recommend, reserve_call


@override_settings(LLM_PROVIDER="gemini", LLM_MODEL="test-model", LLM_API_KEY="unit-test-only")
class RecommendationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("private_reader")
        self.book = Book.objects.create(title="Gökyüzü", description="Yıldızlar ve astronomi")
        BookCopy.objects.create(book=self.book, inventory_code="K-1")

    @patch("recommendations.services.http.client.HTTPSConnection")
    def test_only_catalog_payload_and_existing_candidates(self, connection):
        excluded = Book.objects.create(title="Yemek")
        response = connection.return_value.getresponse.return_value
        response.status = 200
        response.read.return_value = json.dumps({"candidates": [{"content": {"parts": [
            {"text": json.dumps([{"id": excluded.pk, "summary": "uydurma"},
                                 {"id": self.book.pk, "summary": "Astronomi"}])}
        ]}}]}).encode()
        self.client.force_login(self.user)
        page = self.client.post(reverse("recommendations:index"), {"query": "astronomi gizli-tercih"})
        self.assertContains(page, "Gökyüzü")
        self.assertNotContains(page, "uydurma")
        connection.assert_called_once_with("generativelanguage.googleapis.com", timeout=10)
        sent = connection.return_value.request.call_args.args[2]
        self.assertNotIn(self.user.username, sent)
        self.assertNotIn("gizli-tercih", sent)

    @patch("recommendations.services.fetch_suggestions")
    def test_contact_and_length_rejected_before_external_call(self, provider):
        for term in ("okur@example.org", "0500 000 00 00", "x" * 501):
            with self.assertRaises(ValidationError):
                recommend(self.user, term)
        provider.assert_not_called()

    @override_settings(LLM_API_KEY="")
    def test_missing_key_degrades_without_breaking_catalog(self):
        self.client.force_login(self.user)
        self.assertContains(self.client.post(reverse("recommendations:index"), {"query": "astronomi"}), "yapılandırılmamış")
        self.assertEqual(self.client.get(reverse("books:list")).status_code, 200)

    @patch("recommendations.services.http.client.HTTPSConnection")
    def test_timeout_and_bad_payload_do_not_leak_provider_details(self, conn):
        with self.assertRaises(RecommendationUnavailable):
            conn.return_value.request.side_effect = TimeoutError("secret")
            recommend(self.user, "astronomi")
        conn.return_value.request.side_effect = None
        response = conn.return_value.getresponse.return_value
        response.status, response.read.return_value = 200, b"{}"
        with self.assertRaises(RecommendationUnavailable):
            recommend(self.user, "astronomi")

    def test_minute_day_and_global_quota(self):
        for _ in range(5):
            reserve_call(self.user.pk)
        with self.assertRaises(RecommendationUnavailable):
            reserve_call(self.user.pk)
        self.assertEqual(UsageWindow.objects.get(scope="all").used, 5)
        UsageWindow.objects.filter(scope__endswith=":day").update(used=20)
        UsageWindow.objects.filter(scope__endswith=":minute").update(used=0)
        with self.assertRaises(RecommendationUnavailable):
            reserve_call(self.user.pk)
        UsageWindow.objects.filter(scope="all").update(used=100, window=timezone.localdate().isoformat())
        with self.assertRaises(RecommendationUnavailable):
            reserve_call(self.user.pk)

    def test_anonymous_user_redirected(self):
        self.assertEqual(self.client.get(reverse("recommendations:index")).status_code, 302)

    @patch("recommendations.services.fetch_suggestions")
    def test_safe_topics_and_preferences_guide_provider(self, provider):
        from books.models import Category
        topic = Category.objects.create(name="Astronomi")
        self.book.categories.add(topic)
        provider.return_value = [{"id": self.book.pk, "summary": "Yıldızları tanımak için uygun."}]
        results = recommend(self.user, "Bana ASTRONOMİ hakkında bir kitap öner gizliözelbilgi",
                            category=topic, available_only=True, reading_level="introductory")
        self.assertEqual(results[0][0].pk, self.book.pk)
        preferences = provider.call_args.kwargs["preferences"]
        self.assertEqual(preferences["reading_level"], "introductory")
        self.assertIn("Astronomi", preferences["catalog_topics"])
        self.assertNotIn("gizliözelbilgi", json.dumps(provider.call_args.args))
        self.assertNotIn("gizliözelbilgi", json.dumps(preferences))
        self.assertEqual(preferences["category"], topic.name)

    def test_ranking_exclusions_and_stock_happen_before_provider(self):
        from books.models import Category
        from .services import candidate_books
        target = Book.objects.create(title="Astronomi rehberi")
        excluded = Category.objects.create(name="Ders kitabı")
        target.categories.add(excluded)
        candidates, _ = candidate_books("astronomi")
        self.assertEqual(candidates[0].pk, target.pk)
        candidates, _ = candidate_books("astronomi", excluded_category=excluded, available_only=True)
        self.assertEqual([b.pk for b in candidates], [self.book.pk])

    @patch("recommendations.services.fetch_suggestions")
    def test_unknown_query_and_invalid_filter_do_not_spend_quota(self, provider):
        self.assertEqual(recommend(self.user, "olmayanbirbaşlık"), [])
        self.assertFalse(UsageWindow.objects.exists())
        provider.assert_not_called()
        self.client.force_login(self.user)
        page = self.client.post(reverse("recommendations:index"), {"query": "astronomi", "category": "999999"})
        self.assertTrue(page.context["form"].errors)
