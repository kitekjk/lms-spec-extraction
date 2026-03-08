# LMS-SCH-004: 근무일정조회

## 기본 정보
- type: use_case
- domain: schedule

## 관련 Spec
- LMS-API-SCH-001 (근무일정API)

## 개요
인증된 사용자가 조건별로 근무 일정을 조회하거나, 본인의 근무 일정을 조회한다.

## 관련 모델
- 주 모델: WorkSchedule (Aggregate Root)
- 참조 모델: Employee (employeeId 참조), Store (storeId 참조)

## 선행 조건
- 인증된 사용자여야 한다 (EMPLOYEE, MANAGER, SUPER_ADMIN)

## 기본 흐름 (필터링 조회)
1. 사용자가 조건(employeeId, storeId, startDate, endDate)을 지정하여 근무 일정 조회를 요청한다
2. 시스템은 조건에 따라 일정을 조회한다:
   - storeId + startDate + endDate: 매장별 기간 조회
   - employeeId: 근로자별 조회
   - storeId: 매장별 조회
3. 시스템은 일정 목록과 총 건수를 반환한다

## 대안 흐름
- 본인 일정 조회 (/my-schedule): 현재 로그인한 사용자의 근무 일정만 조회한다
- 상세 조회 (scheduleId 지정): 특정 일정의 상세 정보를 조회한다

## 예외 흐름
- 필터 파라미터 없이 조회 시: IllegalArgumentException ("employeeId 또는 storeId 파라미터가 필요합니다") 발생
- 상세 조회 시 일정을 찾을 수 없는 경우: 404 Not Found 응답

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-SCHEDULE-001-근무일정 참조

## 검증 조건
- 인증된 사용자여야 한다
- 필터 조회 시 employeeId 또는 storeId 중 하나 이상의 파라미터가 필요하다
- 상세 조회 시 해당 일정이 존재해야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-SCH-004-01: 매장별 기간 조회 (Integration)
- Given: storeId="store-A"에 2026-03-01~2026-03-09 기간 동안 5건의 일정이 존재
- When: storeId="store-A", startDate=2026-03-01, endDate=2026-03-09로 조회를 요청
- Then: 5건의 일정 목록과 총 건수 5가 반환됨

### TC-SCH-004-02: 근로자별 조회 (Integration)
- Given: 특정 employeeId에 대해 3건의 일정이 존재
- When: employeeId로 조회를 요청
- Then: 해당 근로자의 3건의 일정 목록이 반환됨

### TC-SCH-004-03: 본인 일정 조회 (/my-schedule) (Integration)
- Given: 현재 로그인한 근로자에게 이번 주 일정 3건이 존재
- When: /my-schedule 엔드포인트로 조회를 요청
- Then: 본인의 일정 3건만 반환됨

### TC-SCH-004-04: 필터 파라미터 없이 조회 시도 (Unit)
- Given: employeeId와 storeId 모두 미지정
- When: 근무 일정 조회를 요청
- Then: IllegalArgumentException 발생 - "employeeId 또는 storeId 파라미터가 필요합니다"

### TC-SCH-004-05: 일정 상세 조회 (Integration)
- Given: 특정 scheduleId에 해당하는 일정이 존재
- When: 해당 scheduleId로 상세 조회를 요청
- Then: 일정의 상세 정보(근로자, 매장, 날짜, 시간, 확정 여부)가 반환됨

### TC-SCH-004-06: 존재하지 않는 일정 상세 조회 (E2E)
- Given: 존재하지 않는 scheduleId
- When: 해당 scheduleId로 상세 조회를 요청
- Then: 404 Not Found 응답

### TC-SCH-004-07: 조회 결과 없는 기간 조회 (Integration)
- Given: storeId="store-A"에 2026-04-01~2026-04-30 기간 동안 일정이 없음
- When: 해당 조건으로 조회를 요청
- Then: 빈 목록과 총 건수 0이 반환됨
