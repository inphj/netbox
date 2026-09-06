from django import forms

from netbox.forms import (NetBoxModelFilterSetForm, NetBoxModelForm,
                          NetBoxModelImportForm)
from tenancy.models import Tenant
from utilities.forms.fields import (CSVChoiceField, CSVModelChoiceField,
                                    DynamicModelChoiceField,
                                    DynamicModelMultipleChoiceField)

from .models import (CloudPlatform, CloudResource, CloudService, PlatformKind,
                     ResourceStatus, ServiceCategory)

# --------------------------------------------------------------------------
# 플랫폼
# --------------------------------------------------------------------------


class CloudPlatformForm(NetBoxModelForm):
    class Meta:
        model = CloudPlatform
        fields = ("name", "label", "kind", "description", "tags")


class CloudPlatformFilterForm(NetBoxModelFilterSetForm):
    model = CloudPlatform
    kind = forms.ChoiceField(
        choices=[("", "---")] + list(PlatformKind.choices), required=False,
        label="구분",
    )


class CloudPlatformImportForm(NetBoxModelImportForm):
    kind = CSVChoiceField(choices=PlatformKind.choices, required=False, label="구분")

    class Meta:
        model = CloudPlatform
        fields = ("name", "label", "kind", "description")


# --------------------------------------------------------------------------
# 서비스 카탈로그
# --------------------------------------------------------------------------


class CloudServiceForm(NetBoxModelForm):
    platform = DynamicModelChoiceField(
        queryset=CloudPlatform.objects.all(), label="플랫폼",
    )

    class Meta:
        model = CloudService
        fields = ("platform", "code", "label", "category", "description", "tags")


class CloudServiceFilterForm(NetBoxModelFilterSetForm):
    model = CloudService
    platform_id = DynamicModelMultipleChoiceField(
        queryset=CloudPlatform.objects.all(), required=False, label="플랫폼",
    )
    category = forms.MultipleChoiceField(
        choices=ServiceCategory.choices, required=False, label="분류",
    )


class CloudServiceImportForm(NetBoxModelImportForm):
    platform = CSVModelChoiceField(
        queryset=CloudPlatform.objects.all(), to_field_name="name", label="플랫폼",
        help_text="플랫폼 코드 (aws, azure)",
    )
    category = CSVChoiceField(
        choices=ServiceCategory.choices, required=False, label="분류",
    )

    class Meta:
        model = CloudService
        fields = ("platform", "code", "label", "category", "description")


# --------------------------------------------------------------------------
# 자원
# --------------------------------------------------------------------------


class CloudResourceForm(NetBoxModelForm):
    platform = DynamicModelChoiceField(
        queryset=CloudPlatform.objects.all(), label="플랫폼",
    )
    service = DynamicModelChoiceField(
        queryset=CloudService.objects.all(), label="서비스",
        query_params={"platform_id": "$platform"},
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(), required=False, label="소유",
    )

    class Meta:
        model = CloudResource
        fields = ("platform", "service", "name", "native_id", "account", "region",
                  "environment", "status", "tenant", "monthly_cost", "description",
                  "attrs", "tags")

    def clean_attrs(self):
        """빈 값이면 JSONField 가 None 을 돌려주는데 모델 컬럼은 NOT NULL 이다.

        그대로 저장하면 IntegrityError 로 500 이 난다. attrs 는 선택 항목이고
        대부분의 행이 비어 있을 것이므로, 이걸 안 막으면 **가장 흔한 입력
        경로가 깨진다.** 실측으로 잡았다.
        """
        value = self.cleaned_data.get("attrs")
        return {} if value is None else value


class CloudResourceFilterForm(NetBoxModelFilterSetForm):
    model = CloudResource
    platform_id = DynamicModelMultipleChoiceField(
        queryset=CloudPlatform.objects.all(), required=False, label="플랫폼",
    )
    service_id = DynamicModelMultipleChoiceField(
        queryset=CloudService.objects.all(), required=False, label="서비스",
    )
    category = forms.MultipleChoiceField(
        choices=ServiceCategory.choices, required=False, label="분류",
    )
    status = forms.MultipleChoiceField(
        choices=ResourceStatus.choices, required=False, label="상태",
    )
    account = forms.CharField(required=False, label="계정")
    region = forms.CharField(required=False, label="리전")
    environment = forms.CharField(required=False, label="환경")
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(), required=False, label="소유",
    )


class CloudResourceImportForm(NetBoxModelImportForm):
    """CSV 일괄 등록. 손으로 채우는 것이 주 경로이므로 처음부터 넣는다."""

    platform = CSVModelChoiceField(
        queryset=CloudPlatform.objects.all(), to_field_name="name", label="플랫폼",
        help_text="플랫폼 코드 (aws, azure)",
    )
    service = CSVModelChoiceField(
        queryset=CloudService.objects.all(), to_field_name="code", label="서비스",
        help_text="서비스 코드 (ec2, s3 ...). 플랫폼 안에서 유일해야 한다",
    )
    status = CSVChoiceField(
        choices=ResourceStatus.choices, required=False, label="상태",
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(), to_field_name="name", required=False,
        label="소유",
    )

    class Meta:
        model = CloudResource
        fields = ("platform", "service", "name", "native_id", "account", "region",
                  "environment", "status", "tenant", "monthly_cost", "description")

    def clean(self):
        """서비스 코드는 플랫폼 안에서만 유일하다. 다른 플랫폼의 같은 코드가
        섞이면 조용히 엉뚱한 서비스에 붙으므로 여기서 막는다."""
        super().clean()
        platform = self.cleaned_data.get("platform")
        service = self.cleaned_data.get("service")
        if platform and service and service.platform_id != platform.pk:
            raise forms.ValidationError(
                {"service": f"서비스 '{service.code}' 는 플랫폼 "
                            f"'{platform.name}' 에 속하지 않는다"}
            )
        return self.cleaned_data
