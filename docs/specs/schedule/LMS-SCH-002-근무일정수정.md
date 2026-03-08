# LMS-SCH-002: 근무일정수정

## 기본 정보
- type: use_case
- domain: schedule

## 관련 Spec
- LMS-API-SCH-001 (근무일정API)
- LMS-SCH-001 (근무일정등록)

## 개요
관리자가 미확정 상태의 근무 일정의 날짜, 시작시간, 종료시간을 수정한다.

## 관련 모델
- 주 모델: WorkSchedule (Aggregate Root)
- 참조 모델: WorkDate, WorkTime

## 선행 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 수정 대상 근무 일정이 존재해야 한다
- 근무 일정이 미확정(isConfirmed=false) 상태여야 한다

## 기본 흐름
1. 관리자가 일정 ID와 수정할 정보(근무날짜, 시작시간, 종료시간)를 입력하여 수정을 요청한다
2. 시스템은 일정을 조회한다
3. 시스템은 일정의 확정 상태를 확인한다
4. 시스템은 일정 정보를 수정한다 (workDate, startTime, endTime - 각각 선택적 수정 가능)
5. 시스템은 수정된 일정을 저장하고 결과를 반환한다

## 대안 흐름
- 일부 필드만 수정: workDate, startTime, endTime 중 null이 아닌 필드만 수정한다

## 예외 흐름
- 일정을 찾을 수 없는 경우: WorkScheduleNotFoundException (SCH001) 발생
- 확정된 일정을 수정하려는 경우: ConfirmedScheduleCannotBeModifiedException (SCH003) 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-SCHEDULE-001-근무일정 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 수정 대상 근무 일정이 존재해야 한다
- 근무 일정이 미확정(isConfirmed=false) 상태여야 한다
- 시작시간이 종료시간보다 늦을 수 없다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-SCH-002-01: 미확정 일정 정상 수정 (Unit)
- Given: isConfirmed=false 상태의 근무 일정이 존재
- When: 근무날짜, 시작시간 10:00, 종료시간 19:00으로 수정을 요청
- Then: 일정의 workDate, startTime, endTime이 정상적으로 업데이트됨

### TC-SCH-002-02: 확정된 일정 수정 시도 (Unit)
- Given: isConfirmed=true 상태의 근무 일정이 존재
- When: 일정 수정을 요청
- Then: ConfirmedScheduleCannotBeModifiedException (SCH003) 발생 - "확정된 근무 일정은 수정할 수 없습니다."

### TC-SCH-002-03: 존재하지 않는 일정 수정 시도 (Unit)
- Given: 존재하지 않는 scheduleId
- When: 해당 일정의 수정을 요청
- Then: WorkScheduleNotFoundException (SCH001) 발생

### TC-SCH-002-04: 일부 필드만 수정 (Unit)
- Given: isConfirmed=false 상태의 근무 일정이 존재 (날짜 2026-03-10, 시작 09:00, 종료 18:00)
- When: startTime만 10:00으로 변경하고 나머지는 null로 요청
- Then: startTime만 10:00으로 변경되고, 나머지 필드는 기존 값 유지

### TC-SCH-002-05: 수정 시 시작시간이 종료시간보다 늦은 경우 (Unit)
- Given: isConfirmed=false 상태의 근무 일정이 존재
- When: 시작시간 20:00, 종료시간 09:00으로 수정을 요청
- Then: "시작 시간은 종료 시간보다 늦을 수 없습니다." 에러 발생
