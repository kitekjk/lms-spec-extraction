# LMS-EMP-003 근로자비활성화

## 기본 정보
- type: use_case
- domain: employee
- id: LMS-EMP-003

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 3.2~3.3 SUPER_ADMIN/MANAGER 권한
- POLICY-NFR-001 (비기능 요구사항) — 3.1~3.3 변경 이력 추적

## 관련 Spec
- LMS-API-EMP-001 (근로자API)

## 관련 모델
- 주 모델: Employee — id(EmployeeId, UUID), isActive(Boolean)
- 참조 모델: 없음

## 개요
SUPER_ADMIN 또는 MANAGER 권한의 사용자가 근로자를 비활성화한다. 물리적 삭제가 아닌 논리적 비활성화(isActive=false)로 처리하며, 비활성화된 근로자는 출퇴근, 일정 배정, 휴가 신청 등의 기능을 사용할 수 없다.

## 기본 흐름
1. SUPER_ADMIN 또는 MANAGER 권한의 사용자가 Bearer 토큰과 함께 비활성화 요청을 전송한다.
2. 경로 파라미터의 employeeId로 Employee를 조회한다.
3. Employee의 isActive를 false로 변경한다 (Employee.deactivate).
4. 비활성화된 Employee를 저장한다.
5. 비활성화된 Employee 정보를 응답한다 (isActive=false).

## 대안 흐름
- AF-1: employeeId에 해당하는 Employee가 없으면 HTTP 404와 EMP001("근로자를 찾을 수 없습니다: {employeeId}")을 반환한다.
- AF-2: 요청자가 SUPER_ADMIN 또는 MANAGER가 아니면 HTTP 403을 반환한다.
- AF-3: 인증 토큰이 없거나 만료되었으면 HTTP 401을 반환한다.

## 검증 조건
- employeeId: 유효한 UUID 형식, DB에 존재하는 Employee
- 비활성화 후 Employee.isActive == false
- Employee의 다른 필드(id, userId, name, employeeType, storeId, remainingLeave)는 변경되지 않음
- 물리적 삭제가 아닌 논리적 비활성화 (DB 레코드 유지)

## 비기능 요구사항
- POLICY-NFR-001 참조
- 근로자 비활성화 API 응답시간 500ms 이내
- MANAGER는 소속 매장의 근로자만 비활성화 가능 (EMP003)

## 테스트 시나리오

### TC-EMP-003-01: 활성 근로자 비활성화 성공 (Unit)
- Given: employeeId="emp-1"인 Employee(isActive=true)가 존재한다
- When: PATCH /api/employees/emp-1/deactivate를 요청한다
- Then: HTTP 200, 응답의 isActive=false, 나머지 필드는 변경되지 않는다

### TC-EMP-003-02: 존재하지 않는 근로자 비활성화 시 실패 (Unit)
- Given: employeeId="nonexist"에 해당하는 Employee가 없다
- When: PATCH /api/employees/nonexist/deactivate를 요청한다
- Then: HTTP 404, 에러코드 EMP001

### TC-EMP-003-03: EMPLOYEE 권한으로 비활성화 시도 시 실패 (Unit)
- Given: EMPLOYEE 인증 토큰이 유효하다
- When: PATCH /api/employees/emp-1/deactivate를 요청한다
- Then: HTTP 403 (권한 없음)

### TC-EMP-003-04: 비활성화 후 DB 상태 확인 (Integration)
- Given: DB에 employeeId="emp-int"인 활성 Employee가 존재한다
- When: PATCH /api/employees/emp-int/deactivate를 요청한다
- Then: DB에서 해당 Employee의 isActive=false, 레코드는 삭제되지 않았다

### TC-EMP-003-05: 비활성화 후 목록 조회에서 필터링 (Integration)
- Given: 매장에 활성 Employee 3명, 비활성 Employee 1명이 존재한다
- When: GET /api/employees?storeId={storeId}&activeOnly=true로 조회한다
- Then: 활성 Employee 3명만 응답에 포함된다

### TC-EMP-003-06: 비활성화 전체 플로우 E2E (E2E)
- Given: 시스템에 활성 Employee가 등록되어 있다
- When: PATCH /api/employees/{id}/deactivate로 비활성화한 후, GET /api/employees/{id}로 조회한다
- Then: isActive=false로 조회된다
