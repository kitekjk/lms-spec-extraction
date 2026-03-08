# LMS-USER-001: 로그인

## 기본 정보
- type: use_case
- domain: user

## 관련 Spec
- LMS-API-USER-001 (인증API)
- LMS-USER-002 (회원가입)

## 개요
사용자가 이메일과 비밀번호로 로그인하여 Access Token과 Refresh Token을 발급받는다.

## 관련 모델
- 주 모델: User (Aggregate Root)
- 참조 모델: Employee (storeId 조회), TokenProvider (JWT 발급)

## 선행 조건
- 사용자가 회원가입을 통해 등록되어 있어야 한다
- 사용자 계정이 활성화(isActive=true) 상태여야 한다

## 기본 흐름
1. 사용자가 이메일과 비밀번호를 입력하여 로그인을 요청한다
2. 시스템은 이메일로 사용자를 조회한다
3. 시스템은 입력된 비밀번호와 저장된 암호화 비밀번호를 비교한다
4. 시스템은 사용자의 활성화 상태를 확인한다
5. 시스템은 사용자의 lastLoginAt을 현재 시간으로 업데이트한다
6. 시스템은 Employee 정보를 조회하여 storeId를 확인한다
7. 시스템은 Access Token과 Refresh Token을 생성한다
8. 시스템은 토큰과 사용자 정보를 응답으로 반환한다

## 대안 흐름
- Employee 정보가 없는 경우: storeId 없이 토큰을 생성한다

## 예외 흐름
- 이메일로 사용자를 찾을 수 없는 경우: AuthenticationFailedException (AUTH001) 발생
- 비밀번호가 일치하지 않는 경우: AuthenticationFailedException (AUTH001) 발생
- 사용자가 비활성화 상태인 경우: InactiveUserException (AUTH002) 발생

## 관련 정책
- POLICY-NFR-001 참조 (API 하위호환 유지)

## 검증 조건
- 이메일로 사용자가 존재해야 한다
- 입력된 비밀번호와 저장된 암호화 비밀번호가 일치해야 한다
- 사용자가 활성화(isActive=true) 상태여야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-USER-001-01: 정상 로그인 (Unit)
- Given: 활성 상태의 사용자가 이메일 "user@test.com", 비밀번호 "password123"으로 등록되어 있고, Employee 정보에 storeId가 존재함
- When: 올바른 이메일과 비밀번호로 로그인을 요청
- Then: Access Token과 Refresh Token이 발급되고, 응답에 사용자 정보(employeeId, role, storeId)가 포함됨

### TC-USER-001-02: Employee 정보 없는 사용자 로그인 (Unit)
- Given: 활성 상태의 사용자가 존재하지만 Employee 정보가 등록되지 않음
- When: 올바른 이메일과 비밀번호로 로그인을 요청
- Then: storeId 없이 Access Token과 Refresh Token이 발급됨

### TC-USER-001-03: 잘못된 비밀번호로 로그인 시도 (Unit)
- Given: 등록된 사용자가 존재
- When: 올바른 이메일과 틀린 비밀번호로 로그인을 요청
- Then: AuthenticationFailedException (AUTH001) 발생 - "이메일 또는 비밀번호가 일치하지 않습니다."

### TC-USER-001-04: 존재하지 않는 이메일로 로그인 시도 (Unit)
- Given: 해당 이메일로 등록된 사용자가 없음
- When: 미등록 이메일로 로그인을 요청
- Then: AuthenticationFailedException (AUTH001) 발생

### TC-USER-001-05: 비활성화된 사용자 로그인 시도 (Unit)
- Given: 사용자가 존재하지만 isActive=false 상태
- When: 올바른 이메일과 비밀번호로 로그인을 요청
- Then: InactiveUserException (AUTH002) 발생 - "비활성화된 사용자입니다."

### TC-USER-001-06: 로그인 시 lastLoginAt 업데이트 확인 (Integration)
- Given: 활성 상태의 사용자가 존재하고 lastLoginAt이 null
- When: 정상 로그인을 수행
- Then: lastLoginAt이 현재 시간으로 업데이트됨

### TC-USER-001-07: Access Token 클레임 검증 (Unit)
- Given: MANAGER 역할, storeId="store-1"인 사용자가 정상 로그인
- When: 발급된 Access Token의 클레임을 파싱
- Then: sub=employeeId, role=MANAGER, storeId="store-1"이 포함되고, 만료시간이 1시간(3,600,000ms) 후로 설정됨

### TC-USER-001-08: 로그인 API 응답 형식 검증 (E2E)
- Given: 활성 상태의 사용자가 존재
- When: POST /api/auth/login 으로 올바른 자격 증명을 전송
- Then: 200 OK 응답과 함께 accessToken, refreshToken, 사용자 정보가 JSON 형식으로 반환됨
