# LMS-LEAVE-001: 휴가 신청

## 기본 정보
- type: use_case
- domain: leave
- service: LMS
- priority: high

## 관련 정책
- POLICY-LEAVE-001 (연차 정책, 과거 날짜 불가, 기간 중복 불가, PART_TIME 예외)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-LEAVE-001-휴가API](LMS-API-LEAVE-001-휴가API.md)
- [LMS-LEAVE-002-휴가승인](LMS-LEAVE-002-휴가승인.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **LeaveRequest**: 생성 대상
  - 사용하는 주요 필드: employeeId, leaveType, leavePeriod, status, reason
  - 상태 변경: 새 LeaveRequest 생성 (status=PENDING)

### 참조 모델
- **Employee**: 잔여 연차 검증
  - 참조하는 필드: employeeType, remainingLeave

## 개요
근로자가 휴가를 신청한다. 5단계 유효성 검증을 거친다.

## 선행 조건
- 요청자가 EMPLOYEE, MANAGER 또는 SUPER_ADMIN 역할이어야 한다
- 해당 Employee가 존재해야 한다

## 기본 흐름
1. Employee를 조회한다
2. 날짜 유효성을 검증한다 (과거 날짜, 날짜 범위)
3. LeavePeriod(startDate, endDate)를 생성하고 휴가 일수를 계산한다 (종료일 - 시작일 + 1)
4. LeavePolicyService.validateLeaveRequest()로 잔여 연차를 검증한다
5. 기존 휴가 신청을 조회하여 APPROVED 상태인 휴가와 기간 중복 여부를 확인한다
6. LeaveRequest.create(context, employeeId, leaveType, leavePeriod, reason)을 호출한다
7. LeaveRequest를 저장하고 결과를 반환한다

## 대안 흐름
- Employee가 존재하지 않는 경우: `EmployeeNotFoundException` 발생
- 시작일이 과거인 경우: `PastDateLeaveRequestException` 발생
- 시작일이 종료일 이후인 경우: `InvalidLeaveDateRangeException` 발생
- 잔여 연차가 부족한 경우: `InsufficientLeaveBalanceException` 발생
- 승인된 기존 휴가와 기간이 겹치는 경우: `LeaveRequestDateOverlapException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 유효한 정보로 휴가 신청 시 LeaveRequest가 PENDING 상태로 생성되어야 한다
- 시작일이 과거인 경우 PastDateLeaveRequestException이 발생해야 한다
- 시작일이 종료일 이후인 경우 InvalidLeaveDateRangeException이 발생해야 한다
- 잔여 연차가 신청 일수보다 적으면 InsufficientLeaveBalanceException이 발생해야 한다
- PART_TIME 근로자는 항상 휴가 신청 가능 (canRequestLeave에서 항상 true)
- 이미 APPROVED된 휴가와 기간이 겹치면 LeaveRequestDateOverlapException이 발생해야 한다
- 휴가 일수 = endDate - startDate + 1 (양 끝 포함)

## 비즈니스 규칙
- 모든 LeaveType은 승인이 필요하다 (requiresApproval=true)
- LeaveType: ANNUAL, SICK, PERSONAL, MATERNITY, PATERNITY, BEREAVEMENT, UNPAID
- 중복 검사 대상: APPROVED 상태의 기존 휴가만 (PENDING, REJECTED, CANCELLED 제외)
- LeavePeriod.overlapsWith()로 기간 중복 여부 판정
- PART_TIME 근로자는 잔여 연차 검증을 건너뜀

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용

## 테스트 시나리오

### TC-LEAVE-001-01: 정상 휴가 신청 (Integration)
- Given: REGULAR Employee가 존재하고 잔여 연차가 15.0일이다
- When: 3일 연차 휴가를 신청한다
- Then: PENDING 상태의 LeaveRequest가 생성된다

### TC-LEAVE-001-02: 과거 날짜 신청 (Integration)
- Given: 시작일이 어제이다
- When: 휴가를 신청한다
- Then: PastDateLeaveRequestException이 발생한다

### TC-LEAVE-001-03: 잔여 연차 부족 (Integration)
- Given: REGULAR Employee의 잔여 연차가 2.0일이다
- When: 3일 휴가를 신청한다
- Then: InsufficientLeaveBalanceException이 발생한다

### TC-LEAVE-001-04: PART_TIME 무제한 신청 (Integration)
- Given: PART_TIME Employee (잔여 연차 0.0일)
- When: 무급 휴가를 신청한다
- Then: 정상적으로 PENDING 상태의 LeaveRequest가 생성된다

### TC-LEAVE-001-05: 기간 중복 (Integration)
- Given: 3/10~3/12 APPROVED 휴가가 존재한다
- When: 3/11~3/15 휴가를 신청한다
- Then: LeaveRequestDateOverlapException이 발생한다

### TC-LEAVE-001-06: LeavePeriod 검증 (Unit)
- Given: startDate가 endDate 이후이다
- When: LeavePeriod를 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-LEAVE-001-07: 날짜 범위 역전 (Integration)
- Given: startDate=3/15, endDate=3/10
- When: 휴가를 신청한다
- Then: InvalidLeaveDateRangeException이 발생한다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
