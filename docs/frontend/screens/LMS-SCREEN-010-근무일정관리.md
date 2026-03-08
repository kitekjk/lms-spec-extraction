# LMS-SCREEN-010: 근무일정관리

## 기본 정보
- type: screen_spec
- 화면명: 근무 일정 관리
- 라우트: `/admin/schedules`
- 대상 사용자: 관리자(MANAGER, SUPER_ADMIN)

## 관련 Backend Spec
- LMS-API-SCH-001 (근무일정API)
- LMS-API-STORE-001 (매장API)
- LMS-API-EMP-001 (근로자API)

## 화면 목적
관리자가 매장별 근무 일정을 캘린더 형태로 관리하고, 일정을 생성/수정/삭제한다.

## 화면 구성 요소

### 일정 캘린더 뷰
- 표시 데이터: 매장 필터 드롭다운, "일정 추가" 버튼, 월간 캘린더(TableCalendar, 일정이 있는 날짜에 마커 표시, 최대 3개), 매장 미선택 시 안내 메시지
- Backend API: GET /api/schedules
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: `?storeId={매장ID}&startDate={월초}&endDate={월말}`
  - 응답 매핑: schedules[] → 날짜별 그룹핑하여 캘린더 마커 표시
- 빈 상태: "매장을 선택하면 일정을 조회할 수 있습니다"
- 에러 상태: "오류: {에러 메시지}"

### 선택일 일정 리스트
- 표시 데이터: 선택 날짜 타이틀, 일정 목록(직원명/직원ID, 시작~종료 시간, 근무시간, 확정 Chip, 주말/평일 아이콘), 수정/삭제 버튼
- Backend API: GET /api/schedules
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: `?storeId={매장ID}&startDate={선택일}&endDate={선택일}`
  - 응답 매핑: schedules[] → 리스트, employeeName → 직원명, startTime/endTime → 시간, workHours → 근무시간, isConfirmed → 확정 Chip, isWeekendWork → 주말 아이콘
- 빈 상태: "일정이 없습니다" (일정 추가 버튼과 함께)
- 에러 상태: "오류: {에러 메시지}"

### 일정 추가/수정 다이얼로그
- 표시 데이터: 매장 선택 드롭다운, 근로자 선택 드롭다운(매장 변경 시 초기화), 날짜 선택, 시작 시간 선택, 종료 시간 선택, 취소/등록(수정) 버튼
- Backend API: POST /api/schedules (등록), PUT /api/schedules/{scheduleId} (수정)
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: `{ "employeeId": "string", "storeId": "string", "workDate": "yyyy-MM-dd", "startTime": "HH:mm", "endTime": "HH:mm" }`
  - 응답 매핑: 성공 시 SnackBar "일정이 등록/수정되었습니다", 다이얼로그 닫기
- 빈 상태: "일정 정보를 입력해 주세요"
- 에러 상태: SnackBar "오류: {에러 메시지}"
- 유효성 검증:
  - 매장: 필수
  - 근로자: 필수
  - 날짜: 필수
  - 시작/종료 시간: 필수, 종료 시간 > 시작 시간

### 일정 삭제 다이얼로그
- 표시 데이터: "일정 삭제" 확인 다이얼로그
- Backend API: DELETE /api/schedules/{scheduleId}
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: Path에 scheduleId
  - 응답 매핑: 성공 시 SnackBar "일정이 삭제되었습니다"
- 빈 상태: "삭제할 일정이 없습니다"
- 에러 상태: SnackBar 에러 메시지

## 사용자 흐름

1. 매장을 선택하면 해당 매장의 근무 일정이 캘린더에 표시된다
2. 날짜를 선택하면 우측 패널에 해당 날짜의 일정 목록이 표시된다
3. "일정 추가" 버튼을 눌러 새 일정을 등록한다
4. 일정 수정 아이콘을 눌러 기존 일정을 수정한다
5. 일정 삭제 아이콘을 눌러 확인 후 일정을 삭제한다
6. 캘린더 월을 변경하면 해당 월의 일정을 다시 조회한다
