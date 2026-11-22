# app-policies

모든 앱의 개인정보처리방침을 모은 정적 사이트. GitHub Pages(`dev-hojung/app-policies`, 공개 저장소)로 게시한다. 게시는 대표 승인 후.

| 페이지 | 파일 | 공개 URL |
|---|---|---|
| 목록 | `index.html` | `https://dev-hojung.github.io/app-policies/` |
| Strike Log | `strike-log/privacy/index.html` | `https://dev-hojung.github.io/app-policies/strike-log/privacy/` |
| Bounce Tower | `bounce-tower/privacy/index.html` | `https://dev-hojung.github.io/app-policies/bounce-tower/privacy/` |
| Plain Focus | `plain-focus/privacy/index.html` | `https://dev-hojung.github.io/app-policies/plain-focus/privacy/` |

- **저장소 이름은 반드시 `app-policies`(하이픈).** Pages URL 경로가 저장소 이름을 따른다. 로컬 폴더명은 회사 규칙상 `app_policies`.
  - 현재 로컬 `origin`은 `dev-hojung/app_policies`(밑줄)를 가리킨다. 그대로 올리면 URL이 `/app_policies/`가 되어 앱 상수·Play 등록 URL과 맞지 않는다. 올린 뒤 GitHub에서 저장소 이름을 `app-policies`로 바꾸고 Pages(main, `/`)를 켠다.

## 게시 상태 (#32, 2026-11-22)

| 페이지 | 상태 |
|---|---|
| `index.html` | 게시 가능 (Plain Focus만 링크, 나머지는 "준비 중") |
| `plain-focus/privacy/` | **게시 가능.** 운영자명·연락처·시행일 채움(2026-11-22). Play Console 등록 URL: `https://dev-hojung.github.io/app-policies/plain-focus/privacy/` |
| `bounce-tower/privacy/` | 초안. `DRAFT` 배너와 `noindex` 적용. 대표 확인 값(보관 기간·삭제 기한 등)을 채운 뒤 배너를 지우고 목록에 링크를 단다 |
| `strike-log/privacy/` | 초안. 위와 같음. 아래 서버 변경이 운영에 배포된 뒤에만 시행 |

- 운영자명(김호정 / Hojung Kim)과 연락처(dev.hojung@gmail.com)는 출시된 Strike Log 앱의 방침에 이미 공개된 값을 썼다.
- 확인 도구에서 `mailto:` 링크를 허용하도록 수정했다.
- 각 페이지는 단일 HTML(스타일 내장, JS·외부 리소스 없음). 영어(`#en`) 다음 한국어(`#ko`).
- 계정 삭제 앵커(Play Console '데이터 삭제' URL 입력용): `strike-log/privacy/#delete-account`, `bounce-tower/privacy/#delete-data`.
- 게시 전 `[대표 확인 필요: …]` 문자열을 모두 실제 값으로 바꾼다: `grep -rn "대표 확인 필요" .`
- `.nojekyll`: Jekyll 처리 없이 그대로 게시.
- 앱의 SDK·권한·수집 데이터가 바뀌면 해당 페이지를 같이 고치고 날짜를 갱신한다.

## 게시 전 점검 (`python3 tools/check_policies.py`)

`ALL OK`가 나와야 게시한다. 점검 항목:
- HTML 구조, 외부 리소스·JS 금지, 앵커·상대 링크, EN/KO 섹션 수 일치
- 시행 중 페이지(목록·Plain Focus)에 `[대표 확인 필요: …]`가 남아 있으면 실패
- 초안(Strike Log·Bounce Tower) 격리: `noindex`, `DRAFT` 배너, 목록 비링크
- 공개 금지 정보 스캔(`.git`·`.omc` 제외 전 파일): 회사 메일·도메인, 로컬 경로, 개인키, Google/GitHub/AWS 키, 웹훅, JWT, 실제 AdMob 단위 ID, 비밀번호 대입, 사설 IP, 금지 파일(.env·키스토어·key.properties·google-services.json)

## 앱별 기존 방침 URL (#32 조사, 2026-11-22)

| 앱 | 앱 안 링크 | 현재 쓰는 웹 URL | 비고 |
|---|---|---|---|
| Plain Focus | `AppInfo.privacyPolicyUrl` = `https://dev-hojung.github.io/app-policies/plain-focus/privacy/` | 위와 같음 | 이 저장소가 원본 |
| Strike Log | 앱 내장 화면(`PrivacyPolicyPage`)만, 외부 URL 상수 없음 | `https://dev-hojung.github.io/strike_log_app/privacy` (`strike_log_app/docs/`) | 이 저장소 페이지는 초안. 교체 여부는 대표 결정 |
| Bounce Tower | 없음 (Flutter·WebView 코드에 방침 URL 없음) | `https://dev-hojung.github.io/bounce_tower/privacy`, `/delete-account` (`bounce_tower/docs/`) | 이 저장소 페이지는 초안. 교체 여부는 대표 결정 |

## 게시 전제 조건 (Strike Log)

Strike Log 방침은 아래 서버 변경(`strike_log_api`)이 **운영 서버에 배포된 뒤에** 게시한다. 배포 전에 게시하면 방침과 실제 동작이 다르다.

| 방침 문구 | 근거 코드 |
|---|---|
| 인증 기록은 생성 후 24시간 안에 자동 삭제 | `src/email/email.service.ts` `purgeOldAuthRecords()` (매시간, 보관 1시간) |
| 회원 탈퇴 시 해당 이메일의 인증 기록 삭제 | `src/users/users.service.ts` `deleteMe()` |
| Discord 문의 사본의 계정 이메일은 일부 가림 | `src/inquiries/inquiries.service.ts` `maskEmail()` |

## 운영 절차: 삭제 요청 메일을 받았을 때 (Strike Log)

1. 보낸 주소가 가입 이메일인지 확인한다.
2. 운영 DB에서 해당 계정을 탈퇴 처리한다(`deleteMe`와 같은 범위). `email_auth`도 함께 지워진다.
3. Discord 운영 채널에서 해당 사용자 ID가 들어간 문의·오류 알림 메시지를 삭제한다.
4. 방침에 적은 처리 기한 안에 완료 회신을 보낸다.
5. 정기 작업: Discord 문의 사본은 처리 완료 후 방침에 적은 보관 기간이 지나면 삭제한다.
