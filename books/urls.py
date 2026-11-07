from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("kapak/<int:pk>/", views.cover, name="cover"),
    path("", views.BookList.as_view(), name="list"),
    path("kitap/<int:pk>/", views.BookDetail.as_view(), name="detail"),
]
