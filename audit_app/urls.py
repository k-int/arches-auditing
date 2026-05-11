from django.urls import re_path, path
from django.http import HttpResponse
from audit_app.views.audit import Audit

urlpatterns = [
    path("audit/", Audit.as_view()),
]
