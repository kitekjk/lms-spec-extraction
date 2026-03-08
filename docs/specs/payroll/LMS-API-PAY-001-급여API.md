# LMS-API-PAY-001: 급여API

## 기본 정보
- type: api_spec
- domain: payroll

## 관련 Spec
- LMS-PAY-001 (급여정책등록)
- LMS-PAY-002 (급여정책수정)
- LMS-PAY-003 (급여정책삭제)
- LMS-PAY-004 (급여산정)
- LMS-PAY-005 (급여배치실행)
- LMS-PAY-006 (급여조회)
- LMS-PAY-007 (급여정책조회)
- LMS-PAY-008 (급여배치이력조회)

## 엔드포인트 목록

---

### POST /api/payroll/calculate
- 설명: 특정 근로자의 급여를 계산한다
- 권한: SUPER_ADMIN, MANAGER
- 관련 Use Case: LMS-PAY-004
- Request:
  ```json
  {
    "employeeId": "string (필수)",
    "period": "string (필수, YYYY-MM)",
    "hourlyRate": "number (필수, BigDecimal, 0 초과)"
  }
  ```
- Response (200):
  ```json
  {
    "id": "string",
    "employeeId": "string",
    "period": "string (YYYY-MM)",
    "baseAmount": "number (BigDecimal)",
    "overtimeAmount": "number (BigDecimal)",
    "totalAmount": "number (BigDecimal)",
    "isPaid": "boolean",
    "paidAt": "string (ISO 8601, nullable)",
    "calculatedAt": "string (ISO 8601)",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청 / 이미 급여가 계산됨 (PAYROLL002) / 출퇴근 기록 없음 (PAYROLL003)
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 근로자를 찾을 수 없음

---

### GET /api/payroll/{payrollId}
- 설명: 특정 급여 내역의 상세 정보(급여 + 상세 내역)를 조회한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-PAY-006 (흐름 1)
- Path Parameters:
  - payrollId (필수): 급여 ID
- Response (200):
  ```json
  {
    "payroll": {
      "id": "string",
      "employeeId": "string",
      "period": "string (YYYY-MM)",
      "baseAmount": "number (BigDecimal)",
      "overtimeAmount": "number (BigDecimal)",
      "totalAmount": "number (BigDecimal)",
      "isPaid": "boolean",
      "paidAt": "string (ISO 8601, nullable)",
      "calculatedAt": "string (ISO 8601)",
      "createdAt": "string (ISO 8601)"
    },
    "details": [
      {
        "id": "string",
        "payrollId": "string",
        "workDate": "string (yyyy-MM-dd)",
        "workType": "WEEKDAY | NIGHT | WEEKEND | HOLIDAY",
        "hours": "number (BigDecimal)",
        "hourlyRate": "number (BigDecimal)",
        "multiplier": "number (BigDecimal)",
        "amount": "number (BigDecimal)"
      }
    ]
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 404: 급여 내역을 찾을 수 없음 (PAYROLL001)

---

### GET /api/payroll/my-payroll
- 설명: 로그인한 사용자의 모든 급여 내역을 조회한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-PAY-006 (흐름 2)
- Response (200):
  ```json
  [
    {
      "id": "string",
      "employeeId": "string",
      "period": "string (YYYY-MM)",
      "baseAmount": "number (BigDecimal)",
      "overtimeAmount": "number (BigDecimal)",
      "totalAmount": "number (BigDecimal)",
      "isPaid": "boolean",
      "paidAt": "string (ISO 8601, nullable)",
      "calculatedAt": "string (ISO 8601)",
      "createdAt": "string (ISO 8601)"
    }
  ]
  ```
- 에러 응답:
  - 401: 인증 실패

---

### GET /api/payroll
- 설명: 특정 기간의 모든 급여 내역을 조회한다 (관리자용)
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-PAY-006 (흐름 3)
- Query Parameters:
  - period (필수, YYYY-MM): 조회할 급여 기간
- Response (200):
  ```json
  [
    {
      "id": "string",
      "employeeId": "string",
      "period": "string (YYYY-MM)",
      "baseAmount": "number (BigDecimal)",
      "overtimeAmount": "number (BigDecimal)",
      "totalAmount": "number (BigDecimal)",
      "isPaid": "boolean",
      "paidAt": "string (ISO 8601, nullable)",
      "calculatedAt": "string (ISO 8601)",
      "createdAt": "string (ISO 8601)"
    }
  ]
  ```
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음

---

### POST /api/payroll/batch
- 설명: 급여 계산 배치를 수동으로 실행한다
- 권한: SUPER_ADMIN
- 관련 Use Case: LMS-PAY-005
- Request:
  ```json
  {
    "period": "string (필수, YYYY-MM)",
    "storeId": "string (선택, nullable)"
  }
  ```
- Response (200):
  ```json
  {
    "id": "string",
    "period": "string (YYYY-MM)",
    "storeId": "string (nullable)",
    "status": "RUNNING | COMPLETED | PARTIAL_SUCCESS | FAILED",
    "totalCount": "number (int)",
    "successCount": "number (int)",
    "failureCount": "number (int)",
    "startedAt": "string (ISO 8601)",
    "completedAt": "string (ISO 8601, nullable)",
    "errorMessage": "string (nullable)",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청 / 대상 직원 없음
  - 401: 인증 실패
  - 403: 권한 없음

---

### GET /api/payroll/batch-history
- 설명: 급여 계산 배치의 실행 이력을 조회한다
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-PAY-008
- Query Parameters:
  - startDate (선택, ISO 8601 DateTime): 조회 시작 일시
  - endDate (선택, ISO 8601 DateTime): 조회 종료 일시
- Response (200):
  ```json
  [
    {
      "id": "string",
      "period": "string (YYYY-MM)",
      "storeId": "string (nullable)",
      "status": "RUNNING | COMPLETED | PARTIAL_SUCCESS | FAILED",
      "totalCount": "number (int)",
      "successCount": "number (int)",
      "failureCount": "number (int)",
      "startedAt": "string (ISO 8601)",
      "completedAt": "string (ISO 8601, nullable)",
      "errorMessage": "string (nullable)",
      "createdAt": "string (ISO 8601)"
    }
  ]
  ```
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음

---

### POST /api/payroll-policies
- 설명: 새로운 급여 정책을 생성한다
- 권한: SUPER_ADMIN
- 관련 Use Case: LMS-PAY-001
- Request:
  ```json
  {
    "policyType": "string (필수, OVERTIME_WEEKDAY | OVERTIME_WEEKEND | OVERTIME_HOLIDAY | NIGHT_SHIFT | HOLIDAY_WORK | BONUS | ALLOWANCE)",
    "multiplier": "number (필수, BigDecimal, 0 이상 10.0 이하)",
    "effectiveFrom": "string (필수, yyyy-MM-dd)",
    "effectiveTo": "string (선택, yyyy-MM-dd, nullable)",
    "description": "string (선택, nullable)"
  }
  ```
- Response (201):
  ```json
  {
    "id": "string",
    "policyType": "string",
    "policyTypeDescription": "string",
    "multiplier": "number (BigDecimal)",
    "effectiveFrom": "string (yyyy-MM-dd)",
    "effectiveTo": "string (yyyy-MM-dd, nullable)",
    "description": "string (nullable)",
    "isCurrentlyEffective": "boolean",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청 / 정책 기간 중복 (PAYROLL_POLICY002)
  - 401: 인증 실패
  - 403: 권한 없음

---

### GET /api/payroll-policies/active
- 설명: 현재 적용 중인 모든 급여 정책을 조회한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-PAY-007 (흐름 1)
- Response (200):
  ```json
  {
    "policies": [
      {
        "id": "string",
        "policyType": "string",
        "policyTypeDescription": "string",
        "multiplier": "number (BigDecimal)",
        "effectiveFrom": "string (yyyy-MM-dd)",
        "effectiveTo": "string (yyyy-MM-dd, nullable)",
        "description": "string (nullable)",
        "isCurrentlyEffective": "boolean",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number (int)"
  }
  ```
- 에러 응답:
  - 401: 인증 실패

---

### GET /api/payroll-policies
- 설명: 급여 정책을 조회한다. policyType 파라미터로 유형별 필터링이 가능하다
- 권한: MANAGER, SUPER_ADMIN
- 관련 Use Case: LMS-PAY-007 (흐름 2, 흐름 3)
- Query Parameters:
  - policyType (선택): 정책 유형 필터 (OVERTIME_WEEKDAY | OVERTIME_WEEKEND | OVERTIME_HOLIDAY | NIGHT_SHIFT | HOLIDAY_WORK | BONUS | ALLOWANCE)
- Response (200):
  ```json
  {
    "policies": [
      {
        "id": "string",
        "policyType": "string",
        "policyTypeDescription": "string",
        "multiplier": "number (BigDecimal)",
        "effectiveFrom": "string (yyyy-MM-dd)",
        "effectiveTo": "string (yyyy-MM-dd, nullable)",
        "description": "string (nullable)",
        "isCurrentlyEffective": "boolean",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "totalCount": "number (int)"
  }
  ```
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음

---

### PUT /api/payroll-policies/{policyId}
- 설명: 급여 정책을 수정한다. 현재 유효한 정책만 수정 가능하다
- 권한: SUPER_ADMIN
- 관련 Use Case: LMS-PAY-002
- Path Parameters:
  - policyId (필수): 정책 ID
- Request:
  ```json
  {
    "multiplier": "number (선택, BigDecimal, 0 이상 10.0 이하)",
    "effectiveTo": "string (선택, yyyy-MM-dd, nullable)",
    "description": "string (선택, nullable)"
  }
  ```
- Response (200):
  ```json
  {
    "id": "string",
    "policyType": "string",
    "policyTypeDescription": "string",
    "multiplier": "number (BigDecimal)",
    "effectiveFrom": "string (yyyy-MM-dd)",
    "effectiveTo": "string (yyyy-MM-dd, nullable)",
    "description": "string (nullable)",
    "isCurrentlyEffective": "boolean",
    "createdAt": "string (ISO 8601)"
  }
  ```
- 에러 응답:
  - 400: 잘못된 요청
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 정책을 찾을 수 없음 (PAYROLL_POLICY001) / 유효하지 않은 정책 (PAYROLL_POLICY004)

---

### DELETE /api/payroll-policies/{policyId}
- 설명: 급여 정책을 삭제한다
- 권한: SUPER_ADMIN
- 관련 Use Case: LMS-PAY-003
- Path Parameters:
  - policyId (필수): 정책 ID
- Response (204): No Content
- 에러 응답:
  - 401: 인증 실패
  - 403: 권한 없음
  - 404: 정책을 찾을 수 없음 (PAYROLL_POLICY001)
