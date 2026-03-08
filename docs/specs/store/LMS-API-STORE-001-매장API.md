# LMS-API-STORE-001: 매장API

## 기본 정보
- type: api_spec
- domain: store

## 관련 Spec
- LMS-STORE-001 (매장등록)
- LMS-STORE-002 (매장수정)
- LMS-STORE-003 (매장삭제)
- LMS-STORE-004 (매장조회)

## 엔드포인트 목록

### POST /api/stores
- 설명: 새로운 매장을 생성한다
- 권한: SUPER_ADMIN
- 관련 Use Case: LMS-STORE-001
- Request:
  ```json
  {
    "name": "string (필수)",
    "location": "string (필수)"
  }
  ```
- Response (201):
  ```json
  {
    "id": "string",
    "name": "string",
    "location": "string",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음

### GET /api/stores
- 설명: 전체 매장 목록을 조회한다
- 권한: SUPER_ADMIN
- 관련 Use Case: LMS-STORE-004
- Response (200):
  ```json
  {
    "stores": [
      {
        "id": "string",
        "name": "string",
        "location": "string",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음

### GET /api/stores/{storeId}
- 설명: 특정 매장의 상세 정보를 조회한다
- 권한: 인증된 사용자 모두
- 관련 Use Case: LMS-STORE-004
- Path Parameters:
  - storeId (필수): 매장 ID
- Response (200):
  ```json
  {
    "id": "string",
    "name": "string",
    "location": "string",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 404: 매장을 찾을 수 없음

### PUT /api/stores/{storeId}
- 설명: 매장 정보를 수정한다
- 권한: SUPER_ADMIN
- 관련 Use Case: LMS-STORE-002
- Path Parameters:
  - storeId (필수): 매장 ID
- Request:
  ```json
  {
    "name": "string (필수)",
    "location": "string (필수)"
  }
  ```
- Response (200):
  ```json
  {
    "id": "string",
    "name": "string",
    "location": "string",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 매장을 찾을 수 없음

### DELETE /api/stores/{storeId}
- 설명: 매장을 삭제한다
- 권한: SUPER_ADMIN
- 관련 Use Case: LMS-STORE-003
- Path Parameters:
  - storeId (필수): 매장 ID
- Response (204): No Content
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 매장을 찾을 수 없음
