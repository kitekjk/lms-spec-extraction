# LMS-E2E-003: 스케줄 조회 흐름 E2E 테스트

## 기본 정보
- type: e2e_test_spec
- 화면: MyScheduleScreen (`/schedule`)
- 관련 위젯: `my_schedule_screen.dart`
- 대상 사용자: EMPLOYEE, MANAGER

## 관련 Backend Spec
- LMS-SCH-004 (근무 일정 조회 Use Case)
- LMS-SCH-001 (근무 일정 등록 Use Case)
- LMS-API-SCH-001 (근무 일정 API - GET /api/work-schedules/my-schedules)
- POLICY-SCHEDULE-001 (근무 일정 정책)

## 테스트 시나리오

### TC-FE-003-01: 근무 일정 캘린더 조회 — 데이터 있음 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 + DemoDataInitializer로 생성된 강남점 3주치 일정 (월~금 09:00~18:00, 확정)
  - employee1.gangnam@lms.com (김민수, emp-001)으로 로그인 완료
  - `/schedule` 페이지 열림
- When:
  - 오늘 날짜(근무 일정이 있는 평일) 클릭
- Then:
  - AppBar에 "내 근무 일정" 텍스트 표시
  - TableCalendar에 이벤트 마커(dot) 표시
  - 선택 날짜에 "yyyy년 MM월 dd일 요일" 형식 텍스트 표시
  - 일정 카드에 "09:00 - 18:00" 시간 텍스트 표시
  - "근무 시간: 9.0시간" 텍스트 표시
  - "확정" 상태 칩 텍스트 표시
  - 매장명 "강남점" 텍스트 표시

### TC-FE-003-02: 일정 없는 날짜 선택 — 빈 데이터 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (주말에는 일정 없음)
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/schedule` 페이지 열림
- When:
  - 주말 날짜(토요일 또는 일요일) 클릭
- Then:
  - "근무 일정이 없습니다" 메시지 표시
  - event_busy 아이콘 표시

### TC-FE-003-03: 캘린더 월 변경 — 입력/행위 테스트 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 + 3주치 일정 존재
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/schedule` 페이지 열림
- When:
  - 캘린더 헤더의 다음 달(>) 화살표 버튼 클릭
- Then:
  - 다음 달 캘린더 표시
  - 새로고침 아이콘 버튼 표시
  - 해당 월의 일정이 있으면 이벤트 마커 표시

### TC-FE-003-04: 매니저 vs 직원 일정 조회 — 권한별 화면 차이 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 + 매니저(emp-manager-001, 박수진)와 직원(emp-001, 김민수) 각각의 일정 존재
  - manager.gangnam@lms.com (MANAGER)으로 로그인 완료
  - `/schedule` 페이지 열림
- When:
  - 근무 일정이 있는 평일 날짜 클릭
- Then:
  - 매니저 본인의 근무 일정 목록 표시
  - 일정 카드에 시간대, 근무 시간, 확정 상태 텍스트 표시

### TC-FE-003-05: 스케줄 API 실패 — 에러 상태 검증 (E2E)
- Given:
  - Backend 데이터: API 서버가 500 에러를 반환하도록 설정 (네트워크 장애 시뮬레이션)
  - employee1.gangnam@lms.com 으로 로그인 완료
  - `/schedule` 페이지 열림
- When:
  - 페이지 로드 시 API 호출 실패
- Then:
  - 로딩 스피너(CircularProgressIndicator) 표시 후 에러 상태
  - "새로고침" 버튼 표시
  - 재시도 가능한 UI 표시

## agent-browser 실행 예시

```python
# TC-FE-003-01: 근무 일정 조회
await page.goto("/login")
await page.fill('input[type="email"]', 'employee1.gangnam@lms.com')
await page.fill('input[type="password"]', 'password123')
await page.click('text=로그인')
await page.goto("/schedule")
await expect(page.locator('text=내 근무 일정')).to_be_visible()
# 오늘 날짜 클릭 (평일 가정)
today_cell = page.locator('.calendar-today')
await today_cell.click()
await expect(page.locator('text=09:00 - 18:00')).to_be_visible()
await expect(page.locator('text=확정')).to_be_visible()

# TC-FE-003-02: 빈 일정 조회
# 주말 날짜 선택
await expect(page.locator('text=근무 일정이 없습니다')).to_be_visible()
```
