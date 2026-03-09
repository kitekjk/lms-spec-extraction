# LMS-STORE-001 매장등록

## 기본 정보
- type: use_case
- domain: store
- id: LMS-STORE-001

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 3.2 SUPER_ADMIN 전체 권한, 4 매장 등록은 SUPER_ADMIN만
- POLICY-NFR-001 (비기능 요구사항) — 5.1 응답시간 500ms 이내, 1.1~1.4 API 하위호환성

## 관련 Spec
- LMS-API-STORE-001 (매장API)

## 관련 모델
- 주 모델: Store — id(StoreId, UUID), name(StoreName), location(StoreLocation), createdAt(Instant)
- 참조 모델: 없음

## 개요
SUPER_ADMIN 권한의 사용자가 새로운 매장을 등록한다. 매장명은 시스템 전체에서 고유해야 하며, 매장명과 위치 정보를 필수로 입력해야 한다. 등록된 매장에 이후 근로자를 배정하고 일정을 관리할 수 있다.

## 기본 흐름
1. SUPER_ADMIN 권한의 사용자가 Bearer 토큰과 함께 매장 정보를 전송한다.
2. name 필드가 빈 문자열이 아닌지 검증한다.
3. location 필드가 빈 문자열이 아닌지 검증한다.
4. 매장명 중복 여부를 확인한다 (StoreRepository.findByName).
5. Store 엔티티를 생성한다 (Store.create, id는 UUID v4 자동 생성).
6. Store를 저장한다.
7. 생성된 Store 정보(id, name, location, createdAt)를 응답한다.

## 대안 흐름
- AF-1: name이 빈 문자열이면 HTTP 400과 VALIDATION_ERROR("매장명은 필수입니다")를 반환한다.
- AF-2: location이 빈 문자열이면 HTTP 400과 VALIDATION_ERROR("위치는 필수입니다")를 반환한다.
- AF-3: 동일한 매장명이 이미 존재하면 HTTP 409와 STORE002("이미 존재하는 매장명입니다: {name}")를 반환한다.
- AF-4: 요청자가 SUPER_ADMIN이 아니면 HTTP 403을 반환한다.
- AF-5: 인증 토큰이 없거나 만료되었으면 HTTP 401을 반환한다.

## 검증 조건
- name 필드: 빈 문자열 불가, 시스템 전체에서 고유
- location 필드: 빈 문자열 불가
- 생성된 Store의 id는 UUID v4 형식
- 생성된 Store의 createdAt은 생성 시점의 Instant

## 비기능 요구사항
- POLICY-NFR-001 참조
- 매장 등록 API 응답시간 500ms 이내
- SUPER_ADMIN만 매장 등록 가능 (@PreAuthorize)

## 테스트 시나리오

### TC-STORE-001-01: 매장 등록 성공 (Unit)
- Given: name="강남점"인 매장이 존재하지 않는다
- When: POST /api/stores에 name="강남점", location="서울시 강남구 역삼동 123-45"로 요청한다
- Then: HTTP 201, 응답에 id(UUID), name="강남점", location="서울시 강남구 역삼동 123-45", createdAt이 포함된다

### TC-STORE-001-02: 중복 매장명으로 등록 시 실패 (Unit)
- Given: name="홍대점"인 매장이 이미 존재한다
- When: POST /api/stores에 name="홍대점"으로 요청한다
- Then: HTTP 409, 에러코드 STORE002, 메시지에 "이미 존재하는 매장명입니다" 포함

### TC-STORE-001-03: 매장명 빈 문자열로 등록 시 실패 (Unit)
- Given: SUPER_ADMIN 인증 토큰이 유효하다
- When: POST /api/stores에 name=""으로 요청한다
- Then: HTTP 400, 에러코드 VALIDATION_ERROR, 메시지에 "매장명은 필수입니다" 포함

### TC-STORE-001-04: MANAGER 권한으로 매장 등록 시도 시 실패 (Unit)
- Given: MANAGER 인증 토큰이 유효하다
- When: POST /api/stores에 매장 정보를 요청한다
- Then: HTTP 403 (권한 없음)

### TC-STORE-001-05: 매장 등록 후 DB 저장 상태 확인 (Integration)
- Given: name="통합테스트점"인 매장이 존재하지 않는다
- When: POST /api/stores에 해당 매장명으로 등록 요청한다
- Then: DB에서 Store 조회 시 name="통합테스트점", location이 입력값과 일치한다

### TC-STORE-001-06: 매장 등록 후 상세 조회 E2E (E2E)
- Given: 시스템에 name="E2E테스트점"인 매장이 없다
- When: POST /api/stores로 매장을 등록한 후, GET /api/stores/{id}로 조회한다
- Then: 등록 시 응답과 동일한 정보가 조회된다
