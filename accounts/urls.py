from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("giris/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("cikis/", LogoutView.as_view(), name="logout"),
    path("kayit/", views.signup, name="signup"),
    path("profil/", views.profile, name="profile"),
    path("yonetim/", views.dashboard, name="dashboard"),
]
