# LMS-E2E-001: 로그인 흐름 E2E 테스트

## 기본 정보
- type: e2e_test_spec
- 화면: LoginScreen (`/login`)
- 관련 위젯: `login_screen.dart`
- 대상 사용자: EMPLOYEE, MANAGER, SUPER_ADMIN

## 관련 Backend Spec
- LMS-USER-001 (로그인 Use Case)
- LMS-USER-003 (토큰 갱신 Use Case)
- LMS-API-USER-001 (인증 API - POST /api/auth/login)
- POLICY-AUTH-001 (인증/인가 정책)

## 테스트 시나리오

### TC-FE-001-01: 정상 로그인 — 데이터 있음 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (employee1.gangnam@lms.com / password123, 역할: EMPLOYEE)
  - `/login` 페이지 열림
- When:
  - 이메일 입력란(`labelText: '이메일'`)에 "employee1.gangnam@lms.com" 입력
  - 비밀번호 입력란(`labelText: '비밀번호'`)에 "password123" 입력
  - "로그인" 버튼 클릭
- Then:
  - `/home` 페이지로 이동 표시
  - 사용자 정보 카드에 "employee1.gangnam@lms.com" 텍스트 표시
  - 역할 "EMPLOYEE" 텍스트 표시
  - "출퇴근 체크", "근무 일정", "휴가 신청", "급여 조회" 메뉴 카드 4건 표시

### TC-FE-001-02: 빈 입력 상태에서 로그인 시도 — 빈 데이터 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (서버 가동 상태)
  - `/login` 페이지 열림
- When:
  - 이메일, 비밀번호 입력란을 비운 채로 "로그인" 버튼 클릭
- Then:
  - "이메일을 입력해주세요" 유효성 검증 메시지 표시
  - "비밀번호를 입력해주세요" 유효성 검증 메시지 표시
  - 페이지 이동 없이 `/login` 유지 표시

### TC-FE-001-03: 잘못된 비밀번호 입력 — 입력/행위 테스트 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (employee1.gangnam@lms.com 계정 존재)
  - `/login` 페이지 열림
- When:
  - 이메일 입력란에 "employee1.gangnam@lms.com" 입력
  - 비밀번호 입력란에 "wrongpassword" 입력
  - "로그인" 버튼 클릭
- Then:
  - SnackBar에 에러 메시지 표시 (AUTH001: "이메일 또는 비밀번호가 일치하지 않습니다.")
  - `/login` 페이지 유지 표시

### TC-FE-001-04: 역할별 로그인 — 관리자 로그인 링크 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (admin@lms.com / password123, 역할: SUPER_ADMIN)
  - `/login` 페이지 열림
- When:
  - "관리자로 로그인" 텍스트 버튼 클릭
- Then:
  - `/admin/login` 페이지로 이동 표시
  - 관리자 로그인 폼 표시

### TC-FE-001-05: 비활성 계정 로그인 — 에러 상태 검증 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터에서 특정 사용자 비활성 상태 (isActive=false)
  - `/login` 페이지 열림
- When:
  - 이메일 입력란에 비활성 계정 이메일 입력
  - 비밀번호 입력란에 "password123" 입력
  - "로그인" 버튼 클릭
- Then:
  - SnackBar에 "비활성화된 사용자입니다." 에러 메시지 표시 (AUTH002)
  - `/login` 페이지 유지 표시

## agent-browser 실행 예시

```python
# TC-FE-001-01: 정상 로그인
await page.goto("/login")
await page.fill('input[type="email"]', 'employee1.gangnam@lms.com')
await page.fill('input[type="password"]', 'password123')
await page.click('text=로그인')
await expect(page).to_have_url("/home")
await expect(page.locator('text=employee1.gangnam@lms.com')).to_be_visible()

# TC-FE-001-02: 빈 입력 유효성 검증
await page.goto("/login")
await page.click('text=로그인')
await expect(page.locator('text=이메일을 입력해주세요')).to_be_visible()
await expect(page.locator('text=비밀번호를 입력해주세요')).to_be_visible()
```
