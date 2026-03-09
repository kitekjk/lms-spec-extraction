# LMS-SCH-004 근무일정조회

## 기본 정보
- type: use_case
- domain: schedule
- id: LMS-SCH-004

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
역할에 따라 근무 일정을 조회한다. EMPLOYEE는 본인의 근무 일정만 조회할 수 있고, MANAGER는 소속 매장의 전체 근로자 일정을 조회할 수 있으며, SUPER_ADMIN은 모든 매장의 일정을 조회할 수 있다. 근로자별, 매장별, 날짜 범위별 필터링과 단건 조회를 지원한다.

## 기본 흐름

### 흐름 A: 본인 근무 일정 조회 (GET /api/schedules/my-schedule)
1. 근로자가 JWT 인증 토큰과 함께 본인 일정 조회 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증하여 인증된 사용자인지 확인한다.
3. 시스템이 인증된 userId로부터 employeeId를 조회한다.
4. 해당 employeeId의 모든 근무 일정을 조회한다.
5. 조회 결과를 WorkScheduleListResponse 형태로 200 OK 응답과 함께 반환한다.

### 흐름 B: 필터 기반 일정 조회 (GET /api/schedules)
1. 관리자가 JWT 인증 토큰과 함께 일정 조회 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증한다.
3. 쿼리 파라미터를 확인하여 조회 모드를 결정한다:
   - storeId + startDate + endDate: 해당 매장의 날짜 범위 내 일정 조회
   - employeeId: 해당 근로자의 전체 일정 조회
   - storeId만: 해당 매장의 전체 일정 조회
4. employeeId도 storeId도 없으면 HTTP 400 Bad Request를 반환한다.
5. 조회 결과를 WorkScheduleListResponse 형태로 200 OK 응답과 함께 반환한다.

### 흐름 C: 단건 일정 조회 (GET /api/schedules/{scheduleId})
1. 사용자가 JWT 인증 토큰과 함께 단건 일정 조회 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증한다.
3. scheduleId로 WorkSchedule을 조회한다.
4. 존재하면 WorkScheduleResponse 형태로 200 OK 응답을 반환한다.

## 대안 흐름
- **AF-1: 인증 실패** - JWT 토큰이 없거나 만료된 경우 HTTP 401 Unauthorized를 반환한다.
- **AF-2: 필터 파라미터 없음** - GET /api/schedules에서 employeeId도 storeId도 제공되지 않으면 HTTP 400 Bad Request를 반환한다 (메시지: "employeeId 또는 storeId 파라미터가 필요합니다").
- **AF-3: 단건 조회 - 일정 없음** - scheduleId에 해당하는 WorkSchedule이 존재하지 않으면 HTTP 404 Not Found를 반환한다.
- **AF-4: 조회 결과 없음** - 조건에 맞는 일정이 없으면 빈 목록(schedules: [], totalCount: 0)을 200 OK로 반환한다.

## 검증 조건
- EMPLOYEE의 본인 일정 조회(GET /api/schedules/my-schedule)에서 반환되는 일정의 employeeId가 모두 본인의 것이어야 한다.
- GET /api/schedules에서 employeeId와 storeId 중 하나 이상이 반드시 제공되어야 한다.
- storeId + startDate + endDate 조합 조회 시, 반환되는 일정의 workDate가 startDate ~ endDate 범위 내여야 한다.
- 단건 조회(GET /api/schedules/{scheduleId})에서 존재하지 않는 scheduleId는 HTTP 404를 반환한다.
- 응답의 totalCount는 schedules 배열의 길이와 일치해야 한다.
- 각 WorkScheduleResponse는 id, employeeId, storeId, workDate, startTime, endTime, workHours, isConfirmed, isWeekendWork, createdAt 필드를 포함해야 한다.

## 비기능 요구사항
- POLICY-NFR-001 참조
- API 응답 시간: 500ms 이내
- 매장 기반 데이터 격리: MANAGER는 소속 매장 데이터만 접근 가능 (POLICY-NFR-001 멀티 매장 지원)

## 테스트 시나리오

### TC-SCH-004-01: 본인 일정 전체 조회 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자의 근무 일정이 5건 존재한다.
- **When**: employeeId "emp-001"로 일정 조회를 요청한다.
- **Then**: 5건의 WorkScheduleResult가 반환되고, 모든 일정의 employeeId가 "emp-001"이다.

### TC-SCH-004-02: 매장 + 날짜 범위 조회 (Unit)
- **Given**: storeId가 "store-001"인 매장에 2026-03-01 ~ 2026-03-07 기간의 근무 일정이 10건 존재한다.
- **When**: storeId "store-001", startDate 2026-03-01, endDate 2026-03-07로 조회를 요청한다.
- **Then**: 10건의 WorkScheduleResult가 반환되고, 모든 일정의 workDate가 2026-03-01 ~ 2026-03-07 범위 내이다.

### TC-SCH-004-03: 필터 파라미터 없이 조회 시 에러 (Integration)
- **Given**: MANAGER 역할로 인증된 사용자가 존재한다.
- **When**: GET /api/schedules 요청을 employeeId, storeId 파라미터 없이 전송한다.
- **Then**: HTTP 400 Bad Request 응답이 반환된다.

### TC-SCH-004-04: 단건 조회 성공 (Integration)
- **Given**: scheduleId가 "sch-001"인 WorkSchedule이 존재한다.
- **When**: GET /api/schedules/sch-001 요청을 전송한다.
- **Then**: HTTP 200 OK 응답과 WorkScheduleResponse가 반환되고, id가 "sch-001"이다.

### TC-SCH-004-05: 단건 조회 - 일정 없음 (Integration)
- **Given**: scheduleId가 "sch-999"인 WorkSchedule이 존재하지 않는다.
- **When**: GET /api/schedules/sch-999 요청을 전송한다.
- **Then**: HTTP 404 Not Found 응답이 반환된다.

### TC-SCH-004-06: 본인 일정 조회 API 전체 흐름 (E2E)
- **Given**: EMPLOYEE 역할의 사용자가 인증되어 있고, 해당 근로자의 근무 일정이 3건 존재한다.
- **When**: GET /api/schedules/my-schedule 요청을 전송한다.
- **Then**: HTTP 200 OK 응답과 함께 schedules 배열에 3건, totalCount 3이 반환된다.
