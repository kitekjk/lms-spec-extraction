# LMS-PAY-004: 급여산정

## 기본 정보
- type: use_case
- domain: payroll

## 관련 Spec
- LMS-API-PAY-001 (급여API)
- LMS-PAY-005 (급여배치실행)
- LMS-PAY-006 (급여조회)

## 개요
관리자가 근로자 ID, 급여 기간, 시급을 입력하여 출퇴근 기록과 정책을 기반으로 급여를 계산한다.

## 관련 모델
- 주 모델: Payroll (Aggregate Root)
- 참조 모델: Employee, AttendanceRecord, LeaveRequest, PayrollPolicy, PayrollDetail, PayrollAmount, PayrollPeriod, PayrollCalculationEngine, WorkType, PolicyType

## 선행 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 대상 근로자가 존재해야 한다
- 해당 기간에 출퇴근 기록이 존재해야 한다
- 해당 기간/근로자에 대해 아직 급여가 계산되지 않은 상태여야 한다

## 기본 흐름
1. 관리자가 근로자 ID, 급여 기간(YYYY-MM), 시급을 입력하여 급여 계산을 요청한다
2. 시스템은 근로자 존재를 확인한다
3. 시스템은 해당 기간에 이미 계산된 급여가 있는지 확인한다 (중복 방지)
4. 시스템은 해당 기간(월 1일~말일)의 출퇴근 기록을 조회한다
5. 시스템은 해당 기간의 승인된(APPROVED) 휴가를 조회하여 기간 내에 속하는 휴가를 필터링한다
6. 시스템은 기간 시작일 기준 유효한 급여 정책을 조회한다
7. 시스템은 PayrollCalculationEngine을 통해 급여를 계산한다:
   - 출퇴근 기록, 승인된 휴가, 시급, 정책 목록을 입력으로 계산 수행
   - 기본급(baseAmount)과 초과근무수당(overtimeAmount) 산출
   - 일별 상세 내역(근무일, 근무유형, 시간, 시급, 가산율, 금액) 생성
8. 시스템은 Payroll을 생성하여 저장한다 (지급상태: 미지급, 지급일: null)
9. 시스템은 PayrollDetail 목록을 일괄 생성하여 저장한다
10. 시스템은 계산 결과를 반환한다

## 대안 흐름
- 승인된 휴가가 없는 경우: 출퇴근 기록만으로 급여를 계산한다
- 유효한 급여 정책이 없는 경우: 기본 가산율(1.0)로 계산한다

## 예외 흐름
- 근로자를 찾을 수 없는 경우: EmployeeNotFoundException 발생
- 해당 기간에 이미 급여가 계산된 경우: PayrollAlreadyCalculatedException (PAYROLL002) 발생
- 출퇴근 기록이 없는 경우: NoAttendanceRecordsFoundException (PAYROLL003) 발생

## 검증 조건
- 근로자 ID(employeeId)는 비어 있지 않은 문자열이어야 한다
- 급여 기간(period)은 YYYY-MM 형식의 유효한 연월이어야 한다
- 시급(hourlyRate)은 0보다 큰 BigDecimal 값이어야 한다
- 동일 근로자의 동일 기간에 대해 급여가 중복 계산되지 않아야 한다
- 금액 계산 시 소수점 둘째 자리 반올림(HALF_UP) 적용

## 관련 정책
- POLICY-PAYROLL-001 참조 (급여 계산, 가산율 적용, 근무유형 판정, 공휴일 우선순위, 소수점 반올림 규칙)
- POLICY-NFR-001 참조

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-PAY-004-01: 평일 기본 근무 급여 산정 (Integration)

- Given: MANAGER 권한 사용자가 로그인하고, 대상 근로자가 2026-03에 평일 기본 근무(WEEKDAY) 출퇴근 기록 20건 보유, 시급 10,000원
- When: 해당 근로자의 2026-03 급여 산정 요청
- Then: 기본급 = 근무시간 x 10,000 x 1.0으로 계산되고, 초과근무수당 0원, Payroll이 미지급 상태로 생성됨

### TC-PAY-004-02: 야간 근무 가산율 적용 급여 산정 (Integration)

- Given: 근로자가 2026-03에 22:00~06:00 야간 근무 기록 보유, OVERTIME_WEEKDAY 정책(배율 1.5) 유효, 시급 10,000원
- When: 해당 근로자의 2026-03 급여 산정 요청
- Then: 야간 근무 시간에 대해 가산율 1.5가 적용되어 초과근무수당이 산정됨

### TC-PAY-004-03: 주말 근무 가산율 적용 (Integration)

- Given: 근로자가 토요일/일요일 출퇴근 기록 보유, OVERTIME_WEEKEND 정책(배율 2.0) 유효
- When: 급여 산정 요청
- Then: 주말 근무에 대해 가산율 2.0이 적용됨

### TC-PAY-004-04: 공휴일(1월 1일, 12월 25일) 근무 가산율 적용 (Integration)

- Given: 근로자가 1월 1일 출퇴근 기록 보유, OVERTIME_HOLIDAY 정책(배율 2.5) 유효
- When: 급여 산정 요청
- Then: 공휴일 근무에 대해 가산율 2.5가 적용됨 (공휴일 > 주말 > 야간 > 평일 우선순위)

### TC-PAY-004-05: 승인된 휴가 날짜 제외 계산 (Integration)

- Given: 근로자가 2026-03에 출퇴근 기록 20건 보유, 그 중 3일이 승인된(APPROVED) 휴가에 해당
- When: 급여 산정 요청
- Then: 휴가 날짜의 출퇴근 기록 3건이 제외되고 17건만으로 급여가 산정됨

### TC-PAY-004-06: 유효한 정책이 없을 때 기본 가산율 1.0 적용 (Integration)

- Given: 근로자가 주말 출퇴근 기록 보유, 해당 날짜에 유효한 OVERTIME_WEEKEND 정책이 없음
- When: 급여 산정 요청
- Then: 기본 가산율 1.0이 적용되어 계산됨

### TC-PAY-004-07: 동일 기간 급여 중복 계산 방지 (Integration)

- Given: 근로자의 2026-03 급여가 이미 계산된 상태
- When: 동일 근로자의 2026-03 급여 산정 재요청
- Then: PayrollAlreadyCalculatedException (PAYROLL002) 발생 - "해당 기간의 급여가 이미 계산되었습니다."

### TC-PAY-004-08: 출퇴근 기록이 없는 경우 (Integration)

- Given: 근로자가 2026-03에 출퇴근 기록이 없음
- When: 급여 산정 요청
- Then: NoAttendanceRecordsFoundException (PAYROLL003) 발생 - "출퇴근 기록이 없습니다."

### TC-PAY-004-09: 근로자를 찾을 수 없는 경우 (Integration)

- Given: 존재하지 않는 근로자 ID
- When: 급여 산정 요청
- Then: EmployeeNotFoundException 발생

### TC-PAY-004-10: 소수점 둘째 자리 반올림 검증 (Unit)

- Given: 근무시간 7.5시간, 시급 9,860원, 가산율 1.5
- When: PayrollDetail 금액 계산
- Then: 금액 = 7.5 x 9,860 x 1.5 = 110,925.00 (setScale(2, HALF_UP) 적용)

### TC-PAY-004-11: 시급 0 이하 검증 실패 (Unit)

- Given: PayrollDetail 생성 시
- When: 시급 0으로 생성 시도
- Then: 검증 오류 발생 - "시급은 0보다 커야 합니다. 입력값: 0"

### TC-PAY-004-12: 퇴근 미완료 기록 제외 검증 (Unit)

- Given: 출퇴근 기록 중 퇴근 처리가 안 된(isCompleted = false) 기록 포함
- When: PayrollCalculationEngine으로 급여 계산
- Then: 퇴근 미완료 기록은 계산에서 제외됨

### TC-PAY-004-13: EMPLOYEE 권한 사용자의 급여 산정 거부 (E2E)

- Given: EMPLOYEE 권한 사용자가 로그인한 상태
- When: 급여 산정 API 호출
- Then: 403 Forbidden 응답 반환
