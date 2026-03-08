# LMS-LEAVE-003: 휴가반려

## 기본 정보
- type: use_case
- domain: leave

## 관련 Spec
- LMS-API-LEAVE-001 (휴가API)
- LMS-LEAVE-001 (휴가신청)
- LMS-LEAVE-002 (휴가승인)

## 개요
관리자가 대기 중인 휴가 신청을 반려 사유와 함께 반려한다.

## 관련 모델
- 주 모델: LeaveRequest (Aggregate Root)
- 참조 모델: User (approverId)

## 선행 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 권한을 보유해야 한다
- 반려 대상 휴가 신청이 존재해야 한다
- 휴가 신청이 PENDING 상태여야 한다

## 기본 흐름
1. 관리자가 휴가 신청 ID와 반려 사유를 입력하여 반려를 요청한다
2. 시스템은 휴가 신청을 조회한다
3. 시스템은 휴가 신청 상태가 PENDING인지 확인한다
4. 시스템은 반려 사유가 비어있지 않은지 확인한다
5. 시스템은 휴가를 반려한다 (status: REJECTED, approvedBy, approvedAt, rejectionReason 설정)
6. 시스템은 휴가 신청을 저장하고 결과를 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 휴가 신청을 찾을 수 없는 경우: LeaveRequestNotFoundException (LEAVE001) 발생
- PENDING 상태가 아닌 경우: LeaveRequestCannotBeProcessedException (LEAVE005) 발생
- 반려 사유가 비어있는 경우: 유효성 검증 실패 (VALIDATION_ERROR)

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-LEAVE-001-휴가 참조

## 검증 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 권한을 보유해야 한다
- 반려 대상 휴가 신청이 존재해야 한다
- 휴가 신청이 PENDING 상태여야 한다
- 반려 사유가 비어있지 않아야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-LEAVE-003-01: 정상 휴가 반려 (Unit)
- Given: PENDING 상태의 휴가 신청이 존재하고, MANAGER가 인증된 상태
- When: 반려 사유 "인원 부족으로 해당 기간 휴가 불가"와 함께 반려를 요청
- Then: status가 REJECTED로 변경되고, rejectionReason에 반려 사유가 기록됨

### TC-LEAVE-003-02: 반려 사유 없이 반려 시도 (Unit)
- Given: PENDING 상태의 휴가 신청이 존재
- When: 반려 사유를 빈 문자열("")로 반려를 요청
- Then: 유효성 검증 실패 (VALIDATION_ERROR) 발생 - "거부 사유는 필수입니다."

### TC-LEAVE-003-03: PENDING 상태가 아닌 휴가 반려 시도 (Unit)
- Given: APPROVED 상태의 휴가 신청이 존재
- When: 해당 휴가 신청의 반려를 요청
- Then: LeaveRequestCannotBeProcessedException (LEAVE005) 발생 - "대기 중인 휴가 신청만 거부할 수 있습니다."

### TC-LEAVE-003-04: 존재하지 않는 휴가 신청 반려 시도 (Unit)
- Given: 존재하지 않는 leaveRequestId
- When: 해당 휴가 신청의 반려를 요청
- Then: LeaveRequestNotFoundException (LEAVE001) 발생

### TC-LEAVE-003-05: EMPLOYEE 권한으로 휴가 반려 시도 (E2E)
- Given: EMPLOYEE 역할의 사용자가 인증된 상태
- When: 휴가 반려를 요청
- Then: 403 Forbidden 응답

### TC-LEAVE-003-06: 이미 취소된 휴가 반려 시도 (Unit)
- Given: CANCELLED 상태의 휴가 신청이 존재
- When: 해당 휴가 신청의 반려를 요청
- Then: LeaveRequestCannotBeProcessedException (LEAVE005) 발생
