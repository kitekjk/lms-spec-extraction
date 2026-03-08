# LMS-EMP-002: 근로자수정

## 기본 정보
- type: use_case
- domain: employee

## 관련 Spec
- LMS-API-EMP-001 (근로자API)
- LMS-EMP-001 (근로자등록)

## 개요
관리자가 근로자의 이름, 근로자유형, 매장ID 정보를 수정한다.

## 관련 모델
- 주 모델: Employee (Aggregate Root)
- 참조 모델: EmployeeType, Store (storeId 참조)

## 선행 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 수정 대상 근로자가 존재해야 한다

## 기본 흐름
1. 관리자가 근로자 ID와 수정할 정보(이름, 근로자유형, 매장ID)를 입력하여 수정을 요청한다
2. 시스템은 근로자를 조회한다
3. 시스템은 근로자 정보를 수정한다 (이름, 근로자유형, 매장ID)
4. 시스템은 수정된 근로자를 저장하고 결과를 반환한다

## 대안 흐름
- storeId가 null인 경우: 매장 미배정 상태로 변경된다

## 예외 흐름
- 근로자를 찾을 수 없는 경우: EmployeeNotFoundException (EMP001) 발생
- 권한이 없는 매장에 접근 시도한 경우: UnauthorizedStoreAccessException (EMP003) 발생

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 수정 대상 근로자가 존재해야 한다
- MANAGER는 자신의 매장 소속 근로자만 수정할 수 있다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-EMP-002-01: 정상 근로자 정보 수정 (Unit)
- Given: employeeId에 해당하는 활성 근로자가 존재
- When: 이름 "김철수", 근로자유형 IRREGULAR, storeId="store-B"로 수정을 요청
- Then: 근로자 정보가 정상적으로 업데이트됨

### TC-EMP-002-02: 존재하지 않는 근로자 수정 시도 (Unit)
- Given: 존재하지 않는 employeeId
- When: 해당 근로자의 정보 수정을 요청
- Then: EmployeeNotFoundException (EMP001) 발생

### TC-EMP-002-03: 매장 미배정으로 변경 (Unit)
- Given: storeId="store-A"에 소속된 근로자가 존재
- When: storeId를 null로 수정을 요청
- Then: 근로자의 매장이 미배정(storeId=null) 상태로 변경됨

### TC-EMP-002-04: MANAGER가 타 매장 근로자 수정 시도 (E2E)
- Given: MANAGER 역할의 사용자가 storeId="store-A"에 소속, 수정 대상 근로자는 storeId="store-B"에 소속
- When: 해당 근로자의 정보 수정을 요청
- Then: UnauthorizedStoreAccessException (EMP003) 발생

### TC-EMP-002-05: 근로자유형 변경 시 데이터 일관성 확인 (Integration)
- Given: REGULAR(정규직) 근로자가 존재하고 잔여 연차가 10일
- When: 근로자유형을 PART_TIME으로 수정
- Then: 근로자유형이 변경되고, 기존 잔여 연차 데이터는 유지됨
