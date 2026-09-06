from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets
from ..models import CloudPlatform, CloudResource, CloudService
from .serializers import (CloudPlatformSerializer, CloudResourceSerializer,
                          CloudServiceSerializer)


class CloudPlatformViewSet(NetBoxModelViewSet):
    queryset = CloudPlatform.objects.prefetch_related("tags")
    serializer_class = CloudPlatformSerializer
    filterset_class = filtersets.CloudPlatformFilterSet


class CloudServiceViewSet(NetBoxModelViewSet):
    queryset = CloudService.objects.select_related("platform").prefetch_related("tags")
    serializer_class = CloudServiceSerializer
    filterset_class = filtersets.CloudServiceFilterSet


class CloudResourceViewSet(NetBoxModelViewSet):
    queryset = CloudResource.objects.select_related(
        "platform", "service", "tenant").prefetch_related("tags")
    serializer_class = CloudResourceSerializer
    filterset_class = filtersets.CloudResourceFilterSet
