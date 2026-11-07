from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from recommendations.services import RecommendationUnavailable, recommend


class Command(BaseCommand):
    help = "Explicitly opted-in live Gemini check, using catalog data and normal quotas."

    def add_arguments(self, parser):
        parser.add_argument("--live", action="store_true", help="Permit one real provider call, which may incur cost.")
        parser.add_argument("--user-id", type=int)
        parser.add_argument("--query", default="bilim")

    def handle(self, *args, **options):
        if not settings.LLM_API_KEY:
            self.stdout.write("SKIPPED: LLM_API_KEY is absent. No API call made.")
            return
        if not options["live"]:
            self.stdout.write("SKIPPED: pass --live to permit a real API call.")
            return
        if not options["user_id"]:
            raise CommandError("--user-id for an existing active account is required.")
        user = get_user_model().objects.filter(pk=options["user_id"], is_active=True).first()
        if user is None:
            raise CommandError("Active smoke-test account not found.")
        try:
            results = recommend(user, options["query"])
        except (RecommendationUnavailable, ValidationError):
            raise CommandError("Live check failed. Review provider configuration, input and quotas.") from None
        if not results:
            raise CommandError("No valid catalog recommendation was accepted. Live check is not verified.")
        self.stdout.write(f"LIVE VERIFIED: {len(results)} accepted catalog recommendation(s).")
