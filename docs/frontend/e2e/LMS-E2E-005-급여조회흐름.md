# LMS-E2E-005: 급여 조회 흐름 E2E 테스트

## 기본 정보
- type: e2e_test_spec
- 화면: PayrollListScreen (`/payroll`), PayrollDetailScreen (`/payroll/:id`)
- 관련 위젯: `payroll_list_screen.dart`, `payroll_detail_screen.dart`
- 대상 사용자: EMPLOYEE

## 관련 Backend Spec
- LMS-PAY-006 (급여 조회 Use Case)
- LMS-PAY-004 (급여 산정 Use Case)
- LMS-API-PAY-001 (급여 API - GET /api/payroll/my-payroll, GET /api/payroll/:id)
- POLICY-PAYROLL-001 (급여 정책)

## 테스트 시나리오

### TC-FE-005-01: 급여 목록 조회 — 데이터 있음 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 + emp-001(김민수)의 최근 3개월 급여 내역 존재 (확정 2건, 미확정 1건)
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/payroll` 페이지 열림
- When:
  - 페이지 로드 완료 대기
- Then:
  - AppBar에 "급여 내역" 텍스트 표시
  - 급여 카드 목록 3건 표시
  - 각 카드에 기간(periodString) 텍스트 표시
  - "실수령액" 라벨 텍스트 표시
  - 금액이 원화(₩) 형식으로 표시
  - "확정" 또는 "미확정" 상태 칩 텍스트 표시
  - 근무일수 "N일", 근무시간 "N.N시간" 정보 칩 텍스트 표시

### TC-FE-005-02: 급여 내역 없음 — 빈 데이터 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터에서 급여 산정 전 상태 (emp-003, 정서연)
  - employee1.hongdae@lms.com 으로 로그인 완료
  - `/payroll` 페이지 열림
- When:
  - 페이지 로드 완료 대기
- Then:
  - "급여 내역이 없습니다" 메시지 표시
  - attach_money 아이콘 표시

### TC-FE-005-03: 급여 상세 조회 — 입력/행위 테스트 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 + emp-001(김민수)의 급여 내역 존재 (기본급, 연장근무수당, 야간근무수당, 휴일근무수당, 소득세, 4대보험 항목 포함)
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/payroll` 페이지 열림
- When:
  - 첫 번째 급여 카드 클릭
- Then:
  - `/payroll/:id` 상세 페이지로 이동 표시
  - AppBar에 "급여 상세" 텍스트 표시
  - 기간 및 매장명 텍스트 표시
  - "실수령액" 카드에 금액(₩) 표시
  - "근무 정보" 섹션에 "근무일수" N일, "근무시간" N.N시간 텍스트 표시
  - "지급 항목" 섹션에 "기본급", "연장근무수당", "야간근무수당", "휴일근무수당", "총 지급액" 텍스트 표시
  - "공제 항목" 섹션에 "소득세", "4대보험", "총 공제액" 텍스트 표시

### TC-FE-005-04: 직원만 접근 가능 — 권한별 화면 차이 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터
  - employee1.gangnam@lms.com (EMPLOYEE)으로 로그인 완료
  - `/home` 페이지 열림
- When:
  - "급여 조회" 메뉴 카드 클릭
- Then:
  - `/payroll` 페이지로 이동 표시
  - "급여 내역" AppBar 타이틀 텍스트 표시
  - "새로고침" 아이콘 버튼 표시

### TC-FE-005-05: 급여 상세 API 실패 — 에러 상태 검증 (E2E)
- Given:
  - Backend 데이터: 존재하지 않는 급여 ID로 접근
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/payroll/non-existent-id` 페이지 직접 접근
- When:
  - 페이지 로드 시 API 호출 실패
- Then:
  - "급여 정보를 불러올 수 없습니다" 메시지 표시

## agent-browser 실행 예시

```python
# TC-FE-005-01: 급여 목록 조회
await page.goto("/login")
await page.fill('input[type="email"]', 'employee1.gangnam@lms.com')
await page.fill('input[type="password"]', 'password123')
await page.click('text=로그인')
await page.goto("/payroll")
await expect(page.locator('text=급여 내역')).to_be_visible()
await expect(page.locator('text=실수령액')).to_be_visible()

# TC-FE-005-03: 급여 상세
first_card = page.locator('.payroll-card').first
await first_card.click()
await expect(page.locator('text=급여 상세')).to_be_visible()
await expect(page.locator('text=기본급')).to_be_visible()
await expect(page.locator('text=총 지급액')).to_be_visible()
await expect(page.locator('text=총 공제액')).to_be_visible()
```
