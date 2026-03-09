# LMS-USER-003 토큰갱신

## 기본 정보
- type: use_case
- domain: user
- id: LMS-USER-003

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 1.1~1.5 인증 방식, 5.1~5.4 토큰 검증 규칙
- POLICY-NFR-001 (비기능 요구사항) — 5.1 응답시간 500ms 이내

## 관련 Spec
- LMS-API-USER-001 (인증API)

## 관련 모델
- 주 모델: User — id(UserId, UUID), role(Role), isActive(Boolean)
- 참조 모델: Employee — userId(UserId), storeId(StoreId?) / TokenProvider — validateToken, extractEmployeeId, generateAccessToken

## 개요
사용자가 Refresh Token을 전송하여 새로운 Access Token을 발급받는다. Refresh Token의 유효성을 검증하고, 토큰에 포함된 사용자 ID로 사용자 존재 여부와 활성 상태를 확인한 뒤, Employee의 storeId를 포함한 새 Access Token을 생성하여 응답한다.

## 기본 흐름
1. 사용자가 Refresh Token을 전송한다.
2. refreshToken 필드가 빈 문자열이 아닌지 검증한다.
3. Refresh Token의 유효성을 검증한다 (TokenProvider.validateToken).
4. Refresh Token에서 사용자 ID를 추출한다 (TokenProvider.extractEmployeeId).
5. 사용자 ID로 User를 조회한다.
6. User의 isActive가 true인지 확인한다.
7. Employee를 userId로 조회하여 storeId를 가져온다 (없으면 null).
8. 새로운 Access Token을 생성한다 (employeeId, role, storeId 포함).
9. 새 accessToken을 응답한다.

## 대안 흐름
- AF-1: refreshToken이 빈 문자열이면 HTTP 400과 VALIDATION_ERROR를 반환한다.
- AF-2: Refresh Token이 유효하지 않으면(만료, 변조) HTTP 401과 TOKEN001("유효하지 않은 Refresh Token입니다")을 반환한다.
- AF-3: 토큰의 사용자 ID에 해당하는 User가 없으면 HTTP 401과 TOKEN002("사용자를 찾을 수 없습니다")를 반환한다.
- AF-4: User의 isActive가 false이면 HTTP 401과 TOKEN003("비활성화된 사용자입니다")을 반환한다.

## 검증 조건
- refreshToken 필드: 빈 문자열 불가
- Refresh Token은 HS256으로 서명된 유효한 JWT
- Refresh Token이 만료되지 않았음 (유효시간 604,800,000ms 이내)
- 토큰에서 추출한 사용자 ID에 해당하는 User가 DB에 존재
- 해당 User의 isActive == true
- 응답의 accessToken은 유효한 JWT (유효시간 3,600,000ms)

## 비기능 요구사항
- POLICY-NFR-001 참조
- 토큰 갱신 API 응답시간 500ms 이내
- 읽기 전용 트랜잭션 (readOnly = true)
- Refresh Token은 Stateless 검증 (DB 조회 없이 서명 검증)

## 테스트 시나리오

### TC-USER-003-01: 유효한 Refresh Token으로 Access Token 갱신 성공 (Unit)
- Given: 유효한 Refresh Token이 발급되어 있고, 해당 User가 활성 상태이다
- When: POST /api/auth/refresh에 해당 refreshToken으로 요청한다
- Then: HTTP 200, 응답에 새로운 accessToken이 포함된다

### TC-USER-003-02: 만료된 Refresh Token으로 갱신 실패 (Unit)
- Given: 만료된 Refresh Token이 존재한다
- When: POST /api/auth/refresh에 만료된 refreshToken으로 요청한다
- Then: HTTP 401, 에러코드 TOKEN001, 메시지 "유효하지 않은 Refresh Token입니다"

### TC-USER-003-03: 비활성화된 사용자의 Refresh Token으로 갱신 실패 (Unit)
- Given: 유효한 Refresh Token이 존재하지만, 해당 User의 isActive=false이다
- When: POST /api/auth/refresh에 해당 refreshToken으로 요청한다
- Then: HTTP 401, 에러코드 TOKEN003, 메시지 "비활성화된 사용자입니다"

### TC-USER-003-04: 삭제된 사용자의 Refresh Token으로 갱신 실패 (Unit)
- Given: 유효한 Refresh Token이 존재하지만, 해당 User가 DB에서 삭제되었다
- When: POST /api/auth/refresh에 해당 refreshToken으로 요청한다
- Then: HTTP 401, 에러코드 TOKEN002, 메시지 "사용자를 찾을 수 없습니다"

### TC-USER-003-05: 갱신된 Access Token으로 인증 API 호출 성공 (Integration)
- Given: Refresh Token으로 새 Access Token을 발급받았다
- When: 새 Access Token으로 인증이 필요한 API(GET /api/stores)를 호출한다
- Then: HTTP 200으로 정상 응답한다

### TC-USER-003-06: 토큰 갱신 전체 플로우 E2E (E2E)
- Given: 사용자가 로그인하여 accessToken과 refreshToken을 발급받았다
- When: refreshToken으로 POST /api/auth/refresh를 호출한다
- Then: 새로운 accessToken을 발급받고, 이전 accessToken과 다른 값이다
