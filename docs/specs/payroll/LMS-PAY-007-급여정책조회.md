# LMS-PAY-007 급여정책조회

## 기본 정보
- type: use_case
- id: LMS-PAY-007
- domain: payroll
- last-updated: 2026-03-09

## 관련 정책
- POLICY-PAYROLL-001: 급여 정책 유형 (§4), 가산율 정책 (§3)
- POLICY-NFR-001: 성능 요구사항 (§5)

## 관련 Spec
- LMS-PAY-001-급여정책등록 (선행)
- LMS-API-PAY-001-급여API (GET /api/payroll-policies, GET /api/payroll-policies/active)

## 관련 모델
- **주 모델**: `PayrollPolicy` (Aggregate Root)
- 참조 모델: `PolicyType` (Enum), `PolicyMultiplier` (Value Object), `PolicyEffectivePeriod` (Value Object)

## 개요
인증된 사용자가 급여 정책 목록을 조회한다. 현재 유효한 정책만 조회하거나, 정책 유형(PolicyType)별로 필터링하여 조회할 수 있다.

## 기본 흐름

### 흐름 A: 현재 유효 정책 조회 (GET /api/payroll-policies/active)
1. 인증된 사용자(EMPLOYEE, MANAGER, SUPER_ADMIN)가 현재 유효한 정책 조회를 요청한다.
2. 시스템이 isCurrentlyEffective == true인 PayrollPolicy 목록을 조회한다.
3. 시스템이 정책 목록과 총 건수(totalCount)를 반환한다 (HTTP 200).

### 흐름 B: 정책 유형별 조회 (GET /api/payroll-policies?policyType={type})
1. MANAGER 또는 SUPER_ADMIN이 정책 유형(policyType, 선택)을 지정하여 조회를 요청한다.
2. policyType이 지정된 경우 해당 유형의 PayrollPolicy 목록을, 미지정인 경우 현재 유효한 전체 정책 목록을 조회한다.
3. 시스템이 정책 목록과 총 건수(totalCount)를 반환한다 (HTTP 200).

## 대안 흐름
- **AF-1**: 조회 결과가 0건인 경우 → 빈 배열([])과 totalCount: 0을 반환한다. HTTP 200이 반환된다.
- **AF-2**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.
- **AF-3**: EMPLOYEE가 정책 유형별 조회(흐름 B)를 시도하는 경우 → HTTP 403을 반환한다.

## 검증 조건
- 정책 유형별 조회(GET /api/payroll-policies?policyType={type})는 MANAGER 또는 SUPER_ADMIN만 가능하다. 위반 시 HTTP 403
- policyType 필터가 지정된 경우 PolicyType ENUM 값(OVERTIME_WEEKDAY, NIGHT_SHIFT, HOLIDAY_WORK, OVERTIME_WEEKEND) 중 하나여야 한다. 위반 시 HTTP 400

## 비기능 요구사항
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-PAY-007-01: 현재 유효 정책 조회 성공
- **레벨**: Integration
- **Given**: 현재 유효한 정책이 4건(OVERTIME_WEEKDAY, NIGHT_SHIFT, HOLIDAY_WORK, OVERTIME_WEEKEND) 존재하고, 종료된 정책이 1건 존재한다.
- **When**: EMPLOYEE가 현재 유효 정책을 조회한다 (GET /api/payroll-policies/active).
- **Then**: 4건의 정책이 반환되고, totalCount는 4이다. 각 항목에 id, policyType, policyTypeDescription, multiplier, effectiveFrom, effectiveTo, isCurrentlyEffective=true가 포함된다. HTTP 200이 반환된다.

### TC-PAY-007-02: 정책 유형별 필터링 조회 성공
- **레벨**: Integration
- **Given**: NIGHT_SHIFT 유형의 정책이 2건 존재한다.
- **When**: SUPER_ADMIN이 policyType=NIGHT_SHIFT로 조회한다 (GET /api/payroll-policies?policyType=NIGHT_SHIFT).
- **Then**: 2건의 NIGHT_SHIFT 정책이 반환된다. HTTP 200이 반환된다.

### TC-PAY-007-03: EMPLOYEE의 유형별 조회 시도 시 권한 오류
- **레벨**: Unit
- **Given**: EMPLOYEE가 인증되어 있다.
- **When**: EMPLOYEE가 유형별 정책 조회를 시도한다 (GET /api/payroll-policies?policyType=NIGHT_SHIFT).
- **Then**: HTTP 403이 반환된다.
