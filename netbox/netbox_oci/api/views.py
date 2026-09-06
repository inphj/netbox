from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets
from ..models import SecurityList, SecurityRule
from .serializers import SecurityListSerializer, SecurityRuleSerializer


class SecurityListViewSet(NetBoxModelViewSet):
    queryset = SecurityList.objects.select_related("tenant").prefetch_related("tags")
    serializer_class = SecurityListSerializer
    filterset_class = filtersets.SecurityListFilterSet


class SecurityRuleViewSet(NetBoxModelViewSet):
    queryset = SecurityRule.objects.select_related(
        "security_list__tenant").prefetch_related("tags")
    serializer_class = SecurityRuleSerializer
    filterset_class = filtersets.SecurityRuleFilterSet
