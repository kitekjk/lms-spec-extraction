# LMS-SCREEN-004: 스케줄

## 기본 정보
- type: screen_spec
- route: /schedule

## 관련 Backend Spec
- LMS-API-SCH-001 (근무 일정 CRUD API)
- LMS-SCH-001 (근무일정 등록 Use Case), LMS-SCH-002 (근무일정 수정 Use Case), LMS-SCH-003 (근무일정 삭제 Use Case), LMS-SCH-004 (근무일정 조회 Use Case)
- LMS-API-EMP-001 (근로자 목록 조회 API)

## 화면 목적
MANAGER/ADMIN은 소속 매장 근로자의 주간/월간 근무 일정을 등록, 수정, 삭제, 확정하고, EMPLOYEE는 본인의 근무 일정을 조회한다.

## 접근 권한
- SUPER_ADMIN: 전체 매장 일정 관리
- MANAGER: 소속 매장 일정 관리
- EMPLOYEE: 본인 일정 조회만

## 화면 구성 요소

### 주간 일정 캘린더
- 표시 데이터: 주간 그리드 (월~일 7컬럼), 각 셀에 직원명 + 근무시간(HH:mm ~ HH:mm), 확정 일정은 파란색 배경, 미확정 일정은 회색 배경
- Backend API: GET /api/schedules?storeId={storeId}&startDate={weekStart}&endDate={weekEnd}
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: storeId, startDate (주 시작일, 월요일), endDate (주 종료일, 일요일)
  - 응답 매핑: schedules[].workDate -> 해당 날짜 컬럼, schedules[].employeeName -> 직원명, schedules[].workTime.startTime + endTime -> "HH:mm ~ HH:mm", schedules[].isConfirmed -> 배경색 (true: 파란색, false: 회색)
- EMPLOYEE 역할: 본인 일정만 표시 (GET /api/schedules?employeeId={myId}&startDate=...&endDate=...)
- 빈 상태: "해당 주에 등록된 근무 일정이 없습니다"
- 에러 상태: "근무 일정을 불러올 수 없습니다. 다시 시도해주세요."

### 주간 네비게이션
- 표시 데이터: 이전 주(< 버튼), 현재 주 표시("2026.03.09 ~ 2026.03.15"), 다음 주(> 버튼), 오늘 버튼
- Backend API: GET /api/schedules?startDate={newWeekStart}&endDate={newWeekEnd}
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: 주간 이동에 따른 startDate, endDate 변경
  - 응답 매핑: 주간 일정 캘린더 갱신
- 빈 상태: 해당 없음 (네비게이션은 항상 표시)
- 에러 상태: 해당 없음

### 일정 등록 모달 (MANAGER/ADMIN 전용)
- 표시 데이터: 직원 선택 드롭다운(소속 매장 근로자 목록), 근무 날짜(DatePicker), 시작 시간(TimePicker, HH:mm), 종료 시간(TimePicker, HH:mm)
- Backend API: POST /api/schedules
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: { employeeId: string, storeId: string, workDate: string, startTime: string, endTime: string }
  - 응답 매핑: 등록 성공 시 "근무 일정이 등록되었습니다." 메시지 표시, 캘린더 갱신
- Backend API: GET /api/employees?storeId={storeId}
  - 참조 Spec: LMS-API-EMP-001
  - 응답 매핑: employees[].id + name -> 직원 드롭다운 옵션
- 권한: MANAGER, SUPER_ADMIN만 사용 가능 — EMPLOYEE에게는 미표시
- 빈 상태: 직원 목록이 없으면 "배정된 근로자가 없습니다" 표시
- 에러 상태: "일정 등록에 실패했습니다. 다시 시도해주세요."

### 일정 상세/수정 모달 (MANAGER/ADMIN 전용)
- 표시 데이터: 선택한 일정의 직원명(읽기 전용), 근무 날짜, 시작 시간, 종료 시간, 확정 여부 토글, 삭제 버튼
- Backend API: PUT /api/schedules/{id}
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: { workDate: string, startTime: string, endTime: string, isConfirmed: boolean }
  - 응답 매핑: 수정 성공 시 "근무 일정이 수정되었습니다." 메시지 표시, 캘린더 갱신
- Backend API: DELETE /api/schedules/{id}
  - 참조 Spec: LMS-API-SCH-001
  - 응답 매핑: 삭제 성공 시 "근무 일정이 삭제되었습니다." 메시지, 캘린더 갱신
- 권한: MANAGER, SUPER_ADMIN만 사용 가능 — EMPLOYEE에게는 미표시
- 빈 상태: 해당 없음
- 에러 상태: 확정된 일정 수정 시도 시 "확정된 일정은 수정할 수 없습니다." (SCH003), "일정 수정에 실패했습니다. 다시 시도해주세요." (500)

## 사용자 흐름
1. 사용자가 /schedule에 접속하면 이번 주 근무 일정 캘린더가 표시된다
2. 주간 네비게이션으로 이전/다음 주를 탐색할 수 있다
3. MANAGER: 캘린더 빈 셀 클릭 -> 일정 등록 모달 열림 -> 직원/시간 선택 후 "등록" 클릭
4. MANAGER: 기존 일정 셀 클릭 -> 일정 상세/수정 모달 열림 -> 시간 수정 또는 삭제
5. MANAGER: 일정 확정 토글을 켜면 해당 일정이 확정 상태로 변경된다
6. EMPLOYEE: 본인 일정만 읽기 전용으로 확인한다

## 검증 조건
- 시작 시간이 종료 시간보다 이후일 수 없음
- 직원 선택은 필수 (빈 값 불가)
- 확정된 일정은 시간/날짜 변경 불가 (확정 해제 후 수정 가능)
- 동일 직원의 동일 날짜에 중복 일정 등록 시도 시 "해당 날짜에 이미 일정이 존재합니다." 표시

## 비기능 요구사항
- 초기 로딩: 2초 이내
- 인터랙션 반응: 100ms 이내
- API 실패 시: 에러 메시지 표시 + 재시도 버튼
- 캘린더 주간 이동 시 스켈레톤 로딩 표시
