from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render

from books.models import Category

from .services import RecommendationUnavailable, recommend


class PreferenceForm(forms.Form):
    query = forms.CharField(max_length=500, label="Hangi türde bir kitap arıyorsunuz?",
                            help_text="Bir konu, yazar veya tür girin. Kişisel bilgilerinizi paylaşmayın.")
    category = forms.ModelChoiceField(label="İlgilendiğin kategori", queryset=Category.objects.all(), required=False, empty_label="Tüm kategoriler")
    excluded_category = forms.ModelChoiceField(label="Hariç tut", queryset=Category.objects.all(), required=False, empty_label="Yok")
    available_only = forms.BooleanField(label="Yalnızca müsait kitaplar", required=False)
    reading_level = forms.ChoiceField(label="Okuma düzeyi", required=False, choices=[
        ("any", "Fark etmez"), ("introductory", "Konuya yeni başlıyorum"), ("advanced", "Derinlemesine okumak istiyorum"),
    ])

    def clean(self):
        data = super().clean()
        if data.get("category") and data.get("category") == data.get("excluded_category"):
            self.add_error("excluded_category", "Aynı kategori seçilip hariç tutulamaz.")
        return data


@login_required
def index(request):
    form = PreferenceForm(request.POST if request.method == "POST" else None)
    results = None
    if request.method == "POST" and form.is_valid():
        try:
            results = recommend(
                request.user, form.cleaned_data["query"], category=form.cleaned_data["category"],
                excluded_category=form.cleaned_data["excluded_category"],
                available_only=form.cleaned_data["available_only"], reading_level=form.cleaned_data["reading_level"] or "any",
            )
        except (RecommendationUnavailable, ValidationError) as exc:
            form.add_error(None, exc if isinstance(exc, ValidationError) else str(exc))
    return render(request, "recommendations/index.html", {"form": form, "results": results})
