# LMS-E2E-004: 휴가 신청 흐름 E2E 테스트

## 기본 정보
- type: e2e_test_spec
- 화면: LeaveHistoryScreen (`/leave`), LeaveRequestScreen (`/leave/request`)
- 관련 위젯: `leave_history_screen.dart`, `leave_request_screen.dart`
- 대상 사용자: EMPLOYEE, MANAGER

## 관련 Backend Spec
- LMS-LEAVE-001 (휴가 신청 Use Case)
- LMS-LEAVE-004 (휴가 취소 Use Case)
- LMS-LEAVE-005 (휴가 조회 Use Case)
- LMS-API-LEAVE-001 (휴가 API - POST /api/leave-requests, GET /api/leave-requests/my-requests)
- POLICY-LEAVE-001 (휴가 정책)

## 테스트 시나리오

### TC-FE-004-01: 휴가 내역 조회 — 데이터 있음 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 + emp-001(김민수)의 휴가 신청 내역 존재 (연차 1건 승인, 반차 1건 대기)
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/leave` 페이지 열림
- When:
  - 페이지 로드 완료 대기
- Then:
  - AppBar에 "휴가 내역" 텍스트 표시
  - 휴가 신청 목록 2건 이상 표시
  - 각 카드에 상태 칩 ("승인" 또는 "대기중") 텍스트 표시
  - 휴가 유형 ("연차" 등) 텍스트 표시
  - 기간 (yyyy-MM-dd ~ yyyy-MM-dd) 텍스트 표시
  - "총 N일" 텍스트 표시
  - 사유 텍스트 표시
  - "휴가 신청" FAB 버튼 표시

### TC-FE-004-02: 휴가 내역 없음 — 빈 데이터 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터에서 emp-003(정서연)의 휴가 신청 내역 없음
  - employee1.hongdae@lms.com 으로 로그인 완료
  - `/leave` 페이지 열림
- When:
  - 페이지 로드 완료 대기
- Then:
  - "휴가 신청 내역이 없습니다" 메시지 표시
  - beach_access 아이콘 표시
  - "휴가 신청" FAB 버튼 표시

### TC-FE-004-03: 휴가 신청 폼 작성 및 제출 — 입력/행위 테스트 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (emp-001, 김민수, 잔여 연차 13.5일)
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/leave/request` 페이지 열림
- When:
  - 휴가 유형 드롭다운(`labelText: '휴가 유형'`)에서 "연차" 선택
  - 시작일(`title: '시작일'`) 클릭 후 내일 날짜 선택
  - 종료일(`title: '종료일'`) 클릭 후 모레 날짜 선택
  - 사유 입력란(`labelText: '사유'`)에 "개인 사유로 인한 휴가" 입력
  - "휴가 신청" 버튼 클릭
- Then:
  - "총 2일" 텍스트 표시 (신청 전 미리보기)
  - SnackBar에 "휴가 신청이 완료되었습니다" 메시지 표시
  - `/leave` 페이지로 복귀 표시

### TC-FE-004-04: 매니저 vs 직원 휴가 화면 — 권한별 화면 차이 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터
  - employee1.gangnam@lms.com (EMPLOYEE)으로 로그인 완료
  - `/leave` 페이지 열림
- When:
  - 대기중(PENDING) 상태의 휴가 신청 카드 확인
- Then:
  - 직원 화면에서 취소 아이콘 버튼 표시 (대기중인 건에 한해)
  - 승인된 휴가에는 "승인자: 박수진" 등 승인자 이름 텍스트 표시
  - 반려된 휴가에는 "반려 사유:" 텍스트 표시

### TC-FE-004-05: 사유 미입력 휴가 신청 — 에러 상태 검증 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/leave/request` 페이지 열림
- When:
  - 사유 입력란을 비운 채로 "휴가 신청" 버튼 클릭
- Then:
  - "휴가 사유를 입력해주세요" 유효성 검증 메시지 표시
  - 폼 제출 차단, 페이지 유지 표시

## agent-browser 실행 예시

```python
# TC-FE-004-01: 휴가 내역 조회
await page.goto("/login")
await page.fill('input[type="email"]', 'employee1.gangnam@lms.com')
await page.fill('input[type="password"]', 'password123')
await page.click('text=로그인')
await page.goto("/leave")
await expect(page.locator('text=휴가 내역')).to_be_visible()

# TC-FE-004-03: 휴가 신청
await page.click('text=휴가 신청')  # FAB
await expect(page.locator('text=휴가 신청')).to_be_visible()  # AppBar title
await page.fill('textarea', '개인 사유로 인한 휴가')
await page.click('button:has-text("휴가 신청")')
await expect(page.locator('text=휴가 신청이 완료되었습니다')).to_be_visible()
```
