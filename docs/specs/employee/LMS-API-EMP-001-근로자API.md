# LMS-API-EMP-001 근로자API

## 기본 정보
- type: api_spec
- domain: employee
- id: LMS-API-EMP-001

## 관련 Spec
- LMS-EMP-001 (근로자등록)
- LMS-EMP-002 (근로자수정)
- LMS-EMP-003 (근로자비활성화)
- LMS-EMP-004 (근로자조회)

## 엔드포인트 목록

### POST /api/employees
- 설명: 새로운 근로자를 등록한다
- 권한: SUPER_ADMIN, MANAGER (소속 매장)
- 인증: Authorization: Bearer {accessToken}
- Request Body:
  ```json
  {
    "userId": "string (필수, UUID)",
    "name": "string (필수)",
    "employeeType": "string (REGULAR | IRREGULAR | PART_TIME)",
    "storeId": "string? (선택, UUID)"
  }
  ```
- Response 201:
  ```json
  {
    "id": "string (UUID)",
    "userId": "string (UUID)",
    "name": "string",
    "employeeType": "string (REGULAR | IRREGULAR | PART_TIME)",
    "storeId": "string? (nullable, UUID)",
    "remainingLeave": "number (BigDecimal, REGULAR=15.0, IRREGULAR=11.0, PART_TIME=0.0)",
    "isActive": "boolean (항상 true)",
    "createdAt": "string (ISO 8601 Instant)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 400 | VALIDATION_ERROR | userId 또는 name 빈 문자열 |
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 403 | - | SUPER_ADMIN/MANAGER 이외 역할의 접근 |
  | 403 | EMP003 | MANAGER가 소속 매장 외 근로자 등록 시도 |
  | 409 | EMP002 | 이미 근로자로 등록된 사용자 |

---

### GET /api/employees
- 설명: 근로자 목록을 조회한다
- 권한: SUPER_ADMIN (전체), MANAGER (소속 매장), EMPLOYEE (본인)
- 인증: Authorization: Bearer {accessToken}
- Query Parameters:
  | 파라미터 | 타입 | 필수 | 기본값 | 설명 |
  |---------|------|------|--------|------|
  | storeId | string (UUID) | 아니오 | - | 매장 ID로 필터링 |
  | activeOnly | boolean | 아니오 | false | true이면 활성 근로자만 조회 |
- Response 200:
  ```json
  {
    "employees": [
      {
        "id": "string (UUID)",
        "userId": "string (UUID)",
        "name": "string",
        "employeeType": "string (REGULAR | IRREGULAR | PART_TIME)",
        "storeId": "string? (nullable, UUID)",
        "remainingLeave": "number (BigDecimal)",
        "isActive": "boolean",
        "createdAt": "string (ISO 8601 Instant)"
      }
    ],
    "totalCount": "number (int)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 401 | - | 인증 토큰 없음 또는 만료 |

---

### GET /api/employees/{employeeId}
- 설명: 특정 근로자의 상세 정보를 조회한다
- 권한: SUPER_ADMIN (전체), MANAGER (소속 매장), EMPLOYEE (본인)
- 인증: Authorization: Bearer {accessToken}
- Path Parameters:
  | 파라미터 | 타입 | 설명 |
  |---------|------|------|
  | employeeId | string (UUID) | 근로자 ID |
- Response 200:
  ```json
  {
    "id": "string (UUID)",
    "userId": "string (UUID)",
    "name": "string",
    "employeeType": "string (REGULAR | IRREGULAR | PART_TIME)",
    "storeId": "string? (nullable, UUID)",
    "remainingLeave": "number (BigDecimal)",
    "isActive": "boolean",
    "createdAt": "string (ISO 8601 Instant)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 404 | - | 근로자를 찾을 수 없음 (본문 없음) |

---

### PUT /api/employees/{employeeId}
- 설명: 근로자 정보를 수정한다
- 권한: SUPER_ADMIN, MANAGER (소속 매장)
- 인증: Authorization: Bearer {accessToken}
- Path Parameters:
  | 파라미터 | 타입 | 설명 |
  |---------|------|------|
  | employeeId | string (UUID) | 근로자 ID |
- Request Body:
  ```json
  {
    "name": "string (필수)",
    "employeeType": "string (REGULAR | IRREGULAR | PART_TIME)",
    "storeId": "string? (선택, UUID, null이면 매장 배정 해제)"
  }
  ```
- Response 200:
  ```json
  {
    "id": "string (UUID)",
    "userId": "string (UUID)",
    "name": "string",
    "employeeType": "string (REGULAR | IRREGULAR | PART_TIME)",
    "storeId": "string? (nullable, UUID)",
    "remainingLeave": "number (BigDecimal)",
    "isActive": "boolean",
    "createdAt": "string (ISO 8601 Instant)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 400 | VALIDATION_ERROR | name 빈 문자열 |
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 403 | - | SUPER_ADMIN/MANAGER 이외 역할의 접근 |
  | 403 | EMP003 | MANAGER가 소속 매장 외 근로자 수정 시도 |
  | 404 | EMP001 | 근로자를 찾을 수 없음 |

---

### PATCH /api/employees/{employeeId}/deactivate
- 설명: 근로자를 비활성화한다 (논리적 삭제)
- 권한: SUPER_ADMIN, MANAGER (소속 매장)
- 인증: Authorization: Bearer {accessToken}
- Path Parameters:
  | 파라미터 | 타입 | 설명 |
  |---------|------|------|
  | employeeId | string (UUID) | 근로자 ID |
- Request Body: 없음
- Response 200:
  ```json
  {
    "id": "string (UUID)",
    "userId": "string (UUID)",
    "name": "string",
    "employeeType": "string (REGULAR | IRREGULAR | PART_TIME)",
    "storeId": "string? (nullable, UUID)",
    "remainingLeave": "number (BigDecimal)",
    "isActive": "boolean (항상 false)",
    "createdAt": "string (ISO 8601 Instant)"
  }
  ```
- 에러 응답:
  | HTTP 상태 | 에러코드 | 설명 |
  |-----------|---------|------|
  | 401 | - | 인증 토큰 없음 또는 만료 |
  | 403 | - | SUPER_ADMIN/MANAGER 이외 역할의 접근 |
  | 403 | EMP003 | MANAGER가 소속 매장 외 근로자 비활성화 시도 |
  | 404 | EMP001 | 근로자를 찾을 수 없음 |
- 비고: service-definition.md에서는 DELETE /api/employees/{id}로 정의되어 있으나, 실제 구현은 PATCH /api/employees/{employeeId}/deactivate이다. 논리적 삭제(soft delete)이므로 PATCH가 더 적합하다.

## 공통 에러 응답 형식
```json
{
  "code": "string (에러코드)",
  "message": "string (에러 메시지)",
  "timestamp": "string (ISO 8601, e.g. 2026-03-09T09:00:00Z)"
}
```

## EmployeeType Enum 값
| 값 | 설명 | 초기 연차 |
|----|------|----------|
| REGULAR | 정규직 | 15.0일 |
| IRREGULAR | 계약직 | 11.0일 |
| PART_TIME | 아르바이트 | 0.0일 |
