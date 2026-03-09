# LMS-LEAVE-004 휴가취소

## 기본 정보
- type: use_case
- id: LMS-LEAVE-004
- domain: leave
- last-updated: 2026-03-09

## 관련 정책
- POLICY-LEAVE-001: 휴가 취소 규칙 (§6), 연차 복구 규칙
- POLICY-NFR-001: 데이터 무결성, 변경 이력 추적

## 관련 Spec
- LMS-LEAVE-001-휴가신청 (선행)
- LMS-LEAVE-002-휴가승인 (APPROVED 상태 취소 시)
- LMS-API-LEAVE-001-휴가API (DELETE /api/leaves/{leaveId})

## 관련 모델
- **주 모델**: `LeaveRequest` (Aggregate Root)
- 참조 모델: `Employee` (잔여 연차 복구), `LeaveStatus` (Enum)

## 개요
근로자(EMPLOYEE, MANAGER, SUPER_ADMIN)가 본인이 신청한 PENDING 또는 APPROVED 상태의 휴가를 취소한다. APPROVED 상태의 휴가를 취소하면 차감된 연차가 복구된다. REJECTED 또는 CANCELLED 상태의 휴가는 취소할 수 없다.

## 기본 흐름
1. 사용자가 취소할 휴가 신청 ID(leaveId)를 지정하여 취소 요청을 보낸다.
2. 시스템이 해당 LeaveRequest를 조회한다. 존재하지 않으면 에러코드 LEAVE001을 반환한다 (HTTP 404).
3. 시스템이 해당 LeaveRequest의 상태가 PENDING 또는 APPROVED인지 검증한다. 그 외 상태이면 에러코드 LEAVE004를 반환한다 (HTTP 409).
4. 기존 상태가 APPROVED인 경우, 시스템이 해당 근로자의 잔여 연차(remainingLeave)에 취소된 휴가 일수를 복구한다.
5. 시스템이 LeaveRequest 상태를 CANCELLED로 변경하고 저장한다.
6. 시스템이 HTTP 204 (No Content)를 반환한다.

## 대안 흐름
- **AF-1**: PENDING 상태 취소 → 연차 복구 없이 상태만 CANCELLED로 변경한다 (연차가 아직 차감되지 않았으므로).
- **AF-2**: REJECTED 상태 취소 시도 → 에러코드 LEAVE004, HTTP 409를 반환한다.
- **AF-3**: CANCELLED 상태 취소 시도 → 에러코드 LEAVE004, HTTP 409를 반환한다.
- **AF-4**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.

## 검증 조건
- leaveId에 해당하는 LeaveRequest가 DB에 존재해야 한다. 위반 시 LEAVE001 / HTTP 404
- LeaveRequest의 status가 PENDING 또는 APPROVED여야 한다. REJECTED, CANCELLED 상태는 취소 불가. 위반 시 LEAVE004 / HTTP 409
- 취소 요청자는 본인(신청자), MANAGER, 또는 SUPER_ADMIN이어야 한다. 위반 시 HTTP 403

## 비기능 요구사항
- **POLICY-NFR-001 §2.1**: APPROVED 상태 취소 시 연차 복구와 상태 변경은 하나의 트랜잭션 내에서 원자적으로 처리한다.
- **POLICY-NFR-001 §3**: 취소 시 AuditLog에 기록한다 (EntityType: LEAVE_REQUEST, ActionType: CANCEL).
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-LEAVE-004-01: PENDING 상태 휴가 취소 성공
- **레벨**: Unit
- **Given**: PENDING 상태의 휴가 신청(3일)이 존재하고, 근로자의 잔여 연차가 10일이다.
- **When**: 해당 근로자가 휴가 신청을 취소한다.
- **Then**: LeaveRequest 상태가 CANCELLED로 변경되고, 근로자의 잔여 연차는 10일로 유지된다. HTTP 204가 반환된다.

### TC-LEAVE-004-02: APPROVED 상태 휴가 취소 성공 (연차 복구)
- **레벨**: Integration
- **Given**: APPROVED 상태의 휴가 신청(3일)이 존재하고, 근로자의 잔여 연차가 7일이다 (승인 시 10일에서 3일 차감됨).
- **When**: 해당 근로자가 휴가 신청을 취소한다.
- **Then**: LeaveRequest 상태가 CANCELLED로 변경되고, 근로자의 잔여 연차가 10일로 복구된다. HTTP 204가 반환된다.

### TC-LEAVE-004-03: REJECTED 상태 휴가 취소 시도 실패
- **레벨**: Unit
- **Given**: REJECTED 상태의 휴가 신청이 존재한다.
- **When**: 해당 근로자가 휴가 신청을 취소한다.
- **Then**: 에러코드 LEAVE004가 반환되고 상태가 변경되지 않는다. HTTP 409가 반환된다.

### TC-LEAVE-004-04: CANCELLED 상태 휴가 취소 시도 실패
- **레벨**: Unit
- **Given**: CANCELLED 상태의 휴가 신청이 존재한다.
- **When**: 해당 근로자가 휴가 신청을 취소한다.
- **Then**: 에러코드 LEAVE004가 반환되고 상태가 변경되지 않는다. HTTP 409가 반환된다.
