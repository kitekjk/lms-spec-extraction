# LMS-PAY-004 급여산정

## 기본 정보
- type: use_case
- id: LMS-PAY-004
- domain: payroll
- last-updated: 2026-03-09

## 관련 정책
- POLICY-PAYROLL-001: 급여 산정 방식 (§1), 근무 유형별 가산율 (§2), 가산율 정책 (§3), 근무 유형 판정 우선순위 (§5), 급여 계산 시 제외 조건 (§6)
- POLICY-NFR-001: 데이터 무결성 (§2), BigDecimal 정밀도 (§2.2)

## 관련 Spec
- LMS-PAY-006-급여조회 (산정 후 조회)
- LMS-API-PAY-001-급여API (POST /api/payroll/calculate)

## 관련 모델
- **주 모델**: `Payroll` (Aggregate Root), `PayrollDetail` (Entity)
- 참조 모델: `Employee` (근로자 정보), `AttendanceRecord` (출퇴근 기록), `PayrollPolicy` (가산율), `WorkType` (Enum), `PayrollAmount` (Value Object), `PayrollPeriod` (Value Object)

## 개요
SUPER_ADMIN 또는 MANAGER가 특정 근로자의 특정 기간(YYYY-MM) 급여를 산정한다. 시스템은 해당 기간의 출퇴근 기록을 기반으로, 일별 근무 유형을 판정하고, 유효한 가산율 정책을 적용하여 기본급(baseAmount)과 가산금액(overtimeAmount)을 계산한다. 모든 금액 계산은 BigDecimal을 사용하며, 소수점 2자리 HALF_UP 반올림을 적용한다.

## 기본 흐름
1. SUPER_ADMIN 또는 MANAGER가 근로자 ID(employeeId), 급여 기간(period, YearMonth), 시급(hourlyRate, BigDecimal)을 입력한다.
2. 시스템이 해당 근로자의 존재 여부를 확인한다. 존재하지 않으면 HTTP 404를 반환한다.
3. 시스템이 해당 근로자의 해당 기간에 이미 산정된 급여가 있는지 확인한다. 존재하면 에러코드 PAYROLL002를 반환한다 (HTTP 409).
4. 시스템이 해당 기간의 출퇴근 기록(AttendanceRecord)을 조회한다. 기록이 없으면 에러코드 PAYROLL003을 반환한다 (HTTP 409).
5. 시스템이 출퇴근 기록에서 다음 조건에 해당하는 기록을 제외한다:
   - 퇴근 기록이 없는(PENDING 상태) 기록
   - 해당 근로자의 승인된(APPROVED) 휴가 기간에 속하는 기록
6. 시스템이 각 출퇴근 기록에 대해 일별 급여를 계산한다:
   - 근무 시간 = (퇴근 시각 - 출근 시각)을 시간 단위로 환산 (소수점 2자리, HALF_UP)
   - 근무 유형(WorkType) 판정: 공휴일(1월 1일, 12월 25일) > 주말(토, 일) > 야간(출근 또는 퇴근 시각이 22:00~06:00) > 평일(WEEKDAY) 순으로 판정
   - 해당 근무 날짜에 유효한 PayrollPolicy를 조회하여 가산율(multiplier)을 결정한다. 유효 정책이 없으면 가산율 1.0을 적용한다
   - 일별 급여 = 근무 시간 x 시급 x 가산율 (소수점 2자리, HALF_UP)
7. 시스템이 WEEKDAY 근무의 합계를 기본급(baseAmount), 그 외(NIGHT, WEEKEND, HOLIDAY) 근무의 합계를 가산금액(overtimeAmount)으로 분류한다.
8. 시스템이 Payroll과 PayrollDetail 레코드를 생성하고 저장한다.
9. 시스템이 산정된 급여 정보를 반환한다 (HTTP 200).

## 대안 흐름
- **AF-1**: 모든 출퇴근 기록이 제외 조건에 해당하는 경우 → 에러코드 PAYROLL003을 반환한다 (유효한 기록 없음).
- **AF-2**: EMPLOYEE가 급여 산정을 시도하는 경우 → HTTP 403을 반환한다.
- **AF-3**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.

## 검증 조건
- employeeId에 해당하는 Employee가 DB에 존재해야 한다. 위반 시 HTTP 404
- 동일 employeeId + period 조합의 Payroll이 존재하지 않아야 한다 (미산정 기간만 산정 가능). 위반 시 PAYROLL002 / HTTP 409
- 해당 기간에 유효한 출퇴근 기록(AttendanceRecord)이 1건 이상 존재해야 한다. 위반 시 PAYROLL003 / HTTP 409
- 모든 금액 계산은 BigDecimal을 사용하며, 소수점 2자리 RoundingMode.HALF_UP 반올림을 적용한다
- 근무 유형 판정 우선순위: 공휴일(HOLIDAY) > 주말(WEEKEND) > 야간(NIGHT) > 평일(WEEKDAY) 순서로 판정한다
- hourlyRate는 0보다 커야 한다 (hourlyRate > 0). 위반 시 HTTP 400
- employeeId, period, hourlyRate는 NOT NULL이어야 한다. 위반 시 HTTP 400
- 산정 요청자의 역할은 SUPER_ADMIN 또는 MANAGER이어야 한다. 위반 시 HTTP 403

## 비기능 요구사항
- **POLICY-NFR-001 §2.1**: Payroll과 PayrollDetail 저장은 하나의 트랜잭션 내에서 원자적으로 처리한다.
- **POLICY-NFR-001 §2.2**: 모든 금액 계산은 BigDecimal을 사용하며, 소수점 2자리 HALF_UP 반올림을 적용한다.
- **POLICY-NFR-001 §3**: 급여 산정 시 AuditLog에 기록한다 (EntityType: PAYROLL, ActionType: CREATE).
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-PAY-004-01: 평일 근무 급여 산정 성공
- **레벨**: Integration
- **Given**: 근로자 A의 2026-03 기간에 평일 출퇴근 기록이 3건 존재한다 (09:00~18:00, 각 9시간). 시급은 10000원이다. WEEKDAY 가산율 1.0 정책이 유효하다.
- **When**: SUPER_ADMIN이 근로자 A의 2026-03 급여를 산정한다.
- **Then**: baseAmount = 270000.00 (9시간 x 10000원 x 1.0 x 3일), overtimeAmount = 0.00, totalAmount = 270000.00인 Payroll이 생성된다. HTTP 200이 반환된다.

### TC-PAY-004-02: 주말 및 야간 근무 가산율 적용
- **레벨**: Integration
- **Given**: 근로자 A의 2026-03 기간에 평일 근무 1건(09:00~18:00, 9시간)과 주말 근무 1건(토요일 10:00~18:00, 8시간)이 존재한다. 시급은 10000원이다. WEEKEND 가산율 1.5 정책이 유효하다.
- **When**: SUPER_ADMIN이 근로자 A의 2026-03 급여를 산정한다.
- **Then**: baseAmount = 90000.00, overtimeAmount = 120000.00 (8시간 x 10000원 x 1.5), totalAmount = 210000.00인 Payroll이 생성된다. PayrollDetail에 workType=WEEKDAY 1건, workType=WEEKEND 1건이 포함된다.

### TC-PAY-004-03: 이미 산정된 급여 기간 재산정 시도 실패
- **레벨**: Unit
- **Given**: 근로자 A의 2026-03 기간에 이미 Payroll이 존재한다.
- **When**: SUPER_ADMIN이 근로자 A의 2026-03 급여를 다시 산정한다.
- **Then**: 에러코드 PAYROLL002가 반환되고 HTTP 409가 반환된다.

### TC-PAY-004-04: 출퇴근 기록 없는 기간 산정 시도 실패
- **레벨**: Unit
- **Given**: 근로자 A의 2026-05 기간에 출퇴근 기록이 없다.
- **When**: SUPER_ADMIN이 근로자 A의 2026-05 급여를 산정한다.
- **Then**: 에러코드 PAYROLL003이 반환되고 HTTP 409가 반환된다.

### TC-PAY-004-05: 공휴일 근무 가산율 2.0 적용
- **레벨**: Integration
- **Given**: 근로자 A의 2026-01 기간에 1월 1일(신정) 근무 기록(09:00~18:00, 9시간)이 존재한다. 시급은 10000원이다. HOLIDAY_WORK 가산율 2.0 정책이 유효하다.
- **When**: SUPER_ADMIN이 근로자 A의 2026-01 급여를 산정한다.
- **Then**: overtimeAmount에 180000.00 (9시간 x 10000원 x 2.0)이 포함된다. PayrollDetail에 workType=HOLIDAY 1건이 포함된다.

### TC-PAY-004-06: BigDecimal 소수점 HALF_UP 반올림 검증
- **레벨**: Unit
- **Given**: 근무 시간 7.33시간, 시급 9500원, 가산율 1.5.
- **When**: 일별 급여를 계산한다.
- **Then**: 일별 급여 = 7.33 x 9500 x 1.5 = 104452.50 (소수점 2자리 HALF_UP).
