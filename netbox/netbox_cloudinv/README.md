# netbox-plugin-cloudinv

<!-- verify-pending: 코드만 작성됨. 마이그레이션 생성·이미지 빌드·UI 실물
     확인 전이다. 검증 절은 실제로 돌린 뒤에 채운다 -->

AWS·Azure 에서 **쓰고 있는 자원을 손으로 담는 대장.**

## 왜 만들었나

무엇을 쓰고 있는지가 어디에도 정리돼 있지 않았다. 콘솔에 흩어져 있고,
계정이 여러 개면 한눈에 안 보인다.

자동 수집을 하지 않는다. 그래서 **NetBox 가 사본이 아니라 기준**이다.
운영정책의 원칙 그대로다 — 구성을 상태에 맞추는 게 아니라, 상태가 구성에
맞춰져야 한다.

이것이 수기 입력을 감당 가능하게 만드는 이유이기도 하다. 실제 상태를 전부
베끼려면 계정 하나에 수천 건이라 손으로 못 넣는다. **쓰는 것만** 적는 것은
추려진 집합이라 손으로 넣을 수 있다.

## 왜 자원 종류마다 모델을 안 만들었나

AWS 와 Azure 만 해도 서비스가 수백 개다. 종류마다 모델을 만들면 종류가 늘
때마다 마이그레이션 + 이미지 재빌드가 필요하다.

    CloudPlatform   aws / azure          플랫폼 추가 = 행 하나
    CloudService    ec2 / s3 / vm ...    서비스 추가 = 행 하나
    CloudResource   자원 한 건            모델은 이것 하나

세부 속성은 `attrs` (JSON) 에 둔다. 다만 **JSON 은 질의가 약하다.** 검색이나
필터로 쓸 값이면 JSON 이 아니라 컬럼으로 올려야 한다. 지금 컬럼으로 올린 것은
계정 · 리전 · 환경 · 상태 · 소유 · 월 비용이다.

## 넣는 법

세 경로가 있고, **일괄 등록이 주 경로**다.

    UI 폼        한두 건 고칠 때
    일괄 등록    CSV. 처음 채울 때
    REST API     나중에 필요하면

`seed/` 에 바로 쓸 수 있는 CSV 가 있다. **순서대로** 넣는다 - 서비스는
플랫폼을 참조하므로 플랫폼이 먼저다.

    01-platforms.csv          AWS · Azure · OCI · Proxmox VE   4건
    02-services-aws.csv       AWS 서비스 카탈로그              49건
    03-services-azure.csv     Azure 서비스 카탈로그            51건
    04-services-oci.csv       OCI 서비스 카탈로그              34건
    05-services-proxmox.csv   Proxmox VE 서비스 카탈로그       26건
    06-resources-template.csv 자원 입력 서식                   예시 2건

OCI 카탈로그는 임의로 고른 것이 아니라 `ops/netbox/oci-collect.py` 가 실제로
수집하는 자원(인스턴스·볼륨·VCN·서브넷·게이트웨이·라우트테이블·보안목록·
IAM·버킷·예산·한도·LB·컴파트먼트)을 기준으로 잡았다.

Proxmox 는 사설이므로 `kind=private` 이다. `0.0.0.0/0` 이 인터넷 노출을 뜻하지
않는 쪽이라는 표시이기도 하다.

서비스 카탈로그는 **자주 쓰는 것만 추린 것이고 전부가 아니다.** 없는 서비스는
행을 추가한다. 안 쓰는 것은 지운다.

자원 CSV 의 `service` 칸에는 **서비스 코드**(`ec2`, `vm`)를 넣는다. 코드는
플랫폼 안에서만 유일하므로, 다른 플랫폼의 같은 코드가 섞이면 등록이 거부된다
(`nat-gateway` 처럼 양쪽에 다 있는 코드가 실제로 있다).

## 켜기

    PLUGINS = ["netbox_cloudinv"]

배포에서는 `netbox-plugins` ConfigMap 의 `plugins.py` 로 넣는다. netbox-docker
이미지는 `/etc/netbox/config/*.py` 를 전부 읽는데 그 파일이 이미지에 내장돼
있어 환경변수로는 못 바꾼다.

## 마이그레이션

    manage.py migrate netbox_cloudinv

NetBox 는 개발 모드가 아니면 `makemigrations` 를 막는다. 모델을 고쳐
마이그레이션을 새로 만들어야 하면 임시로 `DEVELOPER = True` 를 켜고 만든 뒤
그 파일을 이 저장소에 커밋한다.

## 변경 이력

UI 로 넣으면 NetBox 의 changelog 에 정상적으로 남는다.

`netbox_oci` 는 남지 않는다 — 적용기가 `manage.py shell` 로 ORM 에 직접 쓰는데
request 컨텍스트가 없어 `ObjectChange` 가 만들어지지 않기 때문이다(확인함,
changelog 0건). 자동 수집을 안 하는 대가로 얻는 것이다.

## REST API 는 선택 사항이 아니다

폼의 `DynamicModelChoiceField` 는 드롭다운을 채우려고 그 모델의 REST 목록
엔드포인트를 reverse 한다. API 가 없으면 **추가·편집·필터 폼이 통째로 500** 이
난다.

    NoReverseMatch: 'netbox_cloudinv-api' is not a registered namespace
                    inside 'plugins-api'

처음에 API 를 "나중에 붙이면 되는 것" 으로 미뤘다가 실측에서 잡혔다.
`manage.py check` 는 이것을 잡지 못한다 - 폼을 실제로 렌더해야 드러난다.

## 아직 없는 것

- **일괄 편집(BulkEdit).** 여러 건의 환경·상태를 한 번에 바꾸는 화면이 없다.
  넣기는 쉽다. 첫 판을 얇게 하려고 뺐다.
- **코어 객체와의 연결.** EC2 자원 행이 NetBox 의 `VirtualMachine` 을 가리키게
  하는 FK 가 없다. 값은 있지만 입력 손이 늘어 v1 에서 뺐다.
- **드리프트 탐지.** 기준(여기)과 실제(클라우드)를 비교하는 것. 기준 데이터가
  쌓여 값어치가 확인된 뒤에 한다.

## 검증

<!-- verified: 2026-09-07 | how: 이미지 4.6.9-13-g862826fc0 로 배포 후
     운영 파드에서 아래를 실제로 돌렸다 -->

    마이그레이션    showmigrations [X] 0001_initial
                    makemigrations --check 로 모델과 일치 (No changes detected)
    테이블          netbox_cloudinv_{cloudplatform,cloudresource,cloudservice}
    페이지 렌더     목록·상세·추가·편집·일괄등록·변경이력 × 3모델 + 필터 + 검색
                    전부 200
    카운트          플랫폼 목록에 AWS 49 · Azure 51 · OCI 34 · Proxmox 26
    분류 표시       "컴퓨트" (raw "compute" 아님)
    필터 정확도     category=compute 결과에 EC2 있고 S3 없음
    일괄 등록       CSV 직접 입력으로 생성 확인 (302)
                    플랫폼과 서비스가 어긋난 행은 거부됨
    전역 검색       서비스는 코드로, 자원은 이름·자원ID 로 검색됨
                    새 행은 저장 시 자동 색인, 삭제하면 색인에서도 빠짐
    attrs           빈 값 {} · 유효 JSON 보존 · 깨진 JSON 거부
    편집            이름·상태·비용 변경이 반영됨 (302)
    일괄 삭제        선택한 자원이 실제로 지워짐
    CSV 등록        자원·서비스·플랫폼 세 모델 모두 등록됨
    REST API        목록 실응답 (플랫폼 4 · 서비스 160 · 자원 0)
                    ?brief=1&platform_id= 필터가 26건으로 정확
                    - 폼 드롭다운이 실제로 쓰는 경로다

시험용으로 만든 행은 전부 지웠다. 자원 수는 0 이다.

### 검증에서 잡은 결함 넷 - 전부 실제로 돌려봐야 드러났다

**`manage.py check` 로는 하나도 안 잡혔다.**

1. **REST API 가 없어 추가·편집 폼이 500.** `DynamicModelChoiceField` 가
   드롭다운을 채우려고 API 목록 URL 을 reverse 한다. API 는 선택이 아니다.
2. **카운트 컬럼이 전부 0.** `LinkedCountColumn` 은 annotate 된 값을 읽는데
   뷰에서 안 걸어놨다. AWS 가 서비스 49개인데 화면에 0 으로 나왔다.
   **페이지가 200 이라고 숫자가 맞는 것은 아니다.**
3. **자원 표의 분류가 raw 값.** 관계 너머의 choice 라 `ChoiceFieldColumn` 이
   라벨을 못 찾는다. `get_category_display` 를 쓴다.
4. **attrs 를 비우면 자원 추가가 500.** 폼 JSONField 가 빈 값에 None 을
   돌려주는데 컬럼은 NOT NULL 이다. 예외 경로가 아니라 가장 흔한 경로다.

### 확인할 때 걸리는 것

Django 테스트 클라이언트로 볼 때 **Host 를 실제 인그레스 호스트로** 줘야 한다
(아니면 ALLOWED_HOSTS 로 400). 로컬 `admin` 은 **비활성**이라 로그인이 안 붙는다
- 활성 슈퍼유저는 **`akadmin`** 이다.
