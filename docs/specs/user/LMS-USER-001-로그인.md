# LMS-USER-001: 로그인

## 기본 정보
- type: use_case
- domain: user
- service: LMS
- priority: high

## 관련 정책
- POLICY-AUTH-001 (JWT 인증, Access/Refresh Token 발급)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-USER-001-인증API](LMS-API-USER-001-인증API.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **User**: 인증 대상
  - 사용하는 주요 필드: email, password, role, isActive, lastLoginAt
  - 상태 변경: lastLoginAt 업데이트

### 참조 모델
- **TokenProvider**: JWT 토큰 생성
  - 참조하는 필드: userId, role

## 개요
사용자가 이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받는다.

## 선행 조건
- 등록된 사용자 계정이 존재해야 한다

## 기본 흐름
1. 이메일로 사용자를 조회한다
2. 비밀번호를 검증한다 (BCrypt 매칭)
3. 사용자 활성 상태를 확인한다
4. User.login(context)을 호출하여 lastLoginAt을 업데이트한다
5. 사용자를 저장한다
6. TokenProvider로 Access Token과 Refresh Token을 생성한다
7. 토큰 정보를 반환한다

## 대안 흐름
- 이메일로 사용자를 찾을 수 없는 경우: `AuthenticationFailedException` 발생
- 비밀번호가 일치하지 않는 경우: `AuthenticationFailedException` 발생

## 예외 흐름
- 사용자가 비활성 상태인 경우: `InactiveUserException` 발생

## 검증 조건
- 유효한 이메일/비밀번호로 로그인 시 Access Token과 Refresh Token이 반환되어야 한다
- 존재하지 않는 이메일로 로그인 시 AuthenticationFailedException이 발생해야 한다
- 잘못된 비밀번호로 로그인 시 AuthenticationFailedException이 발생해야 한다
- 비활성 사용자로 로그인 시 InactiveUserException이 발생해야 한다
- 로그인 성공 후 lastLoginAt이 업데이트되어야 한다

## 비즈니스 규칙
- 이메일과 비밀번호 불일치 시 동일한 예외(AuthenticationFailedException)를 사용하여 어떤 정보가 틀렸는지 노출하지 않음
- User.login()에서 isActive=false이면 require 실패

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용

## 테스트 시나리오

### TC-USER-001-01: 정상 로그인 (Integration)
- Given: 활성 사용자(admin@lms.com, password123)가 존재한다
- When: 올바른 이메일/비밀번호로 로그인한다
- Then: Access Token과 Refresh Token이 반환되고, lastLoginAt이 업데이트된다

### TC-USER-001-02: 존재하지 않는 이메일 (Integration)
- Given: 등록되지 않은 이메일이 주어진다
- When: 로그인을 시도한다
- Then: AuthenticationFailedException이 발생한다

### TC-USER-001-03: 잘못된 비밀번호 (Integration)
- Given: 활성 사용자가 존재한다
- When: 틀린 비밀번호로 로그인을 시도한다
- Then: AuthenticationFailedException이 발생한다

### TC-USER-001-04: 비활성 사용자 로그인 (Integration)
- Given: 비활성(isActive=false) 사용자가 존재한다
- When: 올바른 이메일/비밀번호로 로그인을 시도한다
- Then: InactiveUserException이 발생한다

### TC-USER-001-05: 도메인 로그인 규칙 (Unit)
- Given: isActive=false인 User 도메인 객체
- When: login(context)을 호출한다
- Then: require 실패로 IllegalArgumentException이 발생한다

### TC-USER-001-06: 권한 검증 - 인증 없이 접근 (E2E)
- Given: 인증 토큰 없이
- When: 보호된 API에 접근한다
- Then: 401 Unauthorized가 반환된다

## 관련 이벤트
- 발행: 없음 (향후 LoginEvent 발행 예정)
- 수신: 없음
