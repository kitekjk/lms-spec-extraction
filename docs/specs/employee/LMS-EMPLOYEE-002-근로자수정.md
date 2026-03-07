# LMS-EMPLOYEE-002: 근로자 수정

## 기본 정보
- type: use_case
- domain: employee
- service: LMS
- priority: medium

## 관련 정책
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-EMPLOYEE-001-근로자API](LMS-API-EMPLOYEE-001-근로자API.md)
- [LMS-EMPLOYEE-001-근로자등록](LMS-EMPLOYEE-001-근로자등록.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **Employee**: 수정/비활성화 대상
  - 사용하는 주요 필드: name, employeeType, storeId, remainingLeave, isActive
  - 상태 변경: 필드 업데이트 또는 isActive=false

## 개요
근로자 정보를 수정하거나 비활성화한다.

## 선행 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 역할이어야 한다
- 대상 Employee가 존재해야 한다

## 기본 흐름

### 수정
1. employeeId로 Employee를 조회한다
2. Employee.update(context, name, employeeType, storeId)를 호출한다
3. 수정된 Employee를 저장하고 결과를 반환한다

### 비활성화
1. employeeId로 Employee를 조회한다
2. Employee.deactivate(context)를 호출한다
3. 비활성화된 Employee를 저장하고 결과를 반환한다

## 대안 흐름
- Employee가 존재하지 않는 경우: `EmployeeNotFoundException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 수정 후 name, employeeType, storeId가 변경되어야 한다
- 비활성화 후 isActive=false여야 한다
- 존재하지 않는 Employee 수정 시 EmployeeNotFoundException이 발생해야 한다
- 존재하지 않는 Employee 비활성화 시 EmployeeNotFoundException이 발생해야 한다

## 비즈니스 규칙
- 비활성화는 soft delete (isActive=false)
- 수정 시 remainingLeave는 직접 변경하지 않음 (휴가 승인/취소에 의해 변동)

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용

## 테스트 시나리오

### TC-EMP-002-01: 정상 수정 (Integration)
- Given: 활성 Employee가 존재한다
- When: 이름과 유형을 변경하여 수정한다
- Then: 변경된 값이 반영된다

### TC-EMP-002-02: 정상 비활성화 (Integration)
- Given: 활성(isActive=true) Employee가 존재한다
- When: 비활성화를 요청한다
- Then: isActive=false가 된다

### TC-EMP-002-03: 존재하지 않는 Employee 수정 (Integration)
- Given: 존재하지 않는 employeeId가 주어진다
- When: 수정을 시도한다
- Then: EmployeeNotFoundException이 발생한다

### TC-EMP-002-04: 권한 검증 - EMPLOYEE 접근 (E2E)
- Given: EMPLOYEE 역할로 로그인한 상태이다
- When: 다른 근로자 수정 API를 호출한다
- Then: 403 Forbidden이 반환된다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
