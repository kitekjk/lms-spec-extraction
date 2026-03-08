# LMS-PAY-002: 급여정책수정

## 기본 정보
- type: use_case
- domain: payroll

## 관련 Spec
- LMS-API-PAY-001 (급여API)
- LMS-PAY-001 (급여정책등록)
- LMS-PAY-007 (급여정책조회)

## 개요
SUPER_ADMIN이 현재 유효한 급여 정책의 배율, 종료일, 설명을 수정한다.

## 관련 모델
- 주 모델: PayrollPolicy (Aggregate Root)
- 참조 모델: PolicyMultiplier, PolicyEffectivePeriod, PayrollPolicyId

## 선행 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 인증된 사용자여야 한다
- 수정 대상 정책이 존재해야 한다
- 수정 대상 정책이 현재 유효한 상태여야 한다

## 기본 흐름
1. 관리자가 정책 ID와 수정 내용을 지정하여 정책 수정을 요청한다 (배율(선택), 종료일(선택), 설명(선택))
2. 시스템은 해당 ID의 정책이 존재하는지 확인한다
3. 시스템은 해당 정책이 현재 유효한 상태인지 확인한다
4. 시스템은 요청된 항목에 대해 수정을 수행한다
   - 배율(multiplier)이 제공된 경우: 배율을 변경한다
   - 종료일(effectiveTo)이 제공된 경우: 정책을 종료 처리한다 (종료일은 시작일 이후여야 한다)
   - 설명(description)이 제공된 경우: 설명을 변경한다
5. 시스템은 수정된 정책을 저장하고 결과를 반환한다

## 대안 흐름
- 배율만 변경 요청한 경우: 배율만 수정하고 나머지는 유지한다
- 종료일만 설정 요청한 경우: 종료일만 설정하고 나머지는 유지한다
- 설명만 변경 요청한 경우: 설명만 수정하고 나머지는 유지한다

## 예외 흐름
- 정책을 찾을 수 없는 경우: PayrollPolicyNotFoundException (PAYROLL_POLICY001) 발생
- 정책이 현재 유효하지 않은 경우: InactivePolicyCannotBeModifiedException (PAYROLL_POLICY004) 발생
- 종료일이 시작일보다 이전인 경우: 유효성 검증 실패

## 검증 조건
- 정책 ID는 유효한 UUID 문자열이어야 한다
- 배율이 제공된 경우 0 이상 10.0 이하의 BigDecimal 값이어야 한다
- 종료일이 제공된 경우 정책의 시작일 이후여야 한다
- 정책이 현재 유효한 상태여야 수정 가능하다

## 관련 정책
- POLICY-PAYROLL-001 참조 (배율 범위, 유효 기간 규칙)
- POLICY-NFR-001 참조

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-PAY-002-01: 정상 배율 수정 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인하고, 현재 유효한 OVERTIME_WEEKDAY 정책(배율 1.5)이 존재
- When: 해당 정책의 배율을 2.0으로 수정 요청
- Then: 배율이 2.0으로 변경되고 수정된 정책 정보가 반환됨

### TC-PAY-002-02: 종료일 설정으로 정책 종료 처리 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인하고, 시작일 2026-01-01인 무기한 정책이 존재
- When: 종료일을 2026-06-30으로 설정하여 수정 요청
- Then: 정책의 종료일이 2026-06-30으로 설정됨

### TC-PAY-002-03: 설명만 변경 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인하고, 현재 유효한 정책이 존재
- When: 설명만 "수정된 설명"으로 변경 요청
- Then: 설명이 변경되고 배율과 종료일은 기존 값 유지

### TC-PAY-002-04: 존재하지 않는 정책 수정 시도 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인한 상태
- When: 존재하지 않는 정책 ID로 수정 요청
- Then: PayrollPolicyNotFoundException (PAYROLL_POLICY001) 발생 - "급여 정책을 찾을 수 없습니다: {policyId}"

### TC-PAY-002-05: 유효하지 않은 정책 수정 시도 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인하고, 이미 종료된(유효 기간 만료) 정책이 존재
- When: 해당 정책의 배율 수정 요청
- Then: InactivePolicyCannotBeModifiedException (PAYROLL_POLICY004) 발생 - "유효하지 않은 정책은 수정할 수 없습니다."

### TC-PAY-002-06: 배율 경계값 상한 초과 수정 시도 (Unit)

- Given: 유효한 정책이 존재
- When: 배율을 10.1로 수정 시도
- Then: 검증 오류 발생 - "정책 배율은 10.0 이하여야 합니다. 입력값: 10.1"

### TC-PAY-002-07: 종료일이 시작일보다 이전인 경우 (Integration)

- Given: 시작일이 2026-04-01인 유효한 정책이 존재
- When: 종료일을 2026-03-01로 설정하여 수정 요청
- Then: 유효성 검증 실패

### TC-PAY-002-08: 권한 없는 사용자의 정책 수정 거부 (E2E)

- Given: EMPLOYEE 권한 사용자가 로그인한 상태
- When: 급여 정책 수정 API 호출
- Then: 403 Forbidden 응답 반환
