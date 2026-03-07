# LMS-API-LEAVE-001: 휴가 API

## 기본 정보
- type: api_spec
- domain: leave
- service: LMS
- base_path: /api/leaves

## 관련 Spec
- [LMS-LEAVE-001-휴가신청](LMS-LEAVE-001-휴가신청.md)
- [LMS-LEAVE-002-휴가승인](LMS-LEAVE-002-휴가승인.md)

## 인증/인가
- JWT Bearer Token 필수
- 신청/취소: EMPLOYEE, MANAGER, SUPER_ADMIN
- 본인 조회: EMPLOYEE, MANAGER, SUPER_ADMIN
- 승인/거절/매장별 조회/대기 목록: MANAGER, SUPER_ADMIN

## 엔드포인트 목록

### POST /api/leaves
- 설명: 휴가 신청
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "employeeId": "employee-uuid",
    "leaveType": "ANNUAL",
    "startDate": "2026-03-15",
    "endDate": "2026-03-17",
    "reason": "개인 사유"
  }
  ```
  - employeeId: 필수
  - leaveType: 필수 (ANNUAL, SICK, PERSONAL, MATERNITY, PATERNITY, BEREAVEMENT, UNPAID)
  - startDate: 필수, 오늘 이후
  - endDate: 필수, startDate 이후
  - reason: 선택
- 응답 (201): LeaveRequestResponse (status=PENDING)
- 응답 (400): PastDateLeaveRequestException, InvalidLeaveDateRangeException, InsufficientLeaveBalanceException, LeaveRequestDateOverlapException
- 응답 (404): EmployeeNotFoundException

### GET /api/leaves/my-leaves
- 설명: 본인 휴가 신청 목록 조회
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 응답 (200): LeaveRequestListResponse

### GET /api/leaves
- 설명: 매장별 휴가 신청 목록 조회
- 권한: MANAGER, SUPER_ADMIN
- 쿼리 파라미터: storeId (필수)
- 응답 (200): LeaveRequestListResponse

### GET /api/leaves/pending
- 설명: 승인 대기 휴가 목록 조회
- 권한: MANAGER, SUPER_ADMIN
- 응답 (200): LeaveRequestListResponse (status=PENDING만)

### PATCH /api/leaves/{id}/approve
- 설명: 휴가 승인
- 권한: MANAGER, SUPER_ADMIN
- 요청: 없음 (Body 불필요)
- 응답 (200): LeaveRequestResponse (status=APPROVED)
- 응답 (400): LeaveRequestCannotBeProcessedException
- 응답 (404): LeaveRequestNotFoundException

### PATCH /api/leaves/{id}/reject
- 설명: 휴가 거절
- 권한: MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "rejectionReason": "해당 기간 인력 부족"
  }
  ```
  - rejectionReason: 필수, 비어있을 수 없음
- 응답 (200): LeaveRequestResponse (status=REJECTED)
- 응답 (400): LeaveRequestCannotBeProcessedException
- 응답 (404): LeaveRequestNotFoundException

### DELETE /api/leaves/{id}
- 설명: 휴가 취소
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 응답 (204): No Content
- 응답 (400): LeaveRequestCannotBeCancelledException
- 응답 (404): LeaveRequestNotFoundException

## 공통 규칙
- 에러 응답: `{ "code": "LEAVE001", "message": "..." }`
- 하위호환: POLICY-NFR-001 하위호환 규칙 적용
