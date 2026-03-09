# LMS-EMP-002 근로자수정

## 기본 정보
- type: use_case
- domain: employee
- id: LMS-EMP-002

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 3.2~3.3 SUPER_ADMIN/MANAGER 권한
- POLICY-NFR-001 (비기능 요구사항) — 4.1~4.4 멀티 매장 지원, 3.1~3.3 변경 이력 추적

## 관련 Spec
- LMS-API-EMP-001 (근로자API)

## 관련 모델
- 주 모델: Employee — id(EmployeeId, UUID), userId(UserId), name(EmployeeName), employeeType(EmployeeType), storeId(StoreId?), remainingLeave(RemainingLeave, BigDecimal), isActive(Boolean), createdAt(Instant)
- 참조 모델: Store — id(StoreId)

## 개요
SUPER_ADMIN 또는 MANAGER 권한의 사용자가 기존 근로자의 이름, 근로자 유형, 매장 배정을 수정한다. 근로자 유형 변경 시 Employee.changeType을 통해 처리하고, 매장 변경 시 Employee.assignStore를 통해 처리한다.

## 기본 흐름
1. SUPER_ADMIN 또는 MANAGER 권한의 사용자가 Bearer 토큰과 함께 수정 정보를 전송한다.
2. 경로 파라미터의 employeeId로 Employee를 조회한다.
3. name 필드가 빈 문자열이 아닌지 검증한다.
4. 이름을 변경한다 (EmployeeName 값 객체 재생성).
5. employeeType이 기존과 다르면 유형을 변경한다.
6. storeId가 기존과 다르면 매장 배정을 변경한다 (null이면 매장 배정 해제).
7. 수정된 Employee를 저장한다.
8. 수정된 Employee 정보를 응답한다.

## 대안 흐름
- AF-1: employeeId에 해당하는 Employee가 없으면 HTTP 404와 EMP001("근로자를 찾을 수 없습니다: {employeeId}")을 반환한다.
- AF-2: name이 빈 문자열이면 HTTP 400과 VALIDATION_ERROR("이름은 필수입니다")를 반환한다.
- AF-3: 요청자가 SUPER_ADMIN 또는 MANAGER가 아니면 HTTP 403을 반환한다.
- AF-4: 인증 토큰이 없거나 만료되었으면 HTTP 401을 반환한다.

## 검증 조건
- employeeId: 유효한 UUID 형식, DB에 존재하는 Employee
- name 필드: 빈 문자열 불가
- employeeType 필드: REGULAR | IRREGULAR | PART_TIME 중 하나
- storeId 필드: null 허용 (매장 미배정), UUID 형식
- 수정 후 Employee.id, Employee.userId, Employee.createdAt은 변경되지 않음

## 비기능 요구사항
- POLICY-NFR-001 참조
- 근로자 수정 API 응답시간 500ms 이내
- MANAGER는 소속 매장의 근로자만 수정 가능 (EMP003)

## 테스트 시나리오

### TC-EMP-002-01: 근로자 이름 수정 성공 (Unit)
- Given: employeeId="emp-1"인 Employee(name="홍길동")가 존재한다
- When: PUT /api/employees/emp-1에 name="김철수"로 요청한다
- Then: HTTP 200, 응답의 name="김철수", 나머지 필드는 변경되지 않는다

### TC-EMP-002-02: 근로자 유형 변경 성공 (Unit)
- Given: employeeId="emp-2"인 Employee(employeeType=REGULAR)가 존재한다
- When: PUT /api/employees/emp-2에 employeeType=PART_TIME으로 요청한다
- Then: HTTP 200, 응답의 employeeType="PART_TIME"

### TC-EMP-002-03: 매장 배정 변경 성공 (Unit)
- Given: employeeId="emp-3"인 Employee(storeId="store-A")가 존재한다
- When: PUT /api/employees/emp-3에 storeId="store-B"로 요청한다
- Then: HTTP 200, 응답의 storeId="store-B"

### TC-EMP-002-04: 존재하지 않는 근로자 수정 시 실패 (Unit)
- Given: employeeId="nonexist"에 해당하는 Employee가 없다
- When: PUT /api/employees/nonexist에 수정 요청한다
- Then: HTTP 404, 에러코드 EMP001

### TC-EMP-002-05: 매장 배정 해제 (Unit)
- Given: employeeId="emp-4"인 Employee(storeId="store-C")가 존재한다
- When: PUT /api/employees/emp-4에 storeId=null로 요청한다
- Then: HTTP 200, 응답의 storeId=null

### TC-EMP-002-06: 근로자 수정 후 DB 반영 확인 (Integration)
- Given: DB에 employeeId="emp-int"인 Employee가 존재한다
- When: PUT /api/employees/emp-int에 name="변경된이름", employeeType=IRREGULAR로 요청한다
- Then: DB에서 해당 Employee의 name="변경된이름", employeeType=IRREGULAR로 갱신되어 있다

### TC-EMP-002-07: 근로자 수정 후 조회 일치 E2E (E2E)
- Given: 시스템에 Employee가 등록되어 있다
- When: PUT /api/employees/{id}로 이름을 수정한 후, GET /api/employees/{id}로 조회한다
- Then: 수정된 이름으로 조회된다
