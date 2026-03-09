# LMS-SCH-001 근무일정등록

## 기본 정보
- type: use_case
- domain: schedule
- id: LMS-SCH-001

## 관련 정책
- POLICY-AUTH-001 (인증/인가)
- POLICY-NFR-001 (비기능 요구사항)
- POLICY-SCHEDULE-001 (근무일정)

## 관련 Spec
- LMS-API-SCH-001

## 관련 모델
- 주 모델: WorkSchedule
- 참조 모델: Employee, Store

## 개요
MANAGER 또는 SUPER_ADMIN이 특정 근로자에 대해 근무 일정을 등록한다. 근무 일정은 근로자 ID(employeeId), 매장 ID(storeId), 근무 날짜(workDate), 근무 시작 시간(startTime), 근무 종료 시간(endTime)으로 구성된다. 동일 근로자에 대해 동일 날짜에 중복 일정을 등록할 수 없으며, 근로자는 해당 매장에 소속되어 있어야 한다. 생성된 일정은 미확정(isConfirmed: false) 상태로 시작한다.

## 기본 흐름
1. 관리자(MANAGER 또는 SUPER_ADMIN)가 JWT 인증 토큰과 함께 근무 일정 생성 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증하고 역할(MANAGER 또는 SUPER_ADMIN)을 확인한다.
3. 요청 바디에서 employeeId(필수), storeId(필수), workDate(필수), startTime(필수), endTime(필수)을 추출한다.
4. MANAGER인 경우, storeId가 자신의 소속 매장인지 확인한다.
5. 해당 employeeId의 근로자가 storeId 매장에 소속되어 있는지 확인한다.
6. 동일 employeeId + 동일 workDate 조합으로 기존 일정이 있는지 중복 확인한다.
7. endTime이 startTime보다 이후인지 검증한다.
8. WorkSchedule을 생성한다 (isConfirmed: false).
9. 생성된 WorkSchedule을 저장하고 201 Created 응답을 반환한다.

## 대안 흐름
- **AF-1: 동일 날짜 중복 일정** - 동일 근로자의 동일 날짜에 이미 일정이 존재하면 에러코드 SCH002와 HTTP 409 Conflict를 반환한다.
- **AF-2: 근로자 매장 미소속** - 해당 근로자가 storeId 매장에 소속되어 있지 않으면 에러코드 SCH004와 HTTP 409 Conflict를 반환한다.
- **AF-3: MANAGER 타 매장 등록 시도** - MANAGER가 소속 매장이 아닌 storeId로 일정을 등록하려 하면 에러코드 SCH005와 HTTP 403 Forbidden을 반환한다.
- **AF-4: EMPLOYEE 등록 시도** - EMPLOYEE 역할의 사용자가 일정 등록을 시도하면 HTTP 403 Forbidden을 반환한다.
- **AF-5: 필수 필드 누락** - employeeId, storeId, workDate, startTime, endTime 중 하나라도 누락되면 HTTP 400 Bad Request를 반환한다.
- **AF-6: 인증 실패** - JWT 토큰이 없거나 만료된 경우 HTTP 401 Unauthorized를 반환한다.
- **AF-7: endTime이 startTime 이전** - endTime이 startTime보다 이전이면 HTTP 400 Bad Request를 반환한다.

## 검증 조건
- 생성된 WorkSchedule의 isConfirmed는 false여야 한다.
- employeeId는 빈 문자열이 아니어야 한다 (@NotBlank).
- storeId는 빈 문자열이 아니어야 한다 (@NotBlank).
- workDate는 null이 아니어야 한다 (@NotNull).
- startTime은 null이 아니어야 한다 (@NotNull).
- endTime은 null이 아니어야 한다 (@NotNull).
- endTime은 startTime보다 이후여야 한다.
- 동일 employeeId + 동일 workDate 조합으로 2건 이상 일정을 생성할 수 없다.
- 근로자는 storeId 매장에 소속(Employee.storeId == storeId)되어 있어야 한다.

## 비기능 요구사항
- POLICY-NFR-001 참조
- API 응답 시간: 500ms 이내
- MANAGER의 매장 접근 권한은 쿼리 레벨에서 storeId 필터링으로 강제된다.

## 테스트 시나리오

### TC-SCH-001-01: 정상 근무 일정 등록 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자가 storeId "store-001"에 소속되어 있고, 2026-03-10에 기존 일정이 없다.
- **When**: workDate를 2026-03-10, startTime을 09:00, endTime을 18:00으로 일정 생성을 요청한다.
- **Then**: WorkSchedule이 생성되고, isConfirmed는 false, workHours는 9.0이다.

### TC-SCH-001-02: 동일 날짜 중복 일정 등록 시도 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자의 2026-03-10 일정이 이미 존재한다.
- **When**: 동일 employeeId, 동일 workDate로 일정 생성을 요청한다.
- **Then**: 에러코드 SCH002와 함께 예외가 발생하고, 새로운 일정은 생성되지 않는다.

### TC-SCH-001-03: 매장 미소속 근로자 일정 등록 시도 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자가 storeId "store-002"에 소속되어 있지 않다.
- **When**: storeId "store-002"로 일정 생성을 요청한다.
- **Then**: 에러코드 SCH004와 함께 예외가 발생한다.

### TC-SCH-001-04: EMPLOYEE 역할의 등록 시도 차단 (Integration)
- **Given**: EMPLOYEE 역할로 인증된 사용자가 존재한다.
- **When**: POST /api/schedules 요청을 전송한다.
- **Then**: HTTP 403 Forbidden 응답이 반환된다.

### TC-SCH-001-05: 필수 필드 누락 시 검증 실패 (Integration)
- **Given**: MANAGER 역할로 인증된 사용자가 존재한다.
- **When**: employeeId를 빈 문자열로 설정하여 POST /api/schedules 요청을 전송한다.
- **Then**: HTTP 400 Bad Request 응답이 반환된다.

### TC-SCH-001-06: 일정 등록 전체 흐름 (E2E)
- **Given**: MANAGER 역할의 사용자가 인증되어 있고, 소속 매장에 근로자 "emp-001"이 소속되어 있다.
- **When**: POST /api/schedules 요청을 employeeId, storeId, workDate, startTime, endTime과 함께 전송한다.
- **Then**: HTTP 201 Created 응답과 WorkScheduleResponse가 반환되고, isConfirmed는 false이다.
