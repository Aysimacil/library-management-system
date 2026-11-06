from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.roles import LIBRARIAN, MEMBER
from books.models import BookCopy
from circulation.services import borrow_book, return_book


class Command(BaseCommand):
    help = "Yerel demo için örnek üyeyi, personeli, aktif ve iade edilmiş ödünçleri kurar."

    @transaction.atomic
    def handle(self, *args, **options):
        if settings.PRODUCTION:
            raise CommandError("Bu komut yalnız yerel geliştirme içindir.")
        call_command("sync_library_roles", stdout=self.stdout)
        call_command("seed_catalog", stdout=self.stdout)
        marker, _ = Group.objects.get_or_create(name="Yerel demo kullanıcıları")
        reader = self.demo_user("demo_okur", MEMBER, marker)
        self.demo_user("demo_gorevli", LIBRARIAN, marker)
        for number in (1, 2):
            source = BookCopy.objects.get(inventory_code=f"DEMO-KAT-{number:02}")
            copy, _ = BookCopy.objects.get_or_create(
                inventory_code=f"DEMO-ISLEM-{number:02}", defaults={"book": source.book},
            )
            if copy.book_id != source.book_id:
                raise CommandError("Demo demirbaş kodu başka bir kitaba ait.")
            if not copy.loans.exists():
                loan = borrow_book(member_id=reader.pk, copy_id=copy.pk)
                if number == 2:
                    return_book(loan_id=loan.pk)
        self.stdout.write("Demo hazır. Demo hesabına yerel parola vermek için changepassword kullanın.")

    def demo_user(self, username, role, marker):
        user, created = get_user_model().objects.get_or_create(username=username)
        if not created:
            if not user.groups.filter(pk=marker.pk).exists():
                raise CommandError(f"{username} demo dışındaki bir hesaba ait.")
            return user
        user.set_unusable_password()
        user.is_staff = role == LIBRARIAN
        user.save(update_fields=["password", "is_staff"])
        user.groups.add(marker, Group.objects.get(name=role))
        return user
