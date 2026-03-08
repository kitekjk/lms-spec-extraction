# LMS-STORE-003: 매장삭제

## 기본 정보
- type: use_case
- domain: store

## 관련 Spec
- LMS-API-STORE-001 (매장API)
- LMS-STORE-001 (매장등록)

## 개요
SUPER_ADMIN이 매장을 삭제한다.

## 관련 모델
- 주 모델: Store (Aggregate Root)

## 선행 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 삭제 대상 매장이 존재해야 한다

## 기본 흐름
1. SUPER_ADMIN이 매장 ID를 지정하여 삭제를 요청한다
2. 시스템은 매장을 조회한다
3. 시스템은 매장을 삭제한다
4. 시스템은 204 No Content를 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 매장을 찾을 수 없는 경우: StoreNotFoundException (STORE001) 발생

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 삭제 대상 매장이 존재해야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-STORE-003-01: 정상 매장 삭제 (Integration)
- Given: storeId에 해당하는 매장이 존재
- When: 해당 매장의 삭제를 요청
- Then: 매장이 삭제되고, 204 No Content 응답

### TC-STORE-003-02: 존재하지 않는 매장 삭제 시도 (Unit)
- Given: 존재하지 않는 storeId
- When: 해당 매장의 삭제를 요청
- Then: StoreNotFoundException (STORE001) 발생

### TC-STORE-003-03: MANAGER 권한으로 매장 삭제 시도 (E2E)
- Given: MANAGER 역할의 사용자가 인증된 상태
- When: 매장 삭제를 요청
- Then: 403 Forbidden 응답

### TC-STORE-003-04: 소속 근로자가 있는 매장 삭제 시 영향 확인 (Integration)
- Given: storeId에 소속된 근로자가 3명 존재하는 매장
- When: 해당 매장의 삭제를 요청
- Then: 매장이 삭제되고, 소속 근로자의 데이터 무결성이 확인됨
