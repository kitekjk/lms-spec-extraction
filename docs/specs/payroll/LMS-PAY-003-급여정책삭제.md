# LMS-PAY-003: 급여정책삭제

## 기본 정보
- type: use_case
- domain: payroll

## 관련 Spec
- LMS-API-PAY-001 (급여API)
- LMS-PAY-001 (급여정책등록)

## 개요
SUPER_ADMIN이 급여 정책을 삭제(soft delete)한다.

## 관련 모델
- 주 모델: PayrollPolicy (Aggregate Root)
- 참조 모델: PayrollPolicyId

## 선행 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 인증된 사용자여야 한다
- 삭제 대상 정책이 존재해야 한다

## 기본 흐름
1. 관리자가 정책 ID를 지정하여 급여 정책 삭제를 요청한다
2. 시스템은 해당 ID의 정책이 존재하는지 확인한다
3. 시스템은 정책을 삭제한다 (infrastructure 레이어에서 soft delete 처리)
4. 시스템은 204 No Content 응답을 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 정책을 찾을 수 없는 경우: PayrollPolicyNotFoundException (PAYROLL_POLICY001) 발생

## 검증 조건
- 정책 ID는 비어 있지 않은 유효한 문자열이어야 한다
- 해당 ID의 정책이 시스템에 존재해야 한다

## 관련 정책
- POLICY-NFR-001 참조

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-PAY-003-01: 정상 급여 정책 삭제 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인하고, 삭제 대상 정책이 존재
- When: 해당 정책 ID로 삭제 요청
- Then: 정책이 삭제(soft delete)되고 204 No Content 응답 반환

### TC-PAY-003-02: 존재하지 않는 정책 삭제 시도 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인한 상태
- When: 존재하지 않는 정책 ID로 삭제 요청
- Then: PayrollPolicyNotFoundException (PAYROLL_POLICY001) 발생 - "급여 정책을 찾을 수 없습니다: {policyId}"

### TC-PAY-003-03: 권한 없는 사용자의 정책 삭제 거부 (E2E)

- Given: EMPLOYEE 권한 사용자가 로그인한 상태
- When: 급여 정책 삭제 API 호출
- Then: 403 Forbidden 응답 반환

### TC-PAY-003-04: 삭제된 정책이 조회되지 않음 확인 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 정책을 삭제한 상태
- When: 삭제된 정책 ID로 조회 요청
- Then: 해당 정책이 조회 결과에 포함되지 않음

### TC-PAY-003-05: MANAGER 권한 사용자의 정책 삭제 거부 (E2E)

- Given: MANAGER 권한 사용자가 로그인한 상태
- When: 급여 정책 삭제 API 호출
- Then: 403 Forbidden 응답 반환
