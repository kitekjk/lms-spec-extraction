# LMS-STORE-003 매장삭제

## 기본 정보
- type: use_case
- domain: store
- id: LMS-STORE-003

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 3.2 SUPER_ADMIN 전체 권한, 4 매장 삭제는 SUPER_ADMIN만
- POLICY-NFR-001 (비기능 요구사항) — 2.1 데이터 무결성

## 관련 Spec
- LMS-API-STORE-001 (매장API)

## 관련 모델
- 주 모델: Store — id(StoreId, UUID)
- 참조 모델: Employee — storeId(StoreId?) / WorkSchedule — storeId(StoreId)

## 개요
SUPER_ADMIN 권한의 사용자가 매장을 삭제한다. 매장의 존재 여부를 확인한 후 물리적으로 삭제하며, 삭제 성공 시 HTTP 204 No Content를 응답한다.

## 기본 흐름
1. SUPER_ADMIN 권한의 사용자가 Bearer 토큰과 함께 삭제 요청을 전송한다.
2. 경로 파라미터의 storeId로 Store 존재 여부를 확인한다.
3. Store를 삭제한다 (StoreRepository.delete).
4. HTTP 204 No Content를 응답한다 (본문 없음).

## 대안 흐름
- AF-1: storeId에 해당하는 Store가 없으면 HTTP 404와 STORE001("매장을 찾을 수 없습니다: {storeId}")을 반환한다.
- AF-2: 요청자가 SUPER_ADMIN이 아니면 HTTP 403을 반환한다.
- AF-3: 인증 토큰이 없거나 만료되었으면 HTTP 401을 반환한다.

## 검증 조건
- storeId: 유효한 UUID 형식, DB에 존재하는 Store
- 삭제 후 해당 storeId로 Store 조회 시 결과 없음
- 삭제 성공 시 응답 본문 없음 (HTTP 204)

## 비기능 요구사항
- POLICY-NFR-001 참조
- 매장 삭제 API 응답시간 500ms 이내
- SUPER_ADMIN만 매장 삭제 가능 (@PreAuthorize)
- 매장에 배정된 근로자나 일정이 있는 경우의 처리는 현재 구현에서 별도 검증 없이 삭제 허용 (향후 cascade 정책 검토 필요)

## 테스트 시나리오

### TC-STORE-003-01: 매장 삭제 성공 (Unit)
- Given: storeId="store-1"인 Store가 존재한다
- When: DELETE /api/stores/store-1을 요청한다
- Then: HTTP 204, 응답 본문 없음

### TC-STORE-003-02: 존재하지 않는 매장 삭제 시 실패 (Unit)
- Given: storeId="nonexist"에 해당하는 Store가 없다
- When: DELETE /api/stores/nonexist를 요청한다
- Then: HTTP 404, 에러코드 STORE001

### TC-STORE-003-03: MANAGER 권한으로 매장 삭제 시도 시 실패 (Unit)
- Given: MANAGER 인증 토큰이 유효하다
- When: DELETE /api/stores/store-1을 요청한다
- Then: HTTP 403 (권한 없음)

### TC-STORE-003-04: EMPLOYEE 권한으로 매장 삭제 시도 시 실패 (Unit)
- Given: EMPLOYEE 인증 토큰이 유효하다
- When: DELETE /api/stores/store-1을 요청한다
- Then: HTTP 403 (권한 없음)

### TC-STORE-003-05: 매장 삭제 후 DB에서 레코드 제거 확인 (Integration)
- Given: DB에 storeId="store-int"인 Store가 존재한다
- When: DELETE /api/stores/store-int를 요청한다
- Then: DB에서 해당 storeId로 조회 시 결과가 없다

### TC-STORE-003-06: 매장 삭제 후 조회 시 404 E2E (E2E)
- Given: 시스템에 매장이 등록되어 있다
- When: DELETE /api/stores/{id}로 삭제한 후, GET /api/stores/{id}로 조회한다
- Then: HTTP 404
