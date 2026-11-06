from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("", views.BookList.as_view(), name="list"),
    path("kitap/<int:pk>/", views.BookDetail.as_view(), name="detail"),
]
