from django.utils import timezone

from netbox.views import generic
from utilities.query import count_related

from . import filtersets, forms, tables
from .models import CloudPlatform, CloudResource, CloudService

# --------------------------------------------------------------------------
# 플랫폼
# --------------------------------------------------------------------------


class CloudPlatformListView(generic.ObjectListView):
    # LinkedCountColumn 은 annotate 된 값을 읽는다. 안 걸면 default=0 이 그대로
    # 찍혀 서비스가 49개인데 화면에 0 으로 나온다 (실측으로 잡음).
    queryset = CloudPlatform.objects.annotate(
        service_count=count_related(CloudService, "platform"),
        resource_count=count_related(CloudResource, "platform"),
    )
    table = tables.CloudPlatformTable
    filterset = filtersets.CloudPlatformFilterSet
    filterset_form = forms.CloudPlatformFilterForm


class CloudPlatformView(generic.ObjectView):
    queryset = CloudPlatform.objects.all()

    def get_extra_context(self, request, instance):
        services = CloudService.objects.filter(platform=instance).annotate(
            resource_count=count_related(CloudResource, "service"))
        t = tables.CloudServiceTable(services)
        t.configure(request)
        return {"services_table": t}


class CloudPlatformEditView(generic.ObjectEditView):
    queryset = CloudPlatform.objects.all()
    form = forms.CloudPlatformForm


class CloudPlatformDeleteView(generic.ObjectDeleteView):
    queryset = CloudPlatform.objects.all()


class CloudPlatformBulkImportView(generic.BulkImportView):
    queryset = CloudPlatform.objects.all()
    model_form = forms.CloudPlatformImportForm


class CloudPlatformBulkEditView(generic.BulkEditView):
    queryset = CloudPlatform.objects.all()
    filterset = filtersets.CloudPlatformFilterSet
    table = tables.CloudPlatformTable
    form = forms.CloudPlatformBulkEditForm


class CloudPlatformBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudPlatform.objects.all()
    table = tables.CloudPlatformTable


# --------------------------------------------------------------------------
# 서비스 카탈로그
# --------------------------------------------------------------------------


class CloudServiceListView(generic.ObjectListView):
    queryset = CloudService.objects.select_related("platform").annotate(
        resource_count=count_related(CloudResource, "service"),
    )
    table = tables.CloudServiceTable
    filterset = filtersets.CloudServiceFilterSet
    filterset_form = forms.CloudServiceFilterForm


class CloudServiceView(generic.ObjectView):
    queryset = CloudService.objects.select_related("platform")

    def get_extra_context(self, request, instance):
        resources = CloudResource.objects.filter(service=instance)
        t = tables.CloudResourceTable(resources)
        t.configure(request)
        return {"resources_table": t}


class CloudServiceEditView(generic.ObjectEditView):
    queryset = CloudService.objects.all()
    form = forms.CloudServiceForm


class CloudServiceDeleteView(generic.ObjectDeleteView):
    queryset = CloudService.objects.all()


class CloudServiceBulkImportView(generic.BulkImportView):
    queryset = CloudService.objects.all()
    model_form = forms.CloudServiceImportForm


class CloudServiceBulkEditView(generic.BulkEditView):
    queryset = CloudService.objects.all()
    filterset = filtersets.CloudServiceFilterSet
    table = tables.CloudServiceTable
    form = forms.CloudServiceBulkEditForm


class CloudServiceBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudService.objects.all()
    table = tables.CloudServiceTable


# --------------------------------------------------------------------------
# 자원
# --------------------------------------------------------------------------


class CloudResourceListView(generic.ObjectListView):
    queryset = CloudResource.objects.select_related("platform", "service", "tenant")
    table = tables.CloudResourceTable
    filterset = filtersets.CloudResourceFilterSet
    filterset_form = forms.CloudResourceFilterForm


class CloudResourceView(generic.ObjectView):
    queryset = CloudResource.objects.select_related("platform", "service", "tenant")


class CloudResourceEditView(generic.ObjectEditView):
    queryset = CloudResource.objects.all()
    form = forms.CloudResourceForm


class CloudResourceDeleteView(generic.ObjectDeleteView):
    queryset = CloudResource.objects.all()


class CloudResourceBulkImportView(generic.BulkImportView):
    queryset = CloudResource.objects.all()
    model_form = forms.CloudResourceImportForm

    def _process_import_records(self, form, request, records, prefetched_objects):
        """같은 자원을 다시 넣으면 새로 만들지 말고 갱신한다.

        자산 대장은 주기적으로 다시 수집해 넣는다. 그때마다 행이 새로 생기면
        대장이 아니라 로그가 된다. 유일 제약이 중복을 막아주지만, 갱신이 없으면
        재수입이 통째로 실패할 뿐이라 쓸 수가 없다.

        코어는 레코드에 `id` 가 있으면 그 객체를 갱신한다(_process_import_records).
        그러므로 자연키로 찾은 pk 를 미리 채워 넣으면 코어 로직을 그대로 쓰면서
        upsert 가 된다 - 변경 이력 스냅샷과 검증도 코어 것을 그대로 탄다.

        자연키는 제약과 같은 (platform, account, native_id) 다. native_id 가
        없는 행은 손으로 넣은 것이므로 건드리지 않는다.
        """
        for record in records:
            if record.get("id") or not record.get("native_id"):
                continue
            obj = CloudResource.objects.filter(
                platform__name=record.get("platform") or "",
                account=record.get("account") or "",
                native_id=record["native_id"],
            ).first()
            if obj is not None:
                record["id"] = obj.pk
                prefetched_objects[obj.pk] = obj
        saved = super()._process_import_records(
            form, request, records, prefetched_objects)

        # 이번 수집에서 확인된 자원에 시각을 남긴다. 사라진 자원을 자동으로
        # 폐기 처리하지 않는 이유는 **부분 수입** 때문이다 - ec2-instances 만
        # 넣었는데 나머지를 "사라졌다"고 판정하면 멀쩡한 자원이 죽는다.
        # 대신 마지막으로 확인된 시각을 남기고, 오래된 것을 사람이 보고 정한다.
        #
        # update() 를 쓰는 것은 의도적이다. save() 를 돌리면 시각만 바뀐 변경
        # 이력이 매 수입마다 쌓여 진짜 변경이 묻힌다.
        now = timezone.now()
        if saved:
            CloudResource.objects.filter(pk__in=[o.pk for o in saved]).update(
                last_seen=now)
            for o in saved:
                o.last_seen = now
        return saved


class CloudResourceBulkEditView(generic.BulkEditView):
    queryset = CloudResource.objects.all()
    filterset = filtersets.CloudResourceFilterSet
    table = tables.CloudResourceTable
    form = forms.CloudResourceBulkEditForm


class CloudResourceBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudResource.objects.all()
    table = tables.CloudResourceTable
