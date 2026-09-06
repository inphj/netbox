# 이 API 는 선택 사항이 아니다.
#
# forms.py 의 SecurityRuleForm 이 SecurityList 를 DynamicModelChoiceField 로
# 받는다. 그 필드는 드롭다운을 채우려고 모델의 REST 목록 URL 을 reverse 하므로,
# API 가 없으면 **보안규칙 추가·편집 화면이 500** 이 난다.
#
#   NoReverseMatch: 'netbox_oci-api' is not a registered namespace inside
#                   'plugins-api'
#
# 2026-09-07 에 실측으로 확인했다. 목록·상세와 보안목록 쪽 폼은 멀쩡했다 -
# 보안목록 폼이 참조하는 Tenant 는 코어 모델이라 API 가 이미 있기 때문이다.
# 동기화가 ORM 으로 채우니 이 두 화면을 쓸 일이 없어 드러나지 않았다.

from netbox.api.routers import NetBoxRouter

from . import views

router = NetBoxRouter()
router.register("security-lists", views.SecurityListViewSet)
router.register("security-rules", views.SecurityRuleViewSet)

app_name = "netbox_oci-api"
urlpatterns = router.urls
