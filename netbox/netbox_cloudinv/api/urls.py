# 이 API 는 선택 사항이 아니다.
#
# 폼의 DynamicModelChoiceField 는 드롭다운을 채우려고 모델의 REST 목록
# 엔드포인트를 reverse 한다. 없으면 추가·편집·필터 폼이 통째로 500 이 난다
#   NoReverseMatch: 'netbox_cloudinv-api' is not a registered namespace
# 실측으로 확인했다.

from netbox.api.routers import NetBoxRouter

from . import views

router = NetBoxRouter()
router.register("platforms", views.CloudPlatformViewSet)
router.register("services", views.CloudServiceViewSet)
router.register("resources", views.CloudResourceViewSet)

app_name = "netbox_cloudinv-api"
urlpatterns = router.urls
