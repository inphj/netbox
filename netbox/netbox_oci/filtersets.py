import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from .models import SecurityList, SecurityRule


class SecurityListFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = SecurityList
        fields = ("id", "name", "vcn", "tenant")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(vcn__icontains=value)
            | Q(description__icontains=value)
        )


class SecurityRuleFilterSet(NetBoxModelFilterSet):
    # 이게 핵심이다 - "22번이 열린 규칙 전부" 를 물을 수 있어야 한다.
    port = django_filters.CharFilter(
        method="filter_port", label="포트(범위 포함)",
    )

    class Meta:
        model = SecurityRule
        fields = ("id", "direction", "protocol", "ports", "peer", "stateless",
                  "security_list")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(peer__icontains=value) | Q(ports__icontains=value)
            | Q(protocol__icontains=value) | Q(description__icontains=value)
        )

    def filter_port(self, queryset, name, value):
        """단일 포트를 넣으면 '22' 뿐 아니라 '20-30' 같은 범위도 잡는다."""
        try:
            want = int(value)
        except (TypeError, ValueError):
            return queryset.filter(ports__icontains=value)
        keep = []
        for r in queryset:
            p = (r.ports or "").strip()
            if not p:
                keep.append(r.pk)          # 빈 값은 전체 허용
                continue
            if "-" in p:
                try:
                    lo, hi = (int(x) for x in p.split("-", 1))
                    if lo <= want <= hi:
                        keep.append(r.pk)
                except ValueError:
                    pass
            elif p == str(want):
                keep.append(r.pk)
        return queryset.filter(pk__in=keep)
