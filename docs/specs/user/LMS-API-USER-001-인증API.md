# LMS-API-USER-001 인증API

## 기본 정보
- type: api_spec
- domain: user
- id: LMS-API-USER-001

## 관련 Spec
- LMS-USER-001 (로그인)
- LMS-USER-002 (회원가입)
- LMS-USER-003 (토큰갱신)

## 엔드포인트 목록

### POST /api/auth/login
- 설명: 이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받는다
- 권한: 전체 (비인증)
- Request Body:
  ```json
  {
    "email": "string (필수, 이메일 형식)",
    "password": "string (필수, 최소 8자)"
  }
  ```
- Response 200:
  ```json
  {
    "accessToken": "string (JWT)",
    "refreshToken": "string (JWT)",
    "userInfo": {
      "userId": "string (UUID)",
      "email": "string",
      "role": "string (SUPER_ADMIN | MANAGER | EMPLOYEE)",
      "isActive": "boolean"
    }
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 400 | VALIDATION_ERROR | 이메일 형식 오류, 비밀번호 8자 미만 |
  | 401 | AUTH001 | 이메일 또는 비밀번호 불일치 |
  | 403 | AUTH002 | 비활성화된 사용자 |

---

### POST /api/auth/register
- 설명: 새로운 사용자를 등록한다
- 권한: SUPER_ADMIN
- 인증: Authorization: Bearer {accessToken}
- Request Body:
  ```json
  {
    "email": "string (필수, 이메일 형식)",
    "password": "string (필수, 최소 8자)",
    "role": "string (필수, SUPER_ADMIN | MANAGER | EMPLOYEE)",
    "storeId": "string? (선택, UUID)"
  }
  ```
- Response 201:
  ```json
  {
    "userId": "string (UUID)",
    "email": "string",
    "role": "string (SUPER_ADMIN | MANAGER | EMPLOYEE)",
    "isActive": "boolean (항상 true)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 400 | VALIDATION_ERROR | 이메일 형식 오류, 비밀번호 8자 미만, 역할 빈 문자열 |
  | 400 | REG002 | 유효하지 않은 역할 (SUPER_ADMIN, MANAGER, EMPLOYEE 이외) |
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 403 | - | SUPER_ADMIN 이외 역할의 접근 |
  | 409 | REG001 | 중복된 이메일 |

---

### POST /api/auth/refresh
- 설명: Refresh Token으로 새로운 Access Token을 발급받는다
- 권한: 전체 (비인증)
- Request Body:
  ```json
  {
    "refreshToken": "string (필수, JWT)"
  }
  ```
- Response 200:
  ```json
  {
    "accessToken": "string (JWT)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 400 | VALIDATION_ERROR | refreshToken 빈 문자열 |
  | 401 | TOKEN001 | 유효하지 않은 Refresh Token (만료, 변조) |
  | 401 | TOKEN002 | 토큰의 사용자가 존재하지 않음 |
  | 401 | TOKEN003 | 토큰의 사용자가 비활성 상태 |

---

### POST /api/auth/logout
- 설명: 로그아웃한다 (클라이언트에서 토큰 삭제)
- 권한: 인증된 사용자
- 인증: Authorization: Bearer {accessToken}
- Request Body: 없음
- Response 200:
  ```json
  {
    "message": "로그아웃 되었습니다"
  }
  ```
- 비고: 현재 서버 측 Refresh Token 무효화 미구현. 클라이언트에서 토큰 삭제만 수행.

## 공통 에러 응답 형식
```json
{
  "code": "string (에러코드)",
  "message": "string (에러 메시지)",
  "timestamp": "string (ISO 8601, e.g. 2026-03-09T09:00:00Z)"
}
```

## JWT 토큰 규격
- 서명 알고리즘: HS256
- Access Token 유효시간: 3,600,000ms (1시간)
- Refresh Token 유효시간: 604,800,000ms (7일)
- Access Token 클레임: employeeId(sub), role, storeId(nullable)
- 전달 방식: Authorization: Bearer {accessToken}
