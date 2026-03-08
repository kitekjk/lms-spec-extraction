# LMS-LEAVE-002: 휴가승인

## 기본 정보
- type: use_case
- domain: leave

## 관련 Spec
- LMS-API-LEAVE-001 (휴가API)
- LMS-LEAVE-001 (휴가신청)
- LMS-LEAVE-003 (휴가반려)

## 개요
관리자가 대기 중인 휴가 신청을 승인하고 신청자의 잔여 연차를 차감한다.

## 관련 모델
- 주 모델: LeaveRequest (Aggregate Root)
- 참조 모델: Employee (잔여연차 차감), User (approverId)

## 선행 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 권한을 보유해야 한다
- 승인 대상 휴가 신청이 존재해야 한다
- 휴가 신청이 PENDING 상태여야 한다
- 휴가 신청자(Employee)가 존재해야 한다

## 기본 흐름
1. 관리자가 휴가 신청 ID를 지정하여 승인을 요청한다
2. 시스템은 휴가 신청을 조회한다
3. 시스템은 휴가 신청 상태가 PENDING인지 확인한다
4. 시스템은 신청자(Employee)를 조회한다
5. 시스템은 휴가를 승인한다 (status: APPROVED, approvedBy, approvedAt 설정)
6. 시스템은 신청자의 잔여 연차를 차감한다
7. 시스템은 휴가 신청과 근로자 정보를 저장하고 결과를 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 휴가 신청을 찾을 수 없는 경우: LeaveRequestNotFoundException (LEAVE001) 발생
- PENDING 상태가 아닌 경우: LeaveRequestCannotBeProcessedException (LEAVE005) 발생
- 근로자를 찾을 수 없는 경우: EmployeeNotFoundException (EMP001) 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-LEAVE-001-휴가 참조

## 검증 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 권한을 보유해야 한다
- 승인 대상 휴가 신청이 존재해야 한다
- 휴가 신청이 PENDING 상태여야 한다
- 휴가 신청자(Employee)가 존재해야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-LEAVE-002-01: 정상 휴가 승인 (Unit)
- Given: PENDING 상태의 휴가 신청이 존재하고, MANAGER가 인증된 상태
- When: 해당 휴가 신청의 승인을 요청
- Then: status가 APPROVED로 변경되고, approvedBy에 승인자 ID, approvedAt에 현재 시간이 기록됨

### TC-LEAVE-002-02: 승인 시 잔여 연차 차감 확인 (Integration)
- Given: PENDING 상태의 3일짜리 휴가 신청, 신청자의 잔여 연차 15일
- When: 휴가 승인을 요청
- Then: 신청자의 잔여 연차가 12일(15-3)로 차감됨

### TC-LEAVE-002-03: PENDING 상태가 아닌 휴가 승인 시도 (Unit)
- Given: REJECTED 상태의 휴가 신청이 존재
- When: 해당 휴가 신청의 승인을 요청
- Then: LeaveRequestCannotBeProcessedException (LEAVE005) 발생 - "대기 중인 휴가 신청만 승인할 수 있습니다."

### TC-LEAVE-002-04: 존재하지 않는 휴가 신청 승인 시도 (Unit)
- Given: 존재하지 않는 leaveRequestId
- When: 해당 휴가 신청의 승인을 요청
- Then: LeaveRequestNotFoundException (LEAVE001) 발생

### TC-LEAVE-002-05: 신청자 근로자를 찾을 수 없는 경우 (Integration)
- Given: PENDING 상태의 휴가 신청이 존재하지만, 신청자 Employee가 삭제됨
- When: 휴가 승인을 요청
- Then: EmployeeNotFoundException (EMP001) 발생

### TC-LEAVE-002-06: EMPLOYEE 권한으로 휴가 승인 시도 (E2E)
- Given: EMPLOYEE 역할의 사용자가 인증된 상태
- When: 휴가 승인을 요청
- Then: 403 Forbidden 응답

### TC-LEAVE-002-07: 이미 승인된 휴가 재승인 시도 (Unit)
- Given: APPROVED 상태의 휴가 신청이 존재
- When: 해당 휴가 신청의 승인을 요청
- Then: LeaveRequestCannotBeProcessedException (LEAVE005) 발생
