# LMS-API-LEAVE-001: 휴가API

## 기본 정보
- type: api_spec
- domain: leave

## 관련 Spec
- LMS-LEAVE-001 (휴가신청)
- LMS-LEAVE-002 (휴가승인)
- LMS-LEAVE-003 (휴가반려)
- LMS-LEAVE-004 (휴가취소)
- LMS-LEAVE-005 (휴가조회)

## 엔드포인트 목록

### POST /api/leaves
- 설명: 새로운 휴가를 신청한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-LEAVE-001
- Request:
  ```json
  {
    "leaveType": "ANNUAL | SICK | PERSONAL | MATERNITY | PATERNITY | BEREAVEMENT | UNPAID (필수)",
    "startDate": "string (필수, yyyy-MM-dd)",
    "endDate": "string (필수, yyyy-MM-dd)",
    "reason": "string (선택)"
  }
  ```
- Response (201):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "leaveType": "ANNUAL | SICK | PERSONAL | MATERNITY | PATERNITY | BEREAVEMENT | UNPAID",
    "startDate": "string (yyyy-MM-dd)",
    "endDate": "string (yyyy-MM-dd)",
    "requestedDays": "number (long)",
    "reason": "string (nullable)",
    "status": "PENDING",
    "rejectionReason": "null",
    "approvedBy": "null",
    "approvedAt": "null",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청 / 과거 날짜 (LEAVE006) / 잔여 연차 부족 (LEAVE002) / 날짜 중복 (LEAVE003) / 유효하지 않은 날짜 범위 (LEAVE007)
  - 401: 인증 실패

### GET /api/leaves/my-leaves
- 설명: 로그인한 사용자의 휴가 신청 내역을 조회한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-LEAVE-005
- Response (200):
  ```json
  {
    "requests": [
      {
        "id": "string",
        "employeeId": "string",
        "leaveType": "string",
        "startDate": "string (yyyy-MM-dd)",
        "endDate": "string (yyyy-MM-dd)",
        "requestedDays": "number",
        "reason": "string (nullable)",
        "status": "PENDING | APPROVED | REJECTED | CANCELLED",
        "rejectionReason": "string (nullable)",
        "approvedBy": "string (nullable)",
        "approvedAt": "string (ISO 8601, nullable)",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number"
  }
  ```
- 에러 응답:
  - 401: 인증 실패

### GET /api/leaves
- 설명: 특정 매장의 모든 휴가 신청 내역을 조회한다 (관리자용)
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-LEAVE-005
- Query Parameters:
  - storeId (필수): 매장 ID
- Response (200):
  ```json
  {
    "requests": [
      {
        "id": "string",
        "employeeId": "string",
        "leaveType": "string",
        "startDate": "string (yyyy-MM-dd)",
        "endDate": "string (yyyy-MM-dd)",
        "requestedDays": "number",
        "reason": "string (nullable)",
        "status": "PENDING | APPROVED | REJECTED | CANCELLED",
        "rejectionReason": "string (nullable)",
        "approvedBy": "string (nullable)",
        "approvedAt": "string (ISO 8601, nullable)",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음

### GET /api/leaves/pending
- 설명: 승인 대기 중인 모든 휴가 신청을 조회한다 (관리자용)
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-LEAVE-005
- Response (200):
  ```json
  {
    "requests": [
      {
        "id": "string",
        "employeeId": "string",
        "leaveType": "string",
        "startDate": "string (yyyy-MM-dd)",
        "endDate": "string (yyyy-MM-dd)",
        "requestedDays": "number",
        "reason": "string (nullable)",
        "status": "PENDING",
        "rejectionReason": "null",
        "approvedBy": "null",
        "approvedAt": "null",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음

### PATCH /api/leaves/{leaveId}/approve
- 설명: 휴가 신청을 승인한다 (관리자용)
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-LEAVE-002
- Path Parameters:
  - leaveId (필수): 휴가 신청 ID
- Request: 없음
- Response (200):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "leaveType": "string",
    "startDate": "string (yyyy-MM-dd)",
    "endDate": "string (yyyy-MM-dd)",
    "requestedDays": "number",
    "reason": "string (nullable)",
    "status": "APPROVED",
    "rejectionReason": "null",
    "approvedBy": "string",
    "approvedAt": "string (ISO 8601)",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 휴가 신청을 찾을 수 없음 (LEAVE001)

### PATCH /api/leaves/{leaveId}/reject
- 설명: 휴가 신청을 반려한다 (관리자용)
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-LEAVE-003
- Path Parameters:
  - leaveId (필수): 휴가 신청 ID
- Request:
  ```json
  {
    "rejectionReason": "string (필수)"
  }
  ```
- Response (200):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "leaveType": "string",
    "startDate": "string (yyyy-MM-dd)",
    "endDate": "string (yyyy-MM-dd)",
    "requestedDays": "number",
    "reason": "string (nullable)",
    "status": "REJECTED",
    "rejectionReason": "string",
    "approvedBy": "string",
    "approvedAt": "string (ISO 8601)",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청 (반려 사유 누락)
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 휴가 신청을 찾을 수 없음 (LEAVE001)

### DELETE /api/leaves/{leaveId}
- 설명: 본인이 신청한 휴가를 취소한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-LEAVE-004
- Path Parameters:
  - leaveId (필수): 휴가 신청 ID
- Response (204): No Content
- 에러 응답:
  - 401: 인증 실패
  - 404: 휴가 신청을 찾을 수 없음 (LEAVE001)
