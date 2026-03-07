# LMS-SCHEDULE-002: 근무 일정 변경

## 기본 정보
- type: use_case
- domain: schedule
- service: LMS
- priority: medium

## 관련 정책
- POLICY-SCHEDULE-001 (확정된 일정 변경 불가, MANAGER 또는 SUPER_ADMIN만)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-SCHEDULE-001-스케줄API](LMS-API-SCHEDULE-001-스케줄API.md)
- [LMS-SCHEDULE-001-근무일정생성](LMS-SCHEDULE-001-근무일정생성.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **WorkSchedule**: 변경/삭제 대상
  - 사용하는 주요 필드: workDate, workTime, isConfirmed
  - 상태 변경: 시간/날짜 변경, 확정/확정해제

## 개요
근무 일정의 날짜, 시간을 변경하거나 일정을 삭제한다.

## 선행 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 역할이어야 한다
- 대상 WorkSchedule이 존재해야 한다

## 기본 흐름

### 수정
1. scheduleId로 WorkSchedule을 조회한다
2. 날짜가 변경된 경우 changeWorkDate(context, newWorkDate)를 호출한다
3. 시간이 변경된 경우 changeWorkTime(context, newWorkTime)를 호출한다
4. 수정된 WorkSchedule을 저장하고 결과를 반환한다

### 삭제
1. scheduleId로 WorkSchedule 존재 여부를 확인한다
2. WorkSchedule을 삭제한다

## 대안 흐름
- WorkSchedule이 존재하지 않는 경우: `WorkScheduleNotFoundException` 발생
- 확정된 일정 변경 시도: `ConfirmedScheduleCannotBeModifiedException` 발생 (도메인 require에 의해)

## 예외 흐름
- 없음

## 검증 조건
- 미확정 일정의 날짜/시간 변경이 정상 반영되어야 한다
- 확정된(isConfirmed=true) 일정의 날짜/시간 변경 시 require 실패해야 한다
- 존재하지 않는 일정 수정 시 WorkScheduleNotFoundException이 발생해야 한다
- 존재하지 않는 일정 삭제 시 WorkScheduleNotFoundException이 발생해야 한다
- 수정 command의 필드는 optional이며, 제공된 필드만 변경된다

## 비즈니스 규칙
- 확정된 일정은 시간/날짜 변경 불가 (changeWorkTime, changeWorkDate에서 require(!isConfirmed))
- 확정/확정해제는 별도 도메인 메서드 (confirm, unconfirm)
- UpdateWorkScheduleCommand의 모든 필드는 optional

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용

## 테스트 시나리오

### TC-SCH-002-01: 정상 시간 변경 (Integration)
- Given: 미확정 WorkSchedule이 존재한다
- When: 시간을 10:00~19:00으로 변경한다
- Then: 변경된 시간이 반영된다

### TC-SCH-002-02: 확정 일정 변경 시도 (Integration)
- Given: 확정된(isConfirmed=true) WorkSchedule이 존재한다
- When: 시간을 변경하려 한다
- Then: IllegalArgumentException이 발생한다

### TC-SCH-002-03: 정상 삭제 (Integration)
- Given: WorkSchedule이 존재한다
- When: 삭제를 요청한다
- Then: WorkSchedule이 삭제된다

### TC-SCH-002-04: 존재하지 않는 일정 변경 (Integration)
- Given: 존재하지 않는 scheduleId가 주어진다
- When: 수정을 시도한다
- Then: WorkScheduleNotFoundException이 발생한다

### TC-SCH-002-05: 확정/확정해제 도메인 규칙 (Unit)
- Given: 미확정 WorkSchedule 도메인 객체
- When: confirm()을 호출한다
- Then: isConfirmed=true인 새 인스턴스가 반환된다

### TC-SCH-002-06: 권한 검증 - EMPLOYEE 접근 (E2E)
- Given: EMPLOYEE 역할로 로그인한 상태이다
- When: 일정 수정 API를 호출한다
- Then: 403 Forbidden이 반환된다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
