# LMS-SCREEN-004: 스케줄

## 기본 정보
- type: screen_spec
- 화면명: 내 근무 일정
- 라우트: `/schedule`
- 대상 사용자: 직원(EMPLOYEE)

## 관련 Backend Spec
- LMS-API-SCH-001 (근무일정API)

## 화면 목적
직원이 캘린더 형태로 자신의 근무 일정을 확인하고, 날짜별 근무 시간/매장/상태를 조회한다.

## 화면 구성 요소

### 캘린더 뷰
- 표시 데이터: 월간 캘린더(TableCalendar), 일정이 있는 날짜에 마커 표시, 월/2주/주 형식 전환 가능, 한국어 로케일
- Backend API: GET /api/work-schedules/my-schedules
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: `?startDate={월초-1달}&endDate={월말+1달}`
  - 응답 매핑: schedules[] → 날짜별 그룹핑하여 캘린더 마커 표시
- 빈 상태: "근무 일정이 없습니다"
- 에러 상태: "데이터를 불러올 수 없습니다"

### 선택일 일정 리스트
- 표시 데이터: 선택한 날짜의 근무 일정 목록, 각 일정 카드에 시작~종료 시간, 근무 시간(X.X시간), 매장명, 확정/미확정 상태 Chip, 주말 근무 태그
- Backend API: GET /api/work-schedules/my-schedules
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: `?startDate={선택일}&endDate={선택일}`
  - 응답 매핑: schedules[] → 카드 목록, startTime/endTime → 시간 표시, workHours → 근무 시간, storeName → 매장명, isConfirmed → 확정/미확정, isWeekendWork → 주말 근무 태그
- 빈 상태: "근무 일정이 없습니다" (Icons.event_busy 아이콘과 함께)
- 에러 상태: "데이터를 불러올 수 없습니다"

## 사용자 흐름

1. 화면 진입 시 현재 월의 근무 일정이 캘린더에 마커로 표시된다
2. 날짜를 선택하면 해당 날짜의 근무 일정 상세가 하단 리스트에 표시된다
3. 캘린더 월을 변경하면 새로운 기간의 일정을 조회한다
4. 새로고침 버튼(Icons.refresh)으로 일정을 다시 불러올 수 있다
5. 캘린더 형식(월/2주/주)을 전환하여 다양한 뷰로 확인할 수 있다
