# LMS-PAYROLL-001: 급여 산정

## 기본 정보
- type: use_case
- domain: payroll
- service: LMS
- priority: high

## 관련 정책
- POLICY-PAYROLL-001 (급여 계산 공식, 근무유형 판정, 가산율, 배치 규칙)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-PAYROLL-001-급여API](LMS-API-PAYROLL-001-급여API.md)
- [LMS-PAYROLL-002-급여정책관리](LMS-PAYROLL-002-급여정책관리.md)
- [LMS-ATTENDANCE-001-출퇴근기록](../attendance/LMS-ATTENDANCE-001-출퇴근기록.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **Payroll**: 생성 대상
  - 사용하는 주요 필드: employeeId, period, amount (baseAmount/overtimeAmount/deductions), isPaid
  - 상태 변경: 새 Payroll 생성 (isPaid=false)

### 참조 모델
- **Employee**: 대상 근로자 확인
  - 참조하는 필드: id
- **AttendanceRecord**: 근무 시간 데이터
  - 참조하는 필드: attendanceDate, attendanceTime, isCompleted()
- **LeaveRequest**: 휴가 날짜 제외
  - 참조하는 필드: leavePeriod, status (APPROVED만)
- **PayrollPolicy**: 가산율 적용
  - 참조하는 필드: policyType, multiplier, effectivePeriod
- **PayrollDetail**: 일별 급여 상세
  - 참조하는 필드: workDate, workType, hours, hourlyRate, multiplier, amount

## 개요
근로자의 특정 기간 출퇴근 기록과 급여 정책을 기반으로 급여를 산정한다.

## 선행 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 역할이어야 한다
- 대상 Employee가 존재해야 한다
- 해당 기간에 이미 산정된 급여가 없어야 한다
- 해당 기간에 출퇴근 기록이 존재해야 한다

## 기본 흐름
1. Employee를 조회한다
2. 해당 기간(YYYY-MM)에 이미 급여가 존재하는지 확인한다
3. 기간의 시작일(1일)과 종료일(말일)을 계산한다
4. 해당 기간의 출퇴근 기록을 조회한다
5. 해당 기간의 승인된 휴가를 조회하여 기간과 겹치는 것만 필터링한다
6. 유효한 급여 정책을 조회한다
7. PayrollCalculationEngine.calculate()를 호출한다
8. Payroll.create(context, employeeId, period, amount)로 Payroll을 생성한다
9. 계산 결과의 상세 내역으로 PayrollDetail.create()를 생성한다
10. Payroll과 PayrollDetail을 모두 저장한다

## 대안 흐름
- Employee가 존재하지 않는 경우: `EmployeeNotFoundException` 발생
- 해당 기간에 이미 급여가 산정된 경우: `PayrollAlreadyCalculatedException` 발생
- 해당 기간에 출퇴근 기록이 없는 경우: `NoAttendanceRecordsFoundException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 유효한 정보로 급여 산정 시 Payroll과 PayrollDetail이 생성되어야 한다
- 생성된 Payroll의 isPaid는 false여야 한다
- baseAmount는 WEEKDAY 근무의 합계여야 한다
- overtimeAmount는 비WEEKDAY(NIGHT, WEEKEND, HOLIDAY) 근무의 합계여야 한다
- totalAmount = baseAmount + overtimeAmount - deductions여야 한다
- 동일 기간에 중복 급여 산정 시 PayrollAlreadyCalculatedException이 발생해야 한다
- 출퇴근 기록이 없는 기간 산정 시 NoAttendanceRecordsFoundException이 발생해야 한다
- PayrollDetail의 amount = hours × hourlyRate × multiplier (HALF_UP, scale 2)

## 비즈니스 규칙

### 근무유형 판정 (우선순위)
1. HOLIDAY: 공휴일 (1월 1일, 12월 25일)
2. WEEKEND: 토요일 또는 일요일
3. NIGHT: 22:00 ~ 06:00
4. WEEKDAY: 위에 해당하지 않는 경우

### 가산율 기본값 (정책 없는 경우)
- 모든 유형: 1.0배

### 급여 분류
- 기본급(baseAmount): WorkType.WEEKDAY인 PayrollDetail의 합계
- 초과근무수당(overtimeAmount): WorkType.WEEKDAY가 아닌 PayrollDetail의 합계
- 총액: baseAmount + overtimeAmount - deductions

### PayrollAmount 제약
- baseAmount >= 0
- overtimeAmount >= 0
- deductions >= 0
- calculateTotal(): HALF_UP, scale 2

### 배치 급여 산정 (ExecutePayrollBatchAppService)
- 특정 매장 또는 전체 활성 근로자 대상
- 개별 실패 시에도 나머지 계속 처리 (graceful degradation)
- BatchStatus: 모든 성공 → COMPLETED, 부분 실패 → PARTIAL_SUCCESS, 전체 실패 → FAILED
- hourlyRate 하드코딩: 10,000원 (FIXME)
- 스케줄: 매월 마지막 날 01:00 (cron: `0 0 1 L * ?`)

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용. 추가 특화 사항:

### 데이터 정합성
- Payroll과 PayrollDetail 저장은 같은 트랜잭션에서 처리되어야 한다

## 테스트 시나리오

### TC-PAY-001-01: 정상 급여 산정 (Integration)
- Given: Employee에 2026-02 기간 출퇴근 기록이 존재하고 급여 미산정이다
- When: 2026-02 급여를 산정한다
- Then: Payroll(isPaid=false)과 PayrollDetail이 생성된다

### TC-PAY-001-02: 중복 급여 산정 (Integration)
- Given: 2026-02 급여가 이미 산정되어 있다
- When: 같은 기간 급여를 산정한다
- Then: PayrollAlreadyCalculatedException이 발생한다

### TC-PAY-001-03: 출퇴근 기록 없음 (Integration)
- Given: 해당 기간에 출퇴근 기록이 없다
- When: 급여를 산정한다
- Then: NoAttendanceRecordsFoundException이 발생한다

### TC-PAY-001-04: 근무유형별 가산율 적용 (Integration)
- Given: 평일/야간/주말/공휴일 출퇴근 기록이 존재한다
- When: 급여를 산정한다
- Then: 각 근무유형에 해당하는 가산율이 적용된 PayrollDetail이 생성된다

### TC-PAY-001-05: 휴가 날짜 제외 (Integration)
- Given: 출퇴근 기록과 승인된 휴가가 겹치는 날짜가 있다
- When: 급여를 산정한다
- Then: 휴가 날짜의 출퇴근 기록은 계산에서 제외된다

### TC-PAY-001-06: PayrollAmount 검증 (Unit)
- Given: baseAmount가 음수이다
- When: PayrollAmount를 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-PAY-001-07: 배치 급여 산정 - 부분 실패 (Integration)
- Given: 3명의 활성 Employee 중 1명은 출퇴근 기록이 없다
- When: 배치 급여 산정을 실행한다
- Then: 2명은 성공, 1명은 실패, BatchStatus=PARTIAL_SUCCESS

### TC-PAY-001-08: 권한 검증 - EMPLOYEE 접근 (E2E)
- Given: EMPLOYEE 역할로 로그인한 상태이다
- When: 급여 산정 API를 호출한다
- Then: 403 Forbidden이 반환된다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
