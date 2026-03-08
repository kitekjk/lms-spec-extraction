# LMS-EMP-004: 근로자조회

## 기본 정보
- type: use_case
- domain: employee

## 관련 Spec
- LMS-API-EMP-001 (근로자API)

## 개요
인증된 사용자가 근로자 목록을 조회하거나 특정 근로자의 상세 정보를 조회한다.

## 관련 모델
- 주 모델: Employee (Aggregate Root)
- 참조 모델: Store (storeId 참조)

## 선행 조건
- 인증된 사용자여야 한다

## 기본 흐름 (전체 목록 조회)
1. 사용자가 근로자 목록 조회를 요청한다
2. 시스템은 모든 근로자를 조회한다
3. 시스템은 근로자 목록과 총 건수를 반환한다

## 대안 흐름
- 매장별 조회 (storeId 파라미터 지정): 해당 매장에 소속된 근로자만 조회한다
- 활성 근로자만 조회 (activeOnly=true): 활성화된 근로자만 필터링한다
- 매장별 + 활성 근로자 조회: storeId와 activeOnly를 동시에 적용한다
- 상세 조회 (employeeId 지정): 특정 근로자의 상세 정보를 조회한다

## 예외 흐름
- 상세 조회 시 근로자를 찾을 수 없는 경우: 404 Not Found 응답

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- 인증된 사용자여야 한다
- 상세 조회 시 해당 근로자가 존재해야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-EMP-004-01: 전체 근로자 목록 조회 (Integration)
- Given: 5명의 근로자가 등록되어 있음 (활성 3명, 비활성 2명)
- When: 전체 근로자 목록 조회를 요청
- Then: 5명의 근로자 목록과 총 건수 5가 반환됨

### TC-EMP-004-02: 매장별 근로자 조회 (Integration)
- Given: storeId="store-A"에 3명, storeId="store-B"에 2명의 근로자가 소속
- When: storeId="store-A"로 근로자 목록 조회를 요청
- Then: 3명의 근로자 목록만 반환됨

### TC-EMP-004-03: 활성 근로자만 조회 (Integration)
- Given: 활성 근로자 3명, 비활성 근로자 2명이 존재
- When: activeOnly=true로 근로자 목록 조회를 요청
- Then: 활성 상태의 3명만 반환됨

### TC-EMP-004-04: 매장별 + 활성 근로자 복합 필터 조회 (Integration)
- Given: storeId="store-A"에 활성 2명, 비활성 1명이 존재
- When: storeId="store-A", activeOnly=true로 조회를 요청
- Then: 활성 상태의 2명만 반환됨

### TC-EMP-004-05: 근로자 상세 조회 (Integration)
- Given: 특정 employeeId에 해당하는 근로자가 존재
- When: 해당 employeeId로 상세 조회를 요청
- Then: 근로자의 상세 정보(이름, 유형, 매장, 잔여연차 등)가 반환됨

### TC-EMP-004-06: 존재하지 않는 근로자 상세 조회 (E2E)
- Given: 존재하지 않는 employeeId
- When: 해당 employeeId로 상세 조회를 요청
- Then: 404 Not Found 응답

### TC-EMP-004-07: 데이터 없는 매장 조회 시 빈 목록 반환 (Integration)
- Given: storeId="store-C"에 소속된 근로자가 없음
- When: storeId="store-C"로 근로자 목록 조회를 요청
- Then: 빈 목록과 총 건수 0이 반환됨
