# LMS-EMP-001 근로자등록

## 기본 정보
- type: use_case
- domain: employee
- id: LMS-EMP-001

## 관련 정책
- POLICY-AUTH-001 (인증/인가) — 3.2~3.3 SUPER_ADMIN/MANAGER 권한, 4 역할별 접근 권한
- POLICY-NFR-001 (비기능 요구사항) — 4.1~4.4 멀티 매장 지원, 5.1 응답시간 500ms 이내

## 관련 Spec
- LMS-API-EMP-001 (근로자API)

## 관련 모델
- 주 모델: Employee — id(EmployeeId, UUID), userId(UserId), name(EmployeeName), employeeType(EmployeeType), storeId(StoreId?), remainingLeave(RemainingLeave, BigDecimal), isActive(Boolean), createdAt(Instant)
- 참조 모델: User — id(UserId) / Store — id(StoreId)

## 개요
SUPER_ADMIN 또는 MANAGER 권한의 사용자가 새로운 근로자를 등록한다. 근로자는 기존 User에 연결되며, 근로자 유형(REGULAR, IRREGULAR, PART_TIME)에 따라 초기 연차가 자동 설정된다. 하나의 User에 하나의 Employee만 등록할 수 있다.

## 기본 흐름
1. SUPER_ADMIN 또는 MANAGER 권한의 사용자가 Bearer 토큰과 함께 근로자 정보를 전송한다.
2. userId 필드가 빈 문자열이 아닌지 검증한다.
3. name 필드가 빈 문자열이 아닌지 검증한다.
4. employeeType이 REGULAR, IRREGULAR, PART_TIME 중 하나인지 검증한다.
5. userId로 기존 Employee가 존재하는지 확인한다 (중복 검증).
6. Employee 엔티티를 생성한다 (remainingLeave는 employeeType에 따라 자동 설정).
7. Employee를 저장한다.
8. 생성된 Employee 정보를 응답한다.

## 대안 흐름
- AF-1: userId가 빈 문자열이면 HTTP 400과 VALIDATION_ERROR("사용자 ID는 필수입니다")를 반환한다.
- AF-2: name이 빈 문자열이면 HTTP 400과 VALIDATION_ERROR("이름은 필수입니다")를 반환한다.
- AF-3: 해당 userId로 이미 Employee가 등록되어 있으면 HTTP 409와 EMP002("이미 근로자로 등록된 사용자입니다: {userId}")를 반환한다.
- AF-4: 요청자가 SUPER_ADMIN 또는 MANAGER가 아니면 HTTP 403을 반환한다.
- AF-5: 인증 토큰이 없거나 만료되었으면 HTTP 401을 반환한다.

## 검증 조건
- userId 필드: 빈 문자열 불가
- name 필드: 빈 문자열 불가
- employeeType 필드: REGULAR | IRREGULAR | PART_TIME 중 하나
- 하나의 userId에 하나의 Employee만 존재
- 초기 연차: REGULAR=15.0, IRREGULAR=11.0, PART_TIME=0.0
- 생성된 Employee의 isActive == true
- 생성된 Employee의 id는 UUID v4 형식

## 비기능 요구사항
- POLICY-NFR-001 참조
- 근로자 등록 API 응답시간 500ms 이내
- MANAGER는 소속 매장의 근로자만 등록 가능 (EMP003)

## 테스트 시나리오

### TC-EMP-001-01: SUPER_ADMIN이 정규직 근로자 등록 성공 (Unit)
- Given: userId="user-123"에 해당하는 Employee가 없다
- When: POST /api/employees에 userId="user-123", name="홍길동", employeeType=REGULAR, storeId="store-1"로 요청한다
- Then: HTTP 201, 응답에 id(UUID), userId="user-123", name="홍길동", employeeType="REGULAR", remainingLeave=15.0, isActive=true가 포함된다

### TC-EMP-001-02: 중복 userId로 등록 시 실패 (Unit)
- Given: userId="user-456"에 해당하는 Employee가 이미 존재한다
- When: POST /api/employees에 userId="user-456"으로 요청한다
- Then: HTTP 409, 에러코드 EMP002, 메시지에 "이미 근로자로 등록된 사용자입니다" 포함

### TC-EMP-001-03: 아르바이트 근로자 등록 시 초기 연차 0.0 (Unit)
- Given: userId="user-789"에 해당하는 Employee가 없다
- When: POST /api/employees에 employeeType=PART_TIME으로 요청한다
- Then: HTTP 201, 응답의 remainingLeave=0.0

### TC-EMP-001-04: 계약직 근로자 등록 시 초기 연차 11.0 (Unit)
- Given: userId="user-101"에 해당하는 Employee가 없다
- When: POST /api/employees에 employeeType=IRREGULAR로 요청한다
- Then: HTTP 201, 응답의 remainingLeave=11.0

### TC-EMP-001-05: EMPLOYEE 권한으로 등록 시도 시 실패 (Unit)
- Given: EMPLOYEE 인증 토큰이 유효하다
- When: POST /api/employees에 등록 정보를 요청한다
- Then: HTTP 403 (권한 없음)

### TC-EMP-001-06: 근로자 등록 후 DB 저장 상태 확인 (Integration)
- Given: userId="inttest-user"에 해당하는 Employee가 없다
- When: POST /api/employees에 해당 userId로 등록 요청한다
- Then: DB에서 Employee 조회 시 userId="inttest-user", isActive=true, remainingLeave가 employeeType에 따른 값이다

### TC-EMP-001-07: 근로자 등록 후 상세 조회 E2E (E2E)
- Given: 시스템에 User가 등록되어 있고, 아직 Employee가 없다
- When: POST /api/employees로 근로자를 등록한 후, GET /api/employees/{id}로 조회한다
- Then: 등록 시 응답과 동일한 정보가 조회된다
