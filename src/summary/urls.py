from .views import SummaryView
from django.urls import path

urlpatterns = [
    path("", SummaryView.as_view(), name="summary-view"),
]
