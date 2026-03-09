# LMS-PAY-003 급여정책삭제

## 기본 정보
- type: use_case
- id: LMS-PAY-003
- domain: payroll
- last-updated: 2026-03-09

## 관련 정책
- POLICY-PAYROLL-001: 급여 정책 관리 (§7)
- POLICY-NFR-001: 변경 이력 추적

## 관련 Spec
- LMS-PAY-001-급여정책등록 (선행)
- LMS-API-PAY-001-급여API (DELETE /api/payroll-policies/{policyId})

## 관련 모델
- **주 모델**: `PayrollPolicy` (Aggregate Root)

## 개요
SUPER_ADMIN이 기존 급여 정책을 삭제한다. 삭제 대상 정책이 존재하지 않으면 HTTP 404를 반환한다.

## 기본 흐름
1. SUPER_ADMIN이 삭제할 정책 ID(policyId)를 지정하여 삭제 요청을 보낸다.
2. 시스템이 해당 PayrollPolicy를 조회한다. 존재하지 않으면 에러코드 PAYROLL_POLICY001을 반환한다 (HTTP 404).
3. 시스템이 PayrollPolicy를 삭제한다.
4. 시스템이 HTTP 204 (No Content)를 반환한다.

## 대안 흐름
- **AF-1**: MANAGER 또는 EMPLOYEE가 정책 삭제를 시도하는 경우 → HTTP 403을 반환한다.
- **AF-2**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.

## 검증 조건
- policyId에 해당하는 PayrollPolicy가 DB에 존재해야 한다. 위반 시 PAYROLL_POLICY001 / HTTP 404
- 삭제 요청자의 역할은 SUPER_ADMIN이어야 한다. 위반 시 HTTP 403
- 삭제된 정책은 이후 급여 산정(LMS-PAY-004) 시 가산율 조회 대상에서 제외된다

## 비기능 요구사항
- **POLICY-NFR-001 §3**: 정책 삭제 시 AuditLog에 기록한다 (EntityType: PAYROLL_POLICY, ActionType: DELETE, oldValue에 삭제 전 데이터 포함).
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-PAY-003-01: SUPER_ADMIN의 정책 삭제 성공
- **레벨**: Integration
- **Given**: 정책 ID "policy-001"에 해당하는 PayrollPolicy가 존재한다.
- **When**: SUPER_ADMIN이 해당 정책을 삭제한다.
- **Then**: PayrollPolicy가 DB에서 삭제되고 HTTP 204가 반환된다.

### TC-PAY-003-02: 존재하지 않는 정책 삭제 시도
- **레벨**: Unit
- **Given**: 존재하지 않는 policyId.
- **When**: SUPER_ADMIN이 해당 policyId로 삭제를 요청한다.
- **Then**: 에러코드 PAYROLL_POLICY001이 반환되고 HTTP 404가 반환된다.

### TC-PAY-003-03: MANAGER의 정책 삭제 시도 시 권한 오류
- **레벨**: Unit
- **Given**: MANAGER가 인증되어 있다.
- **When**: MANAGER가 급여 정책 삭제를 시도한다.
- **Then**: HTTP 403이 반환된다.
