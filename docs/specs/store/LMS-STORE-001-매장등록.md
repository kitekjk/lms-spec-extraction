# LMS-STORE-001: 매장등록

## 기본 정보
- type: use_case
- domain: store

## 관련 Spec
- LMS-API-STORE-001 (매장API)
- LMS-STORE-002 (매장수정)
- LMS-STORE-004 (매장조회)

## 개요
SUPER_ADMIN이 매장명과 위치를 입력하여 새로운 매장을 등록한다.

## 관련 모델
- 주 모델: Store (Aggregate Root)
- 참조 모델: StoreName, StoreLocation

## 선행 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다

## 기본 흐름
1. SUPER_ADMIN이 매장명과 위치를 입력하여 매장 등록을 요청한다
2. 시스템은 매장명의 유효성을 검증한다
3. 시스템은 새로운 Store를 생성한다 (UUID 자동 생성)
4. 시스템은 매장을 저장하고 결과를 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 이미 존재하는 매장명인 경우: DuplicateStoreNameException (STORE002) 발생
- 매장명이 비어있는 경우: 유효성 검증 실패 (VALIDATION_ERROR)
- 위치가 비어있는 경우: 유효성 검증 실패 (VALIDATION_ERROR)

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 매장명이 비어있지 않아야 한다
- 위치가 비어있지 않아야 한다
- 동일한 매장명이 이미 존재하지 않아야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-STORE-001-01: 정상 매장 등록 (Unit)
- Given: SUPER_ADMIN이 인증된 상태이고, 매장명 "강남점"은 미등록 상태
- When: 매장명 "강남점", 위치 "서울시 강남구"로 매장 등록을 요청
- Then: Store가 생성되고, UUID 기반 storeId가 자동 부여됨

### TC-STORE-001-02: 중복 매장명으로 등록 시도 (Unit)
- Given: "강남점"이라는 매장명이 이미 등록되어 있음
- When: 동일한 매장명 "강남점"으로 매장 등록을 요청
- Then: DuplicateStoreNameException (STORE002) 발생

### TC-STORE-001-03: 빈 매장명으로 등록 시도 (Unit)
- Given: SUPER_ADMIN이 인증된 상태
- When: 매장명을 빈 문자열("")로 매장 등록을 요청
- Then: 유효성 검증 실패 (VALIDATION_ERROR) 발생

### TC-STORE-001-04: 빈 위치로 등록 시도 (Unit)
- Given: SUPER_ADMIN이 인증된 상태
- When: 위치를 빈 문자열("")로 매장 등록을 요청
- Then: 유효성 검증 실패 (VALIDATION_ERROR) 발생

### TC-STORE-001-05: MANAGER 권한으로 매장 등록 시도 (E2E)
- Given: MANAGER 역할의 사용자가 인증된 상태
- When: 매장 등록을 요청
- Then: 403 Forbidden 응답

### TC-STORE-001-06: EMPLOYEE 권한으로 매장 등록 시도 (E2E)
- Given: EMPLOYEE 역할의 사용자가 인증된 상태
- When: 매장 등록을 요청
- Then: 403 Forbidden 응답
