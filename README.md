# app-policies

모든 앱의 개인정보처리방침을 모은 정적 사이트. GitHub Pages(`dev-hojung/app-policies`, 공개 저장소)로 게시한다. 게시는 대표 승인 후.

| 페이지 | 파일 | 공개 URL |
|---|---|---|
| 목록 | `index.html` | `https://dev-hojung.github.io/app-policies/` |
| Strike Log | `strike-log/privacy/index.html` | `https://dev-hojung.github.io/app-policies/strike-log/privacy/` |
| Bounce Tower | `bounce-tower/privacy/index.html` | `https://dev-hojung.github.io/app-policies/bounce-tower/privacy/` |
| Plain Focus | `plain-focus/privacy/index.html` | `https://dev-hojung.github.io/app-policies/plain-focus/privacy/` |

- **저장소 이름은 반드시 `app-policies`(하이픈).** Pages URL 경로가 저장소 이름을 따른다. 로컬 폴더명은 회사 규칙상 `app_policies`.
- 각 페이지는 단일 HTML(스타일 내장, JS·외부 리소스 없음). 영어(`#en`) 다음 한국어(`#ko`).
- 계정 삭제 앵커(Play Console '데이터 삭제' URL 입력용): `strike-log/privacy/#delete-account`, `bounce-tower/privacy/#delete-data`.
- 게시 전 `[대표 확인 필요: …]` 문자열을 모두 실제 값으로 바꾼다: `grep -rn "대표 확인 필요" .`
- `.nojekyll`: Jekyll 처리 없이 그대로 게시.
- 앱의 SDK·권한·수집 데이터가 바뀌면 해당 페이지를 같이 고치고 날짜를 갱신한다.

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
