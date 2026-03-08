# POLICY-ATTENDANCE-001: 출퇴근 정책

## 기본 정보
- type: policy
- domain: attendance
- related-models: AttendanceRecord, AttendanceTime, AttendanceStatus
- related-specs: [POLICY-SCHEDULE-001-근무일정.md]

## 정책 규칙

### RULE-001: 출근 체크 (Check-In)
- 조건: 근로자가 출근 시
- 결과:
  - 출근 시간(`checkInTime`)을 `Instant`로 기록
  - `attendanceDate`는 출근 시간 기준 시스템 기본 타임존(`ZoneId.systemDefault()`)의 `LocalDate`로 설정
  - 초기 상태: `PENDING` (퇴근 대기 중)
  - `checkOutTime`은 `null`로 설정
  - `workScheduleId`는 선택적 (nullable)
- 근거: `AttendanceRecord.kt` - `checkIn()`

### RULE-002: 퇴근 체크 (Check-Out)
- 조건: 출근 기록이 있는 상태에서 퇴근 시
- 결과:
  - 퇴근 시간(`checkOutTime`)을 `Instant`로 기록
  - 상태를 `NORMAL`로 변경 (이후 `evaluateStatus`에서 재평가)
- 검증 조건:
  - `checkOutTime`이 이미 설정되어 있으면 실패: "이미 퇴근 처리되었습니다."
  - `checkOutTime`이 `checkInTime`보다 이전이면 실패: "퇴근 시간은 출근 시간보다 이전일 수 없습니다."
- 근거: `AttendanceTime.kt` - `checkOut()`

### RULE-003: 출퇴근 시간 유효성 검증
- 조건: `AttendanceTime` Value Object 생성 시
- 결과: `checkOutTime`이 `null`이 아닌 경우, `checkInTime`이 `checkOutTime`보다 늦으면 실패
- 에러 메시지: "출근 시간은 퇴근 시간보다 늦을 수 없습니다. 출근: {checkInTime}, 퇴근: {checkOutTime}"
- 근거: `AttendanceTime.kt` - `init` 블록

### RULE-004: 근무 상태 평가 (evaluateStatus)
- 조건: 퇴근 완료 후 근무 일정과 비교하여 상태 평가
- 전제 조건: `attendanceTime.isCompleted()` (퇴근 처리 완료). 미완료 시 에러: "퇴근 처리되지 않은 기록은 평가할 수 없습니다."
- 결과 (우선순위 순):
  1. **LATE (지각)**: 실제 출근 시간이 `예정 시작 시간 + 10분` 이후이고, 실제 퇴근 시간이 예정 종료 시간 이전
  2. **EARLY_LEAVE (조퇴)**: 실제 출근 시간이 `예정 시작 시간 + 10분` 이내이고, 실제 퇴근 시간이 예정 종료 시간 이전
  3. **NORMAL (정상)**: 그 외 모든 경우
- 지각 허용 시간: 10분 (`LATE_TOLERANCE_MINUTES = 10L`)
- 근거: `AttendanceRecord.kt` - `evaluateStatus()`, `LATE_TOLERANCE_MINUTES`

### RULE-005: 출퇴근 상태 종류
- 조건: 출퇴근 상태 분류
- 결과:
  | 상태 | 코드 | 설명 |
  |------|------|------|
  | 정상 출근 | `NORMAL` | 정상적인 출퇴근 |
  | 지각 | `LATE` | 예정 시작 시간 + 10분 이후 출근 |
  | 조퇴 | `EARLY_LEAVE` | 예정 종료 시간 이전 퇴근 |
  | 결근 | `ABSENT` | 출근하지 않음 |
  | 퇴근 대기 중 | `PENDING` | 출근 후 퇴근 전 상태 |
- 근거: `AttendanceStatus.kt`

### RULE-006: 결근 처리
- 조건: 관리자/매니저가 근로자를 결근 처리할 때
- 결과: 상태를 `ABSENT`로 변경
- 근거: `AttendanceRecord.kt` - `markAsAbsent()`

### RULE-007: 실제 근무 시간 계산
- 조건: 퇴근이 완료된 기록에 대해 실제 근무 시간 계산
- 결과: `Duration.between(checkInTime, checkOutTime).toMinutes() / 60.0` (시간 단위, 소수점)
- `checkOutTime`이 `null`이면 `null` 반환
- 근거: `AttendanceTime.kt` - `calculateActualWorkHours()`

### RULE-008: 중복 출근 방지
- 조건: 동일 근로자, 동일 날짜에 이미 출근 기록이 있을 때 재출근 시도
- 결과: `AlreadyCheckedInException` 발생
- 에러 코드: `ATT002`
- 에러 메시지: "이미 출근 처리되었습니다. 근로자: {employeeId}, 날짜: {date}"
- 근거: `AttendanceException.kt`

### RULE-009: 미출근 상태에서 퇴근 시도
- 조건: 출근 기록이 없는 상태에서 퇴근 시도
- 결과: `NotCheckedInException` 발생
- 에러 코드: `ATT003`
- 에러 메시지: "출근 기록이 없습니다. 근로자: {employeeId}, 날짜: {date}"
- 근거: `AttendanceException.kt`

### RULE-010: 중복 퇴근 방지
- 조건: 이미 퇴근한 상태에서 재퇴근 시도
- 결과: `AlreadyCheckedOutException` 발생
- 에러 코드: `ATT004`
- 에러 메시지: "이미 퇴근 처리되었습니다. 근로자: {employeeId}, 날짜: {date}"
- 근거: `AttendanceException.kt`

## 에러 코드

| 코드 | 예외 클래스 | 기본 메시지 |
|------|-------------|-------------|
| ATT001 | `AttendanceNotFoundException` | "출퇴근 기록을 찾을 수 없습니다: {attendanceId}" |
| ATT002 | `AlreadyCheckedInException` | "이미 출근 처리되었습니다. 근로자: {employeeId}, 날짜: {date}" |
| ATT003 | `NotCheckedInException` | "출근 기록이 없습니다. 근로자: {employeeId}, 날짜: {date}" |
| ATT004 | `AlreadyCheckedOutException` | "이미 퇴근 처리되었습니다. 근로자: {employeeId}, 날짜: {date}" |

## 적용 대상

- LMS-ATT-001 (출근)
- LMS-ATT-002 (퇴근)
- LMS-ATT-003 (출퇴근 조정)
- LMS-ATT-004 (출퇴근 조회)
