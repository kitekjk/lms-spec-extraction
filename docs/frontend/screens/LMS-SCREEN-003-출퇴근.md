# LMS-SCREEN-003: 출퇴근

## 기본 정보
- type: screen_spec
- route: /attendance

## 관련 Backend Spec
- LMS-API-ATT-001 (출퇴근 기록 조회/처리 API)
- LMS-ATT-001 (출근 Use Case), LMS-ATT-002 (퇴근 Use Case), LMS-ATT-003 (출퇴근 조정 Use Case), LMS-ATT-004 (출퇴근 조회 Use Case)
- LMS-API-SCH-001 (근무 일정 조회 API)

## 화면 목적
EMPLOYEE는 출근/퇴근 버튼으로 본인의 출퇴근을 처리하고, MANAGER/ADMIN은 소속 매장 근로자의 출퇴근 기록을 조회하고 조정한다.

## 접근 권한
- SUPER_ADMIN: 전체 매장 출퇴근 기록 조회 및 조정
- MANAGER: 소속 매장 출퇴근 기록 조회 및 조정
- EMPLOYEE: 본인 출퇴근 처리 및 기록 조회

## 화면 구성 요소

### 출퇴근 버튼 영역 (EMPLOYEE 전용)
- 표시 데이터: 출근 버튼 또는 퇴근 버튼 (현재 상태에 따라 토글), 현재 시각(HH:mm:ss 실시간), 금일 근무 일정 시간 (예: "09:00 ~ 18:00")
- Backend API: POST /api/attendance/check-in
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: { employeeId: string }
  - 응답 매핑: attendanceRecord.checkInTime -> "출근 완료: {HH:mm}" 텍스트 표시
- Backend API: POST /api/attendance/check-out
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: { attendanceRecordId: string }
  - 응답 매핑: attendanceRecord.checkOutTime -> "퇴근 완료: {HH:mm}" 텍스트 표시, status -> 상태 배지 (NORMAL: 정상, LATE: 지각, EARLY_LEAVE: 조퇴)
- 권한: EMPLOYEE만 표시 — MANAGER, SUPER_ADMIN에게는 미표시
- 빈 상태: 금일 출근 기록이 없으면 "출근" 버튼 활성화 상태
- 에러 상태: "출퇴근 처리에 실패했습니다. 다시 시도해주세요."

### 출퇴근 기록 목록
- 표시 데이터: 테이블 형태 - 날짜(YYYY-MM-DD), 직원명, 출근 시간(HH:mm), 퇴근 시간(HH:mm), 상태 배지(NORMAL: 초록, LATE: 주황, EARLY_LEAVE: 노랑, ABSENT: 빨강, PENDING: 회색), 메모
- Backend API: GET /api/attendance?storeId={storeId}&startDate={startDate}&endDate={endDate}
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: storeId (MANAGER의 소속 매장), startDate, endDate (기본값: 이번 주 월요일 ~ 오늘)
  - 응답 매핑: records[].attendanceDate -> 날짜, records[].employeeName -> 직원명, records[].attendanceTime.checkInTime -> 출근 시간, records[].attendanceTime.checkOutTime -> 퇴근 시간, records[].status -> 상태 배지, records[].note -> 메모
- EMPLOYEE 역할: 본인 기록만 표시 (GET /api/attendance?employeeId={myId}&startDate=...&endDate=...)
- 빈 상태: "해당 기간의 출퇴근 기록이 없습니다"
- 에러 상태: "출퇴근 기록을 불러올 수 없습니다. 다시 시도해주세요."

### 날짜 필터
- 표시 데이터: 시작일/종료일 날짜 선택기 (DatePicker), 조회 버튼
- Backend API: GET /api/attendance?startDate={startDate}&endDate={endDate}
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: startDate, endDate (YYYY-MM-DD)
  - 응답 매핑: 출퇴근 기록 목록 갱신
- 빈 상태: 기본값 - 이번 주 월요일 ~ 오늘
- 에러 상태: 날짜 형식 오류 시 "올바른 날짜를 선택해주세요." 표시

### 출퇴근 조정 모달 (MANAGER/ADMIN 전용)
- 표시 데이터: 선택한 기록의 출근 시간, 퇴근 시간 수정 필드, 조정 사유 입력 필드
- Backend API: PUT /api/attendance/{id}/adjust
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: { checkInTime: string, checkOutTime: string, note: string }
  - 응답 매핑: 수정 완료 시 "출퇴근 기록이 조정되었습니다." 메시지 표시, 목록 갱신
- 권한: MANAGER, SUPER_ADMIN만 사용 가능 — EMPLOYEE에게는 미표시
- 빈 상태: 해당 없음
- 에러 상태: "출퇴근 조정에 실패했습니다. 다시 시도해주세요."

## 사용자 흐름
1. EMPLOYEE: /attendance 접속 시 상단에 출퇴근 버튼 영역, 하단에 본인 기록 목록 표시
2. EMPLOYEE: "출근" 버튼 클릭 -> 출근 처리 -> 버튼이 "퇴근"으로 변경, "출근 완료: 09:00" 텍스트 표시
3. EMPLOYEE: "퇴근" 버튼 클릭 -> 퇴근 처리 -> 상태 배지 표시 (정상/지각/조퇴), 버튼 비활성화
4. MANAGER: /attendance 접속 시 소속 매장 전체 근로자의 출퇴근 기록 목록 표시
5. MANAGER: 특정 기록 행 클릭 -> 출퇴근 조정 모달 열림 -> 시간 수정 후 "저장" 클릭
6. 날짜 필터로 조회 기간을 변경할 수 있다

## 검증 조건
- 출근 버튼: 이미 출근한 경우 비활성화
- 퇴근 버튼: 출근하지 않은 경우 비활성화
- 출퇴근 조정: 조정 사유(note)는 필수 입력 (빈 값 불가)
- 날짜 필터: 시작일이 종료일보다 이후일 수 없음

## 비기능 요구사항
- 초기 로딩: 2초 이내
- 인터랙션 반응: 100ms 이내
- API 실패 시: 에러 메시지 표시 + 재시도 버튼
- 출퇴근 버튼 클릭 후 중복 요청 방지 (버튼 즉시 비활성화)
