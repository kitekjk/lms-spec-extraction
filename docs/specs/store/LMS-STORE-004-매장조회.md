# LMS-STORE-004 매장조회

## 기본 정보
- type: use_case
- domain: store
- id: LMS-STORE-004

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 3.2~3.4 역할별 조회 범위, 4 매장 목록 조회 권한
- POLICY-NFR-001 (비기능 요구사항) — 4.1~4.4 멀티 매장 지원, 5.1 응답시간 500ms 이내

## 관련 Spec
- LMS-API-STORE-001 (매장API)

## 관련 모델
- 주 모델: Store — id(StoreId, UUID), name(StoreName), location(StoreLocation), createdAt(Instant)
- 참조 모델: 없음

## 개요
인증된 사용자가 매장 정보를 조회한다. 단건 상세 조회와 전체 목록 조회를 지원한다. 전체 목록 조회는 SUPER_ADMIN만 가능하며, 상세 조회는 인증된 사용자 모두 가능하다.

## 기본 흐름 — 단건 상세 조회
1. 인증된 사용자가 Bearer 토큰과 함께 GET /api/stores/{storeId}를 요청한다.
2. 경로 파라미터의 storeId로 Store를 조회한다.
3. Store 정보(id, name, location, createdAt)를 응답한다.

## 기본 흐름 — 전체 목록 조회
1. SUPER_ADMIN 권한의 사용자가 Bearer 토큰과 함께 GET /api/stores를 요청한다.
2. 모든 Store를 조회한다.
3. stores 배열과 totalCount를 응답한다.

## 대안 흐름
- AF-1: storeId에 해당하는 Store가 없으면 HTTP 404를 반환한다 (본문 없음).
- AF-2: 전체 목록 조회 시 요청자가 SUPER_ADMIN이 아니면 HTTP 403을 반환한다.
- AF-3: 인증 토큰이 없거나 만료되었으면 HTTP 401을 반환한다.

## 검증 조건
- 단건 조회: storeId에 해당하는 Store가 DB에 존재해야 함
- 전체 목록 조회: SUPER_ADMIN 권한 필수
- totalCount는 응답의 stores 배열 크기와 동일
- 응답의 모든 필드 타입이 정확: id(String/UUID), name(String), location(String), createdAt(ISO 8601 Instant)

## 비기능 요구사항
- POLICY-NFR-001 참조
- 매장 조회 API 응답시간 500ms 이내
- SUPER_ADMIN: 전체 매장 목록 조회 가능
- MANAGER: 소속 매장 상세 조회 가능
- EMPLOYEE: 소속 매장 상세 조회 가능

## 테스트 시나리오

### TC-STORE-004-01: 매장 상세 조회 성공 (Unit)
- Given: storeId="store-1"인 Store(name="강남점", location="서울시 강남구")가 존재한다
- When: GET /api/stores/store-1을 요청한다
- Then: HTTP 200, 응답에 id="store-1", name="강남점", location="서울시 강남구", createdAt이 포함된다

### TC-STORE-004-02: 존재하지 않는 매장 상세 조회 시 실패 (Unit)
- Given: storeId="nonexist"에 해당하는 Store가 없다
- When: GET /api/stores/nonexist를 요청한다
- Then: HTTP 404 (본문 없음)

### TC-STORE-004-03: SUPER_ADMIN이 전체 매장 목록 조회 성공 (Unit)
- Given: 시스템에 Store가 3개 존재한다
- When: GET /api/stores를 SUPER_ADMIN 토큰으로 요청한다
- Then: HTTP 200, stores 배열에 3개 항목, totalCount=3

### TC-STORE-004-04: MANAGER가 전체 매장 목록 조회 시 실패 (Unit)
- Given: MANAGER 인증 토큰이 유효하다
- When: GET /api/stores를 요청한다
- Then: HTTP 403 (권한 없음)

### TC-STORE-004-05: 매장이 없을 때 목록 조회 (Unit)
- Given: 시스템에 Store가 0개 존재한다
- When: GET /api/stores를 SUPER_ADMIN 토큰으로 요청한다
- Then: HTTP 200, stores 배열이 비어있고, totalCount=0

### TC-STORE-004-06: DB 데이터와 API 응답 일치 확인 (Integration)
- Given: DB에 Store 레코드가 저장되어 있다
- When: GET /api/stores/{id}로 조회한다
- Then: DB 레코드의 모든 필드 값과 API 응답 값이 일치한다

### TC-STORE-004-07: 매장 등록 후 목록 조회에 반영 E2E (E2E)
- Given: 시스템에 Store가 2개 존재한다
- When: POST /api/stores로 1개를 추가 등록한 후, GET /api/stores로 조회한다
- Then: stores 배열에 3개 항목, totalCount=3
