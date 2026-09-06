from django.urls import path

from netbox.views.generic import ObjectChangeLogView

from . import views
from .models import CloudPlatform, CloudResource, CloudService


def _crud(prefix, name, viewset, model):
    """목록/추가/일괄등록/일괄삭제/상세/편집/삭제/변경이력 8종을 한 벌로 만든다.
    모델마다 같은 8줄을 세 번 쓰면 하나만 빠뜨려도 조용히 404 가 된다."""
    return [
        path(f"{prefix}/", viewset["list"].as_view(), name=f"{name}_list"),
        path(f"{prefix}/add/", viewset["edit"].as_view(), name=f"{name}_add"),
        path(f"{prefix}/import/", viewset["import"].as_view(), name=f"{name}_import"),
        path(f"{prefix}/delete/", viewset["bulk_delete"].as_view(),
             name=f"{name}_bulk_delete"),
        path(f"{prefix}/<int:pk>/", viewset["detail"].as_view(), name=name),
        path(f"{prefix}/<int:pk>/edit/", viewset["edit"].as_view(), name=f"{name}_edit"),
        path(f"{prefix}/<int:pk>/delete/", viewset["delete"].as_view(),
             name=f"{name}_delete"),
        path(f"{prefix}/<int:pk>/changelog/", ObjectChangeLogView.as_view(),
             name=f"{name}_changelog", kwargs={"model": model}),
    ]


urlpatterns = (
    _crud("platforms", "cloudplatform", {
        "list": views.CloudPlatformListView,
        "detail": views.CloudPlatformView,
        "edit": views.CloudPlatformEditView,
        "delete": views.CloudPlatformDeleteView,
        "import": views.CloudPlatformBulkImportView,
        "bulk_delete": views.CloudPlatformBulkDeleteView,
    }, CloudPlatform)
    + _crud("services", "cloudservice", {
        "list": views.CloudServiceListView,
        "detail": views.CloudServiceView,
        "edit": views.CloudServiceEditView,
        "delete": views.CloudServiceDeleteView,
        "import": views.CloudServiceBulkImportView,
        "bulk_delete": views.CloudServiceBulkDeleteView,
    }, CloudService)
    + _crud("resources", "cloudresource", {
        "list": views.CloudResourceListView,
        "detail": views.CloudResourceView,
        "edit": views.CloudResourceEditView,
        "delete": views.CloudResourceDeleteView,
        "import": views.CloudResourceBulkImportView,
        "bulk_delete": views.CloudResourceBulkDeleteView,
    }, CloudResource)
)
