from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel


class Direction(models.TextChoices):
    INGRESS = "ingress", "수신"
    EGRESS = "egress", "송신"


class SecurityList(NetBoxModel):
    """OCI 보안 목록. VCN 에 붙어 서브넷의 트래픽을 통제한다."""

    name = models.CharField(max_length=200)
    vcn = models.CharField(max_length=200, verbose_name="VCN")
    tenant = models.ForeignKey(
        to="tenancy.Tenant", on_delete=models.PROTECT,
        related_name="oci_security_lists", verbose_name="테넌시",
    )
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ("tenant", "vcn", "name")
        unique_together = ("tenant", "vcn", "name")
        verbose_name = "OCI 보안목록"
        verbose_name_plural = "OCI 보안목록"

    def __str__(self):
        return f"{self.tenant}/{self.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_oci:securitylist", args=[self.pk])


class SecurityRule(NetBoxModel):
    """보안 목록 안의 규칙 한 줄.

    ConfigContext 의 JSON 으로는 '22번이 열린 규칙 전부' 같은 질의가 안 된다.
    그것이 이 모델을 만든 이유다.
    """

    security_list = models.ForeignKey(
        to=SecurityList, on_delete=models.CASCADE, related_name="rules",
        verbose_name="보안목록",
    )
    direction = models.CharField(
        max_length=10, choices=Direction.choices, verbose_name="방향",
    )
    protocol = models.CharField(max_length=10, verbose_name="프로토콜")
    ports = models.CharField(
        max_length=50, blank=True, verbose_name="포트",
        help_text="빈 값은 전체를 뜻한다 (ICMP/ALL 등)",
    )
    peer = models.CharField(
        max_length=100, verbose_name="상대",
        help_text="ingress 면 출발지, egress 면 목적지",
    )
    stateless = models.BooleanField(default=False, verbose_name="스테이트리스")
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ("security_list", "direction", "protocol", "ports")
        verbose_name = "OCI 보안규칙"
        verbose_name_plural = "OCI 보안규칙"

    def __str__(self):
        return f"{self.direction} {self.protocol} {self.ports or 'all'} {self.peer}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_oci:securityrule", args=[self.pk])
