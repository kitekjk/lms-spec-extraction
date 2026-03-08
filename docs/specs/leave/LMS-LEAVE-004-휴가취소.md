# LMS-LEAVE-004: 휴가취소

## 기본 정보
- type: use_case
- domain: leave

## 관련 Spec
- LMS-API-LEAVE-001 (휴가API)
- LMS-LEAVE-001 (휴가신청)
- LMS-LEAVE-002 (휴가승인)

## 개요
근로자가 본인이 신청한 PENDING 또는 APPROVED 상태의 휴가를 취소한다.

## 관련 모델
- 주 모델: LeaveRequest (Aggregate Root)
- 참조 모델: Employee (잔여연차 복구 - 승인된 휴가 취소 시)

## 선행 조건
- 인증된 사용자여야 한다 (EMPLOYEE, MANAGER, SUPER_ADMIN)
- 취소 대상 휴가 신청이 존재해야 한다
- 휴가 신청이 PENDING 또는 APPROVED 상태여야 한다

## 기본 흐름
1. 근로자가 휴가 신청 ID를 지정하여 취소를 요청한다
2. 시스템은 휴가 신청을 조회한다
3. 시스템은 휴가 신청 상태가 PENDING 또는 APPROVED인지 확인한다
4. 시스템은 휴가를 취소한다 (status: CANCELLED)
5. 시스템은 휴가 신청을 저장한다
6. 시스템은 204 No Content를 반환한다

## 대안 흐름
- 승인된(APPROVED) 휴가를 취소하는 경우: 근로자의 잔여 연차를 복구해야 한다 (현재 구현에서는 별도 처리 필요)

## 예외 흐름
- 휴가 신청을 찾을 수 없는 경우: LeaveRequestNotFoundException (LEAVE001) 발생
- PENDING/APPROVED 이외 상태에서 취소 시도: LeaveRequestCannotBeCancelledException (LEAVE004) 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-LEAVE-001-휴가 참조

## 검증 조건
- 인증된 사용자여야 한다
- 취소 대상 휴가 신청이 존재해야 한다
- 휴가 신청이 PENDING 또는 APPROVED 상태여야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-LEAVE-004-01: PENDING 상태 휴가 취소 (Unit)
- Given: PENDING 상태의 휴가 신청이 존재
- When: 해당 휴가 신청의 취소를 요청
- Then: status가 CANCELLED로 변경되고, 204 No Content 응답

### TC-LEAVE-004-02: APPROVED 상태 휴가 취소 (Unit)
- Given: APPROVED 상태의 3일짜리 휴가 신청이 존재
- When: 해당 휴가 신청의 취소를 요청
- Then: status가 CANCELLED로 변경됨

### TC-LEAVE-004-03: 승인된 휴가 취소 시 잔여 연차 복구 확인 (Integration)
- Given: APPROVED 상태의 3일짜리 휴가 신청, 신청자의 잔여 연차 12일
- When: 해당 휴가 신청의 취소를 요청
- Then: 신청자의 잔여 연차가 15일(12+3)로 복구됨

### TC-LEAVE-004-04: REJECTED 상태 휴가 취소 시도 (Unit)
- Given: REJECTED 상태의 휴가 신청이 존재
- When: 해당 휴가 신청의 취소를 요청
- Then: LeaveRequestCannotBeCancelledException (LEAVE004) 발생 - "현재 상태에서는 휴가 신청을 취소할 수 없습니다."

### TC-LEAVE-004-05: CANCELLED 상태 휴가 재취소 시도 (Unit)
- Given: CANCELLED 상태의 휴가 신청이 존재
- When: 해당 휴가 신청의 취소를 요청
- Then: LeaveRequestCannotBeCancelledException (LEAVE004) 발생

### TC-LEAVE-004-06: 존재하지 않는 휴가 신청 취소 시도 (Unit)
- Given: 존재하지 않는 leaveRequestId
- When: 해당 휴가 신청의 취소를 요청
- Then: LeaveRequestNotFoundException (LEAVE001) 발생

### TC-LEAVE-004-07: PENDING 상태 취소 시 연차 복구 불필요 확인 (Integration)
- Given: PENDING 상태의 3일짜리 휴가 신청, 신청자의 잔여 연차 15일 (아직 차감 안 됨)
- When: 해당 휴가 신청의 취소를 요청
- Then: status가 CANCELLED로 변경되고, 잔여 연차는 15일 그대로 유지됨
