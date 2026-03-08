# LMS-API-EMP-001: 근로자API

## 기본 정보
- type: api_spec
- domain: employee

## 관련 Spec
- LMS-EMP-001 (근로자등록)
- LMS-EMP-002 (근로자수정)
- LMS-EMP-003 (근로자비활성화)
- LMS-EMP-004 (근로자조회)

## 엔드포인트 목록

### POST /api/employees
- 설명: 새로운 근로자를 등록한다
- 권한: SUPER_ADMIN, MANAGER
- 관련 Use Case: LMS-EMP-001
- Request:
  ```json
  {
    "userId": "string (필수)",
    "name": "string (필수)",
    "employeeType": "REGULAR | IRREGULAR | PART_TIME (필수)",
    "storeId": "string (선택)"
  }
  ```
- Response (201):
  ```json
  {
    "id": "string",
    "userId": "string",
    "name": "string",
    "employeeType": "REGULAR | IRREGULAR | PART_TIME",
    "storeId": "string (nullable)",
    "remainingLeave": "number (BigDecimal)",
    "isActive": "boolean",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음

### GET /api/employees
- 설명: 근로자 목록을 조회한다. storeId로 매장별 필터링, activeOnly로 활성 근로자만 조회 가능
- 권한: 인증된 사용자 모두
- 관련 Use Case: LMS-EMP-004
- Query Parameters:
  - storeId (선택): 매장 ID로 필터링
  - activeOnly (선택, 기본값: false): true이면 활성 근로자만 조회
- Response (200):
  ```json
  {
    "employees": [
      {
        "id": "string",
        "userId": "string",
        "name": "string",
        "employeeType": "REGULAR | IRREGULAR | PART_TIME",
        "storeId": "string (nullable)",
        "remainingLeave": "number",
        "isActive": "boolean",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number"
  }
  ```
- 에러 응답:
  - 401: 인증 실패

### GET /api/employees/{employeeId}
- 설명: 특정 근로자의 상세 정보를 조회한다
- 권한: 인증된 사용자 모두
- 관련 Use Case: LMS-EMP-004
- Path Parameters:
  - employeeId (필수): 근로자 ID
- Response (200):
  ```json
  {
    "id": "string",
    "userId": "string",
    "name": "string",
    "employeeType": "REGULAR | IRREGULAR | PART_TIME",
    "storeId": "string (nullable)",
    "remainingLeave": "number",
    "isActive": "boolean",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 404: 근로자를 찾을 수 없음

### PUT /api/employees/{employeeId}
- 설명: 근로자 정보를 수정한다
- 권한: SUPER_ADMIN, MANAGER
- 관련 Use Case: LMS-EMP-002
- Path Parameters:
  - employeeId (필수): 근로자 ID
- Request:
  ```json
  {
    "name": "string (필수)",
    "employeeType": "REGULAR | IRREGULAR | PART_TIME (필수)",
    "storeId": "string (선택)"
  }
  ```
- Response (200):
  ```json
  {
    "id": "string",
    "userId": "string",
    "name": "string",
    "employeeType": "REGULAR | IRREGULAR | PART_TIME",
    "storeId": "string (nullable)",
    "remainingLeave": "number",
    "isActive": "boolean",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 근로자를 찾을 수 없음

### PATCH /api/employees/{employeeId}/deactivate
- 설명: 근로자를 비활성화한다
- 권한: SUPER_ADMIN, MANAGER
- 관련 Use Case: LMS-EMP-003
- Path Parameters:
  - employeeId (필수): 근로자 ID
- Request: 없음
- Response (200):
  ```json
  {
    "id": "string",
    "userId": "string",
    "name": "string",
    "employeeType": "REGULAR | IRREGULAR | PART_TIME",
    "storeId": "string (nullable)",
    "remainingLeave": "number",
    "isActive": "boolean (false)",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 근로자를 찾을 수 없음
