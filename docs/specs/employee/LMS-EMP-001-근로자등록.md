# LMS-EMP-001: 근로자등록

## 기본 정보
- type: use_case
- domain: employee

## 관련 Spec
- LMS-API-EMP-001 (근로자API)
- LMS-EMP-002 (근로자수정)
- LMS-EMP-003 (근로자비활성화)
- LMS-EMP-004 (근로자조회)

## 개요
관리자가 userId, 이름, 근로자유형, 매장ID를 입력하여 새로운 근로자를 등록하고 근로자 유형별 초기 연차를 설정한다.

## 관련 모델
- 주 모델: Employee (Aggregate Root)
- 참조 모델: User (userId 참조), Store (storeId 참조), EmployeeType, RemainingLeave

## 선행 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 등록 대상 userId에 해당하는 User가 존재해야 한다
- 해당 userId로 이미 등록된 Employee가 없어야 한다

## 기본 흐름
1. 관리자가 userId, 이름, 근로자유형(EmployeeType), 매장ID(선택)를 입력하여 근로자 등록을 요청한다
2. 시스템은 Employee를 생성한다
3. 근로자 유형별 초기 연차를 설정한다:
   - REGULAR(정규직): 15일
   - IRREGULAR(계약직): 11일
   - PART_TIME(아르바이트): 0일
4. 시스템은 생성된 근로자를 저장하고 결과를 반환한다

## 대안 흐름
- storeId가 null인 경우: 매장 미배정 상태로 생성된다

## 예외 흐름
- 이미 해당 userId로 등록된 근로자가 존재하는 경우: DuplicateEmployeeUserException (EMP002) 발생
- 권한이 없는 매장에 접근 시도한 경우: UnauthorizedStoreAccessException (EMP003) 발생

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 등록 대상 userId에 해당하는 User가 존재해야 한다
- 해당 userId로 이미 등록된 Employee가 없어야 한다
- MANAGER는 자신의 매장에만 근로자를 등록할 수 있다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-EMP-001-01: 정규직 근로자 정상 등록 (Unit)
- Given: 유효한 userId가 존재하고, 해당 userId로 등록된 Employee가 없음
- When: 이름 "홍길동", 근로자유형 REGULAR, storeId를 지정하여 근로자 등록을 요청
- Then: Employee가 생성되고, 초기 잔여 연차가 15일로 설정됨

### TC-EMP-001-02: 계약직 근로자 등록 시 초기 연차 확인 (Unit)
- Given: 유효한 userId가 존재하고, 해당 userId로 등록된 Employee가 없음
- When: 근로자유형 IRREGULAR로 근로자 등록을 요청
- Then: Employee가 생성되고, 초기 잔여 연차가 11일로 설정됨

### TC-EMP-001-03: 아르바이트 근로자 등록 시 초기 연차 확인 (Unit)
- Given: 유효한 userId가 존재하고, 해당 userId로 등록된 Employee가 없음
- When: 근로자유형 PART_TIME으로 근로자 등록을 요청
- Then: Employee가 생성되고, 초기 잔여 연차가 0일로 설정됨

### TC-EMP-001-04: 중복 userId로 근로자 등록 시도 (Unit)
- Given: 해당 userId로 이미 Employee가 등록되어 있음
- When: 동일한 userId로 근로자 등록을 요청
- Then: DuplicateEmployeeUserException (EMP002) 발생

### TC-EMP-001-05: 매장 미배정 상태로 근로자 등록 (Unit)
- Given: 유효한 userId가 존재하고, storeId가 null
- When: storeId 없이 근로자 등록을 요청
- Then: Employee가 매장 미배정(storeId=null) 상태로 생성됨

### TC-EMP-001-06: MANAGER가 타 매장 근로자 등록 시도 (E2E)
- Given: MANAGER 역할의 사용자가 storeId="store-A"에 소속
- When: storeId="store-B"로 근로자 등록을 요청
- Then: UnauthorizedStoreAccessException (EMP003) 발생

### TC-EMP-001-07: EMPLOYEE 권한으로 근로자 등록 시도 (E2E)
- Given: EMPLOYEE 역할의 사용자가 인증된 상태
- When: 근로자 등록을 요청
- Then: 403 Forbidden 응답
