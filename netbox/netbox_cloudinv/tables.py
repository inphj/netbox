import django_tables2 as tables

from netbox.tables import NetBoxTable, columns

from .models import CloudPlatform, CloudResource, CloudService


class CloudPlatformTable(NetBoxTable):
    label = tables.Column(linkify=True, verbose_name="표시명")
    name = tables.Column(verbose_name="코드")
    kind = columns.ChoiceFieldColumn(verbose_name="구분")
    service_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_cloudinv:cloudservice_list",
        url_params={"platform_id": "pk"}, verbose_name="서비스",
    )
    resource_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_cloudinv:cloudresource_list",
        url_params={"platform_id": "pk"}, verbose_name="자원",
    )

    class Meta(NetBoxTable.Meta):
        model = CloudPlatform
        fields = ("pk", "id", "label", "name", "kind", "service_count",
                  "resource_count", "description")
        default_columns = ("label", "name", "kind", "service_count", "resource_count")


class CloudServiceTable(NetBoxTable):
    code = tables.Column(linkify=True, verbose_name="코드")
    platform = tables.Column(linkify=True, verbose_name="플랫폼")
    label = tables.Column(verbose_name="표시명")
    category = columns.ChoiceFieldColumn(verbose_name="분류")
    resource_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_cloudinv:cloudresource_list",
        url_params={"service_id": "pk"}, verbose_name="자원",
    )

    class Meta(NetBoxTable.Meta):
        model = CloudService
        fields = ("pk", "id", "platform", "code", "label", "category",
                  "resource_count", "description")
        default_columns = ("platform", "code", "label", "category", "resource_count")


class CloudResourceTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name="이름")
    platform = tables.Column(linkify=True, verbose_name="플랫폼")
    service = tables.Column(linkify=True, verbose_name="서비스")
    # 관계 너머의 choice 라 ChoiceFieldColumn 이 라벨을 못 찾는다. 모델의
    # get_..._display 를 직접 부른다 - 아니면 "compute" 같은 raw 값이 찍힌다.
    category = tables.Column(accessor="service__get_category_display",
                             verbose_name="분류", orderable=False)
    account = tables.Column(verbose_name="계정")
    region = tables.Column(verbose_name="리전")
    environment = tables.Column(verbose_name="환경")
    status = columns.ChoiceFieldColumn(verbose_name="상태")
    tenant = tables.Column(linkify=True, verbose_name="소유")
    monthly_cost = tables.Column(verbose_name="월 비용")
    native_id = tables.Column(verbose_name="자원 ID")

    class Meta(NetBoxTable.Meta):
        model = CloudResource
        fields = ("pk", "id", "name", "platform", "service", "category", "account",
                  "region", "environment", "status", "tenant", "monthly_cost",
                  "native_id", "description")
        default_columns = ("name", "platform", "service", "account", "region",
                           "environment", "status")
