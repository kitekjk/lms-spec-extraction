# LMS-API-STORE-001 매장API

## 기본 정보
- type: api_spec
- domain: store
- id: LMS-API-STORE-001

## 관련 Spec
- LMS-STORE-001 (매장등록)
- LMS-STORE-002 (매장수정)
- LMS-STORE-003 (매장삭제)
- LMS-STORE-004 (매장조회)

## 엔드포인트 목록

### POST /api/stores
- 설명: 새로운 매장을 등록한다
- 권한: SUPER_ADMIN
- 인증: Authorization: Bearer {accessToken}
- Request Body:
  ```json
  {
    "name": "string (필수)",
    "location": "string (필수)"
  }
  ```
- Response 201:
  ```json
  {
    "id": "string (UUID)",
    "name": "string",
    "location": "string",
    "createdAt": "string (ISO 8601 Instant)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 400 | VALIDATION_ERROR | name 또는 location 빈 문자열 |
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 403 | - | SUPER_ADMIN 이외 역할의 접근 |
  | 409 | STORE002 | 중복된 매장명 |

---

### GET /api/stores
- 설명: 전체 매장 목록을 조회한다
- 권한: SUPER_ADMIN
- 인증: Authorization: Bearer {accessToken}
- Query Parameters: 없음
- Response 200:
  ```json
  {
    "stores": [
      {
        "id": "string (UUID)",
        "name": "string",
        "location": "string",
        "createdAt": "string (ISO 8601 Instant)"
      }
    ],
    "totalCount": "number (int)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 403 | - | SUPER_ADMIN 이외 역할의 접근 |

---

### GET /api/stores/{storeId}
- 설명: 특정 매장의 상세 정보를 조회한다
- 권한: 인증된 사용자 전체 (SUPER_ADMIN, MANAGER, EMPLOYEE)
- 인증: Authorization: Bearer {accessToken}
- Path Parameters:
  | 파라미터 | 타입 | 설명 |
  |---------|------|------|
  | storeId | string (UUID) | 매장 ID |
- Response 200:
  ```json
  {
    "id": "string (UUID)",
    "name": "string",
    "location": "string",
    "createdAt": "string (ISO 8601 Instant)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 404 | - | 매장을 찾을 수 없음 (본문 없음) |

---

### PUT /api/stores/{storeId}
- 설명: 매장 정보를 수정한다
- 권한: SUPER_ADMIN
- 인증: Authorization: Bearer {accessToken}
- Path Parameters:
  | 파라미터 | 타입 | 설명 |
  |---------|------|------|
  | storeId | string (UUID) | 매장 ID |
- Request Body:
  ```json
  {
    "name": "string (필수)",
    "location": "string (필수)"
  }
  ```
- Response 200:
  ```json
  {
    "id": "string (UUID)",
    "name": "string",
    "location": "string",
    "createdAt": "string (ISO 8601 Instant)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 400 | VALIDATION_ERROR | name 또는 location 빈 문자열 |
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 403 | - | SUPER_ADMIN 이외 역할의 접근 |
  | 404 | STORE001 | 매장을 찾을 수 없음 |

---

### DELETE /api/stores/{storeId}
- 설명: 매장을 삭제한다 (물리적 삭제)
- 권한: SUPER_ADMIN
- 인증: Authorization: Bearer {accessToken}
- Path Parameters:
  | 파라미터 | 타입 | 설명 |
  |---------|------|------|
  | storeId | string (UUID) | 매장 ID |
- Request Body: 없음
- Response 204: 본문 없음
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 403 | - | SUPER_ADMIN 이외 역할의 접근 |
  | 404 | STORE001 | 매장을 찾을 수 없음 |

## 공통 에러 응답 형식
```json
{
  "code": "string (에러코드)",
  "message": "string (에러 메시지)",
  "timestamp": "string (ISO 8601, e.g. 2026-03-09T09:00:00Z)"
}
```

## Store 모델 필드 상세
| 필드 | JSON 키 | 타입 | 설명 |
|------|---------|------|------|
| id | id | string (UUID) | 매장 고유 식별자 |
| name | name | string | 매장명 (시스템 전체 고유) |
| location | location | string | 매장 위치 (주소) |
| createdAt | createdAt | string (ISO 8601 Instant) | 생성 시점 |
