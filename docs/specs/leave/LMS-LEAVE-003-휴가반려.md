# LMS-LEAVE-003 휴가반려

## 기본 정보
- type: use_case
- id: LMS-LEAVE-003
- domain: leave
- last-updated: 2026-03-09

## 관련 정책
- POLICY-LEAVE-001: 승인/반려 규칙 (§5), 에러 코드
- POLICY-NFR-001: 변경 이력 추적, 멀티 매장 지원

## 관련 Spec
- LMS-LEAVE-001-휴가신청 (선행)
- LMS-API-LEAVE-001-휴가API (PATCH /api/leaves/{leaveId}/reject)

## 관련 모델
- **주 모델**: `LeaveRequest` (Aggregate Root)
- 참조 모델: `UserId` (반려 처리자), `LeaveStatus` (Enum)

## 개요
MANAGER 또는 SUPER_ADMIN이 PENDING 상태의 휴가 신청을 반려한다. 반려 시 반드시 반려 사유(rejectionReason)를 입력해야 하며, LeaveRequest 상태를 REJECTED로 변경한다. 반려된 휴가에서는 연차 차감이 발생하지 않는다.

## 기본 흐름
1. 반려 처리자(MANAGER 또는 SUPER_ADMIN)가 대상 휴가 신청 ID(leaveId)와 반려 사유(rejectionReason)를 입력한다.
2. 시스템이 해당 LeaveRequest를 조회한다. 존재하지 않으면 에러코드 LEAVE001을 반환한다 (HTTP 404).
3. 시스템이 해당 LeaveRequest의 상태가 PENDING인지 검증한다. PENDING이 아니면 에러코드 LEAVE005를 반환한다 (HTTP 409).
4. 시스템이 반려 사유(rejectionReason)가 비어있지 않은지 검증한다. 빈 문자열이면 HTTP 400을 반환한다.
5. MANAGER인 경우, 시스템이 반려 처리자의 소속 매장과 휴가 신청 근로자의 소속 매장이 동일한지 검증한다. 다르면 HTTP 403을 반환한다.
6. 시스템이 LeaveRequest 상태를 REJECTED로 변경하고, approvedBy에 처리자 UserId, approvedAt에 현재 시점, rejectionReason에 반려 사유를 기록한다.
7. 시스템이 변경된 LeaveRequest 정보를 반환한다 (HTTP 200).

## 대안 흐름
- **AF-1**: SUPER_ADMIN이 반려하는 경우 → 매장 소속 검증(단계 5)을 건너뛴다.
- **AF-2**: EMPLOYEE 역할이 반려를 시도하는 경우 → HTTP 403을 반환한다.
- **AF-3**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.

## 검증 조건
- leaveId에 해당하는 LeaveRequest가 DB에 존재해야 한다. 위반 시 LEAVE001 / HTTP 404
- LeaveRequest의 status가 PENDING이어야 한다. 위반 시 LEAVE005 / HTTP 409
- rejectionReason은 1자 이상의 비공백 문자열이어야 한다 (rejectionReason.isNotBlank() == true). 위반 시 HTTP 400
- MANAGER인 경우, 반려자의 소속 매장(storeId)과 신청자의 소속 매장(storeId)이 동일해야 한다. 위반 시 HTTP 403
- 반려자의 역할은 MANAGER 또는 SUPER_ADMIN이어야 한다. 위반 시 HTTP 403

## 비기능 요구사항
- **POLICY-NFR-001 §3**: 반려 시 AuditLog에 기록한다 (EntityType: LEAVE_REQUEST, ActionType: REJECT).
- **POLICY-NFR-001 §4**: MANAGER는 소속 매장 데이터만 접근 가능하다.
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-LEAVE-003-01: MANAGER의 PENDING 상태 휴가 반려 성공
- **레벨**: Integration
- **Given**: 매장 A에 소속된 MANAGER와, 같은 매장 A에 소속된 근로자의 PENDING 상태 휴가 신청이 존재한다.
- **When**: MANAGER가 반려 사유 "인원 부족으로 해당 기간 휴가 불가"를 입력하여 해당 휴가 신청을 반려한다.
- **Then**: LeaveRequest 상태가 REJECTED로 변경되고, rejectionReason에 입력된 사유가 기록된다. 근로자의 잔여 연차는 변경되지 않는다. HTTP 200이 반환된다.

### TC-LEAVE-003-02: 반려 사유 미입력 시 실패
- **레벨**: Unit
- **Given**: PENDING 상태의 휴가 신청이 존재한다.
- **When**: MANAGER가 반려 사유를 빈 문자열("")로 입력하여 반려한다.
- **Then**: HTTP 400이 반환되고 상태가 변경되지 않는다.

### TC-LEAVE-003-03: PENDING이 아닌 상태 반려 시도 실패
- **레벨**: Unit
- **Given**: APPROVED 상태의 휴가 신청이 존재한다.
- **When**: MANAGER가 해당 휴가 신청을 반려한다.
- **Then**: 에러코드 LEAVE005가 반환되고 상태가 변경되지 않는다. HTTP 409가 반환된다.
