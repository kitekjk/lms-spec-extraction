# LMS-USER-002: 회원가입

## 기본 정보
- type: use_case
- domain: user

## 관련 Spec
- LMS-API-USER-001 (인증API)
- LMS-USER-001 (로그인)

## 개요
SUPER_ADMIN이 이메일, 비밀번호, 역할을 입력하여 새로운 사용자를 등록한다.

## 관련 모델
- 주 모델: User (Aggregate Root)
- 참조 모델: Email, Password, Role

## 선행 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 등록하려는 이메일이 기존에 등록되지 않은 이메일이어야 한다

## 기본 흐름
1. SUPER_ADMIN이 이메일, 비밀번호, 역할, 매장ID(선택)를 입력하여 회원가입을 요청한다
2. 시스템은 이메일 중복 여부를 확인한다
3. 시스템은 역할(Role) 값의 유효성을 검증한다 (SUPER_ADMIN, MANAGER, EMPLOYEE)
4. 시스템은 비밀번호를 암호화한다
5. 시스템은 새로운 User를 생성한다
6. 시스템은 사용자를 저장하고 결과를 반환한다

## 대안 흐름
- SUPER_ADMIN 역할로 등록 요청 시: reconstruct() 방식으로 생성 (도메인 규칙 우회)
- storeId가 제공된 경우: 요청에 포함하여 전달 (현재 User 모델에서는 직접 사용하지 않음)

## 예외 흐름
- 이메일이 이미 등록된 경우: DuplicateEmailException (REG001) 발생
- 유효하지 않은 역할인 경우: InvalidRoleException (REG002) 발생
- 이메일 형식이 올바르지 않은 경우: 유효성 검증 실패 (VALIDATION_ERROR)
- 비밀번호가 8자 미만인 경우: 유효성 검증 실패 (VALIDATION_ERROR)

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 이메일이 기존에 등록되지 않은 이메일이어야 한다
- 역할(Role)은 SUPER_ADMIN, MANAGER, EMPLOYEE 중 하나여야 한다
- 이메일 형식이 올바라야 한다
- 비밀번호가 8자 이상이어야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-USER-002-01: 정상 회원가입 (Unit)
- Given: SUPER_ADMIN 권한의 사용자가 인증된 상태이고, "new@test.com"은 미등록 이메일
- When: 이메일 "new@test.com", 비밀번호 "password123", 역할 "EMPLOYEE"로 회원가입을 요청
- Then: 새로운 User가 생성되고, 비밀번호가 BCrypt로 암호화되어 저장됨

### TC-USER-002-02: 중복 이메일로 회원가입 시도 (Unit)
- Given: "existing@test.com" 이메일로 이미 사용자가 등록되어 있음
- When: 동일한 이메일로 회원가입을 요청
- Then: DuplicateEmailException (REG001) 발생 - "이미 등록된 이메일입니다: existing@test.com"

### TC-USER-002-03: 유효하지 않은 역할로 회원가입 시도 (Unit)
- Given: SUPER_ADMIN이 인증된 상태
- When: 역할 "INVALID_ROLE"로 회원가입을 요청
- Then: InvalidRoleException (REG002) 발생 - "유효하지 않은 역할입니다: INVALID_ROLE"

### TC-USER-002-04: 잘못된 이메일 형식으로 회원가입 시도 (Unit)
- Given: SUPER_ADMIN이 인증된 상태
- When: 이메일 "invalid-email"로 회원가입을 요청
- Then: 유효성 검증 실패 (VALIDATION_ERROR) 발생

### TC-USER-002-05: 8자 미만 비밀번호로 회원가입 시도 (Unit)
- Given: SUPER_ADMIN이 인증된 상태
- When: 비밀번호 "short"(5자)로 회원가입을 요청
- Then: 유효성 검증 실패 (VALIDATION_ERROR) 발생

### TC-USER-002-06: SUPER_ADMIN 권한 없이 회원가입 시도 (E2E)
- Given: EMPLOYEE 역할의 사용자가 인증된 상태
- When: 회원가입을 요청
- Then: 403 Forbidden 응답

### TC-USER-002-07: storeId 포함 회원가입 (Integration)
- Given: SUPER_ADMIN이 인증된 상태이고, 유효한 storeId가 존재
- When: storeId를 포함하여 회원가입을 요청
- Then: User가 정상 생성되고 storeId 정보가 요청에 포함되어 전달됨
