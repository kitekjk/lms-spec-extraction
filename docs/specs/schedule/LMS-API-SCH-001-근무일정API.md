# LMS-API-SCH-001: 근무일정API

## 기본 정보
- type: api_spec
- domain: schedule

## 관련 Spec
- LMS-SCH-001 (근무일정등록)
- LMS-SCH-002 (근무일정수정)
- LMS-SCH-003 (근무일정삭제)
- LMS-SCH-004 (근무일정조회)

## 엔드포인트 목록

### POST /api/schedules
- 설명: 새로운 근무 일정을 생성한다
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-SCH-001
- Request:
  ```json
  {
    "employeeId": "string (필수)",
    "storeId": "string (필수)",
    "workDate": "string (필수, yyyy-MM-dd)",
    "startTime": "string (필수, HH:mm)",
    "endTime": "string (필수, HH:mm)"
  }
  ```
- Response (201):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "storeId": "string",
    "workDate": "string (yyyy-MM-dd)",
    "startTime": "string (HH:mm)",
    "endTime": "string (HH:mm)",
    "workHours": "number",
    "isConfirmed": "boolean",
    "isWeekendWork": "boolean",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음

### GET /api/schedules
- 설명: 근무 일정을 조회한다. employeeId, storeId, startDate, endDate 파라미터로 필터링 가능
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-SCH-004
- Query Parameters:
  - employeeId (선택): 근로자 ID로 필터링
  - storeId (선택): 매장 ID로 필터링
  - startDate (선택, yyyy-MM-dd): 기간 시작일
  - endDate (선택, yyyy-MM-dd): 기간 종료일
- Response (200):
  ```json
  {
    "schedules": [
      {
        "id": "string",
        "employeeId": "string",
        "storeId": "string",
        "workDate": "string (yyyy-MM-dd)",
        "startTime": "string (HH:mm)",
        "endTime": "string (HH:mm)",
        "workHours": "number",
        "isConfirmed": "boolean",
        "isWeekendWork": "boolean",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number"
  }
  ```
- 에러 응답:
  - 400: 필수 파라미터 누락 (employeeId 또는 storeId 필요)
  - 401: 인증 실패

### GET /api/schedules/my-schedule
- 설명: 현재 로그인한 사용자의 근무 일정을 조회한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-SCH-004
- Response (200):
  ```json
  {
    "schedules": [
      {
        "id": "string",
        "employeeId": "string",
        "storeId": "string",
        "workDate": "string (yyyy-MM-dd)",
        "startTime": "string (HH:mm)",
        "endTime": "string (HH:mm)",
        "workHours": "number",
        "isConfirmed": "boolean",
        "isWeekendWork": "boolean",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number"
  }
  ```
- 에러 응답:
  - 401: 인증 실패

### GET /api/schedules/{scheduleId}
- 설명: 특정 근무 일정의 상세 정보를 조회한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-SCH-004
- Path Parameters:
  - scheduleId (필수): 일정 ID
- Response (200):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "storeId": "string",
    "workDate": "string (yyyy-MM-dd)",
    "startTime": "string (HH:mm)",
    "endTime": "string (HH:mm)",
    "workHours": "number",
    "isConfirmed": "boolean",
    "isWeekendWork": "boolean",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 404: 일정을 찾을 수 없음

### PUT /api/schedules/{scheduleId}
- 설명: 근무 일정을 수정한다
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-SCH-002
- Path Parameters:
  - scheduleId (필수): 일정 ID
- Request:
  ```json
  {
    "workDate": "string (선택, yyyy-MM-dd)",
    "startTime": "string (선택, HH:mm)",
    "endTime": "string (선택, HH:mm)"
  }
  ```
- Response (200):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "storeId": "string",
    "workDate": "string (yyyy-MM-dd)",
    "startTime": "string (HH:mm)",
    "endTime": "string (HH:mm)",
    "workHours": "number",
    "isConfirmed": "boolean",
    "isWeekendWork": "boolean",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 일정을 찾을 수 없음

### DELETE /api/schedules/{scheduleId}
- 설명: 근무 일정을 삭제한다
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-SCH-003
- Path Parameters:
  - scheduleId (필수): 일정 ID
- Response (204): No Content
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 일정을 찾을 수 없음
