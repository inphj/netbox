from django.urls import path

from netbox.views.generic import ObjectChangeLogView

from . import views
from .models import SecurityList, SecurityRule

urlpatterns = [
    path("security-lists/", views.SecurityListListView.as_view(), name="securitylist_list"),
    path("security-lists/add/", views.SecurityListEditView.as_view(), name="securitylist_add"),
    path("security-lists/<int:pk>/", views.SecurityListView.as_view(), name="securitylist"),
    path("security-lists/<int:pk>/edit/", views.SecurityListEditView.as_view(), name="securitylist_edit"),
    path("security-lists/<int:pk>/delete/", views.SecurityListDeleteView.as_view(), name="securitylist_delete"),
    path("security-lists/<int:pk>/changelog/", ObjectChangeLogView.as_view(),
         name="securitylist_changelog", kwargs={"model": SecurityList}),

    path("security-rules/", views.SecurityRuleListView.as_view(), name="securityrule_list"),
    path("security-rules/add/", views.SecurityRuleEditView.as_view(), name="securityrule_add"),
    path("security-rules/<int:pk>/", views.SecurityRuleView.as_view(), name="securityrule"),
    path("security-rules/<int:pk>/edit/", views.SecurityRuleEditView.as_view(), name="securityrule_edit"),
    path("security-rules/<int:pk>/delete/", views.SecurityRuleDeleteView.as_view(), name="securityrule_delete"),
    path("security-rules/<int:pk>/changelog/", ObjectChangeLogView.as_view(),
         name="securityrule_changelog", kwargs={"model": SecurityRule}),
]
