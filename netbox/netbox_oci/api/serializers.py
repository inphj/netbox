from netbox.api.serializers import NetBoxModelSerializer

from ..models import SecurityList, SecurityRule

__all__ = (
    "SecurityListSerializer",
    "SecurityRuleSerializer",
)


class SecurityListSerializer(NetBoxModelSerializer):
    class Meta:
        model = SecurityList
        fields = ("id", "url", "display", "name", "vcn", "tenant", "description",
                  "tags", "custom_fields", "created", "last_updated")
        brief_fields = ("id", "url", "display", "name", "vcn")


class SecurityRuleSerializer(NetBoxModelSerializer):
    security_list = SecurityListSerializer(nested=True)

    class Meta:
        model = SecurityRule
        fields = ("id", "url", "display", "security_list", "direction", "protocol",
                  "ports", "peer", "stateless", "description", "tags",
                  "custom_fields", "created", "last_updated")
        brief_fields = ("id", "url", "display", "direction", "protocol", "ports", "peer")
