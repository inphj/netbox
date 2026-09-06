"""netbox-cloudinv — 클라우드에서 쓰는 자원을 NetBox 에 손으로 담는다.

자동 수집하지 않는다. NetBox 가 사본이 아니라 기준이다.

자원 종류마다 모델을 만들지 않는다. AWS/Azure 만 해도 서비스가 수백 개라
모델을 늘리면 종류가 늘 때마다 마이그레이션이 필요해진다. 서비스는 카탈로그
테이블(CloudService)에 행으로 두고, 자원은 CloudResource 한 모델로 받는다.
"""

from netbox.plugins import PluginConfig


class CloudInvConfig(PluginConfig):
    name = "netbox_cloudinv"
    verbose_name = "클라우드 자원"
    description = "AWS·Azure 등에서 사용 중인 자원을 검색 가능한 대장으로"
    version = "0.1.0"
    author = "inphj"
    base_url = "cloudinv"
    min_version = "4.6.0"


config = CloudInvConfig
