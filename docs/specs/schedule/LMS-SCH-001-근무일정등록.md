# LMS-SCH-001: 근무일정등록

## 기본 정보
- type: use_case
- domain: schedule

## 관련 Spec
- LMS-API-SCH-001 (근무일정API)
- LMS-SCH-002 (근무일정수정)
- LMS-SCH-004 (근무일정조회)

## 개요
관리자가 근로자ID, 매장ID, 근무날짜, 시작시간, 종료시간을 입력하여 새로운 근무 일정을 생성한다.

## 관련 모델
- 주 모델: WorkSchedule (Aggregate Root)
- 참조 모델: Employee (employeeId 참조), Store (storeId 참조), WorkDate, WorkTime

## 선행 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 지정된 근로자가 존재해야 한다
- 지정된 매장이 존재해야 한다
- 근로자가 해당 매장에 소속되어 있어야 한다
- MANAGER는 자신의 매장 일정만 생성할 수 있다

## 기본 흐름
1. 관리자가 근로자ID, 매장ID, 근무날짜, 시작시간, 종료시간을 입력하여 일정 생성을 요청한다
2. 시스템은 근로자와 매장의 존재 여부를 확인한다
3. 시스템은 근로자가 해당 매장에 소속되어 있는지 확인한다
4. 시스템은 동일 근로자/날짜에 중복 일정이 있는지 확인한다
5. 시스템은 새로운 WorkSchedule을 생성한다 (isConfirmed=false)
6. 시스템은 일정을 저장하고 결과를 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 근로자를 찾을 수 없는 경우: EmployeeNotFoundException (EMP001) 발생
- 동일 근로자/날짜에 이미 일정이 존재하는 경우: DuplicateWorkScheduleException (SCH002) 발생
- 근로자가 매장에 속하지 않는 경우: EmployeeNotBelongToStoreException (SCH004) 발생
- MANAGER가 다른 매장 일정을 생성하려는 경우: ManagerCanOnlyManageOwnStoreSchedulesException (SCH005) 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-SCHEDULE-001-근무일정 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 지정된 근로자가 존재해야 한다
- 근로자가 해당 매장에 소속되어 있어야 한다
- 동일 근로자/날짜에 중복 일정이 없어야 한다
- MANAGER는 자신의 매장 일정만 생성할 수 있다
- 시작시간이 종료시간보다 늦을 수 없다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-SCH-001-01: 정상 근무 일정 등록 (Unit)
- Given: 근로자가 해당 매장에 소속되어 있고, 동일 날짜에 기존 일정이 없음
- When: 근로자ID, 매장ID, 근무날짜 2026-03-10, 시작시간 09:00, 종료시간 18:00으로 일정 생성을 요청
- Then: WorkSchedule이 생성되고, isConfirmed=false로 설정됨

### TC-SCH-001-02: 동일 근로자/날짜 중복 일정 등록 시도 (Unit)
- Given: 근로자에게 2026-03-10 날짜에 이미 근무 일정이 존재
- When: 동일 날짜에 다시 일정 생성을 요청
- Then: DuplicateWorkScheduleException (SCH002) 발생 - "이미 해당 날짜에 근무 일정이 존재합니다."

### TC-SCH-001-03: 매장 미소속 근로자에 대한 일정 등록 시도 (Unit)
- Given: 근로자가 storeId="store-A"에 소속되어 있음
- When: storeId="store-B"로 근무 일정 생성을 요청
- Then: EmployeeNotBelongToStoreException (SCH004) 발생

### TC-SCH-001-04: MANAGER가 타 매장 일정 등록 시도 (Integration)
- Given: MANAGER가 storeId="store-A"에 소속
- When: storeId="store-B"의 근무 일정 생성을 요청
- Then: ManagerCanOnlyManageOwnStoreSchedulesException (SCH005) 발생

### TC-SCH-001-05: 시작시간이 종료시간보다 늦은 일정 등록 시도 (Unit)
- Given: 유효한 근로자와 매장이 존재
- When: 시작시간 18:00, 종료시간 09:00으로 일정 생성을 요청
- Then: "시작 시간은 종료 시간보다 늦을 수 없습니다." 에러 발생

### TC-SCH-001-06: 존재하지 않는 근로자로 일정 등록 시도 (Integration)
- Given: 존재하지 않는 employeeId
- When: 해당 근로자의 근무 일정 생성을 요청
- Then: EmployeeNotFoundException (EMP001) 발생

### TC-SCH-001-07: 주말 근무 일정 등록 (Unit)
- Given: 유효한 근로자와 매장이 존재
- When: 토요일 날짜로 일정 생성을 요청
- Then: WorkSchedule이 생성되고, isWeekendWork()가 true를 반환함
