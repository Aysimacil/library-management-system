from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from accounts.roles import LIBRARIAN, MEMBER


class Command(BaseCommand):
    help = "Üye ve kütüphaneci gruplarının yetkilerini kurar."

    @transaction.atomic
    def handle(self, *args, **options):
        Group.objects.get_or_create(name=MEMBER)
        librarians, _ = Group.objects.get_or_create(name=LIBRARIAN)
        allowed = list(Permission.objects.filter(
            Q(content_type__app_label="books") |
            Q(content_type__app_label="circulation", codename__in=[
                "view_loan", "view_fine", "issue_loan", "renew_loan", "return_loan", "pay_fine",
            ])
        ))
        librarians.permissions.set(allowed)
        self.stdout.write("Kütüphane rolleri hazır.")
