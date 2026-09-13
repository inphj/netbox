# 이 포크에서 바꾼 것

`netbox-community/netbox` 의 포크다. **업스트림과 다른 점만** 여기 적는다.
`git diff <기반태그>..main` 으로 차이는 볼 수 있지만 **왜 그렇게 했는지**는
안 나온다. 업스트림을 병합하다 충돌이 났을 때 판단 근거가 되는 것은 이 글이다.

## 원칙

- **수정은 최소한으로.** 고친 파일이 많을수록 업스트림 병합이 어려워진다.
- **홈랩/회사 설정은 여기 넣지 않는다.** 도메인·인증서·OIDC·리소스는 배포
  매니페스트(k3s-gitops)에 둔다. 이 포크는 어느 환경에나 그대로 옮겨간다.
- 바꿀 때마다 아래에 **한 항목씩** 추가한다. 되돌리는 법까지 적는다.

## 작업자(사람·Claude 세션)가 지킬 것 — 2026-09-13

`CLAUDE.md` 는 업스트림 파일(`@./AGENTS.md`)이라 덮어쓰지 않는다. 우리 규칙은 여기 두고 `CLAUDE.md` 가
이 파일을 한 줄로 가리킨다 — 업스트림 병합 때 그 한 줄만 다시 붙이면 된다.

- **기능은 포크에 넣지 않는다.** 플러그인으로 만들 수 있으면 `inphj-org/infra-opensource` 의
  `netbox-selfplugin/` 으로. 실측(2026-09-13): 포크와 v4.7.0 의 차이는 `netbox/netbox_oci`·
  `netbox/netbox_cloudinv` 두 디렉터리(45파일)와 이 파일뿐이다.
- **포크 안 `netbox/netbox_oci`·`netbox/netbox_cloudinv` 는 고치지 않는다.** selfplugin 저장소의 구식 사본이다.
  이미지 빌드(`infra-gitops` `k3s/ops/netbox-build/build.sh`)가 selfplugin 을 복사해 덮으므로 여기 고쳐도
  이미지에 안 들어간다. 지울지는 사용자 결정으로 남겨 뒀다.
- **코어(`netbox/`)를 고치면 이 파일에 한 항목을 더한다** — 무엇을 왜, 되돌리는 법까지. PR 체크
  (`.github/workflows/local-check.yml`, GitHub 호스트 러너)가 확인한다. 업스트림을 끌어오는 머지 커밋이 있는 PR 만 예외
  (main 을 feature 에 병합한 것은 예외가 아니다).
- **업스트림 병합은 별도 PR 로.** 기능 변경과 섞지 않는다.
- 클라우드 세션은 홈랩에 닿지 않는다. 이미지·릴리스·배포는 노드에서 사람이 한다 — 여기서 "릴리스됐다"·
  "배포됐다"고 쓰지 않는다. 체크는 둘: 업스트림 `ci.yml` 등 + `local-check.yml`(바뀐 `.py` 컴파일 + 이 파일 규칙). 둘 다 GitHub
  호스트 러너다 — 공개 저장소라 무료고, org 자체 러너 그룹은 공개 저장소를 안 받는다(2026-09-13 실측).

## 기반

    2026-08-30  upstream v4.6.9 에서 갈라짐
    2026-09-07  upstream v4.6.10 병합 (충돌 1건: requirements.txt)
    2026-09-07  upstream v4.7.0  병합 (충돌 1건: login.html)

**v4.7.0 시점에 코어 수정이 0건이 됐다.** 아래 1·2번을 업스트림이 같은 방식으로
흡수했다. 지금 이 포크가 업스트림과 다른 점은 **플러그인 두 개뿐**이고, 그것은
업스트림에 없는 디렉터리라 충돌하지 않는다. 병합 부담이 사실상 사라졌다.


## 병합 기록

**v4.7.0 (2026-09-07).** 충돌은 `login.html` 한 곳. **업스트림 것을 받았다** -
업스트림도 social-auth 6.0 의 `require_POST` 를 폼으로 처리했고, 그쪽이 더 낫다.
우리 판은 쿼리 파라미터가 action URL 에 남는 것에 의존했는데 업스트림은
`backend.params` 를 hidden input 으로 명시 전달한다.

`requirements.txt` 는 **충돌조차 나지 않았다** - 업스트림 4.7.0 이
`social-auth-app-django 6.0.1` / `social-auth-core 5.1.0` 을 채택했다. 우리가
포크를 만들면서 핀했던 바로 그 조합이다.

전제조건 확인(4.7 의 Breaking Changes): PostgreSQL **16.14** (15+ 필요),
Redis **7.4.10** (6+ 필요), `RQ_DEFAULT_TIMEOUT` 미설정이라
`WEBHOOK_DEFAULT_TIMEOUT` 강제 조건에 안 걸림. 마이그레이션 **41건**
(ltree, denormalization 트리거, unique 제약 통합).

빌드 도구 `netbox-docker` 는 **5.0.2 그대로 뒀다.** 5.1.0 이 나와 있지만
의존성 갱신뿐이고, 문제가 났을 때 원인이 NetBox 4.7 인지 빌드도구인지
섞이면 안 되기 때문이다.

**v4.6.10 (2026-09-07).** 충돌은 `requirements.txt` 한 곳뿐이었다 - 아래
1번에서 고친 바로 그 줄이다. 해소 방침:

    rq                      업스트림 2.12.0 을 받는다 (우리 고정이 아니었다)
    social-auth-app-django  우리 6.0.1 유지
    social-auth-core        우리 5.1.0 유지

**업스트림 4.6.10 에도 social-auth-core 4.8.7 이 그대로 들어 있다.** 즉 아래
1번의 CVE 는 아직 업스트림에서 안 고쳐졌고, 우리 핀은 계속 필요하다.

4.6.10 에는 **마이그레이션 추가가 없다**(스키마 변경 없음).

---

## 1. social-auth-core 5.1.0 으로 올림 (2026-08-30)

> **해소됨 (v4.7.0, 2026-09-07).** 업스트림이 같은 버전을 채택했다.
> 이 항목은 더 이상 로컬 수정이 아니다. 기록으로만 남긴다.

**왜** — Trivy 가 운영 이미지에서 `CVE-2026-48526` (HIGH) 를 잡았다.
PyJWT 2.12.1 의 *Authentication bypass due to forged JSON Web Tokens* 다.
NetBox 가 authentik OIDC 로 로그인하므로 JWT 를 실제로 다룬다. 고침 버전은
2.13.0 인데 **업스트림 4.6.9 에도 2.12.1 이 그대로** 들어 있다.

**처음에 PyJWT 만 올리려다 실패했다.** PyJWT 는 NetBox 가 직접 쓰는 것이
아니라 `social-auth-core` 가 끌고 온다. 4.8.7 은 `PyJWT[crypto]==2.12.1` 로
**등호 고정**이라 `uv` 가 정확히 거부한다:

    Because social-auth-core==4.8.7 depends on pyjwt[crypto]==2.12.1
    and you require pyjwt==2.13.0 → incompatible

억지로 넣을 수 없다는 뜻이고, 잘못된 조합이 조용히 설치되는 것보다 낫다.
netbox-docker 의 Dockerfile 주석도 이 상황을 예고한다
("we have potential version conflicts and the build will fail").

**어떻게** — `social-auth-core` 4.8.7 → **5.1.0**, 그리고 짝인
`social-auth-app-django` 5.9.0 → **6.0.1**.

코어만 올리면 또 막힌다. `app-django` 가 코어 버전을 좁게 묶고 있다:

    app-django 5.9.0  social-auth-core <5.0.0,>=4.8.3   ← 코어 5.x 를 거부
    app-django 6.0.1  social-auth-core <6.0.0,>=5.0.0   ← 여기
                      Django 6.0 분류 있음 (NetBox 는 Django 6.0.8)

    4.8.7  PyJWT[crypto]==2.12.1
    4.9.0  PyJWT[crypto]>=2.12.1
    5.0.0  PyJWT[crypto]>=2.13.0
    5.1.0  PyJWT[crypto]>=2.13.0   ← 여기

**메이저 상승인데 왜 받아들였나** — 5.x 변경의 대부분이 보안 수정이다.
LINE/Shopify/LoginRadius/Twilio 로그인 CSRF, SAML 응답 검증, partial pipeline
세션 소유권 확인. 특히 5.1.0 의 **"OIDC 백엔드가 토큰 갱신 시 ID 토큰을
검증하고 신원 변경을 거부"** 는 authentik OIDC 를 쓰는 이 환경에 직접 해당한다.

NetBox 의 사용면도 좁다 - `social_core`/`social_django` 참조가 16곳뿐이고 전부
표준 파이프라인(`social_details`, `social_uid`, `social_user` …)과 미들웨어다.
5.x 가 바꾼 것은 백엔드별 검증 로직이지 이 파이프라인 API 가 아니다.

**주의** — 4.9.0 릴리스 노트에 "This release might contain breaking changes"
가 있다. 제거된 백엔드들이 있는데 여기서 쓰는 것은 일반 OIDC 하나뿐이다.

### 딸려온 수정 — 로그인 링크를 POST 폼으로

`social-auth-app-django` 6.0 부터 `social:begin` 뷰에 `@require_POST` 가 붙었다.
로그인 CSRF 를 막기 위한 변경이다.

    social_django/views.py
      @require_POST
      def auth(request, backend): ...

NetBox 4.6.9 의 `netbox/templates/login.html` 은 SSO 버튼을 `<a href>` 로
그리므로 GET 이 되고, **405 Method Not Allowed** 가 난다. 처음 배포했을 때
실제로 이 증상이 났고 되돌렸다.

`<a>` 를 `<form method="post">` + `{% csrf_token %}` 으로 바꿨다. 쿼리
파라미터(`next`, `idp`)는 `action` 에 그대로 남는다 - POST 여도 전달된다.

**되돌리지 말 것.** `@require_POST` 는 보안 수정이므로, 업스트림이 언젠가
같은 방식으로 템플릿을 고칠 것이다. 그때 병합에서 충돌이 나면 업스트림 쪽을
받으면 된다.

### 검증에서 배운 것

첫 배포 때 컨테이너 안에서 JWT 왕복·서명 검증·백엔드 로드를 확인하고 넘어갔다.
전부 통과했지만 **URL 뷰의 허용 메서드 변경은 그 검증으로 잡히지 않았다.**
라이브러리가 로드되는 것과 로그인 흐름이 도는 것은 다른 문제다.

이후로는 배포 전에 **실제 흐름을 태운다** - `/login/` 에서 CSRF 토큰을 받아
`/oauth/login/oidc/` 로 POST 해서 authentik 으로 302 가 나오는지 확인한다.

**되돌리려면** — `social-auth-core==4.8.7` 로 되돌린다. 그러면 PyJWT 도 2.12.1
로 내려가고 CVE 가 다시 열린다.

**언제 이 수정을 버리나** — 업스트림이 `social-auth-core` 를 5.x 로 올리면
이 줄은 업스트림과 같아진다. 그때 병합하며 자연히 사라진다.

