# LMS-SCH-002 근무일정수정

## 기본 정보
- type: use_case
- domain: schedule
- id: LMS-SCH-002

## 관련 정책
- POLICY-AUTH-001 (인증/인가)
- POLICY-NFR-001 (비기능 요구사항)
- POLICY-SCHEDULE-001 (근무일정)

## 관련 Spec
- LMS-API-SCH-001
- LMS-SCH-001 (근무일정등록)

## 관련 모델
- 주 모델: WorkSchedule
- 참조 모델: Employee, Store

## 개요
MANAGER 또는 SUPER_ADMIN이 기존 근무 일정의 날짜(workDate), 시작 시간(startTime), 종료 시간(endTime)을 수정한다. 확정(isConfirmed: true) 상태의 일정은 수정할 수 없다. 수정 시 workDate, startTime, endTime은 모두 선택적(optional)이며, 제공된 필드만 업데이트된다.

## 기본 흐름
1. 관리자(MANAGER 또는 SUPER_ADMIN)가 JWT 인증 토큰과 함께 근무 일정 수정 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증하고 역할(MANAGER 또는 SUPER_ADMIN)을 확인한다.
3. 시스템이 scheduleId로 WorkSchedule을 조회한다.
4. MANAGER인 경우, 해당 일정의 storeId가 자신의 소속 매장인지 확인한다.
5. 해당 일정이 확정 상태(isConfirmed: true)인지 확인한다.
6. 요청 바디에서 workDate(선택), startTime(선택), endTime(선택)을 추출한다.
7. workDate가 제공되면 WorkSchedule의 workDate를 변경한다.
8. startTime 또는 endTime이 제공되면 WorkSchedule의 workTime을 변경한다.
9. 업데이트된 WorkSchedule을 저장하고 200 OK 응답을 반환한다.

## 대안 흐름
- **AF-1: 일정 없음** - scheduleId에 해당하는 WorkSchedule이 존재하지 않으면 에러코드 SCH001과 HTTP 404 Not Found를 반환한다.
- **AF-2: 확정된 일정 수정 시도** - isConfirmed가 true인 일정을 수정하려 하면 에러코드 SCH003과 HTTP 409 Conflict를 반환한다.
- **AF-3: MANAGER 타 매장 수정 시도** - MANAGER가 소속 매장이 아닌 일정을 수정하려 하면 에러코드 SCH005와 HTTP 403 Forbidden을 반환한다.
- **AF-4: EMPLOYEE 수정 시도** - EMPLOYEE 역할의 사용자가 일정 수정을 시도하면 HTTP 403 Forbidden을 반환한다.
- **AF-5: 인증 실패** - JWT 토큰이 없거나 만료된 경우 HTTP 401 Unauthorized를 반환한다.
- **AF-6: endTime이 startTime 이전** - 수정 결과 endTime이 startTime보다 이전이 되면 HTTP 400 Bad Request를 반환한다.

## 검증 조건
- 확정된 일정(isConfirmed: true)은 workDate, startTime, endTime을 변경할 수 없다.
- workDate가 변경되면 변경된 날짜에 동일 근로자의 다른 일정이 없어야 한다.
- startTime과 endTime이 변경되면 endTime은 startTime보다 이후여야 한다.
- 수정 요청의 모든 필드가 null인 경우에도 에러 없이 기존 값을 유지하고 200 OK를 반환한다.
- EMPLOYEE 역할은 이 기능에 접근할 수 없다.
- MANAGER는 소속 매장의 일정만 수정 가능하다.

## 비기능 요구사항
- POLICY-NFR-001 참조
- API 응답 시간: 500ms 이내

## 테스트 시나리오

### TC-SCH-002-01: 정상 근무 일정 수정 (Unit)
- **Given**: scheduleId가 "sch-001"인 WorkSchedule이 존재하고, isConfirmed는 false, workTime은 09:00~18:00이다.
- **When**: startTime을 10:00, endTime을 19:00으로 수정 요청한다.
- **Then**: WorkSchedule의 workTime이 10:00~19:00으로 업데이트되고, workHours는 9.0이다.

### TC-SCH-002-02: 확정된 일정 수정 시도 (Unit)
- **Given**: scheduleId가 "sch-001"인 WorkSchedule이 존재하고, isConfirmed는 true이다.
- **When**: startTime을 10:00으로 수정 요청한다.
- **Then**: 에러코드 SCH003과 함께 예외가 발생하고, 일정은 변경되지 않는다.

### TC-SCH-002-03: 존재하지 않는 일정 수정 시도 (Unit)
- **Given**: scheduleId가 "sch-999"인 WorkSchedule이 존재하지 않는다.
- **When**: 수정 요청을 전송한다.
- **Then**: 에러코드 SCH001과 함께 예외가 발생한다.

### TC-SCH-002-04: workDate 변경 (Unit)
- **Given**: scheduleId가 "sch-001"인 WorkSchedule이 존재하고, isConfirmed는 false, workDate는 2026-03-10이다.
- **When**: workDate를 2026-03-11로 수정 요청한다.
- **Then**: WorkSchedule의 workDate가 2026-03-11로 업데이트된다.

### TC-SCH-002-05: EMPLOYEE 역할의 수정 시도 차단 (Integration)
- **Given**: EMPLOYEE 역할로 인증된 사용자가 존재한다.
- **When**: PUT /api/schedules/{scheduleId} 요청을 전송한다.
- **Then**: HTTP 403 Forbidden 응답이 반환된다.

### TC-SCH-002-06: 수정 API 전체 흐름 (E2E)
- **Given**: MANAGER 역할의 사용자가 인증되어 있고, 소속 매장의 미확정 일정이 존재한다.
- **When**: PUT /api/schedules/{scheduleId} 요청을 startTime, endTime과 함께 전송한다.
- **Then**: HTTP 200 OK 응답과 수정된 WorkScheduleResponse가 반환된다.
