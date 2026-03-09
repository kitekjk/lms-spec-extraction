# LMS-PAY-002 급여정책수정

## 기본 정보
- type: use_case
- id: LMS-PAY-002
- domain: payroll
- last-updated: 2026-03-09

## 관련 정책
- POLICY-PAYROLL-001: 급여 정책 관리 (§7)
- POLICY-NFR-001: 변경 이력 추적, API 하위호환성

## 관련 Spec
- LMS-PAY-001-급여정책등록 (선행)
- LMS-API-PAY-001-급여API (PUT /api/payroll-policies/{policyId})

## 관련 모델
- **주 모델**: `PayrollPolicy` (Aggregate Root)
- 참조 모델: `PolicyMultiplier` (Value Object), `PolicyEffectivePeriod` (Value Object)

## 개요
SUPER_ADMIN이 기존 급여 정책의 배율(multiplier), 종료일(effectiveTo), 설명(description)을 수정한다. 유효하지 않은(종료된) 정책은 수정할 수 없다.

## 기본 흐름
1. SUPER_ADMIN이 대상 정책 ID(policyId)와 수정할 필드(multiplier, effectiveTo, description 중 하나 이상)를 입력한다.
2. 시스템이 해당 PayrollPolicy를 조회한다. 존재하지 않으면 에러코드 PAYROLL_POLICY001을 반환한다 (HTTP 404).
3. 시스템이 해당 정책이 현재 유효한지 검증한다. 종료되었거나 유효하지 않으면 에러코드 PAYROLL_POLICY004를 반환한다 (HTTP 409).
4. multiplier가 입력된 경우, 시스템이 0.0 이상 10.0 이하인지 검증한다. 범위 초과 시 HTTP 400을 반환한다.
5. 시스템이 PayrollPolicy를 수정하고 저장한다.
6. 시스템이 수정된 PayrollPolicy 정보를 반환한다 (HTTP 200).

## 대안 흐름
- **AF-1**: 모든 수정 필드(multiplier, effectiveTo, description)가 null인 경우 → 기존 정책을 그대로 반환한다 (HTTP 200).
- **AF-2**: MANAGER 또는 EMPLOYEE가 정책 수정을 시도하는 경우 → HTTP 403을 반환한다.
- **AF-3**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.

## 검증 조건
- policyId에 해당하는 PayrollPolicy가 DB에 존재해야 한다. 위반 시 PAYROLL_POLICY001 / HTTP 404
- 대상 정책이 현재 유효해야 한다 (isCurrentlyEffective == true). 종료된 정책은 수정 불가. 위반 시 PAYROLL_POLICY004 / HTTP 409
- multiplier가 입력된 경우 0.0 이상 10.0 이하여야 한다 (0.0 <= multiplier <= 10.0). 위반 시 HTTP 400
- 수정 요청자의 역할은 SUPER_ADMIN이어야 한다. 위반 시 HTTP 403

## 비기능 요구사항
- **POLICY-NFR-001 §2.2**: 배율은 BigDecimal을 사용한다.
- **POLICY-NFR-001 §3**: 정책 수정 시 AuditLog에 기록한다 (EntityType: PAYROLL_POLICY, ActionType: UPDATE, oldValue/newValue 포함).
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-PAY-002-01: SUPER_ADMIN의 유효 정책 배율 수정 성공
- **레벨**: Integration
- **Given**: 현재 유효한 NIGHT_SHIFT 정책(multiplier=1.5)이 존재한다.
- **When**: SUPER_ADMIN이 multiplier=2.0으로 수정한다.
- **Then**: 정책의 multiplier가 2.0으로 변경되고 HTTP 200이 반환된다.

### TC-PAY-002-02: 종료된 정책 수정 시도 실패
- **레벨**: Unit
- **Given**: effectiveTo=2025-12-31인 종료된 정책이 존재한다.
- **When**: SUPER_ADMIN이 해당 정책의 multiplier를 수정한다.
- **Then**: 에러코드 PAYROLL_POLICY004가 반환되고 HTTP 409가 반환된다.

### TC-PAY-002-03: 존재하지 않는 정책 수정 시도
- **레벨**: Unit
- **Given**: 존재하지 않는 policyId.
- **When**: SUPER_ADMIN이 해당 policyId로 수정을 요청한다.
- **Then**: 에러코드 PAYROLL_POLICY001이 반환되고 HTTP 404가 반환된다.
