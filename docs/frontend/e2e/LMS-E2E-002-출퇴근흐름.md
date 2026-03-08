# LMS-E2E-002: 출퇴근 흐름 E2E 테스트

## 기본 정보
- type: e2e_test_spec
- 화면: CheckInOutScreen (`/attendance`), AttendanceRecordsScreen (`/attendance/records`)
- 관련 위젯: `check_in_out_screen.dart`, `attendance_records_screen.dart`
- 대상 사용자: EMPLOYEE

## 관련 Backend Spec
- LMS-ATT-001 (출근 Use Case)
- LMS-ATT-002 (퇴근 Use Case)
- LMS-ATT-004 (출퇴근 조회 Use Case)
- LMS-API-ATT-001 (출퇴근 API - POST /api/attendance/check-in, POST /api/attendance/check-out, GET /api/attendance/my-records)
- POLICY-ATTENDANCE-001 (출퇴근 정책)

## 테스트 시나리오

### TC-FE-002-01: 출퇴근 기록 조회 — 데이터 있음 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 + 강남점 emp-001(김민수)에 최근 30일 출퇴근 기록 존재
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/attendance/records` 페이지 열림
- When:
  - 페이지 로드 완료 대기
- Then:
  - AppBar에 "출퇴근 기록" 텍스트 표시
  - 출퇴근 기록 목록 1건 이상 표시
  - 각 기록 카드에 날짜(yyyy-MM-dd 형식) 텍스트 표시
  - "출근:" 시간, "퇴근:" 시간, "근무:" 시간 텍스트 표시
  - 상태 칩에 "정상" 또는 "지각" 등 텍스트 표시

### TC-FE-002-02: 출퇴근 기록 없음 — 빈 데이터 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터에서 출퇴근 기록이 없는 기간 설정
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/attendance/records` 페이지 열림
- When:
  - 날짜 필터를 기록이 없는 기간(예: 2020-01-01 ~ 2020-01-31)으로 설정
- Then:
  - "출퇴근 기록이 없습니다" 메시지 표시

### TC-FE-002-03: 출근 체크 — 입력/행위 테스트 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 + 오늘 날짜 근무 일정 존재 (emp-001)
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/attendance` 페이지 열림
  - 오늘 출근 기록 없음
- When:
  - Work Schedule ID 입력란(`labelText: 'Work Schedule ID'`)에 근무 일정 ID 입력
  - "출근 체크" 버튼 클릭
- Then:
  - SnackBar에 "출근이 완료되었습니다" 메시지 표시
  - "출근 시간" 라벨과 현재 시간(HH:mm:ss) 텍스트 표시
  - "출근 체크" 버튼이 사라지고 "퇴근 체크" 버튼 표시

### TC-FE-002-04: 역할별 출퇴근 화면 차이 — 권한별 화면 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터
  - manager.gangnam@lms.com (MANAGER)으로 로그인 완료
- When:
  - `/attendance` 페이지로 이동
- Then:
  - "출퇴근 체크" AppBar 타이틀 텍스트 표시
  - 현재 날짜(yyyy년 MM월 dd일 형식) 텍스트 표시
  - 실시간 시계(HH:mm:ss) 텍스트 표시
  - "출퇴근 기록" 아이콘 버튼 표시 (히스토리 아이콘)

### TC-FE-002-05: 출근 API 실패 — 에러 상태 검증 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터에서 오늘 이미 출근 완료 상태 (emp-001)
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/attendance` 페이지 열림
- When:
  - 이미 출근한 상태에서 퇴근 완료 후 다시 출근 시도 (API 에러 발생 시나리오)
- Then:
  - SnackBar에 에러 메시지 표시 (빨간색 배경)
  - 출퇴근 완료 상태일 경우 "오늘의 출퇴근이 완료되었습니다" 메시지 표시

## agent-browser 실행 예시

```python
# TC-FE-002-01: 출퇴근 기록 조회
await page.goto("/login")
await page.fill('input[type="email"]', 'employee1.gangnam@lms.com')
await page.fill('input[type="password"]', 'password123')
await page.click('text=로그인')
await page.goto("/attendance/records")
await expect(page.locator('text=출퇴근 기록')).to_be_visible()

# TC-FE-002-03: 출근 체크
await page.goto("/attendance")
await page.fill('input[label="Work Schedule ID"]', 'SCHEDULE_001')
await page.click('text=출근 체크')
await expect(page.locator('text=출근이 완료되었습니다')).to_be_visible()
```
