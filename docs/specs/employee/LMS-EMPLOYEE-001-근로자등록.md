# LMS-EMPLOYEE-001: 근로자 등록

## 기본 정보
- type: use_case
- domain: employee
- service: LMS
- priority: high

## 관련 정책
- POLICY-LEAVE-001 (근로자 유형별 연차 정책: REGULAR 15일, IRREGULAR 11일, PART_TIME 0일)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-EMPLOYEE-001-근로자API](LMS-API-EMPLOYEE-001-근로자API.md)
- [LMS-USER-002-회원가입](../user/LMS-USER-002-회원가입.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **Employee**: 생성 대상
  - 사용하는 주요 필드: userId, name, employeeType, storeId, remainingLeave, isActive
  - 상태 변경: 새 Employee 생성 (isActive=true, 유형별 연차 자동 설정)

### 참조 모델
- **User**: 연결 대상 (1:1 관계)
  - 참조하는 필드: userId

## 개요
새로운 근로자를 등록하고 유형에 따른 초기 연차를 부여한다.

## 선행 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 역할이어야 한다
- 연결할 User 계정이 존재해야 한다
- 동일 User에 이미 Employee가 등록되어 있지 않아야 한다

## 기본 흐름
1. command에서 UserId를 생성한다
2. 동일 UserId로 Employee가 이미 존재하는지 확인한다
3. Employee.create(context, userId, name, employeeType, storeId)를 호출한다
4. Employee를 저장하고 EmployeeResult를 반환한다

## 대안 흐름
- 동일 UserId로 Employee가 이미 존재하는 경우: `DuplicateEmployeeUserException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 유효한 정보로 근로자 등록 시 Employee가 생성되어야 한다
- REGULAR 유형으로 등록 시 remainingLeave가 15.0이어야 한다
- IRREGULAR 유형으로 등록 시 remainingLeave가 11.0이어야 한다
- PART_TIME 유형으로 등록 시 remainingLeave가 0.0이어야 한다
- 동일 User로 중복 등록 시 DuplicateEmployeeUserException이 발생해야 한다
- 생성된 Employee는 isActive=true 상태여야 한다
- EmployeeName은 비어있지 않고 최대 100자여야 한다

## 비즈니스 규칙
- Employee와 User는 1:1 관계이다
- storeId는 선택값이다 (매장 미배정 상태로 등록 가능)
- 초기 연차는 Employee.create() 내부에서 EmployeeType에 따라 자동 설정된다
- Employee 생성 시 isActive=true로 초기화된다

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용

## 테스트 시나리오

### TC-EMP-001-01: 정상 근로자 등록 - REGULAR (Integration)
- Given: 유효한 User 계정이 존재하고 Employee가 미등록이다
- When: REGULAR 유형으로 근로자를 등록한다
- Then: Employee가 생성되고 remainingLeave=15.0, isActive=true이다

### TC-EMP-001-02: 정상 근로자 등록 - IRREGULAR (Integration)
- Given: 유효한 User 계정이 존재한다
- When: IRREGULAR 유형으로 근로자를 등록한다
- Then: remainingLeave=11.0이다

### TC-EMP-001-03: 정상 근로자 등록 - PART_TIME (Integration)
- Given: 유효한 User 계정이 존재한다
- When: PART_TIME 유형으로 근로자를 등록한다
- Then: remainingLeave=0.0이다

### TC-EMP-001-04: 중복 등록 (Integration)
- Given: 동일 UserId로 Employee가 이미 등록되어 있다
- When: 같은 UserId로 근로자를 등록한다
- Then: DuplicateEmployeeUserException이 발생한다

### TC-EMP-001-05: EmployeeName 검증 (Unit)
- Given: 빈 문자열 또는 101자 초과 이름
- When: EmployeeName VO를 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-EMP-001-06: 권한 검증 - EMPLOYEE 접근 (E2E)
- Given: EMPLOYEE 역할로 로그인한 상태이다
- When: 근로자 등록 API를 호출한다
- Then: 403 Forbidden이 반환된다

### TC-EMP-001-07: 매장 미배정 등록 (Integration)
- Given: storeId=null로
- When: 근로자를 등록한다
- Then: Employee가 생성되고 storeId=null이다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
