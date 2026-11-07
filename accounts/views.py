from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from books.models import Book, BookCopy
from circulation.models import CheckoutRequest, Fine, Loan
from circulation.services import calculate_fine
from .roles import MEMBER


def signup(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    form = UserCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()
            user.groups.add(Group.objects.get_or_create(name=MEMBER)[0])
        login(request, user)
        return redirect("accounts:profile")
    return render(request, "accounts/form.html", {"form": form, "heading": "Üyelik oluştur"})


@login_required
def profile(request):
    loans = Loan.objects.filter(member=request.user).select_related("copy__book")
    active = list(loans.filter(returned_at__isnull=True))
    today = timezone.localdate()
    for loan in active:
        loan.estimate = calculate_fine(loan, today)
    fines = Fine.objects.filter(loan__member=request.user).select_related("loan__copy__book")
    return render(request, "accounts/profile.html", {
        "active": active, "active_count": len(active), "overdue_count": sum(loan.due_date < today for loan in active), "history": loans.filter(returned_at__isnull=False),
        "fines": fines, "debt": fines.filter(paid_at__isnull=True).aggregate(total=Sum("amount"))["total"] or 0,
        "today": today, "pending": CheckoutRequest.objects.filter(member=request.user, status="PENDING").select_related("book"),
    })


@login_required
def dashboard(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    from .statistics import library_statistics

    selected = request.GET.get("days", "30")
    days = int(selected) if selected in {"7", "30", "90"} else 30
    return render(request, "accounts/dashboard.html", library_statistics(days))
