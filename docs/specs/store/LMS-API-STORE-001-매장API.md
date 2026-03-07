# LMS-API-STORE-001: 매장 API

## 기본 정보
- type: api_spec
- domain: store
- service: LMS
- base_path: /api/stores

## 관련 Spec
- [LMS-STORE-001-매장관리](LMS-STORE-001-매장관리.md)

## 인증/인가
- JWT Bearer Token 필수
- 생성/수정/삭제: SUPER_ADMIN만
- 전체 조회: SUPER_ADMIN만
- 단건 조회: 인증된 사용자

## 엔드포인트 목록

### POST /api/stores
- 설명: 매장 등록
- 권한: SUPER_ADMIN
- 요청:
  ```json
  {
    "name": "판교점",
    "location": "경기도 성남시 분당구 판교역로 123"
  }
  ```
  - name: 필수, 1~100자
  - location: 필수, 1~200자
- 응답 (201):
  ```json
  {
    "id": "store-uuid",
    "name": "판교점",
    "location": "경기도 성남시 분당구 판교역로 123",
    "createdAt": "2026-03-08T00:00:00Z"
  }
  ```
- 응답 (400): DuplicateStoreNameException

### GET /api/stores
- 설명: 전체 매장 목록 조회
- 권한: SUPER_ADMIN
- 응답 (200):
  ```json
  {
    "stores": [...],
    "totalCount": 3
  }
  ```

### GET /api/stores/{storeId}
- 설명: 매장 상세 조회
- 권한: 인증된 사용자
- 응답 (200): StoreResponse
- 응답 (404): StoreNotFoundException

### PUT /api/stores/{storeId}
- 설명: 매장 정보 수정
- 권한: SUPER_ADMIN
- 요청:
  ```json
  {
    "name": "판교점",
    "location": "경기도 성남시 분당구 판교역로 456"
  }
  ```
- 응답 (200): StoreResponse
- 응답 (404): StoreNotFoundException

### DELETE /api/stores/{storeId}
- 설명: 매장 삭제
- 권한: SUPER_ADMIN
- 응답 (204): No Content
- 응답 (404): StoreNotFoundException

## 공통 규칙
- 에러 응답: `{ "code": "STORE001", "message": "..." }`
- 하위호환: POLICY-NFR-001 하위호환 규칙 적용
