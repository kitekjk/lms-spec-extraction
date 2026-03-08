# POLICY-SCHEDULE-001: 근무 일정 정책

## 기본 정보
- type: policy
- domain: schedule
- related-models: WorkSchedule, WorkTime, WorkDate
- related-specs: [POLICY-ATTENDANCE-001-출퇴근.md]

## 정책 규칙

### RULE-001: 근무 일정 생성
- 조건: 새로운 근무 일정 등록 시
- 결과:
  - 근무 일정 ID 자동 생성 (`WorkScheduleId.generate()`)
  - 초기 확정 상태: `false` (미확정)
  - 필수 항목: `employeeId`, `storeId`, `workDate`, `workTime`
- 근거: `WorkSchedule.kt` - `create()`

### RULE-002: 근무 시간 유효성 검증
- 조건: `WorkTime` Value Object 생성 시
- 결과: `startTime`이 `endTime`보다 늦으면 실패
- 에러 메시지: "시작 시간은 종료 시간보다 늦을 수 없습니다. 시작: {startTime}, 종료: {endTime}"
- 근거: `WorkTime.kt` - `init` 블록

### RULE-003: 표준 근무 시간
- 조건: 기본 근무 시간 생성 시
- 결과: 09:00 ~ 18:00 (9시간)
- 근거: `WorkTime.kt` - `fun standard(): WorkTime = WorkTime(startTime = LocalTime.of(9, 0), endTime = LocalTime.of(18, 0))`

### RULE-004: 근무 시간 계산
- 조건: 근무 시간 조회 시
- 결과: `Duration.between(startTime, endTime).toMinutes() / 60.0` (시간 단위, 소수점)
- 근거: `WorkTime.kt` - `calculateWorkHours()`

### RULE-005: 근무 일정 확정
- 조건: 미확정 상태의 근무 일정에 대해 확정 시도
- 결과: `isConfirmed`를 `true`로 변경
- 검증: 이미 확정된 일정이면 실패 - "이미 확정된 근무 일정입니다."
- 근거: `WorkSchedule.kt` - `confirm()`

### RULE-006: 근무 일정 확정 취소
- 조건: 확정된 근무 일정에 대해 확정 취소 시도
- 결과: `isConfirmed`를 `false`로 변경
- 검증: 확정되지 않은 일정이면 실패 - "확정되지 않은 근무 일정입니다."
- 근거: `WorkSchedule.kt` - `unconfirm()`

### RULE-007: 확정된 일정 변경 불가
- 조건: 확정된 근무 일정의 근무 시간 또는 날짜 변경 시도
- 결과: 변경 실패
- 에러 메시지: "확정된 근무 일정은 변경할 수 없습니다."
- 적용 대상: `changeWorkTime()`, `changeWorkDate()`
- 근거: `WorkSchedule.kt` - `require(!isConfirmed)`

### RULE-008: 중복 일정 방지
- 조건: 동일 근로자, 동일 날짜에 이미 근무 일정이 존재할 때 추가 등록 시도
- 결과: `DuplicateWorkScheduleException` 발생
- 에러 코드: `SCH002`
- 에러 메시지: "이미 해당 날짜에 근무 일정이 존재합니다. 근로자: {employeeId}, 날짜: {date}"
- 근거: `WorkScheduleException.kt`

### RULE-009: 매장 소속 검증
- 조건: 근무 일정 등록 시 근로자의 매장 소속 확인
- 결과: 근로자가 해당 매장에 속하지 않으면 `EmployeeNotBelongToStoreException` 발생
- 에러 코드: `SCH004`
- 에러 메시지: "근로자가 해당 매장에 속하지 않습니다. 근로자: {employeeId}, 매장: {storeId}"
- 근거: `WorkScheduleException.kt`

### RULE-010: 매니저 권한 제한
- 조건: 매니저가 근무 일정 관리 시
- 결과: 자기 매장의 일정만 관리 가능. 다른 매장 접근 시 `ManagerCanOnlyManageOwnStoreSchedulesException` 발생
- 에러 코드: `SCH005`
- 에러 메시지: "관리자는 자신의 매장 일정만 관리할 수 있습니다. 관리자: {managerId}, 매장: {storeId}"
- 근거: `WorkScheduleException.kt`

### RULE-011: 주말 근무 식별
- 조건: 근무 일정의 날짜 확인 시
- 결과: `workDate.isWeekend()`으로 토요일/일요일 여부 판별
- 근거: `WorkSchedule.kt` - `isWeekendWork()`

## 에러 코드

| 코드 | 예외 클래스 | 기본 메시지 |
|------|-------------|-------------|
| SCH001 | `WorkScheduleNotFoundException` | "근무 일정을 찾을 수 없습니다: {scheduleId}" |
| SCH002 | `DuplicateWorkScheduleException` | "이미 해당 날짜에 근무 일정이 존재합니다." |
| SCH003 | `ConfirmedScheduleCannotBeModifiedException` | "확정된 근무 일정은 수정할 수 없습니다: {scheduleId}" |
| SCH004 | `EmployeeNotBelongToStoreException` | "근로자가 해당 매장에 속하지 않습니다." |
| SCH005 | `ManagerCanOnlyManageOwnStoreSchedulesException` | "관리자는 자신의 매장 일정만 관리할 수 있습니다." |

## 적용 대상

- LMS-SCH-001 (근무일정 등록)
- LMS-SCH-002 (근무일정 수정)
- LMS-SCH-003 (근무일정 삭제)
- LMS-SCH-004 (근무일정 조회)
