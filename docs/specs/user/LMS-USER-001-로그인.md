# LMS-USER-001 로그인

## 기본 정보
- type: use_case
- domain: user
- id: LMS-USER-001

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 2.1~2.5 로그인/로그아웃 규칙
- POLICY-NFR-001 (비기능 요구사항) — 6.1 BCrypt 암호화, 5.1 응답시간 500ms 이내

## 관련 Spec
- LMS-API-USER-001 (인증API)

## 관련 모델
- 주 모델: User — id(UserId, UUID), email(Email), password(Password, BCrypt), role(Role), isActive(Boolean), lastLoginAt(Instant?)
- 참조 모델: Employee — userId(UserId), storeId(StoreId?) / TokenProvider — accessToken, refreshToken 생성

## 개요
사용자가 이메일과 비밀번호를 입력하여 시스템에 로그인한다. 인증 성공 시 JWT Access Token(유효시간 1시간)과 Refresh Token(유효시간 7일), 사용자 정보를 응답한다. 로그인 시 lastLoginAt을 현재 시점으로 갱신한다. Employee가 존재하면 storeId를 토큰 클레임에 포함한다.

## 기본 흐름
1. 사용자가 이메일과 비밀번호를 전송한다.
2. 이메일 형식을 검증한다 (jakarta.validation.Email).
3. 비밀번호 길이를 검증한다 (최소 8자).
4. 이메일로 User를 조회한다.
5. BCrypt로 비밀번호를 검증한다.
6. User의 isActive가 true인지 확인한다.
7. User의 lastLoginAt을 현재 시점(DomainContext.requestedAt)으로 갱신하고 저장한다.
8. Employee를 userId로 조회하여 storeId를 가져온다 (없으면 null).
9. Access Token과 Refresh Token을 생성한다.
10. accessToken, refreshToken, userInfo(userId, email, role, isActive)를 응답한다.

## 대안 흐름
- AF-1: 이메일 형식이 유효하지 않으면 HTTP 400과 VALIDATION_ERROR를 반환한다.
- AF-2: 비밀번호가 8자 미만이면 HTTP 400과 VALIDATION_ERROR를 반환한다.
- AF-3: 이메일에 해당하는 사용자가 없으면 HTTP 401과 AUTH001("이메일 또는 비밀번호가 일치하지 않습니다")을 반환한다.
- AF-4: 비밀번호가 일치하지 않으면 HTTP 401과 AUTH001("이메일 또는 비밀번호가 일치하지 않습니다")을 반환한다.
- AF-5: isActive가 false이면 HTTP 403과 AUTH002("비활성화된 사용자입니다")를 반환한다.

## 검증 조건
- email 필드: 빈 문자열 불가, RFC 5322 이메일 형식 필수
- password 필드: 빈 문자열 불가, 최소 8자 이상
- User.isActive == true 필수
- 비밀번호는 BCrypt로 인코딩된 값과 비교
- 로그인 성공 시 lastLoginAt 값이 null이 아닌 현재 시점으로 갱신됨
- Access Token 유효시간: 3,600,000ms (1시간)
- Refresh Token 유효시간: 604,800,000ms (7일)
- JWT 서명 알고리즘: HS256

## 비기능 요구사항
- POLICY-NFR-001 참조
- 로그인 API 응답시간 500ms 이내
- 비밀번호 평문 로깅 금지
- 인증 실패 시 이메일/비밀번호 중 어떤 것이 틀렸는지 구분하지 않음 (보안)

## 테스트 시나리오

### TC-USER-001-01: 유효한 자격증명으로 로그인 성공 (Unit)
- Given: email="test@example.com", password="password123"인 활성 User가 존재한다
- When: POST /api/auth/login에 해당 자격증명으로 요청한다
- Then: HTTP 200, 응답에 accessToken, refreshToken, userInfo(userId, email, role, isActive=true)가 포함된다

### TC-USER-001-02: 존재하지 않는 이메일로 로그인 실패 (Unit)
- Given: email="nonexist@example.com"에 해당하는 User가 없다
- When: POST /api/auth/login에 해당 이메일로 요청한다
- Then: HTTP 401, 에러코드 AUTH001, 메시지 "이메일 또는 비밀번호가 일치하지 않습니다"

### TC-USER-001-03: 비활성화된 사용자 로그인 실패 (Unit)
- Given: email="inactive@example.com"인 User의 isActive=false이다
- When: POST /api/auth/login에 올바른 자격증명으로 요청한다
- Then: HTTP 403, 에러코드 AUTH002, 메시지 "비활성화된 사용자입니다"

### TC-USER-001-04: 잘못된 비밀번호로 로그인 실패 (Unit)
- Given: email="test@example.com"인 활성 User가 존재한다
- When: POST /api/auth/login에 잘못된 비밀번호 "wrongpass1"로 요청한다
- Then: HTTP 401, 에러코드 AUTH001

### TC-USER-001-05: 로그인 성공 시 lastLoginAt 갱신 확인 (Integration)
- Given: email="test@example.com"인 활성 User의 lastLoginAt이 null이다
- When: POST /api/auth/login에 올바른 자격증명으로 요청한다
- Then: DB에서 해당 User의 lastLoginAt이 null이 아닌 현재 시점으로 갱신되어 있다

### TC-USER-001-06: Employee가 있는 사용자 로그인 시 storeId 포함 (Integration)
- Given: User와 연결된 Employee가 storeId="store-123"으로 배정되어 있다
- When: POST /api/auth/login에 올바른 자격증명으로 요청한다
- Then: 발급된 Access Token의 클레임에 storeId="store-123"이 포함된다

### TC-USER-001-07: 로그인 전체 플로우 E2E (E2E)
- Given: 시스템에 email="e2e@example.com", password="securepass1"인 활성 User가 등록되어 있다
- When: POST /api/auth/login에 해당 자격증명으로 요청한다
- Then: HTTP 200, 응답의 accessToken으로 인증이 필요한 API 호출이 성공한다
