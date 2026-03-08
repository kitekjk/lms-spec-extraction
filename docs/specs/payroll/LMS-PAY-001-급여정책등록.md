# LMS-PAY-001: 급여정책등록

## 기본 정보
- type: use_case
- domain: payroll

## 관련 Spec
- LMS-API-PAY-001 (급여API)
- LMS-PAY-002 (급여정책수정)
- LMS-PAY-007 (급여정책조회)

## 개요
SUPER_ADMIN이 급여 정책 유형, 배율, 유효 기간을 입력하여 새로운 급여 정책을 등록한다.

## 관련 모델
- 주 모델: PayrollPolicy (Aggregate Root)
- 참조 모델: PolicyType, PolicyMultiplier, PolicyEffectivePeriod, PayrollPolicyId

## 선행 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 인증된 사용자여야 한다

## 기본 흐름
1. 관리자가 급여 정책 생성을 요청한다 (정책 유형, 배율, 시작일, 종료일(선택), 설명(선택))
2. 시스템은 동일한 정책 유형에 대해 유효 기간이 겹치는 기존 정책이 있는지 확인한다
   - 종료일이 지정된 경우: 시작일 기준으로 유효한 동일 유형 정책을 조회하여 기간 중복을 검증한다
   - 종료일이 없는(무기한) 경우: 동일 유형의 현재 유효한 정책을 조회하여 기간 중복을 검증한다
3. 시스템은 새로운 PayrollPolicy를 생성한다
   - 고유 ID 자동 생성 (UUID)
   - 배율은 0 이상 10.0 이하여야 한다
   - 시작일이 종료일보다 늦을 수 없다
4. 시스템은 정책을 저장하고 결과를 반환한다

## 대안 흐름
- 종료일이 지정되지 않은 경우: 무기한 유효한 정책으로 생성된다
- 설명이 제공되지 않은 경우: 설명 없이 정책을 생성한다

## 예외 흐름
- 동일 유형의 기존 정책과 유효 기간이 겹치는 경우: PayrollPolicyPeriodOverlapException (PAYROLL_POLICY002) 발생
- 배율이 0 미만 또는 10.0 초과인 경우: 유효성 검증 실패 (400 Bad Request)
- 시작일이 종료일보다 이후인 경우: 유효성 검증 실패

## 검증 조건
- 정책 유형(policyType)은 필수이며, OVERTIME_WEEKDAY, OVERTIME_WEEKEND, OVERTIME_HOLIDAY, NIGHT_SHIFT, HOLIDAY_WORK, BONUS, ALLOWANCE 중 하나여야 한다
- 배율(multiplier)은 필수이며, 0 이상 10.0 이하의 BigDecimal 값이어야 한다
- 시작일(effectiveFrom)은 필수이며, 유효한 날짜여야 한다
- 종료일(effectiveTo)이 제공된 경우, 시작일 이후여야 한다
- 동일 정책 유형에 대해 기간 중복이 없어야 한다

## 관련 정책
- POLICY-PAYROLL-001 참조 (정책 유형 정의, 배율 범위, 유효 기간 규칙)
- POLICY-NFR-001 참조

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-PAY-001-01: 정상 급여 정책 등록 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인한 상태
- When: 정책 유형 OVERTIME_WEEKDAY, 배율 1.5, 시작일 2026-04-01, 종료일 2026-12-31, 설명 "평일 초과근무 가산"으로 급여 정책 등록 요청
- Then: 급여 정책이 생성되고, 생성된 정책 ID(UUID)가 반환되며, 저장된 정책의 속성이 요청값과 일치함

### TC-PAY-001-02: 종료일 없이 무기한 정책 등록 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인한 상태
- When: 정책 유형 NIGHT_SHIFT, 배율 2.0, 시작일 2026-04-01, 종료일 미지정으로 급여 정책 등록 요청
- Then: 무기한 유효한 정책이 생성되고 정책 ID가 반환됨

### TC-PAY-001-03: 배율 하한 경계값 0 등록 (Unit)

- Given: PolicyMultiplier 생성 시
- When: 배율 값 0.0으로 PolicyMultiplier 생성
- Then: 정상적으로 생성됨 (0은 허용 범위)

### TC-PAY-001-04: 배율 상한 경계값 10.0 등록 (Unit)

- Given: PolicyMultiplier 생성 시
- When: 배율 값 10.0으로 PolicyMultiplier 생성
- Then: 정상적으로 생성됨 (10.0은 허용 범위)

### TC-PAY-001-05: 배율 하한 미만 값 검증 실패 (Unit)

- Given: PolicyMultiplier 생성 시
- When: 배율 값 -0.1로 PolicyMultiplier 생성 시도
- Then: 검증 오류 발생 - "정책 배율은 0 이상이어야 합니다. 입력값: -0.1"

### TC-PAY-001-06: 배율 상한 초과 값 검증 실패 (Unit)

- Given: PolicyMultiplier 생성 시
- When: 배율 값 10.1로 PolicyMultiplier 생성 시도
- Then: 검증 오류 발생 - "정책 배율은 10.0 이하여야 합니다. 입력값: 10.1"

### TC-PAY-001-07: 동일 유형 기간 중복 시 등록 실패 (Integration)

- Given: OVERTIME_WEEKDAY 유형의 정책이 2026-04-01 ~ 2026-12-31 기간으로 이미 존재
- When: 동일 유형 OVERTIME_WEEKDAY, 시작일 2026-06-01로 급여 정책 등록 요청
- Then: PayrollPolicyPeriodOverlapException (PAYROLL_POLICY002) 발생 - "정책 기간이 기존 정책과 겹칩니다."

### TC-PAY-001-08: 시작일이 종료일보다 이후인 경우 검증 실패 (Unit)

- Given: 정책 생성 시
- When: 시작일 2026-12-31, 종료일 2026-01-01로 정책 등록 요청
- Then: 유효성 검증 실패 (InvalidPolicyPeriodException 또는 400 Bad Request)

### TC-PAY-001-09: 권한 없는 사용자의 정책 등록 거부 (E2E)

- Given: EMPLOYEE 권한 사용자가 로그인한 상태
- When: 급여 정책 등록 API 호출
- Then: 403 Forbidden 응답 반환

### TC-PAY-001-10: 유효하지 않은 정책 유형으로 등록 시도 (E2E)

- Given: SUPER_ADMIN 권한 사용자가 로그인한 상태
- When: 존재하지 않는 정책 유형 "INVALID_TYPE"으로 급여 정책 등록 API 호출
- Then: 400 Bad Request 응답 반환
