"""netbox-oci — OCI 자원을 NetBox 안에서 검색 가능한 모델로 담는다.

왜 플러그인인가 - 코어(netbox/dcim/models.py 등)에 모델을 넣으면 업스트림
병합마다 충돌한다. 플러그인 파일은 업스트림에 없으므로 절대 충돌하지 않는다.
우리 포크 안에 있고 우리가 유지보수한다. 외부 패키지가 아니다.
"""

from netbox.plugins import PluginConfig


class NetBoxOCIConfig(PluginConfig):
    name = "netbox_oci"
    verbose_name = "OCI 자원"
    description = "OCI 보안목록/규칙을 검색 가능한 모델로"
    version = "0.1.0"
    author = "inphj"
    base_url = "oci"
    min_version = "4.6.0"


config = NetBoxOCIConfig
