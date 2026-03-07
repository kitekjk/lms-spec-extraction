# LMS-USER-002: 회원가입

## 기본 정보
- type: use_case
- domain: user
- service: LMS
- priority: high

## 관련 정책
- POLICY-AUTH-001 (SUPER_ADMIN만 회원가입 가능, 이메일 중복 불가)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-USER-001-인증API](LMS-API-USER-001-인증API.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **User**: 생성 대상
  - 사용하는 주요 필드: email, password, role, isActive
  - 상태 변경: 새 User 생성 (isActive=true)

## 개요
관리자가 새로운 사용자 계정을 등록한다.

## 선행 조건
- 요청자가 SUPER_ADMIN 역할이어야 한다

## 기본 흐름
1. 이메일 중복 여부를 확인한다
2. 비밀번호를 BCrypt로 암호화한다
3. User.create(context, email, password, role)을 호출한다
4. User를 저장하고 결과를 반환한다

## 대안 흐름
- 동일 이메일이 이미 존재하는 경우: `DuplicateEmailException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 유효한 정보로 회원가입 시 User가 isActive=true 상태로 생성되어야 한다
- 동일 이메일 중복 등록 시 DuplicateEmailException이 발생해야 한다
- SUPER_ADMIN 역할로 User.create() 호출 시 require 실패해야 한다
- 이메일 형식이 `^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$`에 맞아야 한다
- 비밀번호는 비어있을 수 없다

## 비즈니스 규칙
- User.create()로 SUPER_ADMIN 역할 생성 불가 (reconstruct만 허용)
- Email VO: 정규식 검증
- Password VO: 비어있을 수 없음
- 생성된 User의 lastLoginAt은 null

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용

## 테스트 시나리오

### TC-USER-002-01: 정상 회원가입 (Integration)
- Given: SUPER_ADMIN으로 로그인한 상태이다
- When: 유효한 이메일/비밀번호/역할로 회원가입을 요청한다
- Then: User가 isActive=true, lastLoginAt=null로 생성된다

### TC-USER-002-02: 이메일 중복 (Integration)
- Given: admin@lms.com 사용자가 이미 존재한다
- When: 동일 이메일로 회원가입을 시도한다
- Then: DuplicateEmailException이 발생한다

### TC-USER-002-03: 권한 검증 - EMPLOYEE 접근 (E2E)
- Given: EMPLOYEE 역할로 로그인한 상태이다
- When: 회원가입 API를 호출한다
- Then: 403 Forbidden이 반환된다

### TC-USER-002-04: SUPER_ADMIN 역할 생성 시도 (Unit)
- Given: role=SUPER_ADMIN으로
- When: User.create()를 호출한다
- Then: require 실패로 IllegalArgumentException이 발생한다

### TC-USER-002-05: 이메일 형식 검증 (Unit)
- Given: 유효하지 않은 이메일 형식("invalid-email")
- When: Email VO를 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-USER-002-06: 빈 비밀번호 검증 (Unit)
- Given: 빈 문자열 비밀번호
- When: Password VO를 생성한다
- Then: IllegalArgumentException이 발생한다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
