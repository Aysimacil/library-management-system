from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render

from .services import RecommendationUnavailable, recommend


class PreferenceForm(forms.Form):
    query = forms.CharField(max_length=500, label="Hangi türde bir kitap arıyorsunuz?",
                            help_text="Bir konu, yazar veya tür girin. Kişisel bilgilerinizi paylaşmayın.")


@login_required
def index(request):
    form = PreferenceForm(request.POST if request.method == "POST" else None)
    results = None
    if request.method == "POST" and form.is_valid():
        try:
            results = recommend(request.user, form.cleaned_data["query"])
        except (RecommendationUnavailable, ValidationError) as exc:
            form.add_error(None, exc if isinstance(exc, ValidationError) else str(exc))
    return render(request, "recommendations/index.html", {"form": form, "results": results})
