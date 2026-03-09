# LMS-LEAVE-002 휴가승인

## 기본 정보
- type: use_case
- id: LMS-LEAVE-002
- domain: leave
- last-updated: 2026-03-09

## 관련 정책
- POLICY-LEAVE-001: 승인/반려 규칙 (§5), 연차 차감 규칙
- POLICY-NFR-001: 변경 이력 추적, 멀티 매장 지원

## 관련 Spec
- LMS-LEAVE-001-휴가신청 (선행)
- LMS-API-LEAVE-001-휴가API (PATCH /api/leaves/{leaveId}/approve)

## 관련 모델
- **주 모델**: `LeaveRequest` (Aggregate Root)
- 참조 모델: `Employee` (잔여 연차 차감), `UserId` (승인자), `LeaveStatus` (Enum)

## 개요
MANAGER 또는 SUPER_ADMIN이 PENDING 상태의 휴가 신청을 승인한다. 승인 시 LeaveRequest 상태를 APPROVED로 변경하고, 해당 근로자의 잔여 연차(remainingLeave)에서 승인된 일수만큼 차감한다.

## 기본 흐름
1. 승인자(MANAGER 또는 SUPER_ADMIN)가 대상 휴가 신청 ID(leaveId)를 지정하여 승인 요청을 보낸다.
2. 시스템이 해당 LeaveRequest를 조회한다. 존재하지 않으면 에러코드 LEAVE001을 반환한다 (HTTP 404).
3. 시스템이 해당 LeaveRequest의 상태가 PENDING인지 검증한다. PENDING이 아니면 에러코드 LEAVE005를 반환한다 (HTTP 409).
4. MANAGER인 경우, 시스템이 승인자의 소속 매장과 휴가 신청 근로자의 소속 매장이 동일한지 검증한다. 다르면 HTTP 403을 반환한다.
5. 시스템이 LeaveRequest 상태를 APPROVED로 변경하고, approvedBy에 승인자 UserId, approvedAt에 현재 시점을 기록한다.
6. 시스템이 해당 근로자의 잔여 연차(remainingLeave)에서 승인된 일수를 차감한다.
7. 시스템이 변경된 LeaveRequest 정보를 반환한다 (HTTP 200).

## 대안 흐름
- **AF-1**: SUPER_ADMIN이 승인하는 경우 → 매장 소속 검증(단계 4)을 건너뛴다.
- **AF-2**: EMPLOYEE 역할이 승인을 시도하는 경우 → HTTP 403을 반환한다.
- **AF-3**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.

## 검증 조건
- leaveId에 해당하는 LeaveRequest가 DB에 존재해야 한다. 위반 시 LEAVE001 / HTTP 404
- LeaveRequest의 status가 PENDING이어야 한다. 위반 시 LEAVE005 / HTTP 409
- MANAGER인 경우, 승인자의 소속 매장(storeId)과 신청자의 소속 매장(storeId)이 동일해야 한다. 위반 시 HTTP 403
- 승인자의 역할은 MANAGER 또는 SUPER_ADMIN이어야 한다. 위반 시 HTTP 403

## 비기능 요구사항
- **POLICY-NFR-001 §2.1**: 연차 차감과 상태 변경은 하나의 트랜잭션 내에서 원자적으로 처리한다.
- **POLICY-NFR-001 §3**: 승인 시 AuditLog에 기록한다 (EntityType: LEAVE_REQUEST, ActionType: APPROVE).
- **POLICY-NFR-001 §4**: MANAGER는 소속 매장 데이터만 접근 가능하다.
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-LEAVE-002-01: MANAGER의 PENDING 상태 휴가 승인 성공
- **레벨**: Integration
- **Given**: 매장 A에 소속된 MANAGER와, 같은 매장 A에 소속된 근로자의 PENDING 상태 휴가 신청(3일)이 존재한다. 근로자의 잔여 연차는 10일이다.
- **When**: MANAGER가 해당 휴가 신청을 승인한다.
- **Then**: LeaveRequest 상태가 APPROVED로 변경되고, 근로자의 잔여 연차가 7일로 차감된다. HTTP 200이 반환된다.

### TC-LEAVE-002-02: PENDING이 아닌 상태 승인 시도 실패
- **레벨**: Unit
- **Given**: REJECTED 상태의 휴가 신청이 존재한다.
- **When**: MANAGER가 해당 휴가 신청을 승인한다.
- **Then**: 에러코드 LEAVE005가 반환되고 상태가 변경되지 않는다. HTTP 409가 반환된다.

### TC-LEAVE-002-03: 타 매장 근로자 휴가 승인 시도 시 권한 오류
- **레벨**: Integration
- **Given**: 매장 A에 소속된 MANAGER와, 매장 B에 소속된 근로자의 PENDING 상태 휴가 신청이 존재한다.
- **When**: 매장 A MANAGER가 매장 B 근로자의 휴가 신청을 승인한다.
- **Then**: HTTP 403이 반환되고 상태가 변경되지 않는다.

### TC-LEAVE-002-04: 존재하지 않는 휴가 신청 승인 시도
- **레벨**: Unit
- **Given**: 존재하지 않는 leaveId.
- **When**: MANAGER가 해당 leaveId로 승인을 요청한다.
- **Then**: 에러코드 LEAVE001이 반환된다. HTTP 404가 반환된다.
