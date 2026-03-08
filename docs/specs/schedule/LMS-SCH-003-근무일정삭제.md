# LMS-SCH-003: 근무일정삭제

## 기본 정보
- type: use_case
- domain: schedule

## 관련 Spec
- LMS-API-SCH-001 (근무일정API)
- LMS-SCH-001 (근무일정등록)

## 개요
관리자가 근무 일정을 삭제한다.

## 관련 모델
- 주 모델: WorkSchedule (Aggregate Root)

## 선행 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 삭제 대상 근무 일정이 존재해야 한다

## 기본 흐름
1. 관리자가 일정 ID를 지정하여 삭제를 요청한다
2. 시스템은 일정을 조회한다
3. 시스템은 일정을 삭제한다
4. 시스템은 204 No Content를 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 일정을 찾을 수 없는 경우: WorkScheduleNotFoundException (SCH001) 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-SCHEDULE-001-근무일정 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 삭제 대상 근무 일정이 존재해야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-SCH-003-01: 정상 근무 일정 삭제 (Integration)
- Given: scheduleId에 해당하는 근무 일정이 존재하고, MANAGER 또는 SUPER_ADMIN이 인증된 상태
- When: 해당 일정의 삭제를 요청
- Then: 일정이 삭제되고, 204 No Content 응답

### TC-SCH-003-02: 존재하지 않는 일정 삭제 시도 (Unit)
- Given: 존재하지 않는 scheduleId
- When: 해당 일정의 삭제를 요청
- Then: WorkScheduleNotFoundException (SCH001) 발생

### TC-SCH-003-03: EMPLOYEE 권한으로 일정 삭제 시도 (E2E)
- Given: EMPLOYEE 역할의 사용자가 인증된 상태
- When: 근무 일정 삭제를 요청
- Then: 403 Forbidden 응답

### TC-SCH-003-04: 확정된 일정 삭제 가능 여부 확인 (Integration)
- Given: isConfirmed=true 상태의 근무 일정이 존재
- When: 해당 일정의 삭제를 요청
- Then: 일정이 정상적으로 삭제됨 (삭제는 확정 여부와 무관)
