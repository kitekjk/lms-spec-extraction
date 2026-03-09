# LMS-PAY-006 급여조회

## 기본 정보
- type: use_case
- id: LMS-PAY-006
- domain: payroll
- last-updated: 2026-03-09

## 관련 정책
- POLICY-PAYROLL-001: 급여 조회 권한 (§8), 급여 산정 구성 요소 (§9), 급여 상세 (§10)
- POLICY-NFR-001: 멀티 매장 지원 (§4), 성능 요구사항 (§5)

## 관련 Spec
- LMS-PAY-004-급여산정 (선행)
- LMS-API-PAY-001-급여API (GET /api/payroll, GET /api/payroll/my-payroll, GET /api/payroll/{payrollId})

## 관련 모델
- **주 모델**: `Payroll` (Aggregate Root)
- 참조 모델: `PayrollDetail` (Entity), `PayrollAmount` (Value Object), `PayrollPeriod` (Value Object), `WorkType` (Enum)

## 개요
사용자가 역할에 따라 급여 내역을 조회한다. EMPLOYEE는 본인의 급여 내역만, MANAGER는 소속 매장 근로자의 급여 내역을, SUPER_ADMIN은 전체 매장의 급여 내역을 조회할 수 있다. 개별 급여 상세 조회 시 일별 근무 유형/시간/가산율이 포함된 PayrollDetail을 함께 반환한다.

## 기본 흐름

### 흐름 A: 본인 급여 조회 (GET /api/payroll/my-payroll)
1. 인증된 사용자가 본인의 급여 내역 조회를 요청한다.
2. 시스템이 JWT에서 사용자 ID를 추출한다.
3. 시스템이 해당 사용자의 employeeId로 Payroll 목록을 조회한다.
4. 시스템이 급여 목록을 반환한다 (HTTP 200).

### 흐름 B: 기간별 급여 조회 (GET /api/payroll?period={YYYY-MM})
1. MANAGER 또는 SUPER_ADMIN이 급여 기간(period, YearMonth)을 지정하여 조회를 요청한다.
2. 시스템이 해당 기간의 Payroll 목록을 조회한다.
3. 시스템이 급여 목록을 반환한다 (HTTP 200).

### 흐름 C: 급여 상세 조회 (GET /api/payroll/{payrollId})
1. 인증된 사용자가 특정 급여 ID(payrollId)를 지정하여 상세 조회를 요청한다.
2. 시스템이 해당 Payroll을 조회한다. 존재하지 않으면 에러코드 PAYROLL001을 반환한다 (HTTP 404).
3. 시스템이 해당 Payroll에 연결된 PayrollDetail 목록을 조회한다.
4. 시스템이 급여 정보와 상세 내역을 함께 반환한다 (HTTP 200).

## 대안 흐름
- **AF-1**: 조회 결과가 0건인 경우 → 빈 배열([])을 반환한다. HTTP 200이 반환된다.
- **AF-2**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.
- **AF-3**: EMPLOYEE가 기간별 조회(흐름 B)를 시도하는 경우 → HTTP 403을 반환한다.

## 검증 조건
- EMPLOYEE는 본인(employeeId 일치)의 급여 내역만 조회할 수 있다. 타인 조회 시 HTTP 403
- MANAGER는 본인 소속 매장 근로자의 급여 내역만 조회할 수 있다. 타 매장 조회 시 HTTP 403
- 기간별 조회(GET /api/payroll) 시 period 쿼리 파라미터가 존재해야 한다. 위반 시 HTTP 400
- 기간별 조회는 MANAGER 또는 SUPER_ADMIN만 가능하다. 위반 시 HTTP 403
- 상세 조회 시 payrollId에 해당하는 Payroll이 DB에 존재해야 한다. 위반 시 PAYROLL001 / HTTP 404

## 비기능 요구사항
- **POLICY-NFR-001 §4**: MANAGER는 소속 매장 데이터만 접근 가능하다.
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-PAY-006-01: EMPLOYEE 본인 급여 조회 성공
- **레벨**: Integration
- **Given**: 근로자 A에게 2026-01, 2026-02, 2026-03 기간의 Payroll이 각 1건씩 존재한다.
- **When**: 근로자 A가 본인 급여를 조회한다 (GET /api/payroll/my-payroll).
- **Then**: 3건의 Payroll이 반환된다. 각 항목에 id, employeeId, period, baseAmount, overtimeAmount, totalAmount, isPaid, calculatedAt이 포함된다. HTTP 200이 반환된다.

### TC-PAY-006-02: 급여 상세 조회 성공 (PayrollDetail 포함)
- **레벨**: Integration
- **Given**: 근로자 A의 2026-03 Payroll이 존재하고, 5건의 PayrollDetail(WEEKDAY 3건, WEEKEND 1건, NIGHT 1건)이 연결되어 있다.
- **When**: 인증된 사용자가 해당 payrollId로 상세 조회한다 (GET /api/payroll/{payrollId}).
- **Then**: Payroll 정보와 5건의 PayrollDetail이 반환된다. 각 PayrollDetail에 workDate, workType, hours, hourlyRate, multiplier, amount가 포함된다. HTTP 200이 반환된다.

### TC-PAY-006-03: 존재하지 않는 급여 상세 조회 시 실패
- **레벨**: Unit
- **Given**: 존재하지 않는 payrollId.
- **When**: 인증된 사용자가 해당 payrollId로 상세 조회한다.
- **Then**: 에러코드 PAYROLL001이 반환되고 HTTP 404가 반환된다.

### TC-PAY-006-04: MANAGER 기간별 급여 조회 성공
- **레벨**: Integration
- **Given**: 2026-03 기간에 4건의 Payroll이 존재한다.
- **When**: MANAGER가 period=2026-03으로 조회한다 (GET /api/payroll?period=2026-03).
- **Then**: 4건의 Payroll이 반환된다. HTTP 200이 반환된다.
