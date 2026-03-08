# LMS-API-USER-001: 인증API

## 기본 정보
- type: api_spec
- domain: user

## 관련 Spec
- LMS-USER-001 (로그인)
- LMS-USER-002 (회원가입)
- LMS-USER-003 (토큰갱신)

## 엔드포인트 목록

### POST /api/auth/login
- 설명: 이메일과 비밀번호로 로그인하여 액세스 토큰과 리프레시 토큰을 발급받는다
- 권한: 인증 불필요 (Public)
- 관련 Use Case: LMS-USER-001
- Request:
  ```json
  {
    "email": "string (필수, 이메일 형식)",
    "password": "string (필수, 최소 8자)"
  }
  ```
- Response (200):
  ```json
  {
    "accessToken": "string",
    "refreshToken": "string",
    "userInfo": {
      "userId": "string",
      "email": "string",
      "role": "string",
      "isActive": "boolean"
    }
  }
  ```
- 에러 응답:
  - 400: 유효성 검증 실패 (VALIDATION_ERROR)
  - 401: 인증 실패 - 이메일 또는 비밀번호 불일치 (AUTH001)
  - 403: 비활성화된 사용자 (AUTH002)

### POST /api/auth/register
- 설명: 새로운 사용자를 등록한다 (SUPER_ADMIN 전용)
- 권한: SUPER_ADMIN
- 관련 Use Case: LMS-USER-002
- Request:
  ```json
  {
    "email": "string (필수, 이메일 형식)",
    "password": "string (필수, 최소 8자)",
    "role": "string (필수, SUPER_ADMIN | MANAGER | EMPLOYEE)",
    "storeId": "string (선택)"
  }
  ```
- Response (201):
  ```json
  {
    "userId": "string",
    "email": "string",
    "role": "string",
    "isActive": "boolean"
  }
  ```
- 에러 응답:
  - 400: 유효성 검증 실패 (VALIDATION_ERROR)
  - 401: 인증 실패
  - 403: 권한 없음 (SUPER_ADMIN 권한 필요)
  - 409: 중복된 이메일 (REG001)

### POST /api/auth/refresh
- 설명: 리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받는다
- 권한: 인증 불필요 (Public)
- 관련 Use Case: LMS-USER-003
- Request:
  ```json
  {
    "refreshToken": "string (필수)"
  }
  ```
- Response (200):
  ```json
  {
    "accessToken": "string"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청
  - 401: 유효하지 않은 리프레시 토큰 (TOKEN001)

### POST /api/auth/logout
- 설명: 로그아웃 처리 (클라이언트에서 토큰 삭제 필요)
- 권한: 인증 불필요 (Public)
- 관련 Use Case: 없음 (클라이언트 측 처리)
- Request: 없음
- Response (200):
  ```json
  {
    "message": "로그아웃 되었습니다"
  }
  ```
- 에러 응답: 없음
- 비고: 현재 서버 측 Refresh Token 무효화 미구현 (TODO)
