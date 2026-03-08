# LMS-LEAVE-001: 휴가신청

## 기본 정보
- type: use_case
- domain: leave

## 관련 Spec
- LMS-API-LEAVE-001 (휴가API)
- LMS-LEAVE-002 (휴가승인)
- LMS-LEAVE-005 (휴가조회)

## 개요
근로자가 휴가유형, 시작일, 종료일을 입력하여 휴가를 신청한다.

## 관련 모델
- 주 모델: LeaveRequest (Aggregate Root)
- 참조 모델: Employee (employeeId 참조, 잔여연차 확인), LeavePeriod, LeaveType, LeaveStatus, LeavePolicyService

## 선행 조건
- 인증된 사용자여야 한다 (EMPLOYEE, MANAGER, SUPER_ADMIN)
- 신청자에 해당하는 Employee 정보가 존재해야 한다
- 잔여 연차가 충분해야 한다 (정규직/계약직)

## 기본 흐름
1. 근로자가 휴가유형, 시작일, 종료일, 사유(선택)를 입력하여 휴가 신청을 요청한다
2. 시스템은 현재 로그인한 사용자의 ID를 employeeId로 사용한다
3. 시스템은 근로자 정보를 조회한다
4. 시스템은 날짜 유효성을 검증한다:
   - 시작일이 과거가 아닌지 확인
   - 시작일이 종료일 이전인지 확인
5. 시스템은 LeavePeriod를 생성하고 신청일수를 계산한다
6. 시스템은 잔여 연차를 검증한다 (LeavePolicyService)
7. 시스템은 기존 승인된 휴가와 기간이 겹치는지 확인한다
8. 시스템은 새로운 LeaveRequest를 생성한다 (status: PENDING)
9. 시스템은 휴가 신청을 저장하고 결과를 반환한다

## 대안 흐름
- PART_TIME(아르바이트)의 경우: 잔여 연차 검증을 건너뛸 수 있음

## 예외 흐름
- 근로자를 찾을 수 없는 경우: EmployeeNotFoundException (EMP001) 발생
- 과거 날짜로 신청한 경우: PastDateLeaveRequestException (LEAVE006) 발생
- 시작일이 종료일 이후인 경우: InvalidLeaveDateRangeException (LEAVE007) 발생
- 잔여 연차가 부족한 경우: InsufficientLeaveBalanceException (LEAVE002) 발생
- 기존 승인된 휴가와 기간이 겹치는 경우: LeaveRequestDateOverlapException (LEAVE003) 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-LEAVE-001-휴가 참조

## 검증 조건
- 인증된 사용자여야 한다
- 신청자에 해당하는 Employee 정보가 존재해야 한다
- 시작일이 과거가 아니어야 한다
- 시작일이 종료일 이전이어야 한다
- 잔여 연차가 충분해야 한다 (정규직/계약직)
- 기존 승인된 휴가와 기간이 겹치지 않아야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-LEAVE-001-01: 정규직 근로자 정상 휴가 신청 (Unit)
- Given: REGULAR 근로자가 잔여 연차 15일 보유, 기존 승인된 휴가와 기간이 겹치지 않음
- When: 유형 ANNUAL, 시작일 2026-03-16, 종료일 2026-03-18 (3일)로 휴가 신청을 요청
- Then: LeaveRequest가 생성되고, status=PENDING, 신청일수=3일로 설정됨

### TC-LEAVE-001-02: 아르바이트 근로자 휴가 신청 - 연차 검증 건너뛰기 (Unit)
- Given: PART_TIME 근로자 (잔여 연차 0일)
- When: 유형 UNPAID, 시작일 2026-03-16, 종료일 2026-03-16으로 휴가 신청을 요청
- Then: 잔여 연차 검증 없이 LeaveRequest가 정상 생성됨

### TC-LEAVE-001-03: 잔여 연차 부족 시 휴가 신청 (Unit)
- Given: REGULAR 근로자가 잔여 연차 2일 보유
- When: 시작일 2026-03-16, 종료일 2026-03-20 (5일)로 휴가 신청을 요청
- Then: InsufficientLeaveBalanceException (LEAVE002) 발생 - "잔여 연차가 부족합니다. 신청: 5일, 잔여: 2일"

### TC-LEAVE-001-04: 과거 날짜로 휴가 신청 시도 (Unit)
- Given: 오늘이 2026-03-09
- When: 시작일 2026-03-01로 휴가 신청을 요청
- Then: PastDateLeaveRequestException (LEAVE006) 발생

### TC-LEAVE-001-05: 시작일이 종료일 이후인 경우 (Unit)
- Given: 인증된 근로자
- When: 시작일 2026-03-20, 종료일 2026-03-16으로 휴가 신청을 요청
- Then: InvalidLeaveDateRangeException (LEAVE007) 발생

### TC-LEAVE-001-06: 기존 승인된 휴가와 기간 중복 (Integration)
- Given: 2026-03-16~2026-03-18 기간에 이미 APPROVED 상태의 휴가가 존재
- When: 2026-03-17~2026-03-19 기간으로 휴가 신청을 요청
- Then: LeaveRequestDateOverlapException (LEAVE003) 발생 - "이미 승인된 휴가와 기간이 겹칩니다."

### TC-LEAVE-001-07: 근로자를 찾을 수 없는 경우 (Integration)
- Given: 존재하지 않는 employeeId로 인증된 사용자
- When: 휴가 신청을 요청
- Then: EmployeeNotFoundException (EMP001) 발생

### TC-LEAVE-001-08: 휴가 일수 계산 - 시작일과 종료일 동일 (Unit)
- Given: 인증된 근로자
- When: 시작일 2026-03-16, 종료일 2026-03-16으로 휴가 신청을 요청
- Then: 신청일수가 1일로 계산됨 (시작일과 종료일 모두 포함)
