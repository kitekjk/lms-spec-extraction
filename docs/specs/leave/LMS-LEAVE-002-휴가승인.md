# LMS-LEAVE-002: 휴가 승인

## 기본 정보
- type: use_case
- domain: leave
- service: LMS
- priority: high

## 관련 정책
- POLICY-LEAVE-001 (상태 전이 규칙, 승인 시 연차 차감, 취소 시 연차 복원)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-LEAVE-001-휴가API](LMS-API-LEAVE-001-휴가API.md)
- [LMS-LEAVE-001-휴가신청](LMS-LEAVE-001-휴가신청.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **LeaveRequest**: 상태 변경 대상
  - 사용하는 주요 필드: status, approvedBy, approvedAt, rejectionReason
  - 상태 변경: PENDING → APPROVED/REJECTED/CANCELLED, APPROVED → CANCELLED

### 참조 모델
- **Employee**: 연차 차감/복원 대상
  - 참조하는 필드: remainingLeave

## 개요
관리자가 휴가 신청을 승인, 거절, 또는 취소한다.

## 선행 조건
- 승인/거절: 요청자가 MANAGER 또는 SUPER_ADMIN 역할이어야 한다
- 취소: 요청자가 EMPLOYEE, MANAGER 또는 SUPER_ADMIN 역할이어야 한다
- 대상 LeaveRequest가 존재해야 한다

## 기본 흐름

### 승인
1. leaveRequestId로 LeaveRequest를 조회한다
2. 현재 상태가 PENDING인지 확인한다
3. Employee를 조회한다
4. LeaveRequest.approve(context, approverId)를 호출한다
5. Employee.deductLeave(context, days)로 연차를 차감한다
6. LeaveRequest와 Employee를 모두 저장한다

### 거절
1. leaveRequestId로 LeaveRequest를 조회한다
2. 현재 상태가 PENDING인지 확인한다
3. LeaveRequest.reject(context, rejectorId, rejectionReason)을 호출한다
4. LeaveRequest를 저장한다

### 취소
1. leaveRequestId로 LeaveRequest를 조회한다
2. 현재 상태가 PENDING 또는 APPROVED인지 확인한다
3. 기존 상태가 APPROVED였는지 기록한다
4. LeaveRequest.cancel(context)을 호출한다
5. APPROVED였던 경우 Employee.restoreLeave(context, days)로 연차를 복원한다
6. LeaveRequest와 Employee를 저장한다

## 대안 흐름
- LeaveRequest가 존재하지 않는 경우: `LeaveRequestNotFoundException` 발생
- PENDING이 아닌 상태에서 승인/거절 시도: `LeaveRequestCannotBeProcessedException` 발생
- PENDING/APPROVED가 아닌 상태에서 취소 시도: `LeaveRequestCannotBeCancelledException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 승인 후 status=APPROVED, approvedBy 설정, approvedAt 설정되어야 한다
- 승인 후 Employee의 remainingLeave가 휴가 일수만큼 차감되어야 한다
- 거절 후 status=REJECTED, rejectionReason이 기록되어야 한다
- 거절 시 rejectionReason이 비어있으면 require 실패해야 한다
- 거절 후 Employee의 remainingLeave는 변동 없어야 한다
- APPROVED 상태 취소 후 Employee의 remainingLeave가 복원되어야 한다
- PENDING 상태 취소 후 Employee의 remainingLeave는 변동 없어야 한다
- REJECTED/CANCELLED 상태에서 승인 시도 시 예외가 발생해야 한다

## 비즈니스 규칙
- 상태 전이: PENDING → APPROVED, PENDING → REJECTED, PENDING → CANCELLED, APPROVED → CANCELLED
- 승인 시 즉시 연차 차감 (같은 트랜잭션)
- 취소 시 이전 상태가 APPROVED였으면 연차 복원
- 거절 사유(rejectionReason)는 비어있을 수 없음

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용. 추가 특화 사항:

### 데이터 정합성
- 연차 차감/복원과 LeaveRequest 상태 변경은 같은 트랜잭션에서 처리되어야 한다

## 테스트 시나리오

### TC-LEAVE-002-01: 정상 승인 (Integration)
- Given: PENDING 상태의 LeaveRequest가 존재하고, Employee의 잔여 연차가 충분하다
- When: 승인한다
- Then: status=APPROVED, Employee.remainingLeave가 차감된다

### TC-LEAVE-002-02: 정상 거절 (Integration)
- Given: PENDING 상태의 LeaveRequest가 존재한다
- When: 사유와 함께 거절한다
- Then: status=REJECTED, rejectionReason이 기록되고, remainingLeave 변동 없다

### TC-LEAVE-002-03: 승인 후 취소 (Integration)
- Given: APPROVED 상태의 LeaveRequest가 존재한다
- When: 취소한다
- Then: status=CANCELLED, Employee.remainingLeave가 복원된다

### TC-LEAVE-002-04: PENDING 취소 (Integration)
- Given: PENDING 상태의 LeaveRequest가 존재한다
- When: 취소한다
- Then: status=CANCELLED, Employee.remainingLeave 변동 없다

### TC-LEAVE-002-05: 이미 거절된 휴가 승인 시도 (Integration)
- Given: REJECTED 상태의 LeaveRequest가 존재한다
- When: 승인을 시도한다
- Then: LeaveRequestCannotBeProcessedException이 발생한다

### TC-LEAVE-002-06: 거절 사유 누락 (Unit)
- Given: rejectionReason이 빈 문자열이다
- When: LeaveRequest.reject()를 호출한다
- Then: require 실패로 IllegalArgumentException이 발생한다

### TC-LEAVE-002-07: 권한 검증 - EMPLOYEE 승인 시도 (E2E)
- Given: EMPLOYEE 역할로 로그인한 상태이다
- When: 휴가 승인 API를 호출한다
- Then: 403 Forbidden이 반환된다

### TC-LEAVE-002-08: 트랜잭션 정합성 (Integration)
- Given: PENDING 상태의 LeaveRequest가 존재한다
- When: 승인 중 Employee 저장에서 오류가 발생한다
- Then: LeaveRequest 상태 변경도 롤백되어 PENDING 유지

## 관련 이벤트
- 발행: 없음
- 수신: 없음
