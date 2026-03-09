# LMS-STORE-002 매장수정

## 기본 정보
- type: use_case
- domain: store
- id: LMS-STORE-002

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 3.2 SUPER_ADMIN 전체 권한, 4 매장 수정은 SUPER_ADMIN만
- POLICY-NFR-001 (비기능 요구사항) — 1.1~1.4 API 하위호환성, 3.1~3.3 변경 이력 추적

## 관련 Spec
- LMS-API-STORE-001 (매장API)

## 관련 모델
- 주 모델: Store — id(StoreId, UUID), name(StoreName), location(StoreLocation), createdAt(Instant)
- 참조 모델: 없음

## 개요
SUPER_ADMIN 권한의 사용자가 기존 매장의 이름과 위치 정보를 수정한다. Store.update 메서드를 통해 DomainContext와 함께 수정하며, 매장 ID와 생성일시는 변경되지 않는다.

## 기본 흐름
1. SUPER_ADMIN 권한의 사용자가 Bearer 토큰과 함께 수정 정보를 전송한다.
2. 경로 파라미터의 storeId로 Store를 조회한다.
3. name 필드가 빈 문자열이 아닌지 검증한다.
4. location 필드가 빈 문자열이 아닌지 검증한다.
5. Store 정보를 수정한다 (Store.update: name, location 변경).
6. 수정된 Store를 저장한다.
7. 수정된 Store 정보(id, name, location, createdAt)를 응답한다.

## 대안 흐름
- AF-1: storeId에 해당하는 Store가 없으면 HTTP 404와 STORE001("매장을 찾을 수 없습니다: {storeId}")을 반환한다.
- AF-2: name이 빈 문자열이면 HTTP 400과 VALIDATION_ERROR("매장명은 필수입니다")를 반환한다.
- AF-3: location이 빈 문자열이면 HTTP 400과 VALIDATION_ERROR("위치는 필수입니다")를 반환한다.
- AF-4: 요청자가 SUPER_ADMIN이 아니면 HTTP 403을 반환한다.
- AF-5: 인증 토큰이 없거나 만료되었으면 HTTP 401을 반환한다.

## 검증 조건
- storeId: 유효한 UUID 형식, DB에 존재하는 Store
- name 필드: 빈 문자열 불가
- location 필드: 빈 문자열 불가
- 수정 후 Store.id와 Store.createdAt은 변경되지 않음

## 비기능 요구사항
- POLICY-NFR-001 참조
- 매장 수정 API 응답시간 500ms 이내
- SUPER_ADMIN만 매장 수정 가능 (@PreAuthorize)

## 테스트 시나리오

### TC-STORE-002-01: 매장 이름과 위치 수정 성공 (Unit)
- Given: storeId="store-1"인 Store(name="강남점", location="서울시 강남구")가 존재한다
- When: PUT /api/stores/store-1에 name="강남역점", location="서울시 강남구 역삼로 100"으로 요청한다
- Then: HTTP 200, 응답의 name="강남역점", location="서울시 강남구 역삼로 100", id와 createdAt은 변경되지 않는다

### TC-STORE-002-02: 존재하지 않는 매장 수정 시 실패 (Unit)
- Given: storeId="nonexist"에 해당하는 Store가 없다
- When: PUT /api/stores/nonexist에 수정 요청한다
- Then: HTTP 404, 에러코드 STORE001

### TC-STORE-002-03: 매장명 빈 문자열로 수정 시 실패 (Unit)
- Given: storeId="store-2"인 Store가 존재한다
- When: PUT /api/stores/store-2에 name=""으로 요청한다
- Then: HTTP 400, 에러코드 VALIDATION_ERROR

### TC-STORE-002-04: MANAGER 권한으로 매장 수정 시도 시 실패 (Unit)
- Given: MANAGER 인증 토큰이 유효하다
- When: PUT /api/stores/store-1에 수정 요청한다
- Then: HTTP 403 (권한 없음)

### TC-STORE-002-05: 매장 수정 후 DB 반영 확인 (Integration)
- Given: DB에 storeId="store-int"인 Store가 존재한다
- When: PUT /api/stores/store-int에 name="수정된매장", location="수정된위치"로 요청한다
- Then: DB에서 해당 Store의 name="수정된매장", location="수정된위치"로 갱신되어 있다

### TC-STORE-002-06: 매장 수정 후 조회 일치 E2E (E2E)
- Given: 시스템에 매장이 등록되어 있다
- When: PUT /api/stores/{id}로 이름과 위치를 수정한 후, GET /api/stores/{id}로 조회한다
- Then: 수정된 이름과 위치로 조회된다
