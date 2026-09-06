"""전역 검색(상단 검색창) 등록.

이 파일이 없으면 목록 화면의 필터로만 찾을 수 있고 **상단 검색창에는 잡히지
않는다.** 대장의 목적이 검색이므로 없으면 반쪽이다.

가중치는 낮을수록 먼저 걸린다(코어 규약). 자원을 찾는 방법이 이름과 자원 ID
이므로 그 둘을 가장 낮게 둔다.
"""

from netbox.search import SearchIndex, register_search

from .models import CloudPlatform, CloudResource, CloudService


@register_search
class CloudResourceIndex(SearchIndex):
    model = CloudResource
    category = "클라우드 자원"
    fields = (
        ("name", 100),
        ("native_id", 100),
        ("account", 200),
        ("region", 300),
        ("environment", 300),
        ("description", 500),
    )
    display_attrs = ("platform", "service", "account", "region", "environment",
                     "status", "tenant", "description")


@register_search
class CloudServiceIndex(SearchIndex):
    model = CloudService
    category = "클라우드 자원"
    fields = (
        ("code", 100),
        ("label", 200),
        ("description", 500),
    )
    display_attrs = ("platform", "category", "description")


@register_search
class CloudPlatformIndex(SearchIndex):
    model = CloudPlatform
    category = "클라우드 자원"
    fields = (
        ("name", 100),
        ("label", 200),
        ("description", 500),
    )
    display_attrs = ("kind", "description")
