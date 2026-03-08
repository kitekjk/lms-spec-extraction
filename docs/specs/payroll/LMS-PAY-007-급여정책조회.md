# LMS-PAY-007: 급여정책조회

## 기본 정보
- type: use_case
- domain: payroll

## 관련 Spec
- LMS-API-PAY-001 (급여API)
- LMS-PAY-001 (급여정책등록)

## 개요
인증된 사용자가 현재 유효한 급여 정책을 조회하거나, 관리자가 정책 유형별로 조회한다.

## 관련 모델
- 주 모델: PayrollPolicy (Aggregate Root)
- 참조 모델: PolicyType, PolicyMultiplier, PolicyEffectivePeriod, PayrollPolicyId

## 선행 조건
- 인증된 사용자여야 한다

## 기본 흐름

### 흐름 1: 현재 유효한 정책 조회
1. 사용자가 현재 유효한 급여 정책 조회를 요청한다
2. 시스템은 현재 날짜 기준으로 유효한 모든 정책을 조회한다
3. 시스템은 정책 목록과 총 건수를 반환한다
   - 각 정책: ID, 정책 유형, 정책 유형 설명, 배율, 시작일, 종료일, 설명, 유효 여부, 생성일
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN

### 흐름 2: 정책 유형별 조회
1. 관리자가 정책 유형을 지정하여 조회를 요청한다
2. 시스템은 해당 유형의 모든 정책(과거/현재 포함)을 조회한다
3. 시스템은 정책 목록과 총 건수를 반환한다
- 권한: MANAGER, SUPER_ADMIN

### 흐름 3: 전체 정책 조회 (유형 미지정)
1. 관리자가 정책 유형 없이 조회를 요청한다
2. 시스템은 현재 유효한 모든 정책을 반환한다
- 권한: MANAGER, SUPER_ADMIN

## 대안 흐름
- 조건에 맞는 정책이 없는 경우: 빈 목록과 totalCount 0을 반환한다

## 예외 흐름
- 없음 (조회 실패 시 빈 목록 반환)

## 검증 조건
- 정책 유형(policyType)이 제공된 경우 유효한 PolicyType 열거값이어야 한다
  - OVERTIME_WEEKDAY, OVERTIME_WEEKEND, OVERTIME_HOLIDAY, NIGHT_SHIFT, HOLIDAY_WORK, BONUS, ALLOWANCE
- 응답에 현재 유효 여부(isCurrentlyEffective)가 포함되어야 한다

## 관련 정책
- POLICY-PAYROLL-001 참조 (정책 유형 정의, 유효 기간 규칙)
- POLICY-NFR-001 참조

## 비기능 요구사항
- POLICY-NFR-001 참조
- 조회 API는 읽기 전용 트랜잭션으로 처리한다

## 테스트 시나리오

### TC-PAY-007-01: 현재 유효한 정책 조회 - 정상 (Integration)

- Given: 현재 유효한 정책 3건 존재 (OVERTIME_WEEKDAY, NIGHT_SHIFT, OVERTIME_HOLIDAY)
- When: 현재 유효한 급여 정책 조회 요청
- Then: 정책 3건이 반환되고, 각 정책에 isCurrentlyEffective=true 포함

### TC-PAY-007-02: 정책 유형별 조회 - 정상 (Integration)

- Given: MANAGER 권한 사용자가 로그인하고, OVERTIME_WEEKDAY 유형의 정책이 과거 2건 + 현재 1건 존재
- When: 정책 유형 OVERTIME_WEEKDAY로 조회 요청
- Then: 해당 유형의 정책 3건이 반환되고 총 건수 3

### TC-PAY-007-03: 조건에 맞는 정책이 없는 경우 (Integration)

- Given: BONUS 유형의 정책이 존재하지 않음
- When: 정책 유형 BONUS로 조회 요청
- Then: 빈 목록과 totalCount 0 반환

### TC-PAY-007-04: 전체 정책 조회 - 유형 미지정 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인하고, 현재 유효한 정책 5건 존재
- When: 정책 유형 없이 조회 요청
- Then: 현재 유효한 모든 정책 5건이 반환됨

### TC-PAY-007-05: 유효하지 않은 정책 유형 요청 (E2E)

- Given: 인증된 사용자가 로그인한 상태
- When: 잘못된 정책 유형 "INVALID_TYPE"으로 조회 API 호출
- Then: 400 Bad Request 응답 반환

### TC-PAY-007-06: EMPLOYEE 권한으로 현재 유효한 정책 조회 가능 (E2E)

- Given: EMPLOYEE 권한 사용자가 로그인한 상태
- When: 현재 유효한 급여 정책 조회 API 호출
- Then: 200 OK 응답과 함께 정책 목록 반환

### TC-PAY-007-07: 정책 유효 여부 필드 포함 검증 (E2E)

- Given: 유효 기간이 만료된 정책과 현재 유효한 정책이 혼재
- When: 특정 유형으로 정책 조회 API 호출
- Then: 각 정책 응답에 isCurrentlyEffective 필드가 포함되고, 만료 정책은 false, 유효 정책은 true
