from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from books.models import Book, BookCopy
from circulation.models import Fine, Loan
from .roles import MEMBER


def library_statistics(days):
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    loans = Loan.objects.all()
    active = loans.filter(returned_at__isnull=True)
    issued = loans.filter(issued_at__date__gte=start, issued_at__date__lte=today)
    returned = loans.filter(returned_at__date__gte=start, returned_at__date__lte=today)
    copies = BookCopy.objects.aggregate(total=Count("pk"), available=Count("pk", filter=Q(status=BookCopy.Status.AVAILABLE)))
    # Date grouping uses the same local timezone as circulation deadlines.
    daily_issues = dict(issued.annotate(day=TruncDate("issued_at")).values("day").annotate(count=Count("pk")).values_list("day", "count"))
    daily_returns = dict(returned.annotate(day=TruncDate("returned_at")).values("day").annotate(count=Count("pk")).values_list("day", "count"))
    activity = [
        {"day": start + timedelta(days=n), "issued": daily_issues.get(start + timedelta(days=n), 0), "returned": daily_returns.get(start + timedelta(days=n), 0)}
        for n in range(days)
    ]
    metrics = [
        ("Kitap", Book.objects.count()), ("Fiziksel kopya", copies["total"]),
        ("Müsait kopya", copies["available"]), ("Aktif ödünç", active.count()),
        ("Gecikmiş ödünç", active.filter(due_date__lt=today).count()),
        ("Üye", get_user_model().objects.filter(groups__name=MEMBER).count()),
    ]
    return {
        "metrics": metrics, "period_days": days, "activity": activity,
        "issued_total": issued.count(), "returned_total": returned.count(),
        "paid_total": Fine.objects.filter(paid_at__date__gte=start, paid_at__date__lte=today).aggregate(total=Sum("amount"))["total"] or 0,
        "outstanding_total": Fine.objects.filter(paid_at=None).aggregate(total=Sum("amount"))["total"] or 0,
        "loaned_copies": copies["total"] - copies["available"],
        "occupancy": round(100 * (copies["total"] - copies["available"]) / copies["total"]) if copies["total"] else 0,
        "recent_loans": loans.select_related("copy__book", "member")[:8],
        "popular_books": Book.objects.annotate(loan_total=Count("copies__loans")).filter(loan_total__gt=0).order_by("-loan_total", "title", "pk")[:5],
    }
