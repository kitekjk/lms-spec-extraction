# POLICY-PAYROLL-001: 급여 정책

## 기본 정보
- type: policy
- domain: payroll
- related-models: Payroll, PayrollDetail, PayrollPolicy, PolicyType, WorkType, PolicyMultiplier, PayrollAmount
- related-services: PayrollCalculationEngine
- related-specs: [POLICY-ATTENDANCE-001-출퇴근.md, POLICY-SCHEDULE-001-근무일정.md]

## 정책 규칙

### RULE-001: 급여 정책 유형
- 조건: 급여 가산율 정책 구분
- 결과:
  | 유형 | 코드 | 설명 |
  |------|------|------|
  | 평일 초과근무 | `OVERTIME_WEEKDAY` | 평일 초과근무 가산율 |
  | 주말 초과근무 | `OVERTIME_WEEKEND` | 주말 초과근무 가산율 |
  | 공휴일 초과근무 | `OVERTIME_HOLIDAY` | 공휴일 초과근무 가산율 |
  | 야간 근무 | `NIGHT_SHIFT` | 야간 근무 가산율 |
  | 휴일 근무 | `HOLIDAY_WORK` | 휴일 근무 가산율 |
  | 보너스 | `BONUS` | 보너스 |
  | 수당 | `ALLOWANCE` | 수당 |
- 근거: `PolicyType.kt`

### RULE-002: 근무 유형 분류
- 조건: 출퇴근 기록 기반 근무 유형 판단
- 결과:
  | 유형 | 코드 | 기준 |
  |------|------|------|
  | 평일 기본 근무 | `WEEKDAY` | 평일, 주간 근무 |
  | 야간 근무 | `NIGHT` | 22:00 ~ 06:00 시간대 근무 |
  | 주말 근무 | `WEEKEND` | 토요일 또는 일요일 |
  | 공휴일 근무 | `HOLIDAY` | 공휴일 (현재: 1월 1일, 12월 25일) |
- 판단 우선순위: 공휴일 > 주말 > 야간 > 평일
- 근거: `PayrollCalculationEngine.kt` - `determineWorkType()`

### RULE-003: 기본 가산율 배율
- 조건: `PolicyMultiplier` 사전 정의 배율
- 결과:
  | 배율명 | 값 | 용도 |
  |--------|-----|------|
  | standard() | 1.5 | 일반 초과근무 |
  | weekend() | 2.0 | 주말/야간 근무 |
  | holiday() | 2.5 | 공휴일 근무 |
- 배율 값 범위: 0 이상 10.0 이하
  - 0 미만 시 에러: "정책 배율은 0 이상이어야 합니다. 입력값: {value}"
  - 10.0 초과 시 에러: "정책 배율은 10.0 이하여야 합니다. 입력값: {value}"
- 근거: `PolicyMultiplier.kt`

### RULE-004: 급여 상세 내역 계산 공식
- 조건: 일별 급여 상세 내역 계산 시
- 결과: `금액 = 근무시간(hours) x 시급(hourlyRate) x 가산율(multiplier)`
- 소수점 처리: `setScale(2, RoundingMode.HALF_UP)` (소수 둘째자리, 반올림)
- 검증 조건:
  - 근무 시간: 0 이상 - "근무 시간은 0 이상이어야 합니다. 입력값: {hours}"
  - 시급: 0 초과 - "시급은 0보다 커야 합니다. 입력값: {hourlyRate}"
  - 가산율: 0 이상 - "가산율은 0 이상이어야 합니다. 입력값: {multiplier}"
- 근거: `PayrollDetail.kt` - `create()`, `init` 블록

### RULE-005: 급여 계산 엔진 로직
- 조건: 월별 급여 계산 실행 시
- 입력: 출퇴근 기록 목록, 승인된 휴가 목록, 시급, 가산율 정책 목록
- 결과:
  1. 승인된 휴가 날짜를 추출하여 제외 목록 생성
  2. 퇴근 완료된 출퇴근 기록만 대상 (`isCompleted()`)
  3. 휴가 날짜에 해당하는 기록 제외
  4. 일별로 근무 유형 판단 및 가산율 적용하여 급여 계산
  5. 기본급 (WEEKDAY 유형) 과 가산 금액 (NIGHT/WEEKEND/HOLIDAY 유형) 분리 합산
  6. 총 급여 = 기본급 + 가산 금액 (소수 둘째자리 반올림)
- 근거: `PayrollCalculationEngine.kt` - `calculate()`

### RULE-006: 근무 유형별 가산율 매핑
- 조건: 근무 유형에 따른 정책 유형 매핑
- 결과:
  | 근무 유형 (WorkType) | 정책 유형 (PolicyType) | 기본 가산율 |
  |---------------------|----------------------|------------|
  | WEEKDAY | - | 1.0 (가산율 없음) |
  | NIGHT | OVERTIME_WEEKDAY | 정책 조회, 미존재 시 1.0 |
  | WEEKEND | OVERTIME_WEEKEND | 정책 조회, 미존재 시 1.0 |
  | HOLIDAY | OVERTIME_HOLIDAY | 정책 조회, 미존재 시 1.0 |
- 해당 날짜에 유효한 정책이 없으면 기본 가산율 1.0 적용
- 근거: `PayrollCalculationEngine.kt` - `findMultiplier()`

### RULE-007: 야간 근무 판단 기준
- 조건: 출퇴근 기록의 시간대 확인
- 결과: 출근 시간이 22:00 이후이거나 06:00 이전, 또는 퇴근 시간이 22:00 이후이거나 06:00 이전인 경우 야간 근무로 판단
- 야간 시간대: 22:00 ~ 06:00
- 근거: `PayrollCalculationEngine.kt` - `isNightWork()`

### RULE-008: 공휴일 판단 기준
- 조건: 날짜의 공휴일 여부 확인
- 결과: 현재 하드코딩된 공휴일:
  - 1월 1일 (신정)
  - 12월 25일 (크리스마스)
- 참고: 추후 공휴일 테이블 또는 외부 API로 대체 필요 (TODO)
- 근거: `PayrollCalculationEngine.kt` - `isHoliday()`

### RULE-009: 급여 지급 완료 처리
- 조건: 급여 지급 처리 시
- 결과:
  - 이미 지급된 급여면 실패: "이미 지급된 급여입니다."
  - `isPaid`를 `true`로 변경
  - `paidAt`에 지급 시간 기록
- 근거: `Payroll.kt` - `markAsPaid()`

### RULE-010: 지급 완료 급여 수정 불가
- 조건: 이미 지급된 급여에 대해 수정 시도
- 결과: 다음 작업 모두 실패:
  - 초과근무수당 추가: "이미 지급된 급여는 수정할 수 없습니다."
  - 공제액 추가: "이미 지급된 급여는 수정할 수 없습니다."
  - 재계산: "이미 지급된 급여는 재계산할 수 없습니다."
- 근거: `Payroll.kt` - `addOvertime()`, `addDeduction()`, `recalculate()`

### RULE-011: 급여 정책 유효 기간 관리
- 조건: 급여 정책의 시작일/종료일 관리
- 결과:
  - `effectivePeriod`로 유효 기간 관리
  - `isEffectiveOn(date)`: 특정 날짜에 유효한지 확인
  - `isCurrentlyEffective()`: 현재 유효한지 확인
  - 유효하지 않은 정책 배율 수정 시 실패: "유효하지 않은 정책은 수정할 수 없습니다."
- 근거: `PayrollPolicy.kt` - `updateMultiplier()`, `isEffectiveOn()`

### RULE-012: 급여 정책 금액 적용
- 조건: 기본 금액에 정책 배율 적용
- 결과: `baseAmount * multiplier.value`
- 근거: `PayrollPolicy.kt` - `applyTo()`

## 에러 코드

| 코드 | 예외 클래스 | 기본 메시지 |
|------|-------------|-------------|
| PAYROLL001 | `PayrollNotFoundException` | "급여를 찾을 수 없습니다: {payrollId}" |
| PAYROLL002 | `PayrollAlreadyCalculatedException` | "해당 기간의 급여가 이미 계산되었습니다." |
| PAYROLL003 | `NoAttendanceRecordsFoundException` | "출퇴근 기록이 없습니다." |
| PAYROLL_POLICY001 | `PayrollPolicyNotFoundException` | "급여 정책을 찾을 수 없습니다: {policyId}" |
| PAYROLL_POLICY002 | `PayrollPolicyPeriodOverlapException` | "정책 기간이 기존 정책과 겹칩니다." |
| PAYROLL_POLICY003 | `InvalidPolicyPeriodException` | "유효하지 않은 정책 기간입니다." |
| PAYROLL_POLICY004 | `InactivePolicyCannotBeModifiedException` | "종료되거나 유효하지 않은 정책은 수정할 수 없습니다." |

## 적용 대상

- LMS-PAY-001 (급여 계산)
- LMS-PAY-002 (급여 조회)
- LMS-PAY-003 (급여 상세 조회)
- LMS-PAY-004 (급여 지급 처리)
- LMS-PAY-005 (급여 재계산)
- LMS-PAY-006 (급여 정책 등록)
- LMS-PAY-007 (급여 정책 수정)
- LMS-PAY-008 (급여 정책 조회)
