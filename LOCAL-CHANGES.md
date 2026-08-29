# 이 포크에서 바꾼 것

`netbox-community/netbox` 의 포크다. **업스트림과 다른 점만** 여기 적는다.
`git diff <기반태그>..main` 으로 차이는 볼 수 있지만 **왜 그렇게 했는지**는
안 나온다. 업스트림을 병합하다 충돌이 났을 때 판단 근거가 되는 것은 이 글이다.

## 원칙

- **수정은 최소한으로.** 고친 파일이 많을수록 업스트림 병합이 어려워진다.
- **홈랩/회사 설정은 여기 넣지 않는다.** 도메인·인증서·OIDC·리소스는 배포
  매니페스트(k3s-gitops)에 둔다. 이 포크는 어느 환경에나 그대로 옮겨간다.
- 바꿀 때마다 아래에 **한 항목씩** 추가한다. 되돌리는 법까지 적는다.

## 기반

    2026-08-30 현재  upstream v4.6.9 에서 갈라짐

---

## 1. social-auth-core 5.1.0 으로 올림 (2026-08-30)

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

**되돌리려면** — `social-auth-core==4.8.7` 로 되돌린다. 그러면 PyJWT 도 2.12.1
로 내려가고 CVE 가 다시 열린다.

**언제 이 수정을 버리나** — 업스트림이 `social-auth-core` 를 5.x 로 올리면
이 줄은 업스트림과 같아진다. 그때 병합하며 자연히 사라진다.

