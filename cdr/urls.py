from django.urls import path

from .views import CdrExportView, CdrListView

app_name = "cdr"

urlpatterns = [
    path("", CdrListView.as_view(), name="list"),
    path("export/", CdrExportView.as_view(), name="export"),
]
