from datetime import timedelta

import django_filters
from django.db.models import Q
from django.utils import timezone

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

    stale_days = django_filters.NumberFilter(
        method="filter_stale", label="N일 이상 미확인",
    )
    never_seen = django_filters.BooleanFilter(
        field_name="last_seen", lookup_expr="isnull", label="수집된 적 없음",
    )

    class Meta:
        model = CloudResource
        fields = ("id", "name", "native_id", "account", "region", "environment",
                  "status", "platform", "service", "tenant", "last_seen")

    def filter_stale(self, queryset, name, value):
        """N일 넘게 수집에서 안 보인 자원.

        한 번도 수집된 적 없는 자원(last_seen 이 빈 것)은 제외한다. 손으로 넣은
        자원이라 "사라졌다" 고 볼 근거가 없다. 그건 never_seen 으로 따로 본다.
        """
        if value in (None, ""):
            return queryset
        try:
            days = int(value)
        except (TypeError, ValueError):
            return queryset
        cutoff = timezone.now() - timedelta(days=days)
        return queryset.filter(last_seen__lt=cutoff)

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(native_id__icontains=value)
            | Q(account__icontains=value) | Q(description__icontains=value)
        )
