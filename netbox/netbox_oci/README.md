# netbox-oci

OCI 자원을 NetBox 안에서 **검색 가능한 모델**로 담는다.

## 왜 플러그인인가

코어(`netbox/dcim/models.py` 등)에 모델을 넣으면 업스트림 병합마다 충돌한다.
플러그인 파일은 업스트림에 존재하지 않으므로 **절대 충돌하지 않는다.**

우리 포크 안에 있고 우리가 유지보수한다. **외부 패키지가 아니다.**
PyPI 에 올리지 않고 이미지 빌드 때 로컬 경로에서 설치한다.

## 왜 만들었나

수집한 OCI 자료를 ConfigContext 의 JSON 으로 넣었더니 검색도 필터도 안 됐다.
"22번이 열린 규칙 전부" 같은 질의가 안 된다. amd1 의 로그 잡음을 추적할 때
바로 그 질의가 필요했다.

## 담는 것

    SecurityList   보안목록 (테넌시/VCN 별)
    SecurityRule   규칙 한 줄 (방향/프로토콜/포트/상대/스테이트리스)

`SecurityRule` 에는 **포트 필터**가 있다. 숫자를 넣으면 `22` 뿐 아니라
`20-30` 같은 범위 규칙도 함께 잡는다.

## 아직 안 담은 것

게이트웨이(IGW/SGW/LPG/DRG), 라우트테이블, IAM, 쿼터, 예산, 버킷은 여전히
ConfigContext 에 있다. 보안목록으로 값어치를 확인한 뒤 넓힌다.

## 왜 netbox/ 아래에 있나

`netbox-docker` 의 Dockerfile 을 고치지 않으려고 여기 뒀다. Dockerfile 은
`COPY ${NETBOX_PATH} /opt/netbox` 로 소스를 통째로 복사하고, 앱은
`/opt/netbox/netbox` 를 작업 디렉터리로 돈다.

    manage.py sys.path[0]     /opt/netbox/netbox
    granian --working-dir     /opt/netbox/netbox/

그래서 `netbox/netbox_oci` 에 두면 **pip 설치 없이 import 된다.** NetBox 는
플러그인을 `importlib.import_module()` 로만 불러오므로 pip 메타데이터가
필요 없다(`netbox/netbox/settings.py` 의 PLUGINS 처리 참조).

이 디렉터리는 업스트림에 존재하지 않으므로 **병합 충돌이 나지 않는다.**
`netbox-docker` 를 포크할 필요도 없다.

## 켜기

    PLUGINS = ["netbox_oci"]

배포에서는 `netbox-env` ConfigMap 이나 `plugins.py` 로 넣는다.
