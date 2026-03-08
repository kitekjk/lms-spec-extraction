# LMS-STORE-002: 매장수정

## 기본 정보
- type: use_case
- domain: store

## 관련 Spec
- LMS-API-STORE-001 (매장API)
- LMS-STORE-001 (매장등록)

## 개요
SUPER_ADMIN이 매장의 이름과 위치 정보를 수정한다.

## 관련 모델
- 주 모델: Store (Aggregate Root)
- 참조 모델: StoreName, StoreLocation

## 선행 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 수정 대상 매장이 존재해야 한다

## 기본 흐름
1. SUPER_ADMIN이 매장 ID와 수정할 정보(매장명, 위치)를 입력하여 수정을 요청한다
2. 시스템은 매장을 조회한다
3. 시스템은 매장 정보를 수정한다 (name, location)
4. 시스템은 수정된 매장을 저장하고 결과를 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 매장을 찾을 수 없는 경우: StoreNotFoundException (STORE001) 발생
- 매장명이 비어있는 경우: 유효성 검증 실패 (VALIDATION_ERROR)
- 위치가 비어있는 경우: 유효성 검증 실패 (VALIDATION_ERROR)

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 수정 대상 매장이 존재해야 한다
- 매장명이 비어있지 않아야 한다
- 위치가 비어있지 않아야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-STORE-002-01: 정상 매장 정보 수정 (Unit)
- Given: storeId에 해당하는 매장이 존재
- When: 매장명 "역삼점", 위치 "서울시 강남구 역삼동"으로 수정을 요청
- Then: 매장의 name과 location이 정상적으로 업데이트됨

### TC-STORE-002-02: 존재하지 않는 매장 수정 시도 (Unit)
- Given: 존재하지 않는 storeId
- When: 해당 매장의 정보 수정을 요청
- Then: StoreNotFoundException (STORE001) 발생

### TC-STORE-002-03: 빈 매장명으로 수정 시도 (Unit)
- Given: 존재하는 매장
- When: 매장명을 빈 문자열("")로 수정을 요청
- Then: 유효성 검증 실패 (VALIDATION_ERROR) 발생

### TC-STORE-002-04: 빈 위치로 수정 시도 (Unit)
- Given: 존재하는 매장
- When: 위치를 빈 문자열("")로 수정을 요청
- Then: 유효성 검증 실패 (VALIDATION_ERROR) 발생

### TC-STORE-002-05: MANAGER 권한으로 매장 수정 시도 (E2E)
- Given: MANAGER 역할의 사용자가 인증된 상태
- When: 매장 수정을 요청
- Then: 403 Forbidden 응답
