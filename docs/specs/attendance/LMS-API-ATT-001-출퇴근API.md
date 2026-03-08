# LMS-API-ATT-001: 출퇴근API

## 기본 정보
- type: api_spec
- domain: attendance

## 관련 Spec
- LMS-ATT-001 (출근)
- LMS-ATT-002 (퇴근)
- LMS-ATT-003 (출퇴근조정)
- LMS-ATT-004 (출퇴근조회)

## 엔드포인트 목록

### POST /api/attendance/check-in
- 설명: 근로자가 출근을 기록한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-ATT-001
- Request:
  ```json
  {
    "workScheduleId": "string (선택)"
  }
  ```
- Response (201):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "workScheduleId": "string (nullable)",
    "attendanceDate": "string (yyyy-MM-dd)",
    "checkInTime": "string (ISO 8601)",
    "checkOutTime": "null",
    "actualWorkHours": "null",
    "status": "PENDING",
    "note": "null",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청 / 이미 출근 처리됨 (ATT002)
  - 401: 인증 실패

### POST /api/attendance/check-out
- 설명: 근로자가 퇴근을 기록한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-ATT-002
- Request:
  ```json
  {
    "note": "string (선택)"
  }
  ```
- Response (200):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "workScheduleId": "string (nullable)",
    "attendanceDate": "string (yyyy-MM-dd)",
    "checkInTime": "string (ISO 8601)",
    "checkOutTime": "string (ISO 8601)",
    "actualWorkHours": "number (nullable)",
    "status": "NORMAL",
    "note": "string (nullable)",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청 / 출근 기록 없음 (ATT003) / 이미 퇴근 처리됨 (ATT004)
  - 401: 인증 실패

### GET /api/attendance/my-records
- 설명: 로그인한 사용자의 출퇴근 기록을 조회한다. 날짜 범위 필터링 가능
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-ATT-004
- Query Parameters:
  - startDate (선택, yyyy-MM-dd): 조회 시작일
  - endDate (선택, yyyy-MM-dd): 조회 종료일
- Response (200):
  ```json
  {
    "records": [
      {
        "id": "string",
        "employeeId": "string",
        "workScheduleId": "string (nullable)",
        "attendanceDate": "string (yyyy-MM-dd)",
        "checkInTime": "string (ISO 8601)",
        "checkOutTime": "string (ISO 8601, nullable)",
        "actualWorkHours": "number (nullable)",
        "status": "NORMAL | LATE | EARLY_LEAVE | ABSENT | PENDING",
        "note": "string (nullable)",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number"
  }
  ```
- 에러 응답:
  - 401: 인증 실패

### GET /api/attendance/records
- 설명: 특정 매장의 모든 출퇴근 기록을 조회한다 (관리자용)
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-ATT-004
- Query Parameters:
  - storeId (필수): 매장 ID
  - startDate (선택, yyyy-MM-dd): 조회 시작일
  - endDate (선택, yyyy-MM-dd): 조회 종료일
- Response (200):
  ```json
  {
    "records": [
      {
        "id": "string",
        "employeeId": "string",
        "workScheduleId": "string (nullable)",
        "attendanceDate": "string (yyyy-MM-dd)",
        "checkInTime": "string (ISO 8601)",
        "checkOutTime": "string (ISO 8601, nullable)",
        "actualWorkHours": "number (nullable)",
        "status": "NORMAL | LATE | EARLY_LEAVE | ABSENT | PENDING",
        "note": "string (nullable)",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음

### PUT /api/attendance/records/{recordId}
- 설명: 출퇴근 시간을 수정한다 (관리자용)
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-ATT-003
- Path Parameters:
  - recordId (필수): 출퇴근 기록 ID
- Request:
  ```json
  {
    "adjustedCheckInTime": "string (필수, ISO 8601)",
    "adjustedCheckOutTime": "string (선택, ISO 8601)",
    "reason": "string (필수)"
  }
  ```
- Response (200):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "workScheduleId": "string (nullable)",
    "attendanceDate": "string (yyyy-MM-dd)",
    "checkInTime": "string (ISO 8601)",
    "checkOutTime": "string (ISO 8601, nullable)",
    "actualWorkHours": "number (nullable)",
    "status": "NORMAL | LATE | EARLY_LEAVE | ABSENT | PENDING",
    "note": "string (수정 사유)",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 기록을 찾을 수 없음 (ATT001)
