from netbox.api.serializers import NetBoxModelSerializer

from ..models import CloudPlatform, CloudResource, CloudService

__all__ = (
    "CloudPlatformSerializer",
    "CloudResourceSerializer",
    "CloudServiceSerializer",
)


class CloudPlatformSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudPlatform
        fields = ("id", "url", "display", "name", "label", "kind", "description",
                  "tags", "custom_fields", "created", "last_updated")
        brief_fields = ("id", "url", "display", "name", "label")


class CloudServiceSerializer(NetBoxModelSerializer):
    platform = CloudPlatformSerializer(nested=True)

    class Meta:
        model = CloudService
        fields = ("id", "url", "display", "platform", "code", "label", "category",
                  "description", "tags", "custom_fields", "created", "last_updated")
        brief_fields = ("id", "url", "display", "code", "label")


class CloudResourceSerializer(NetBoxModelSerializer):
    platform = CloudPlatformSerializer(nested=True)
    service = CloudServiceSerializer(nested=True)

    class Meta:
        model = CloudResource
        fields = ("id", "url", "display", "platform", "service", "name", "native_id",
                  "account", "region", "environment", "status", "tenant",
                  "monthly_cost", "description", "attrs", "tags", "custom_fields",
                  "created", "last_updated")
        brief_fields = ("id", "url", "display", "name", "native_id")
