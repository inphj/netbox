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


class CloudResourceBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudResource.objects.all()
    table = tables.CloudResourceTable
