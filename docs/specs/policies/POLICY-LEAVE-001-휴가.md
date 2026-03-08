# POLICY-LEAVE-001: 휴가 정책

## 기본 정보
- type: policy
- domain: leave
- related-models: LeaveRequest, LeaveType, LeaveStatus, LeavePeriod, RemainingLeave
- related-services: LeavePolicyService
- related-specs: [POLICY-ATTENDANCE-001-출퇴근.md]

## 정책 규칙

### RULE-001: 직급별 초기 연차 부여
- 조건: 근로자 등록 시 직급에 따라 초기 연차 자동 부여
- 결과:
  | 직급 | 코드 | 초기 연차 (일) | 설명 |
  |------|------|---------------|------|
  | 정규직 | `REGULAR` | 15 | 연간 15일의 유급 연차 |
  | 계약직 | `IRREGULAR` | 11 | 연간 11일의 유급 연차 |
  | 아르바이트 | `PART_TIME` | 0 | 연차 없음, 무급 휴가만 가능 |
- 근거: `Employee.kt` - `create()`, `LeavePolicyService.kt` - `getAnnualLeaveByEmployeeType()`

### RULE-002: 잔여 연차 유효성 검증
- 조건: `RemainingLeave` Value Object 생성/변경 시
- 결과: 잔여 연차 값이 0 미만이면 실패
- 에러 메시지: "잔여 연차는 음수일 수 없습니다."
- 근거: `RemainingLeave.kt` - `init` 블록

### RULE-003: 연차 차감 규칙
- 조건: 휴가 승인으로 연차 차감 시
- 결과:
  - 차감 일수는 0보다 커야 함 - "차감할 연차는 0보다 커야 합니다."
  - 잔여 연차 >= 차감 일수여야 함 - "잔여 연차가 부족합니다. 현재: {value}, 요청: {days}"
  - 파트타임 근로자는 연차 확인 불필요 (무급 휴가로 처리)
- 근거: `RemainingLeave.kt` - `deduct()`

### RULE-004: 연차 복구 규칙
- 조건: 휴가 취소로 연차 복구 시
- 결과: 복구 일수는 0보다 커야 함 - "복구할 연차는 0보다 커야 합니다."
- 근거: `RemainingLeave.kt` - `add()`

### RULE-005: 휴가 유형
- 조건: 휴가 신청 시 유형 선택
- 결과:
  | 유형 | 코드 | 설명 | 승인 필요 |
  |------|------|------|----------|
  | 연차 | `ANNUAL` | 연차 | O |
  | 병가 | `SICK` | 병가 | O |
  | 개인 사유 | `PERSONAL` | 개인 사유 | O |
  | 출산 휴가 | `MATERNITY` | 출산 휴가 | O |
  | 육아 휴가 | `PATERNITY` | 육아 휴가 | O |
  | 경조사 | `BEREAVEMENT` | 경조사 | O |
  | 무급 휴가 | `UNPAID` | 무급 휴가 | O |
- 모든 휴가 유형은 승인이 필요함 (`requiresApproval = true`)
- 근거: `LeaveType.kt`

### RULE-006: 휴가 신청 상태 전이
- 조건: 휴가 신청의 상태 변경
- 결과:
  ```
  PENDING (승인 대기) --> APPROVED (승인됨)
  PENDING (승인 대기) --> REJECTED (거부됨)
  PENDING (승인 대기) --> CANCELLED (취소됨)
  APPROVED (승인됨) --> CANCELLED (취소됨)
  ```
- 허용되지 않는 전이: REJECTED -> 다른 상태, CANCELLED -> 다른 상태
- 근거: `LeaveRequest.kt` - `approve()`, `reject()`, `cancel()`

### RULE-007: 휴가 승인 규칙
- 조건: 매니저/관리자가 휴가 승인 시
- 결과:
  - 현재 상태가 `PENDING`이어야 함 - "대기 중인 휴가 신청만 승인할 수 있습니다. 현재 상태: {status.description}"
  - 상태를 `APPROVED`로 변경
  - `approvedBy`에 승인자 ID 기록
  - `approvedAt`에 승인 시간 기록
- 근거: `LeaveRequest.kt` - `approve()`

### RULE-008: 휴가 거부 규칙
- 조건: 매니저/관리자가 휴가 거부 시
- 결과:
  - 현재 상태가 `PENDING`이어야 함 - "대기 중인 휴가 신청만 거부할 수 있습니다. 현재 상태: {status.description}"
  - 거부 사유는 필수 (공백 불가) - "거부 사유는 필수입니다."
  - 상태를 `REJECTED`로 변경
  - `rejectionReason`에 거부 사유 기록
- 근거: `LeaveRequest.kt` - `reject()`

### RULE-009: 휴가 취소 규칙
- 조건: 근로자가 휴가 취소 시
- 결과:
  - 현재 상태가 `PENDING` 또는 `APPROVED`여야 함 - "대기 중이거나 승인된 휴가 신청만 취소할 수 있습니다. 현재 상태: {status.description}"
  - 상태를 `CANCELLED`로 변경
  - 승인된 휴가를 취소하면 연차 복구 필요 (Employee.restoreLeave)
- 근거: `LeaveRequest.kt` - `cancel()`

### RULE-010: 휴가 기간 유효성 검증
- 조건: `LeavePeriod` Value Object 생성 시
- 결과:
  - `startDate`가 `endDate`보다 늦으면 실패 - "시작일은 종료일보다 늦을 수 없습니다. 시작: {startDate}, 종료: {endDate}"
- 근거: `LeavePeriod.kt` - `init` 블록

### RULE-011: 휴가 일수 계산
- 조건: 휴가 기간 계산 시
- 결과: `ChronoUnit.DAYS.between(startDate, endDate) + 1` (시작일과 종료일 모두 포함)
- 근거: `LeavePeriod.kt` - `calculateDays()`

### RULE-012: 휴가 기간 중복 검사
- 조건: 새 휴가 신청 시 기존 휴가와 기간 비교
- 결과: `!endDate.isBefore(other.startDate) && !startDate.isAfter(other.endDate)` 으로 겹침 여부 판단
- 근거: `LeavePeriod.kt` - `overlapsWith()`, `LeaveRequest.kt` - `overlapsWith()`

### RULE-013: 휴가 신청 가능 여부 검증 (LeavePolicyService)
- 조건: 휴가 신청 전 잔여 연차 확인
- 결과:
  - 파트타임 근로자: 항상 신청 가능 (무급 휴가)
  - 정규직/계약직: `remainingLeave.value >= requestedDays` 여야 신청 가능
  - 불가 시 메시지: "잔여 연차가 부족합니다. 신청: {requestedDays}일, 잔여: {remainingLeave.value}일"
- 근거: `LeavePolicyService.kt` - `canRequestLeave()`, `validateLeaveRequest()`

## 에러 코드

| 코드 | 예외 클래스 | 기본 메시지 |
|------|-------------|-------------|
| LEAVE001 | `LeaveRequestNotFoundException` | "휴가 신청을 찾을 수 없습니다: {leaveRequestId}" |
| LEAVE002 | `InsufficientLeaveBalanceException` | "잔여 연차가 부족합니다. 신청: {requestedDays}일, 잔여: {remainingDays}일" |
| LEAVE003 | `LeaveRequestDateOverlapException` | "이미 승인된 휴가와 기간이 겹칩니다." |
| LEAVE004 | `LeaveRequestCannotBeCancelledException` | "현재 상태에서는 휴가 신청을 취소할 수 없습니다." |
| LEAVE005 | `LeaveRequestCannotBeProcessedException` | "현재 상태에서는 휴가 신청을 승인/반려할 수 없습니다." |
| LEAVE006 | `PastDateLeaveRequestException` | "과거 날짜로 휴가를 신청할 수 없습니다: {requestDate}" |
| LEAVE007 | `InvalidLeaveDateRangeException` | "유효하지 않은 휴가 기간입니다." |

## 적용 대상

- LMS-LEAVE-001 (휴가 신청)
- LMS-LEAVE-002 (휴가 승인)
- LMS-LEAVE-003 (휴가 반려)
- LMS-LEAVE-004 (휴가 취소)
- LMS-LEAVE-005 (휴가 조회)
