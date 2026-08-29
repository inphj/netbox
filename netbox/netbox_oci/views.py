from netbox.views import generic

from . import filtersets, forms, tables
from .models import SecurityList, SecurityRule


class SecurityListListView(generic.ObjectListView):
    queryset = SecurityList.objects.all()
    table = tables.SecurityListTable
    filterset = filtersets.SecurityListFilterSet
    filterset_form = forms.SecurityListFilterForm


class SecurityListView(generic.ObjectView):
    queryset = SecurityList.objects.all()

    def get_extra_context(self, request, instance):
        rules = SecurityRule.objects.filter(security_list=instance)
        t = tables.SecurityRuleTable(rules)
        t.configure(request)
        return {"rules_table": t}


class SecurityListEditView(generic.ObjectEditView):
    queryset = SecurityList.objects.all()
    form = forms.SecurityListForm


class SecurityListDeleteView(generic.ObjectDeleteView):
    queryset = SecurityList.objects.all()


class SecurityRuleListView(generic.ObjectListView):
    queryset = SecurityRule.objects.select_related("security_list__tenant")
    table = tables.SecurityRuleTable
    filterset = filtersets.SecurityRuleFilterSet
    filterset_form = forms.SecurityRuleFilterForm


class SecurityRuleView(generic.ObjectView):
    queryset = SecurityRule.objects.all()


class SecurityRuleEditView(generic.ObjectEditView):
    queryset = SecurityRule.objects.all()
    form = forms.SecurityRuleForm


class SecurityRuleDeleteView(generic.ObjectDeleteView):
    queryset = SecurityRule.objects.all()
