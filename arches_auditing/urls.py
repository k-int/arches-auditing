from django.urls import re_path, path
from arches_auditing.views.api.edit_log import ResourceEditLogAPIView

urlpatterns = [
    path(
        "api/audit/edit-log",
        ResourceEditLogAPIView.as_view(),
        name="audit-app-edit-log",
    ),
]
