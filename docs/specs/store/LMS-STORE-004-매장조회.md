# LMS-STORE-004: 매장조회

## 기본 정보
- type: use_case
- domain: store

## 관련 Spec
- LMS-API-STORE-001 (매장API)

## 개요
인증된 사용자가 매장 목록을 조회하거나 특정 매장의 상세 정보를 조회한다.

## 관련 모델
- 주 모델: Store (Aggregate Root)

## 선행 조건
- 인증된 사용자여야 한다
- 전체 목록 조회는 SUPER_ADMIN 권한이 필요하다

## 기본 흐름 (전체 목록 조회)
1. SUPER_ADMIN이 전체 매장 목록 조회를 요청한다
2. 시스템은 모든 매장을 조회한다
3. 시스템은 매장 목록과 총 건수를 반환한다

## 대안 흐름
- 상세 조회 (storeId 지정): 특정 매장의 상세 정보를 조회한다 (인증된 사용자 모두 가능)

## 예외 흐름
- 상세 조회 시 매장을 찾을 수 없는 경우: 404 Not Found 응답

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- 인증된 사용자여야 한다
- 전체 목록 조회는 SUPER_ADMIN 권한이 필요하다
- 상세 조회 시 해당 매장이 존재해야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-STORE-004-01: SUPER_ADMIN 전체 매장 목록 조회 (Integration)
- Given: 3개의 매장이 등록되어 있고, SUPER_ADMIN이 인증된 상태
- When: 전체 매장 목록 조회를 요청
- Then: 3개의 매장 목록과 총 건수 3이 반환됨

### TC-STORE-004-02: 매장 상세 조회 (Integration)
- Given: 특정 storeId에 해당하는 매장이 존재하고, 인증된 사용자
- When: 해당 storeId로 상세 조회를 요청
- Then: 매장의 상세 정보(이름, 위치 등)가 반환됨

### TC-STORE-004-03: 존재하지 않는 매장 상세 조회 (E2E)
- Given: 존재하지 않는 storeId
- When: 해당 storeId로 상세 조회를 요청
- Then: 404 Not Found 응답

### TC-STORE-004-04: EMPLOYEE 권한으로 매장 상세 조회 (E2E)
- Given: EMPLOYEE 역할의 사용자가 인증된 상태이고, 매장이 존재
- When: 해당 매장의 상세 조회를 요청
- Then: 200 OK 응답과 함께 매장 상세 정보가 반환됨 (인증된 사용자 모두 가능)

### TC-STORE-004-05: 매장이 없을 때 전체 목록 조회 (Integration)
- Given: 등록된 매장이 없고, SUPER_ADMIN이 인증된 상태
- When: 전체 매장 목록 조회를 요청
- Then: 빈 목록과 총 건수 0이 반환됨
