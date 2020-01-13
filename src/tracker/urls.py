from django.contrib import admin
from django.urls import path, include

from .views import IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="index-view"),
    path("summary/", include("summary.urls")),
    path("admin/", admin.site.urls),
]
