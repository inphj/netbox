from django import forms

from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from tenancy.models import Tenant

from .models import Direction, SecurityList, SecurityRule


class SecurityListForm(NetBoxModelForm):
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), label="테넌시")

    class Meta:
        model = SecurityList
        fields = ("name", "vcn", "tenant", "description", "tags")


class SecurityListFilterForm(NetBoxModelFilterSetForm):
    model = SecurityList
    vcn = forms.CharField(required=False, label="VCN")
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(), required=False, label="테넌시",
    )


class SecurityRuleForm(NetBoxModelForm):
    security_list = DynamicModelChoiceField(
        queryset=SecurityList.objects.all(), label="보안목록",
    )

    class Meta:
        model = SecurityRule
        fields = ("security_list", "direction", "protocol", "ports", "peer",
                  "stateless", "description", "tags")


class SecurityRuleFilterForm(NetBoxModelFilterSetForm):
    model = SecurityRule
    port = forms.CharField(
        required=False, label="포트",
        help_text="숫자를 넣으면 20-30 같은 범위 규칙도 함께 잡는다",
    )
    direction = forms.ChoiceField(
        choices=[("", "---")] + list(Direction.choices), required=False, label="방향",
    )
    protocol = forms.CharField(required=False, label="프로토콜")
    peer = forms.CharField(required=False, label="상대")
