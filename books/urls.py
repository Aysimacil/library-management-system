from django.urls import path

from . import views, management_views as manage

app_name = "books"

urlpatterns = [
    path("katalog-yonetimi/", manage.CatalogManagement.as_view(), name="manage"),
    path("katalog-yonetimi/yeni/", manage.book_create, name="manage-create"),
    path("katalog-yonetimi/kitap/<int:pk>/", manage.book_detail, name="manage-detail"),
    path("katalog-yonetimi/kitap/<int:pk>/duzenle/", manage.book_edit, name="manage-edit"),
    path("katalog-yonetimi/kitap/<int:pk>/kopya-ekle/", manage.copy_create, name="manage-copy-create"),
    path("katalog-yonetimi/kopya/<int:pk>/raf/", manage.shelf_edit, name="manage-shelf"),
    path("katalog-yonetimi/<str:kind>/", manage.taxonomy, name="manage-taxonomy"),
    path("katalog-yonetimi/<str:kind>/yeni/", manage.taxonomy, {"create": True}, name="manage-taxonomy-create"),
    path("katalog-yonetimi/<str:kind>/<int:pk>/", manage.taxonomy, name="manage-taxonomy-edit"),
    path("kapak/<int:pk>/", views.cover, name="cover"),
    path("", views.BookList.as_view(), name="list"),
    path("kitap/<int:pk>/", views.BookDetail.as_view(), name="detail"),
]
