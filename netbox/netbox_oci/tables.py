import django_tables2 as tables

from netbox.tables import NetBoxTable, columns

from .models import SecurityList, SecurityRule


class SecurityListTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name="이름")
    tenant = tables.Column(linkify=True, verbose_name="테넌시")
    vcn = tables.Column(verbose_name="VCN")
    rule_count = tables.Column(verbose_name="규칙 수")

    class Meta(NetBoxTable.Meta):
        model = SecurityList
        fields = ("pk", "id", "name", "tenant", "vcn", "rule_count", "description")
        default_columns = ("name", "tenant", "vcn", "rule_count")


class SecurityRuleTable(NetBoxTable):
    security_list = tables.Column(linkify=True, verbose_name="보안목록")
    tenant = tables.Column(
        accessor="security_list__tenant", linkify=True, verbose_name="테넌시",
    )
    direction = columns.ChoiceFieldColumn(verbose_name="방향")
    protocol = tables.Column(verbose_name="프로토콜")
    ports = tables.Column(verbose_name="포트")
    peer = tables.Column(verbose_name="상대")
    stateless = columns.BooleanColumn(verbose_name="스테이트리스")

    class Meta(NetBoxTable.Meta):
        model = SecurityRule
        fields = ("pk", "id", "security_list", "tenant", "direction", "protocol",
                  "ports", "peer", "stateless", "description")
        default_columns = ("security_list", "tenant", "direction", "protocol",
                           "ports", "peer")
