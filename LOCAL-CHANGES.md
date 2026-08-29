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

## 1. PyJWT 를 2.13.0 으로 올림 (2026-08-30)

**왜** — Trivy 가 운영 이미지에서 `CVE-2026-48526` (HIGH) 를 잡았다.
PyJWT 2.12.1 의 *Authentication bypass due to forged JSON Web Tokens* 다.
NetBox 가 authentik OIDC 로 로그인하므로 JWT 를 실제로 다룬다. 고침 버전은
2.13.0 인데 **업스트림 4.6.9 에도 2.12.1 이 그대로** 들어 있다.

**어떻게** — `requirements.txt` 에 `PyJWT==2.13.0` 을 직접 넣었다.

PyJWT 는 NetBox 가 직접 쓰는 것이 아니라 `social-auth-core` 가 끌고 온다.
그런데 4.8.7 은 `PyJWT[crypto]==2.12.1` 로 **등호 고정**이라 그냥은 안 올라간다.

    social-auth-core 4.8.7  PyJWT[crypto]==2.12.1   ← NetBox 가 고정한 버전
                     4.9.0  PyJWT[crypto]>=2.12.1
                     5.0.0  PyJWT[crypto]>=2.13.0
                     5.1.0  PyJWT[crypto]>=2.13.0

`social-auth-core` 를 5.1.0 으로 올리는 정공법도 있지만 **메이저 상승**이라
OIDC 동작이 바뀔 수 있다. 깨지면 NetBox 만이 아니라 로그인 자체가 막힌다.
변경 폭이 작은 쪽을 골랐다 - PyJWT 2.12.1 → 2.13.0 은 패치 수준이다.

의존성 해석기가 `social-auth-core` 의 고정과 충돌한다고 경고할 수 있다.
그래도 설치되며, **실제로 동작하는지는 빌드 후 컨테이너에서 확인했다**
(import, JWT 서명/검증 왕복, social-auth 백엔드 로드).

**되돌리려면** — `requirements.txt` 에서 `PyJWT==2.13.0` 줄을 지우면 된다.

**언제 이 수정을 버리나** — 업스트림이 `social-auth-core` 를 5.x 로 올리면
PyJWT 도 따라 올라가므로 이 줄은 불필요해진다. 그때 지운다.
