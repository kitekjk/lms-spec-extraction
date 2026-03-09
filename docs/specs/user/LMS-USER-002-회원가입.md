# LMS-USER-002 회원가입

## 기본 정보
- type: use_case
- domain: user
- id: LMS-USER-002

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 6.1~6.4 사용자 등록 규칙, 3.1~3.5 RBAC
- POLICY-NFR-001 (비기능 요구사항) — 6.1 BCrypt 암호화, 1.1~1.4 API 하위호환성

## 관련 Spec
- LMS-API-USER-001 (인증API)

## 관련 모델
- 주 모델: User — id(UserId, UUID), email(Email), password(Password, BCrypt), role(Role), isActive(Boolean), createdAt(Instant), lastLoginAt(Instant?)
- 참조 모델: 없음

## 개요
SUPER_ADMIN 권한을 가진 사용자가 새로운 시스템 사용자(SUPER_ADMIN, MANAGER, EMPLOYEE)를 등록한다. 이메일은 시스템 전체에서 고유해야 하며, 비밀번호는 BCrypt로 암호화하여 저장한다. 신규 사용자의 isActive 기본값은 true이고, lastLoginAt은 null이다.

## 기본 흐름
1. SUPER_ADMIN 권한의 사용자가 Bearer 토큰과 함께 등록 정보를 전송한다.
2. 이메일 형식을 검증한다 (jakarta.validation.Email).
3. 비밀번호 길이를 검증한다 (최소 8자).
4. 역할(role) 값이 빈 문자열이 아닌지 검증한다.
5. 이메일 중복 여부를 확인한다 (UserRepository.existsByEmail).
6. 역할이 SUPER_ADMIN, MANAGER, EMPLOYEE 중 하나인지 검증한다.
7. 비밀번호를 BCrypt로 암호화한다.
8. User 엔티티를 생성한다 (isActive=true, lastLoginAt=null).
9. User를 저장한다.
10. userId, email, role, isActive를 응답한다.

## 대안 흐름
- AF-1: 이메일 형식이 유효하지 않으면 HTTP 400과 VALIDATION_ERROR를 반환한다.
- AF-2: 비밀번호가 8자 미만이면 HTTP 400과 VALIDATION_ERROR를 반환한다.
- AF-3: role이 빈 문자열이면 HTTP 400과 VALIDATION_ERROR를 반환한다.
- AF-4: 이메일이 이미 등록되어 있으면 HTTP 409와 REG001("이미 등록된 이메일입니다: {email}")을 반환한다.
- AF-5: role이 SUPER_ADMIN, MANAGER, EMPLOYEE 중 하나가 아니면 HTTP 400과 REG002("유효하지 않은 역할입니다: {role}")를 반환한다.
- AF-6: 요청자가 SUPER_ADMIN이 아니면 HTTP 403을 반환한다.
- AF-7: 인증 토큰이 없거나 만료되었으면 HTTP 401을 반환한다.

## 검증 조건
- email 필드: 빈 문자열 불가, RFC 5322 이메일 형식 필수
- password 필드: 빈 문자열 불가, 최소 8자 이상
- role 필드: 빈 문자열 불가, SUPER_ADMIN | MANAGER | EMPLOYEE 중 하나
- 이메일은 시스템 전체에서 고유
- 생성된 User의 isActive == true
- 생성된 User의 lastLoginAt == null
- 비밀번호는 BCrypt로 인코딩되어 저장

## 비기능 요구사항
- POLICY-NFR-001 참조
- 회원가입 API 응답시간 500ms 이내
- 비밀번호 평문 로깅 금지
- SUPER_ADMIN 권한 검증은 @PreAuthorize로 메서드 레벨에서 수행

## 테스트 시나리오

### TC-USER-002-01: SUPER_ADMIN이 MANAGER 역할 사용자 등록 성공 (Unit)
- Given: SUPER_ADMIN 인증 토큰이 유효하고, email="newmgr@example.com"이 미등록 상태이다
- When: POST /api/auth/register에 email="newmgr@example.com", password="password123", role="MANAGER"로 요청한다
- Then: HTTP 201, 응답에 userId, email="newmgr@example.com", role="MANAGER", isActive=true가 포함된다

### TC-USER-002-02: 중복 이메일로 등록 시 실패 (Unit)
- Given: email="exist@example.com"인 User가 이미 등록되어 있다
- When: POST /api/auth/register에 email="exist@example.com"으로 요청한다
- Then: HTTP 409, 에러코드 REG001, 메시지에 "이미 등록된 이메일입니다" 포함

### TC-USER-002-03: 유효하지 않은 역할로 등록 시 실패 (Unit)
- Given: SUPER_ADMIN 인증 토큰이 유효하다
- When: POST /api/auth/register에 role="INVALID_ROLE"로 요청한다
- Then: HTTP 400, 에러코드 REG002, 메시지에 "유효하지 않은 역할입니다" 포함

### TC-USER-002-04: MANAGER 권한으로 등록 시도 시 실패 (Unit)
- Given: MANAGER 인증 토큰이 유효하다
- When: POST /api/auth/register에 등록 정보를 요청한다
- Then: HTTP 403 (권한 없음)

### TC-USER-002-05: 회원가입 후 DB 저장 상태 확인 (Integration)
- Given: email="inttest@example.com"이 미등록 상태이다
- When: POST /api/auth/register에 해당 이메일로 등록 요청한다
- Then: DB에서 User 조회 시 email="inttest@example.com", isActive=true, lastLoginAt=null, password가 BCrypt 형식이다

### TC-USER-002-06: 회원가입 후 해당 계정으로 로그인 성공 (E2E)
- Given: email="e2enew@example.com"이 미등록 상태이다
- When: SUPER_ADMIN이 해당 이메일로 회원가입 후, 해당 계정으로 로그인한다
- Then: 로그인이 성공하고 accessToken이 발급된다
