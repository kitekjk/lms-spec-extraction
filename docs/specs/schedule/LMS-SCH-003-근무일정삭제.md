# LMS-SCH-003 근무일정삭제

## 기본 정보
- type: use_case
- domain: schedule
- id: LMS-SCH-003

## 관련 정책
- POLICY-AUTH-001 (인증/인가)
- POLICY-NFR-001 (비기능 요구사항)
- POLICY-SCHEDULE-001 (근무일정)

## 관련 Spec
- LMS-API-SCH-001
- LMS-SCH-001 (근무일정등록)

## 관련 모델
- 주 모델: WorkSchedule
- 참조 모델: AttendanceRecord

## 개요
MANAGER 또는 SUPER_ADMIN이 기존 근무 일정을 삭제한다. 삭제 시 해당 일정에 연결된 출퇴근 기록(AttendanceRecord)의 workScheduleId가 null로 초기화될 수 있다. MANAGER는 자신의 소속 매장 근로자의 일정만 삭제할 수 있다.

## 기본 흐름
1. 관리자(MANAGER 또는 SUPER_ADMIN)가 JWT 인증 토큰과 함께 근무 일정 삭제 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증하고 역할(MANAGER 또는 SUPER_ADMIN)을 확인한다.
3. 시스템이 scheduleId로 WorkSchedule을 조회한다.
4. MANAGER인 경우, 해당 일정의 storeId가 자신의 소속 매장인지 확인한다.
5. 해당 WorkSchedule을 삭제한다.
6. 204 No Content 응답을 반환한다.

## 대안 흐름
- **AF-1: 일정 없음** - scheduleId에 해당하는 WorkSchedule이 존재하지 않으면 에러코드 SCH001과 HTTP 404 Not Found를 반환한다.
- **AF-2: MANAGER 타 매장 삭제 시도** - MANAGER가 소속 매장이 아닌 일정을 삭제하려 하면 에러코드 SCH005와 HTTP 403 Forbidden을 반환한다.
- **AF-3: EMPLOYEE 삭제 시도** - EMPLOYEE 역할의 사용자가 일정 삭제를 시도하면 HTTP 403 Forbidden을 반환한다.
- **AF-4: 인증 실패** - JWT 토큰이 없거나 만료된 경우 HTTP 401 Unauthorized를 반환한다.

## 검증 조건
- 삭제 후 동일 scheduleId로 조회하면 결과가 없어야 한다 (404 Not Found).
- EMPLOYEE 역할은 이 기능에 접근할 수 없다.
- MANAGER는 소속 매장의 일정만 삭제 가능하다.
- SUPER_ADMIN은 모든 매장의 일정을 삭제할 수 있다.
- 삭제 성공 시 응답 바디는 없으며 HTTP 204 No Content를 반환한다.

## 비기능 요구사항
- POLICY-NFR-001 참조
- API 응답 시간: 500ms 이내

## 테스트 시나리오

### TC-SCH-003-01: 정상 근무 일정 삭제 (Unit)
- **Given**: scheduleId가 "sch-001"인 WorkSchedule이 존재한다.
- **When**: 해당 일정 삭제를 요청한다.
- **Then**: WorkSchedule이 삭제되고, 동일 scheduleId로 조회 시 null이 반환된다.

### TC-SCH-003-02: 존재하지 않는 일정 삭제 시도 (Unit)
- **Given**: scheduleId가 "sch-999"인 WorkSchedule이 존재하지 않는다.
- **When**: 삭제 요청을 전송한다.
- **Then**: 에러코드 SCH001과 함께 예외가 발생한다.

### TC-SCH-003-03: EMPLOYEE 역할의 삭제 시도 차단 (Integration)
- **Given**: EMPLOYEE 역할로 인증된 사용자가 존재한다.
- **When**: DELETE /api/schedules/{scheduleId} 요청을 전송한다.
- **Then**: HTTP 403 Forbidden 응답이 반환된다.

### TC-SCH-003-04: MANAGER 타 매장 삭제 차단 (Integration)
- **Given**: MANAGER 역할로 인증된 사용자가 storeId "store-001"에 소속되어 있고, storeId "store-002"에 속한 일정이 존재한다.
- **When**: DELETE /api/schedules/{scheduleId} 요청을 전송한다.
- **Then**: HTTP 403 Forbidden 응답이 반환된다.

### TC-SCH-003-05: 삭제 API 전체 흐름 (E2E)
- **Given**: MANAGER 역할의 사용자가 인증되어 있고, 소속 매장의 일정 "sch-001"이 존재한다.
- **When**: DELETE /api/schedules/sch-001 요청을 전송한다.
- **Then**: HTTP 204 No Content 응답이 반환되고, GET /api/schedules/sch-001 요청 시 HTTP 404 Not Found가 반환된다.
