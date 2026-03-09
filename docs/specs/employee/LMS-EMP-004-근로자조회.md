# LMS-EMP-004 근로자조회

## 기본 정보
- type: use_case
- domain: employee
- id: LMS-EMP-004

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 3.2~3.4 역할별 조회 범위, 4 역할별 접근 권한
- POLICY-NFR-001 (비기능 요구사항) — 4.1~4.4 멀티 매장 지원, 5.1 응답시간 500ms 이내

## 관련 Spec
- LMS-API-EMP-001 (근로자API)

## 관련 모델
- 주 모델: Employee — id(EmployeeId, UUID), userId(UserId), name(EmployeeName), employeeType(EmployeeType), storeId(StoreId?), remainingLeave(RemainingLeave, BigDecimal), isActive(Boolean), createdAt(Instant)
- 참조 모델: Store — id(StoreId)

## 개요
인증된 사용자가 근로자 정보를 조회한다. 단건 상세 조회와 목록 조회를 지원하며, 목록 조회 시 storeId와 activeOnly 파라미터로 필터링할 수 있다. SUPER_ADMIN은 전체 매장, MANAGER는 소속 매장, EMPLOYEE는 본인만 조회 가능하다.

## 기본 흐름 — 단건 상세 조회
1. 인증된 사용자가 Bearer 토큰과 함께 GET /api/employees/{employeeId}를 요청한다.
2. 경로 파라미터의 employeeId로 Employee를 조회한다.
3. Employee 정보(id, userId, name, employeeType, storeId, remainingLeave, isActive, createdAt)를 응답한다.

## 기본 흐름 — 목록 조회
1. 인증된 사용자가 Bearer 토큰과 함께 GET /api/employees를 요청한다.
2. storeId 파라미터가 있으면 해당 매장의 근로자를, 없으면 전체 근로자를 조회한다.
3. activeOnly=true이면 isActive=true인 근로자만 필터링한다.
4. employees 배열과 totalCount를 응답한다.

## 대안 흐름
- AF-1: employeeId에 해당하는 Employee가 없으면 HTTP 404를 반환한다 (본문 없음).
- AF-2: 인증 토큰이 없거나 만료되었으면 HTTP 401을 반환한다.

## 검증 조건
- 단건 조회: employeeId에 해당하는 Employee가 DB에 존재해야 함
- 목록 조회: storeId 파라미터는 선택적 (null 허용)
- 목록 조회: activeOnly 파라미터 기본값은 false
- totalCount는 응답의 employees 배열 크기와 동일
- 응답의 모든 필드 타입이 정확: id(String/UUID), remainingLeave(BigDecimal), createdAt(ISO 8601 Instant)

## 비기능 요구사항
- POLICY-NFR-001 참조
- 근로자 조회 API 응답시간 500ms 이내
- 목록 조회 시 storeId 기반 데이터 격리 (MANAGER는 소속 매장만)
- EMPLOYEE는 본인 정보만 조회 가능

## 테스트 시나리오

### TC-EMP-004-01: 근로자 상세 조회 성공 (Unit)
- Given: employeeId="emp-1"인 Employee가 존재한다
- When: GET /api/employees/emp-1을 요청한다
- Then: HTTP 200, 응답에 id="emp-1", userId, name, employeeType, storeId, remainingLeave, isActive, createdAt이 포함된다

### TC-EMP-004-02: 존재하지 않는 근로자 상세 조회 시 실패 (Unit)
- Given: employeeId="nonexist"에 해당하는 Employee가 없다
- When: GET /api/employees/nonexist를 요청한다
- Then: HTTP 404 (본문 없음)

### TC-EMP-004-03: 매장별 근로자 목록 조회 (Unit)
- Given: storeId="store-A"에 Employee 3명이 등록되어 있다
- When: GET /api/employees?storeId=store-A를 요청한다
- Then: HTTP 200, employees 배열에 3개 항목, totalCount=3

### TC-EMP-004-04: 활성 근로자만 목록 조회 (Unit)
- Given: storeId="store-B"에 활성 Employee 2명, 비활성 Employee 1명이 존재한다
- When: GET /api/employees?storeId=store-B&activeOnly=true를 요청한다
- Then: HTTP 200, employees 배열에 2개 항목, totalCount=2

### TC-EMP-004-05: 전체 근로자 목록 조회 (Unit)
- Given: 시스템에 Employee가 총 5명 존재한다
- When: GET /api/employees를 요청한다 (storeId 파라미터 없음)
- Then: HTTP 200, employees 배열에 5개 항목, totalCount=5

### TC-EMP-004-06: DB에서 직접 조회 결과와 API 응답 일치 확인 (Integration)
- Given: DB에 Employee 레코드가 저장되어 있다
- When: GET /api/employees/{id}로 조회한다
- Then: DB 레코드의 모든 필드 값과 API 응답 값이 일치한다

### TC-EMP-004-07: 근로자 등록 후 목록 조회에 반영 E2E (E2E)
- Given: 매장에 Employee가 2명 존재한다
- When: POST /api/employees로 1명을 추가 등록한 후, GET /api/employees?storeId={storeId}로 조회한다
- Then: employees 배열에 3개 항목, totalCount=3
