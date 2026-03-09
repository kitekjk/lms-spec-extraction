# LMS-PAY-001 급여정책등록

## 기본 정보
- type: use_case
- id: LMS-PAY-001
- domain: payroll
- last-updated: 2026-03-09

## 관련 정책
- POLICY-PAYROLL-001: 급여 정책 관리 (§7), 정책 유형 (§4), 가산율 정책 (§3)
- POLICY-NFR-001: API 하위호환성, 변경 이력 추적

## 관련 Spec
- LMS-PAY-007-급여정책조회 (등록 후 조회)
- LMS-API-PAY-001-급여API (POST /api/payroll-policies)

## 관련 모델
- **주 모델**: `PayrollPolicy` (Aggregate Root)
- 참조 모델: `PolicyType` (Enum), `PolicyMultiplier` (Value Object), `PolicyEffectivePeriod` (Value Object)

## 개요
SUPER_ADMIN이 새로운 급여 정책(가산율)을 등록한다. 정책 유형(PolicyType), 배율(multiplier), 시행일(effectiveFrom), 종료일(effectiveTo, 선택), 설명(description, 선택)을 입력하여 PayrollPolicy를 생성한다.

## 기본 흐름
1. SUPER_ADMIN이 정책 유형(PolicyType), 배율(BigDecimal), 시행일(LocalDate), 종료일(LocalDate, 선택), 설명(String, 선택)을 입력한다.
2. 시스템이 배율이 0.0 이상 10.0 이하인지 검증한다. 범위 초과 시 HTTP 400을 반환한다.
3. 시스템이 시행일이 유효한지 검증한다. 종료일이 존재하고 시행일 이전이면 에러코드 PAYROLL_POLICY003을 반환한다 (HTTP 409).
4. 시스템이 동일 유형의 기존 정책과 유효 기간이 겹치는지 검증한다. 겹치면 에러코드 PAYROLL_POLICY002를 반환한다 (HTTP 409).
5. 시스템이 PayrollPolicy를 생성하고 저장한다.
6. 시스템이 생성된 PayrollPolicy 정보를 반환한다 (HTTP 201).

## 대안 흐름
- **AF-1**: 종료일(effectiveTo)이 NULL인 경우 → 무기한 유효한 정책으로 생성한다.
- **AF-2**: MANAGER 또는 EMPLOYEE가 정책 등록을 시도하는 경우 → HTTP 403을 반환한다.
- **AF-3**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.

## 검증 조건
- multiplier는 0.0 이상 10.0 이하여야 한다 (0.0 <= multiplier <= 10.0). 위반 시 HTTP 400
- effectiveTo가 존재하는 경우 effectiveFrom <= effectiveTo여야 한다. 위반 시 PAYROLL_POLICY003 / HTTP 409
- 동일 PolicyType의 기존 정책과 유효 기간이 겹치지 않아야 한다. 위반 시 PAYROLL_POLICY002 / HTTP 409
- policyType은 PolicyType ENUM 값(OVERTIME_WEEKDAY, NIGHT_SHIFT, HOLIDAY_WORK, OVERTIME_WEEKEND) 중 하나여야 한다. 위반 시 HTTP 400
- policyType, multiplier, effectiveFrom은 NOT NULL이어야 한다. 위반 시 HTTP 400
- 등록 요청자의 역할은 SUPER_ADMIN이어야 한다. 위반 시 HTTP 403

## 비기능 요구사항
- **POLICY-NFR-001 §1**: API 요청/응답 구조의 하위호환을 유지한다.
- **POLICY-NFR-001 §2.2**: 배율은 BigDecimal을 사용한다.
- **POLICY-NFR-001 §3**: 정책 등록 시 AuditLog에 기록한다 (EntityType: PAYROLL_POLICY, ActionType: CREATE).
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-PAY-001-01: SUPER_ADMIN의 급여 정책 등록 성공
- **레벨**: Integration
- **Given**: SUPER_ADMIN이 인증되어 있고, NIGHT_SHIFT 유형의 기존 정책이 없다.
- **When**: SUPER_ADMIN이 policyType=NIGHT_SHIFT, multiplier=1.5, effectiveFrom=2026-04-01, effectiveTo=null, description="야간 근무 1.5배"로 정책을 등록한다.
- **Then**: PayrollPolicy가 생성되고 HTTP 201이 반환된다. 반환된 응답에 id, policyType=NIGHT_SHIFT, multiplier=1.5, isCurrentlyEffective가 포함된다.

### TC-PAY-001-02: 유효 기간 중복 시 등록 실패
- **레벨**: Unit
- **Given**: OVERTIME_WEEKDAY 유형의 정책이 2026-01-01 ~ 무기한으로 존재한다.
- **When**: SUPER_ADMIN이 policyType=OVERTIME_WEEKDAY, multiplier=2.0, effectiveFrom=2026-06-01로 정책을 등록한다.
- **Then**: 에러코드 PAYROLL_POLICY002가 반환되고 HTTP 409가 반환된다.

### TC-PAY-001-03: MANAGER의 정책 등록 시도 시 권한 오류
- **레벨**: Unit
- **Given**: MANAGER가 인증되어 있다.
- **When**: MANAGER가 급여 정책 등록을 시도한다.
- **Then**: HTTP 403이 반환된다.

### TC-PAY-001-04: 배율 범위 초과 시 등록 실패
- **레벨**: Unit
- **Given**: SUPER_ADMIN이 인증되어 있다.
- **When**: SUPER_ADMIN이 multiplier=15.0으로 정책을 등록한다.
- **Then**: HTTP 400이 반환된다.
