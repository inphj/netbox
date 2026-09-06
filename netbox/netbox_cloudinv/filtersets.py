import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from .models import (CloudPlatform, CloudResource, CloudService,
                     ServiceCategory)


class CloudPlatformFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = CloudPlatform
        fields = ("id", "name", "label", "kind")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(label__icontains=value)
            | Q(description__icontains=value)
        )


class CloudServiceFilterSet(NetBoxModelFilterSet):
    platform_id = django_filters.ModelMultipleChoiceFilter(
        field_name="platform", queryset=CloudPlatform.objects.all(), label="플랫폼",
    )

    class Meta:
        model = CloudService
        fields = ("id", "code", "label", "category", "platform")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(code__icontains=value) | Q(label__icontains=value)
            | Q(description__icontains=value)
        )


class CloudResourceFilterSet(NetBoxModelFilterSet):
    platform_id = django_filters.ModelMultipleChoiceFilter(
        field_name="platform", queryset=CloudPlatform.objects.all(), label="플랫폼",
    )
    service_id = django_filters.ModelMultipleChoiceFilter(
        field_name="service", queryset=CloudService.objects.all(), label="서비스",
    )
    category = django_filters.MultipleChoiceFilter(
        field_name="service__category", choices=ServiceCategory.choices,
        label="분류",
    )

    class Meta:
        model = CloudResource
        fields = ("id", "name", "native_id", "account", "region", "environment",
                  "status", "platform", "service", "tenant")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(native_id__icontains=value)
            | Q(account__icontains=value) | Q(description__icontains=value)
        )
