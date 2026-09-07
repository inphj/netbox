from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel


class PlatformKind(models.TextChoices):
    PUBLIC = "public", "공용"
    PRIVATE = "private", "사설"


class ServiceCategory(models.TextChoices):
    COMPUTE = "compute", "컴퓨트"
    STORAGE = "storage", "스토리지"
    DATABASE = "database", "데이터베이스"
    NETWORK = "network", "네트워크"
    SECURITY = "security", "보안"
    INTEGRATION = "integration", "연계"
    ANALYTICS = "analytics", "분석"
    OPS = "ops", "운영"
    COST = "cost", "비용"
    OTHER = "other", "기타"


class ResourceStatus(models.TextChoices):
    ACTIVE = "active", "사용중"
    STOPPED = "stopped", "중지"
    PLANNED = "planned", "예정"
    DEPRECATED = "deprecated", "폐기예정"


class CloudPlatform(NetBoxModel):
    """AWS / Azure 같은 플랫폼. enum 이 아니라 테이블인 이유는 플랫폼 추가가
    코드 수정·마이그레이션·이미지 재빌드 없이 행 하나로 끝나야 하기 때문이다."""

    name = models.CharField(max_length=50, unique=True, verbose_name="코드",
                            help_text="aws, azure 처럼 짧은 식별자")
    label = models.CharField(max_length=100, verbose_name="표시명")
    kind = models.CharField(max_length=10, choices=PlatformKind.choices,
                            default=PlatformKind.PUBLIC, verbose_name="구분")
    description = models.CharField(max_length=200, blank=True, verbose_name="설명")

    class Meta:
        ordering = ("name",)
        verbose_name = "클라우드 플랫폼"
        verbose_name_plural = "클라우드 플랫폼"

    def __str__(self):
        return self.label or self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_cloudinv:cloudplatform", args=[self.pk])


class CloudService(NetBoxModel):
    """서비스 카탈로그. EC2·S3·RDS 처럼 자원이 속하는 서비스를 행으로 둔다.
    쓰는 서비스가 늘면 여기에 행을 추가한다. 모델은 안 건드린다."""

    platform = models.ForeignKey(
        to=CloudPlatform, on_delete=models.PROTECT, related_name="services",
        verbose_name="플랫폼",
    )
    code = models.CharField(max_length=50, verbose_name="코드")
    label = models.CharField(max_length=100, verbose_name="표시명")
    category = models.CharField(
        max_length=20, choices=ServiceCategory.choices,
        default=ServiceCategory.OTHER, verbose_name="분류",
    )
    description = models.CharField(max_length=200, blank=True, verbose_name="설명")

    class Meta:
        ordering = ("platform", "category", "code")
        unique_together = ("platform", "code")
        verbose_name = "클라우드 서비스"
        verbose_name_plural = "클라우드 서비스"

    def __str__(self):
        return f"{self.platform.name}/{self.code}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_cloudinv:cloudservice", args=[self.pk])


class CloudResource(NetBoxModel):
    """실제로 쓰고 있는 자원 한 건.

    타입별 세부 속성은 attrs(JSON) 에 둔다. 자원 종류마다 컬럼을 만들면
    종류가 늘 때마다 마이그레이션이 필요해진다. 대신 attrs 는 질의가 약하므로,
    **검색·필터로 쓸 값은 컬럼으로 올린다.**
    """

    platform = models.ForeignKey(
        to=CloudPlatform, on_delete=models.PROTECT, related_name="resources",
        verbose_name="플랫폼",
    )
    service = models.ForeignKey(
        to=CloudService, on_delete=models.PROTECT, related_name="resources",
        verbose_name="서비스",
    )
    name = models.CharField(max_length=200, verbose_name="이름")
    native_id = models.CharField(
        max_length=500, blank=True, verbose_name="자원 ID",
        help_text="AWS ARN 또는 Azure 리소스 ID. 비워도 된다",
    )
    account = models.CharField(
        max_length=100, blank=True, verbose_name="계정",
        help_text="AWS 계정 ID 또는 Azure 구독 ID/이름",
    )
    region = models.CharField(max_length=50, blank=True, verbose_name="리전")
    environment = models.CharField(
        max_length=50, blank=True, verbose_name="환경",
        help_text="prod / stg / dev 등",
    )
    status = models.CharField(
        max_length=20, choices=ResourceStatus.choices,
        default=ResourceStatus.ACTIVE, verbose_name="상태",
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant", on_delete=models.PROTECT, null=True, blank=True,
        related_name="cloud_resources", verbose_name="소유",
    )
    monthly_cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)], verbose_name="월 비용",
    )
    description = models.CharField(max_length=200, blank=True, verbose_name="설명")
    attrs = models.JSONField(
        default=dict, blank=True, verbose_name="속성",
        help_text="타입별 세부 속성. 예: {\"instance_type\": \"t3.medium\"}",
    )

    class Meta:
        ordering = ("platform", "service", "name")
        verbose_name = "클라우드 자원"
        verbose_name_plural = "클라우드 자원"
        # 인덱스 이름을 명시한다. 자동 생성 이름은 해시가 붙어
        # 손으로 쓴 마이그레이션과 어긋난다.
        indexes = [models.Index(fields=["native_id"],
                                name="cloudinv_native_id_idx")]
        constraints = [
            # 자산 대장이므로 같은 자원이 두 벌 있으면 안 된다.
            #
            # platform 만으로는 부족하다. AWS ARN 과 Azure 리소스 ID 는 전역
            # 유일하지만 **Proxmox 의 qemu/101 은 클러스터 안에서만 유일**하다.
            # 그래서 account(= 계정/구독/클러스터)까지 키에 넣는다.
            #
            # native_id 가 빈 행은 제외한다(조건부 제약). 손으로 넣는 자원은
            # 자원 ID 가 없을 수 있는데, 빈 문자열끼리는 서로 같다고 판정돼
            # 두 번째 행부터 막히기 때문이다.
            models.UniqueConstraint(
                fields=("platform", "account", "native_id"),
                condition=~models.Q(native_id=""),
                name="cloudinv_resource_native_uniq",
            ),
        ]

    def __str__(self):
        return f"{self.platform.name}/{self.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_cloudinv:cloudresource", args=[self.pk])
