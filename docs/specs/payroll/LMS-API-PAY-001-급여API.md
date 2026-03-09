# LMS-API-PAY-001 급여 API

## 기본 정보
- type: api_spec
- id: LMS-API-PAY-001
- domain: payroll
- last-updated: 2026-03-09

## 관련 Spec
- LMS-PAY-001-급여정책등록
- LMS-PAY-002-급여정책수정
- LMS-PAY-003-급여정책삭제
- LMS-PAY-004-급여산정
- LMS-PAY-005-급여배치실행
- LMS-PAY-006-급여조회
- LMS-PAY-007-급여정책조회
- LMS-PAY-008-급여배치이력조회

## 엔드포인트 목록

---

### POST /api/payroll/calculate — 급여 계산 실행
- **Method**: POST
- **Path**: `/api/payroll/calculate`
- **Auth**: Bearer Token (SUPER_ADMIN, MANAGER)
- **Request Body**:
```json
{
  "employeeId": "660e8400-e29b-41d4-a716-446655440001",
  "period": "2026-03",
  "hourlyRate": 10000
}
```
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| employeeId | String (UUID) | Y | 대상 근로자 ID |
| period | String (YearMonth, yyyy-MM) | Y | 급여 산정 기간 |
| hourlyRate | BigDecimal | Y | 시급 (0보다 큰 값) |

- **Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "employeeId": "660e8400-e29b-41d4-a716-446655440001",
  "period": "2026-03",
  "baseAmount": 270000.00,
  "overtimeAmount": 120000.00,
  "totalAmount": 390000.00,
  "isPaid": false,
  "paidAt": null,
  "calculatedAt": "2026-03-31T10:00:00Z",
  "createdAt": "2026-03-31T10:00:00Z"
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 400 | (Bean Validation) | 필수 필드 누락 또는 hourlyRate <= 0 |
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | EMPLOYEE 접근 불가 |
| 404 | (Employee 조회 실패) | 근로자를 찾을 수 없음 |
| 409 | PAYROLL002 | 해당 기간의 급여가 이미 산정됨 |
| 409 | PAYROLL003 | 해당 기간에 출퇴근 기록이 없음 |

---

### GET /api/payroll/{payrollId} — 급여 상세 조회
- **Method**: GET
- **Path**: `/api/payroll/{payrollId}`
- **Auth**: Bearer Token (EMPLOYEE, MANAGER, SUPER_ADMIN)
- **Path Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| payrollId | String (UUID) | 조회 대상 급여 ID |

- **Response** (200 OK):
```json
{
  "payroll": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "employeeId": "660e8400-e29b-41d4-a716-446655440001",
    "period": "2026-03",
    "baseAmount": 270000.00,
    "overtimeAmount": 120000.00,
    "totalAmount": 390000.00,
    "isPaid": false,
    "paidAt": null,
    "calculatedAt": "2026-03-31T10:00:00Z",
    "createdAt": "2026-03-31T10:00:00Z"
  },
  "details": [
    {
      "id": "detail-001",
      "payrollId": "550e8400-e29b-41d4-a716-446655440000",
      "workDate": "2026-03-02",
      "workType": "WEEKDAY",
      "hours": 9.00,
      "hourlyRate": 10000.00,
      "multiplier": 1.0,
      "amount": 90000.00
    },
    {
      "id": "detail-002",
      "payrollId": "550e8400-e29b-41d4-a716-446655440000",
      "workDate": "2026-03-07",
      "workType": "WEEKEND",
      "hours": 8.00,
      "hourlyRate": 10000.00,
      "multiplier": 1.5,
      "amount": 120000.00
    }
  ]
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 404 | PAYROLL001 | 급여를 찾을 수 없음 |

---

### GET /api/payroll/my-payroll — 본인 급여 내역 조회
- **Method**: GET
- **Path**: `/api/payroll/my-payroll`
- **Auth**: Bearer Token (EMPLOYEE, MANAGER, SUPER_ADMIN)
- **Request Parameters**: 없음
- **Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "employeeId": "660e8400-e29b-41d4-a716-446655440001",
    "period": "2026-03",
    "baseAmount": 270000.00,
    "overtimeAmount": 120000.00,
    "totalAmount": 390000.00,
    "isPaid": false,
    "paidAt": null,
    "calculatedAt": "2026-03-31T10:00:00Z",
    "createdAt": "2026-03-31T10:00:00Z"
  }
]
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 401 | (인증 실패) | 토큰 없음 또는 만료 |

---

### GET /api/payroll?period={YYYY-MM} — 기간별 급여 내역 조회
- **Method**: GET
- **Path**: `/api/payroll`
- **Auth**: Bearer Token (MANAGER, SUPER_ADMIN)
- **Request Parameters**:

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| period | String (YearMonth, yyyy-MM) | Y | 급여 기간 |

- **Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "employeeId": "660e8400-e29b-41d4-a716-446655440001",
    "period": "2026-03",
    "baseAmount": 270000.00,
    "overtimeAmount": 120000.00,
    "totalAmount": 390000.00,
    "isPaid": false,
    "paidAt": null,
    "calculatedAt": "2026-03-31T10:00:00Z",
    "createdAt": "2026-03-31T10:00:00Z"
  }
]
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 400 | (요청 검증) | period 누락 |
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | EMPLOYEE 접근 불가 |

---

### POST /api/payroll/batch — 급여 배치 실행
- **Method**: POST
- **Path**: `/api/payroll/batch`
- **Auth**: Bearer Token (SUPER_ADMIN)
- **Request Body**:
```json
{
  "period": "2026-03",
  "storeId": "770e8400-e29b-41d4-a716-446655440002"
}
```
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| period | String (YearMonth, yyyy-MM) | Y | 급여 산정 기간 |
| storeId | String (UUID) | N | 대상 매장 ID (미지정 시 전체 매장) |

- **Response** (200 OK):
```json
{
  "id": "batch-001",
  "period": "2026-03",
  "storeId": "770e8400-e29b-41d4-a716-446655440002",
  "status": "COMPLETED",
  "totalCount": 10,
  "successCount": 10,
  "failureCount": 0,
  "startedAt": "2026-03-31T22:00:00Z",
  "completedAt": "2026-03-31T22:00:05Z",
  "errorMessage": null,
  "createdAt": "2026-03-31T22:00:00Z"
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 400 | (Bean Validation) | period 누락 |
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | MANAGER 또는 EMPLOYEE 접근 불가 |

---

### GET /api/payroll/batch-history — 배치 실행 이력 조회
- **Method**: GET
- **Path**: `/api/payroll/batch-history`
- **Auth**: Bearer Token (MANAGER, SUPER_ADMIN)
- **Request Parameters**:

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| startDate | String (Instant, ISO 8601) | N | 조회 시작 시점 |
| endDate | String (Instant, ISO 8601) | N | 조회 종료 시점 |

- **Response** (200 OK):
```json
[
  {
    "id": "batch-001",
    "period": "2026-03",
    "storeId": "770e8400-e29b-41d4-a716-446655440002",
    "status": "COMPLETED",
    "totalCount": 10,
    "successCount": 10,
    "failureCount": 0,
    "startedAt": "2026-03-31T22:00:00Z",
    "completedAt": "2026-03-31T22:00:05Z",
    "errorMessage": null,
    "createdAt": "2026-03-31T22:00:00Z"
  }
]
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | EMPLOYEE 접근 불가 |

---

### POST /api/payroll-policies — 급여 정책 등록
- **Method**: POST
- **Path**: `/api/payroll-policies`
- **Auth**: Bearer Token (SUPER_ADMIN)
- **Request Body**:
```json
{
  "policyType": "NIGHT_SHIFT",
  "multiplier": 1.5,
  "effectiveFrom": "2026-04-01",
  "effectiveTo": null,
  "description": "야간 근무 1.5배 가산"
}
```
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| policyType | String (Enum) | Y | 정책 유형. OVERTIME_WEEKDAY, OVERTIME_WEEKEND, OVERTIME_HOLIDAY, NIGHT_SHIFT, HOLIDAY_WORK, BONUS, ALLOWANCE |
| multiplier | BigDecimal | Y | 배율 (0.0 이상 10.0 이하) |
| effectiveFrom | String (LocalDate, yyyy-MM-dd) | Y | 시행 시작일 |
| effectiveTo | String (LocalDate, yyyy-MM-dd) | N | 시행 종료일 (null이면 무기한) |
| description | String | N | 정책 설명 |

- **Response** (201 Created):
```json
{
  "id": "policy-005",
  "policyType": "NIGHT_SHIFT",
  "policyTypeDescription": "야간 근무",
  "multiplier": 1.5,
  "effectiveFrom": "2026-04-01",
  "effectiveTo": null,
  "description": "야간 근무 1.5배 가산",
  "isCurrentlyEffective": true,
  "createdAt": "2026-03-09T10:00:00Z"
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 400 | (Bean Validation) | 필수 필드 누락 또는 multiplier 범위 초과 (0.0~10.0) |
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | MANAGER 또는 EMPLOYEE 접근 불가 |
| 409 | PAYROLL_POLICY002 | 동일 유형 정책의 유효 기간 중복 |
| 409 | PAYROLL_POLICY003 | 유효하지 않은 정책 기간 (effectiveFrom > effectiveTo) |

---

### GET /api/payroll-policies/active — 현재 유효 정책 조회
- **Method**: GET
- **Path**: `/api/payroll-policies/active`
- **Auth**: Bearer Token (EMPLOYEE, MANAGER, SUPER_ADMIN)
- **Request Parameters**: 없음
- **Response** (200 OK):
```json
{
  "policies": [
    {
      "id": "policy-001",
      "policyType": "OVERTIME_WEEKDAY",
      "policyTypeDescription": "평일 초과근무",
      "multiplier": 1.5,
      "effectiveFrom": "2024-01-01",
      "effectiveTo": null,
      "description": "평일 초과근무 1.5배",
      "isCurrentlyEffective": true,
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "totalCount": 1
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 401 | (인증 실패) | 토큰 없음 또는 만료 |

---

### GET /api/payroll-policies — 정책 목록 조회 (유형별 필터링)
- **Method**: GET
- **Path**: `/api/payroll-policies`
- **Auth**: Bearer Token (MANAGER, SUPER_ADMIN)
- **Request Parameters**:

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| policyType | String (Enum) | N | 정책 유형 필터. OVERTIME_WEEKDAY, OVERTIME_WEEKEND, OVERTIME_HOLIDAY, NIGHT_SHIFT, HOLIDAY_WORK, BONUS, ALLOWANCE |

- **Response** (200 OK):
```json
{
  "policies": [ /* PayrollPolicyResponse 배열 */ ],
  "totalCount": 4
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | EMPLOYEE 접근 불가 |

---

### PUT /api/payroll-policies/{policyId} — 급여 정책 수정
- **Method**: PUT
- **Path**: `/api/payroll-policies/{policyId}`
- **Auth**: Bearer Token (SUPER_ADMIN)
- **Path Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| policyId | String (UUID) | 수정 대상 정책 ID |

- **Request Body**:
```json
{
  "multiplier": 2.0,
  "effectiveTo": "2026-12-31",
  "description": "야간 근무 2.0배 가산으로 변경"
}
```
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| multiplier | BigDecimal | N | 변경할 배율 (0.0 이상 10.0 이하) |
| effectiveTo | String (LocalDate, yyyy-MM-dd) | N | 변경할 종료일 |
| description | String | N | 변경할 설명 |

- **Response** (200 OK):
```json
{
  "id": "policy-005",
  "policyType": "NIGHT_SHIFT",
  "policyTypeDescription": "야간 근무",
  "multiplier": 2.0,
  "effectiveFrom": "2026-04-01",
  "effectiveTo": "2026-12-31",
  "description": "야간 근무 2.0배 가산으로 변경",
  "isCurrentlyEffective": true,
  "createdAt": "2026-03-09T10:00:00Z"
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 400 | (Bean Validation) | multiplier 범위 초과 (0.0~10.0) |
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | MANAGER 또는 EMPLOYEE 접근 불가 |
| 404 | PAYROLL_POLICY001 | 정책을 찾을 수 없음 |
| 409 | PAYROLL_POLICY004 | 종료되거나 유효하지 않은 정책 수정 시도 |

---

### DELETE /api/payroll-policies/{policyId} — 급여 정책 삭제
- **Method**: DELETE
- **Path**: `/api/payroll-policies/{policyId}`
- **Auth**: Bearer Token (SUPER_ADMIN)
- **Path Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| policyId | String (UUID) | 삭제 대상 정책 ID |

- **Request Body**: 없음
- **Response** (204 No Content): 본문 없음
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | MANAGER 또는 EMPLOYEE 접근 불가 |
| 404 | PAYROLL_POLICY001 | 정책을 찾을 수 없음 |
