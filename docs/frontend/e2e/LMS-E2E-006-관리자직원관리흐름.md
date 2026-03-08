# LMS-E2E-006: 관리자 직원 관리 흐름 E2E 테스트

## 기본 정보
- type: e2e_test_spec
- 화면: EmployeeListScreen (`/admin/employees`), EmployeeFormScreen (`/admin/employees/new`, `/admin/employees/:employeeId/edit`)
- 관련 위젯: `employee_list_screen.dart`, `employee_form_screen.dart`
- 대상 사용자: SUPER_ADMIN, MANAGER

## 관련 Backend Spec
- LMS-EMP-001 (근로자 등록 Use Case)
- LMS-EMP-002 (근로자 수정 Use Case)
- LMS-EMP-003 (근로자 비활성화 Use Case)
- LMS-EMP-004 (근로자 조회 Use Case)
- LMS-API-EMP-001 (근로자 API - GET /api/employees, POST /api/employees, PUT /api/employees/:id, POST /api/employees/:id/deactivate)
- POLICY-AUTH-001 (인증/인가 정책 - RBAC)

## 테스트 시나리오

### TC-FE-006-01: 근로자 목록 조회 — 데이터 있음 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (강남점 3명: 박수진/김민수/이지영, 홍대점 2명: 최동현/정서연)
  - admin@lms.com (SUPER_ADMIN)으로 관리자 로그인 완료
  - `/admin/employees` 페이지 열림
- When:
  - 페이지 로드 완료 대기
- Then:
  - AdminLayout에 "근로자 관리" 타이틀 텍스트 표시
  - "근로자 목록" 헤딩 텍스트 표시
  - DataTable에 근로자 목록 5건 표시
  - 테이블 컬럼 헤더에 "이름", "사용자 ID", "근로자 유형", "잔여 연차", "상태", "등록일", "작업" 텍스트 표시
  - "김민수" 행에 "REGULAR" (정규직), "13.5일", "활성" 텍스트 표시
  - "매장 필터" 드롭다운 표시
  - "근로자 추가" 버튼 표시

### TC-FE-006-02: 근로자 없는 매장 필터 — 빈 데이터 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (신촌점에 근로자 없음)
  - admin@lms.com 으로 관리자 로그인 완료
  - `/admin/employees` 페이지 열림
- When:
  - "매장 필터" 드롭다운에서 "신촌점" 선택
- Then:
  - "등록된 근로자가 없습니다" 메시지 표시
  - "근로자 추가" 버튼 표시

### TC-FE-006-03: 근로자 등록 폼 작성 — 입력/행위 테스트 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (매장 목록: 강남점, 홍대점, 신촌점)
  - admin@lms.com 으로 관리자 로그인 완료
  - `/admin/employees/new` 페이지 열림
- When:
  - "새 근로자 등록" 헤딩 확인
  - 사용자 ID 입력란(`labelText: '사용자 ID'`)에 "newuser@lms.com" 입력
  - 이름 입력란(`labelText: '이름'`)에 "홍길동" 입력
  - 근로자 유형 드롭다운(`labelText: '근로자 유형'`)에서 "정규직" 선택
  - 매장 드롭다운(`labelText: '매장'`)에서 "신촌점" 선택
  - "등록" 버튼 클릭
- Then:
  - SnackBar에 "근로자가 등록되었습니다" 메시지 표시
  - `/admin/employees` 페이지로 이동 표시

### TC-FE-006-04: SUPER_ADMIN vs MANAGER 권한 — 권한별 화면 차이 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터
  - admin@lms.com (SUPER_ADMIN)으로 관리자 로그인 완료
  - `/admin/employees` 페이지 열림
- When:
  - 전체 매장 필터(기본값) 상태에서 목록 확인
- Then:
  - 전체 매장의 근로자 목록 표시 (5건)
  - 활성 근로자에 대해 "수정" 아이콘 버튼 표시
  - 활성 근로자에 대해 "비활성화" 아이콘 버튼 표시
  - "매장 필터" 드롭다운에 "전체 매장" 옵션 표시

### TC-FE-006-05: 근로자 등록 유효성 검증 실패 — 에러 상태 검증 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터
  - admin@lms.com 으로 관리자 로그인 완료
  - `/admin/employees/new` 페이지 열림
- When:
  - 모든 필드를 비운 채로 "등록" 버튼 클릭
- Then:
  - "사용자 ID를 입력하세요" 유효성 검증 메시지 표시
  - "이름을 입력하세요" 유효성 검증 메시지 표시
  - "매장을 선택하세요" 유효성 검증 메시지 표시

## agent-browser 실행 예시

```python
# TC-FE-006-01: 근로자 목록 조회
await page.goto("/admin/login")
await page.fill('input[type="email"]', 'admin@lms.com')
await page.fill('input[type="password"]', 'password123')
await page.click('text=로그인')
await page.goto("/admin/employees")
await expect(page.locator('text=근로자 관리')).to_be_visible()
await expect(page.locator('text=김민수')).to_be_visible()
await expect(page.locator('text=이지영')).to_be_visible()

# TC-FE-006-03: 근로자 등록
await page.click('text=근로자 추가')
await expect(page.locator('text=새 근로자 등록')).to_be_visible()
await page.fill('input[label="사용자 ID"]', 'newuser@lms.com')
await page.fill('input[label="이름"]', '홍길동')
await page.click('text=등록')
await expect(page.locator('text=근로자가 등록되었습니다')).to_be_visible()
```
