# LMS-USER-003: 토큰갱신

## 기본 정보
- type: use_case
- domain: user

## 관련 Spec
- LMS-API-USER-001 (인증API)
- LMS-USER-001 (로그인)

## 개요
유효한 Refresh Token을 사용하여 새로운 Access Token을 발급받는다.

## 관련 모델
- 주 모델: User (Aggregate Root)
- 참조 모델: TokenProvider, Employee (storeId 조회)

## 선행 조건
- 유효한 Refresh Token이 존재해야 한다
- Refresh Token에 해당하는 사용자가 존재하고 활성화 상태여야 한다

## 기본 흐름
1. 사용자가 Refresh Token을 전송하여 토큰 갱신을 요청한다
2. 시스템은 Refresh Token의 유효성을 검증한다
3. 시스템은 Refresh Token에서 사용자 ID를 추출한다
4. 시스템은 사용자를 조회하여 존재 여부와 활성화 상태를 확인한다
5. 시스템은 Employee 정보를 조회하여 storeId를 확인한다
6. 시스템은 새로운 Access Token을 생성한다
7. 시스템은 새로운 Access Token을 응답으로 반환한다

## 대안 흐름
- Employee 정보가 없는 경우: storeId 없이 Access Token을 생성한다

## 예외 흐름
- Refresh Token이 유효하지 않은 경우: InvalidTokenException (TOKEN001) 발생
- 사용자를 찾을 수 없는 경우: UserNotFoundException (TOKEN002) 발생
- 사용자가 비활성화 상태인 경우: TokenUserInactiveException (TOKEN003) 발생

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- Refresh Token이 유효해야 한다 (만료되지 않고 변조되지 않아야 한다)
- Refresh Token에 해당하는 사용자가 존재해야 한다
- 사용자가 활성화(isActive=true) 상태여야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-USER-003-01: 정상 토큰 갱신 (Unit)
- Given: 유효한 Refresh Token이 존재하고, 해당 사용자가 활성 상태이며 Employee 정보에 storeId가 있음
- When: Refresh Token으로 토큰 갱신을 요청
- Then: 새로운 Access Token이 발급되고, sub/role/storeId 클레임이 올바르게 포함됨

### TC-USER-003-02: Employee 정보 없는 사용자의 토큰 갱신 (Unit)
- Given: 유효한 Refresh Token이 존재하고, 해당 사용자가 활성 상태이지만 Employee 정보가 없음
- When: Refresh Token으로 토큰 갱신을 요청
- Then: storeId 없이 새로운 Access Token이 발급됨

### TC-USER-003-03: 만료된 Refresh Token으로 갱신 시도 (Unit)
- Given: 만료된 Refresh Token (7일 경과)
- When: 해당 Refresh Token으로 토큰 갱신을 요청
- Then: InvalidTokenException (TOKEN001) 발생 - "유효하지 않은 Refresh Token입니다."

### TC-USER-003-04: 변조된 Refresh Token으로 갱신 시도 (Unit)
- Given: 서명이 변조된 Refresh Token
- When: 해당 Refresh Token으로 토큰 갱신을 요청
- Then: InvalidTokenException (TOKEN001) 발생

### TC-USER-003-05: 삭제된 사용자의 Refresh Token으로 갱신 시도 (Integration)
- Given: 유효한 Refresh Token이 존재하지만, 해당 사용자가 시스템에서 삭제됨
- When: Refresh Token으로 토큰 갱신을 요청
- Then: UserNotFoundException (TOKEN002) 발생 - "사용자를 찾을 수 없습니다."

### TC-USER-003-06: 비활성화된 사용자의 Refresh Token으로 갱신 시도 (Integration)
- Given: 유효한 Refresh Token이 존재하지만, 해당 사용자가 비활성화(isActive=false) 상태
- When: Refresh Token으로 토큰 갱신을 요청
- Then: TokenUserInactiveException (TOKEN003) 발생 - "비활성화된 사용자입니다."

### TC-USER-003-07: 토큰 갱신 API 엔드포인트 인증 불필요 확인 (E2E)
- Given: Authorization 헤더 없이 요청
- When: POST /api/auth/refresh 로 유효한 Refresh Token을 전송
- Then: 200 OK 응답과 함께 새로운 Access Token이 반환됨 (permitAll 경로)
