# LMS-STORE-001: 매장 관리

## 기본 정보
- type: use_case
- domain: store
- service: LMS
- priority: high

## 관련 정책
- POLICY-AUTH-001 (SUPER_ADMIN만 매장 CRUD 가능)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-STORE-001-매장API](LMS-API-STORE-001-매장API.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **Store**: CRUD 대상
  - 사용하는 주요 필드: name (StoreName), location (StoreLocation)
  - 상태 변경: 생성, 수정, 삭제

## 개요
매장을 등록, 조회, 수정, 삭제한다.

## 선행 조건
- 요청자가 SUPER_ADMIN 역할이어야 한다 (생성/수정/삭제)
- 조회는 인증된 사용자 모두 가능

## 기본 흐름

### 등록
1. StoreName과 StoreLocation 값 객체를 생성한다
2. 동일 매장명이 존재하는지 확인한다
3. Store.create(context, name, location)을 호출한다
4. Store를 저장하고 결과를 반환한다

### 수정
1. storeId로 Store를 조회한다
2. Store.update(context, name, location)을 호출한다
3. 수정된 Store를 저장하고 결과를 반환한다

### 삭제
1. storeId로 Store 존재 여부를 확인한다
2. Store를 삭제한다

## 대안 흐름
- 동일 매장명이 이미 존재하는 경우: `DuplicateStoreNameException` 발생
- Store가 존재하지 않는 경우: `StoreNotFoundException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 유효한 정보로 매장 등록 시 Store가 생성되어야 한다
- 동일 매장명 중복 등록 시 DuplicateStoreNameException이 발생해야 한다
- 존재하지 않는 매장 수정 시 StoreNotFoundException이 발생해야 한다
- 존재하지 않는 매장 삭제 시 StoreNotFoundException이 발생해야 한다
- StoreName은 비어있지 않고 최대 100자여야 한다
- StoreLocation은 비어있지 않고 최대 200자여야 한다

## 비즈니스 규칙
- 매장명은 고유해야 한다
- StoreName: 비어있을 수 없음, 최대 100자
- StoreLocation: 비어있을 수 없음, 최대 200자

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용

## 테스트 시나리오

### TC-STORE-001-01: 정상 매장 등록 (Integration)
- Given: 중복되지 않는 매장명이 주어진다
- When: 매장을 등록한다
- Then: Store가 생성되고 name, location이 설정된다

### TC-STORE-001-02: 매장명 중복 (Integration)
- Given: "강남점"이 이미 등록되어 있다
- When: "강남점"으로 매장을 등록한다
- Then: DuplicateStoreNameException이 발생한다

### TC-STORE-001-03: 정상 매장 수정 (Integration)
- Given: Store가 존재한다
- When: 이름과 위치를 변경한다
- Then: 변경된 값이 반영된다

### TC-STORE-001-04: 존재하지 않는 매장 삭제 (Integration)
- Given: 존재하지 않는 storeId가 주어진다
- When: 삭제를 시도한다
- Then: StoreNotFoundException이 발생한다

### TC-STORE-001-05: StoreName 검증 (Unit)
- Given: 빈 문자열 또는 101자 초과 이름
- When: StoreName VO를 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-STORE-001-06: StoreLocation 검증 (Unit)
- Given: 빈 문자열 또는 201자 초과 위치
- When: StoreLocation VO를 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-STORE-001-07: 권한 검증 - MANAGER 접근 (E2E)
- Given: MANAGER 역할로 로그인한 상태이다
- When: 매장 등록 API를 호출한다
- Then: 403 Forbidden이 반환된다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
