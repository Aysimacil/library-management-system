from django.urls import path
from . import views

app_name = "circulation"
urlpatterns = [
    path("", views.desk, name="desk"),
    path("teslim/", views.issue, name="issue"),
    path("iade/<int:pk>/", views.accept_return, name="return"),
    path("uzat/<int:pk>/", views.extend, name="renew"),
    path("kendi-oduncumu-uzat/<int:pk>/", views.member_renew, name="member-renew"),
    path("odeme/<int:pk>/", views.payment, name="pay"),
    path("talep/<int:pk>/", views.request_book, name="request"),
    path("talep-iptal/<int:pk>/", views.cancel_request, name="cancel"),
]
