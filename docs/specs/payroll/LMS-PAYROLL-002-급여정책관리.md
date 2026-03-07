# LMS-PAYROLL-002: 급여 정책 관리

## 기본 정보
- type: use_case
- domain: payroll
- service: LMS
- priority: medium

## 관련 정책
- POLICY-PAYROLL-001 (급여 정책 관리 규칙, 기간 중복 불가, 현재 유효 정책만 수정)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-PAYROLL-001-급여API](LMS-API-PAYROLL-001-급여API.md)
- [LMS-PAYROLL-001-급여산정](LMS-PAYROLL-001-급여산정.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **PayrollPolicy**: CRUD 대상
  - 사용하는 주요 필드: policyType, multiplier, effectivePeriod, description
  - 상태 변경: 생성, 가산율 변경, 종료(terminate)

## 개요
급여 정책(가산율)을 생성, 조회, 수정, 삭제한다.

## 선행 조건
- 생성/수정/삭제: 요청자가 SUPER_ADMIN 역할이어야 한다
- 조회(활성 정책): 인증된 사용자 모두 가능
- 조회(유형별): MANAGER 또는 SUPER_ADMIN 역할이어야 한다

## 기본 흐름

### 생성
1. 동일 PolicyType의 기존 정책을 조회한다
2. 새 정책의 유효 기간과 기존 정책의 유효 기간이 겹치는지 확인한다
3. PayrollPolicy.create(context, policyType, multiplier, effectivePeriod, description)을 호출한다
4. PayrollPolicy를 저장하고 결과를 반환한다

### 수정
1. policyId로 PayrollPolicy를 조회한다
2. 현재 유효한 정책인지 확인한다
3. 제공된 필드만 업데이트한다 (multiplier, effectiveTo, description)
4. 수정된 PayrollPolicy를 저장하고 결과를 반환한다

### 삭제
1. policyId로 PayrollPolicy 존재 여부를 확인한다
2. PayrollPolicy를 삭제한다

## 대안 흐름
- PayrollPolicy가 존재하지 않는 경우: `PayrollPolicyNotFoundException` 발생
- 동일 유형 기간 중복: `PayrollPolicyPeriodOverlapException` 발생
- 비활성 정책 수정 시도: `InactivePolicyCannotBeModifiedException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 유효한 정보로 정책 생성 시 PayrollPolicy가 생성되어야 한다
- 동일 PolicyType에 유효 기간이 겹치는 정책 생성 시 PayrollPolicyPeriodOverlapException이 발생해야 한다
- 비활성 정책 수정 시 InactivePolicyCannotBeModifiedException이 발생해야 한다
- multiplier는 0 이상 10 이하여야 한다
- effectiveFrom은 effectiveTo 이전이어야 한다
- effectiveTo가 null이면 무기한 유효
- 존재하지 않는 정책 삭제 시 PayrollPolicyNotFoundException이 발생해야 한다

## 비즈니스 규칙
- PolicyType: OVERTIME_WEEKDAY, OVERTIME_WEEKEND, OVERTIME_HOLIDAY, NIGHT_SHIFT, HOLIDAY_WORK, BONUS, ALLOWANCE
- PolicyMultiplier: 0 이상 10 이하
- 사전 정의 가산율: standard()=1.5, weekend()=2.0, holiday()=2.5
- effectiveTo가 null이면 무기한 유효
- 동일 PolicyType에 유효 기간이 겹치는 정책 생성 불가
- 현재 유효한 정책만 수정 가능 (isCurrentlyEffective())
- terminate(endDate): effectiveTo를 설정하여 정책 종료

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용

## 테스트 시나리오

### TC-PAY-002-01: 정상 정책 생성 (Integration)
- Given: OVERTIME_WEEKDAY 유형의 기존 정책이 없다
- When: multiplier=1.5, effectiveFrom=2026-01-01로 정책을 생성한다
- Then: PayrollPolicy가 생성되고 isCurrentlyEffective()=true이다

### TC-PAY-002-02: 기간 중복 정책 생성 (Integration)
- Given: 2026-01-01~무기한 OVERTIME_WEEKDAY 정책이 존재한다
- When: 2026-06-01~무기한 같은 유형 정책을 생성한다
- Then: PayrollPolicyPeriodOverlapException이 발생한다

### TC-PAY-002-03: 정상 정책 수정 (Integration)
- Given: 현재 유효한 PayrollPolicy가 존재한다
- When: multiplier를 2.0으로 변경한다
- Then: 변경된 multiplier가 반영된다

### TC-PAY-002-04: 비활성 정책 수정 시도 (Integration)
- Given: effectiveTo가 과거인 PayrollPolicy가 존재한다
- When: 수정을 시도한다
- Then: InactivePolicyCannotBeModifiedException이 발생한다

### TC-PAY-002-05: PolicyMultiplier 검증 (Unit)
- Given: multiplier=-1.0 또는 11.0
- When: PolicyMultiplier VO를 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-PAY-002-06: 정책 종료 (Integration)
- Given: 현재 유효한 무기한 정책이 존재한다
- When: effectiveTo=2026-12-31로 종료한다
- Then: effectiveTo가 설정되고 2027-01-01 이후 isEffectiveOn()=false이다

### TC-PAY-002-07: 권한 검증 - MANAGER 접근 (E2E)
- Given: MANAGER 역할로 로그인한 상태이다
- When: 정책 생성 API를 호출한다
- Then: 403 Forbidden이 반환된다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
