# LMS-SCHEDULE-001: 근무 일정 생성

## 기본 정보
- type: use_case
- domain: schedule
- service: LMS
- priority: high

## 관련 정책
- POLICY-SCHEDULE-001 (MANAGER 또는 SUPER_ADMIN만 일정 생성, 소속 매장만)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-SCHEDULE-001-스케줄API](LMS-API-SCHEDULE-001-스케줄API.md)
- [LMS-EMPLOYEE-001-근로자등록](../employee/LMS-EMPLOYEE-001-근로자등록.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **WorkSchedule**: 생성 대상
  - 사용하는 주요 필드: employeeId, storeId, workDate, workTime, isConfirmed
  - 상태 변경: 새 WorkSchedule 생성 (isConfirmed=false)

### 참조 모델
- **Employee**: 소속 매장 검증
  - 참조하는 필드: storeId
- **Store**: 존재 여부 검증
  - 참조하는 필드: id

## 개요
근로자의 근무 일정을 특정 매장에 생성한다.

## 선행 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 역할이어야 한다
- 대상 Employee가 존재해야 한다
- 대상 Store가 존재해야 한다
- Employee가 해당 Store에 소속되어 있어야 한다

## 기본 흐름
1. Employee 존재 여부를 확인한다
2. Store 존재 여부를 확인한다
3. Employee의 storeId가 요청된 storeId와 일치하는지 확인한다
4. 동일 Employee, 동일 날짜에 이미 일정이 존재하는지 확인한다
5. WorkSchedule.create(context, employeeId, storeId, workDate, workTime)을 호출한다
6. WorkSchedule을 저장하고 결과를 반환한다

## 대안 흐름
- Employee가 존재하지 않는 경우: `EmployeeNotFoundException` 발생
- Store가 존재하지 않는 경우: `StoreNotFoundException` 발생
- Employee가 해당 Store에 소속되지 않은 경우: `EmployeeNotBelongToStoreException` 발생
- 동일 날짜에 이미 일정이 존재하는 경우: `DuplicateWorkScheduleException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 유효한 정보로 일정 생성 시 WorkSchedule이 생성되어야 한다
- 생성된 일정의 isConfirmed는 false여야 한다
- 존재하지 않는 Employee로 일정 생성 시 EmployeeNotFoundException이 발생해야 한다
- 존재하지 않는 Store로 일정 생성 시 StoreNotFoundException이 발생해야 한다
- Employee가 Store에 소속되지 않은 경우 EmployeeNotBelongToStoreException이 발생해야 한다
- 동일 Employee, 동일 날짜에 중복 일정 생성 시 DuplicateWorkScheduleException이 발생해야 한다
- startTime이 endTime 이후일 수 없다

## 비즈니스 규칙
- 하나의 Employee는 하나의 날짜에 하나의 WorkSchedule만 가질 수 있다
- WorkSchedule 생성 시 isConfirmed=false로 초기화된다
- WorkTime 표준 값: 09:00~18:00 (`WorkTime.standard()`)
- startTime은 endTime보다 이전이어야 한다
- WorkDate는 주말 여부를 판별할 수 있다 (`isWeekend()`)

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용

## 테스트 시나리오

### TC-SCH-001-01: 정상 일정 생성 (Integration)
- Given: 강남점에 소속된 활성 Employee가 존재한다
- When: 해당 Employee에 대해 일정을 생성한다
- Then: isConfirmed=false인 WorkSchedule이 생성된다

### TC-SCH-001-02: 미소속 매장 일정 생성 (Integration)
- Given: Employee가 강남점에 소속되어 있다
- When: 홍대점에 일정을 생성하려 한다
- Then: EmployeeNotBelongToStoreException이 발생한다

### TC-SCH-001-03: 중복 날짜 일정 생성 (Integration)
- Given: Employee에 2026-03-10 일정이 이미 존재한다
- When: 같은 날짜에 일정을 생성하려 한다
- Then: DuplicateWorkScheduleException이 발생한다

### TC-SCH-001-04: WorkTime 검증 (Unit)
- Given: startTime=18:00, endTime=09:00
- When: WorkTime을 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-SCH-001-05: 권한 검증 - EMPLOYEE 접근 (E2E)
- Given: EMPLOYEE 역할로 로그인한 상태이다
- When: 일정 생성 API를 호출한다
- Then: 403 Forbidden이 반환된다

### TC-SCH-001-06: 주말 일정 생성 (Integration)
- Given: 토요일 날짜가 주어진다
- When: 일정을 생성한다
- Then: WorkSchedule이 생성되고 workDate.isWeekend()가 true이다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
