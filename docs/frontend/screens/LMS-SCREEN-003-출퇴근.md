# LMS-SCREEN-003: 출퇴근

## 기본 정보
- type: screen_spec
- 화면명: 출퇴근 체크 / 출퇴근 기록
- 라우트: `/attendance`, `/attendance/records`
- 대상 사용자: 직원(EMPLOYEE)

## 관련 Backend Spec
- LMS-API-ATT-001 (출퇴근API)

## 화면 목적
직원이 출근/퇴근을 체크하고, 오늘의 출퇴근 상태를 확인하며, 과거 출퇴근 기록을 기간별로 조회한다.

## 화면 구성 요소

### 현재 시간 표시
- 표시 데이터: 현재 날짜(yyyy년 MM월 dd일 EEEE 형식), 실시간 시계(HH:mm:ss, 1초마다 갱신)
- Backend API: GET /api/attendance/my-records
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: `?startDate={오늘}&endDate={오늘}`
  - 응답 매핑: records[0] → todayRecord (오늘의 출퇴근 기록)
- 빈 상태: "출퇴근 기록이 없습니다"
- 에러 상태: "데이터를 불러올 수 없습니다"

### 오늘의 출퇴근 기록 카드
- 표시 데이터: 출근 시간(HH:mm:ss, 초록색), 퇴근 시간(HH:mm:ss, 빨간색), 근무 시간(X.X시간)
- Backend API: GET /api/attendance/my-records
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: `?startDate={오늘}&endDate={오늘}`
  - 응답 매핑: checkInTime → 출근 시간, checkOutTime → 퇴근 시간, actualWorkHours → 근무 시간
- 빈 상태: "오늘 출퇴근 기록이 없습니다"
- 에러 상태: 카드가 표시되지 않음

### 출근 체크 버튼
- 표시 데이터: "출근 체크" 버튼(초록색, 큰 사이즈), Work Schedule ID 입력 필드
- Backend API: POST /api/attendance/check-in
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: `{ "workScheduleId": "string" }`
  - 응답 매핑: 성공 시 todayRecord 업데이트, SnackBar "출근이 완료되었습니다"
- 빈 상태: "출근 체크 대기 중"
- 에러 상태: SnackBar 빨간색 배경으로 에러 메시지 표시
- 조건: 오늘 출근 기록이 없을 때만 표시

### 퇴근 체크 버튼
- 표시 데이터: "퇴근 체크" 버튼(빨간색, 큰 사이즈)
- Backend API: POST /api/attendance/check-out
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: 없음
  - 응답 매핑: 성공 시 todayRecord 업데이트, SnackBar "퇴근이 완료되었습니다"
- 빈 상태: "퇴근 체크 대기 중"
- 에러 상태: SnackBar 빨간색 배경으로 에러 메시지 표시
- 조건: 오늘 출근 기록이 있고 퇴근 기록이 없을 때만 표시

### 출퇴근 기록 목록 (records 화면)
- 표시 데이터: 날짜 필터(시작일~종료일 선택), 기록 리스트(날짜, 출근시간, 퇴근시간, 근무시간, 상태 Chip)
- Backend API: GET /api/attendance/my-records
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: `?startDate={시작일}&endDate={종료일}`
  - 응답 매핑: records[] → ListView, 각 record의 attendanceDate/checkInTime/checkOutTime/actualWorkHours/status → UI 매핑
- 빈 상태: "출퇴근 기록이 없습니다"
- 에러 상태: "데이터를 불러올 수 없습니다"
- 상태 Chip 색상: PRESENT(초록), LATE(주황), ABSENT(빨강), ON_LEAVE(파랑)

## 사용자 흐름

1. 출퇴근 체크 화면에서 현재 날짜와 실시간 시계를 확인한다
2. 출근 전이면 Work Schedule ID를 입력하고 "출근 체크" 버튼을 누른다
3. 출근 후 퇴근 전이면 "퇴근 체크" 버튼을 누른다
4. 출퇴근 완료 시 "오늘의 출퇴근이 완료되었습니다" 메시지가 표시된다
5. AppBar의 기록 아이콘(Icons.history)을 눌러 출퇴근 기록 화면으로 이동한다
6. 기록 화면에서 날짜 범위를 선택하여 과거 기록을 조회한다
