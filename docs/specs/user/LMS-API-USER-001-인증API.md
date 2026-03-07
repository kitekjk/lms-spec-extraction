# LMS-API-USER-001: 인증 API

## 기본 정보
- type: api_spec
- domain: user
- service: LMS
- base_path: /api/auth

## 관련 Spec
- [LMS-USER-001-로그인](LMS-USER-001-로그인.md)
- [LMS-USER-002-회원가입](LMS-USER-002-회원가입.md)

## 인증/인가
- 로그인, 토큰 갱신: 인증 불필요 (공개 엔드포인트)
- 회원가입: JWT Bearer Token, SUPER_ADMIN만

## 엔드포인트 목록

### POST /api/auth/login
- 설명: 이메일/비밀번호로 로그인하여 JWT 토큰 발급
- 권한: 없음 (공개)
- 요청:
  ```json
  {
    "email": "admin@lms.com",
    "password": "password123"
  }
  ```
- 응답 (200):
  ```json
  {
    "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
    "refreshToken": "...",
    "tokenType": "Bearer"
  }
  ```
- 응답 (401): AuthenticationFailedException - 이메일 또는 비밀번호 불일치
- 응답 (403): InactiveUserException - 비활성 사용자

### POST /api/auth/register
- 설명: 새 사용자 계정 등록
- 권한: SUPER_ADMIN
- 요청:
  ```json
  {
    "email": "newuser@lms.com",
    "password": "password123",
    "role": "MANAGER"
  }
  ```
  - email: 필수, 이메일 형식
  - password: 필수, 비어있을 수 없음
  - role: 필수, MANAGER 또는 EMPLOYEE (SUPER_ADMIN 불가)
- 응답 (201):
  ```json
  {
    "id": "uuid",
    "email": "newuser@lms.com",
    "role": "MANAGER",
    "isActive": true,
    "createdAt": "2026-03-08T00:00:00Z"
  }
  ```
- 응답 (400): DuplicateEmailException - 이메일 중복
- 응답 (403): 권한 없음

### POST /api/auth/refresh
- 설명: Refresh Token으로 새 Access Token 발급
- 권한: 없음 (공개)
- 요청:
  ```json
  {
    "refreshToken": "..."
  }
  ```
- 응답 (200):
  ```json
  {
    "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
    "refreshToken": "...",
    "tokenType": "Bearer"
  }
  ```
- 응답 (401): 유효하지 않은 Refresh Token

## 공통 규칙
- 에러 응답: `{ "code": "AUTH001", "message": "이메일 또는 비밀번호가 일치하지 않습니다." }`
- 하위호환: POLICY-NFR-001 하위호환 규칙 적용
