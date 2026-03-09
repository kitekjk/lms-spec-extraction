# LMS-API-SCH-001 근무일정 API

## 기본 정보
- type: api_spec
- domain: schedule
- id: LMS-API-SCH-001

## 관련 정책
- POLICY-AUTH-001 (인증/인가)
- POLICY-NFR-001 (비기능 요구사항)
- POLICY-SCHEDULE-001 (근무일정)

## 관련 Spec
- LMS-SCH-001 (근무일정등록)
- LMS-SCH-002 (근무일정수정)
- LMS-SCH-003 (근무일정삭제)
- LMS-SCH-004 (근무일정조회)

## 개요
근무일정(Schedule) 도메인의 REST API 명세이다. 일정 생성, 필터 기반 조회, 본인 일정 조회, 단건 조회, 수정, 삭제 6개 엔드포인트를 제공한다. 모든 엔드포인트는 JWT Bearer Token 인증이 필수이며, 역할(EMPLOYEE, MANAGER, SUPER_ADMIN)에 따라 접근 권한이 제한된다.

## 공통 사항

### 인증
- 모든 엔드포인트는 `Authorization: Bearer {accessToken}` 헤더 필수
- Content-Type: `application/json`
- Base Path: `/api/schedules`

### 공통 에러 응답
| HTTP 상태 코드 | 에러코드 | 설명 |
|---------------|---------|------|
| 400 | - | 요청 데이터 검증 실패 (@NotNull, @NotBlank 위반) 또는 필수 파라미터 누락 |
| 401 | - | JWT 토큰 없음 또는 만료 |
| 403 | - | 역할 기반 접근 권한 부족 |
| 404 | SCH001 | 근무 일정을 찾을 수 없음 |
| 409 | SCH002 | 동일 근로자의 동일 날짜에 중복 일정 |
| 409 | SCH003 | 확정된 일정은 수정 불가 |
| 409 | SCH004 | 근로자가 해당 매장에 소속되지 않음 |
| 403 | SCH005 | 매니저는 자신의 매장만 관리 가능 |
| 500 | - | 서버 내부 오류 |

## 엔드포인트 목록

### 1. 근무 일정 생성

- **Method**: POST
- **Path**: `/api/schedules`
- **역할 제한**: MANAGER (소속 매장), SUPER_ADMIN
- **관련 Use Case**: LMS-SCH-001

#### Request Body
```json
{
  "employeeId": "string (UUID)",
  "storeId": "string (UUID)",
  "workDate": "2026-03-10",
  "startTime": "09:00",
  "endTime": "18:00"
}
```

| 필드 | 타입 | 필수 | 검증 조건 | 설명 |
|------|------|------|----------|------|
| employeeId | String (UUID) | 예 | @NotBlank | 근로자 ID |
| storeId | String (UUID) | 예 | @NotBlank | 매장 ID |
| workDate | LocalDate (YYYY-MM-DD) | 예 | @NotNull | 근무 날짜 |
| startTime | LocalTime (HH:mm) | 예 | @NotNull | 근무 시작 시간 |
| endTime | LocalTime (HH:mm) | 예 | @NotNull, startTime보다 이후 | 근무 종료 시간 |

#### Response (201 Created)
```json
{
  "id": "string (UUID)",
  "employeeId": "string (UUID)",
  "storeId": "string (UUID)",
  "workDate": "2026-03-10",
  "startTime": "09:00",
  "endTime": "18:00",
  "workHours": 9.0,
  "isConfirmed": false,
  "isWeekendWork": false,
  "createdAt": "2026-03-09T00:00:00Z"
}
```

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 400 | - | 필수 필드 누락 또는 검증 실패 |
| 403 | SCH005 | MANAGER가 소속 매장이 아닌 매장에 일정 등록 시도 |
| 409 | SCH002 | 동일 근로자의 동일 날짜에 기존 일정 존재 |
| 409 | SCH004 | 근로자가 해당 매장에 미소속 |

---

### 2. 근무 일정 조회 (필터 기반)

- **Method**: GET
- **Path**: `/api/schedules`
- **역할 제한**: EMPLOYEE, MANAGER, SUPER_ADMIN
- **관련 Use Case**: LMS-SCH-004

#### Query Parameters
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| employeeId | String (UUID) | 조건부 | 근로자 ID (storeId와 둘 중 하나 필수) |
| storeId | String (UUID) | 조건부 | 매장 ID (employeeId와 둘 중 하나 필수) |
| startDate | LocalDate (YYYY-MM-DD) | 아니오 | 조회 시작 날짜 (storeId와 함께 사용) |
| endDate | LocalDate (YYYY-MM-DD) | 아니오 | 조회 종료 날짜 (storeId와 함께 사용) |

**조회 모드:**
1. `storeId` + `startDate` + `endDate`: 매장의 날짜 범위 내 일정
2. `employeeId`: 근로자의 전체 일정
3. `storeId`만: 매장의 전체 일정
4. 파라미터 없음: HTTP 400 Bad Request

#### Response (200 OK)
```json
{
  "schedules": [
    {
      "id": "string (UUID)",
      "employeeId": "string (UUID)",
      "storeId": "string (UUID)",
      "workDate": "2026-03-10",
      "startTime": "09:00",
      "endTime": "18:00",
      "workHours": 9.0,
      "isConfirmed": false,
      "isWeekendWork": false,
      "createdAt": "2026-03-09T00:00:00Z"
    }
  ],
  "totalCount": 1
}
```

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 400 | - | employeeId, storeId 모두 미제공 |
| 401 | - | 인증 실패 |

---

### 3. 본인 근무 일정 조회

- **Method**: GET
- **Path**: `/api/schedules/my-schedule`
- **역할 제한**: EMPLOYEE, MANAGER, SUPER_ADMIN
- **관련 Use Case**: LMS-SCH-004

#### Query Parameters
없음

#### Response (200 OK)
```json
{
  "schedules": [
    {
      "id": "string (UUID)",
      "employeeId": "string (UUID)",
      "storeId": "string (UUID)",
      "workDate": "2026-03-10",
      "startTime": "09:00",
      "endTime": "18:00",
      "workHours": 9.0,
      "isConfirmed": false,
      "isWeekendWork": false,
      "createdAt": "2026-03-09T00:00:00Z"
    }
  ],
  "totalCount": 1
}
```

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 401 | - | 인증 실패 |

---

### 4. 근무 일정 단건 조회

- **Method**: GET
- **Path**: `/api/schedules/{scheduleId}`
- **역할 제한**: EMPLOYEE, MANAGER, SUPER_ADMIN
- **관련 Use Case**: LMS-SCH-004

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| scheduleId | String (UUID) | 조회 대상 일정 ID |

#### Response (200 OK)
```json
{
  "id": "string (UUID)",
  "employeeId": "string (UUID)",
  "storeId": "string (UUID)",
  "workDate": "2026-03-10",
  "startTime": "09:00",
  "endTime": "18:00",
  "workHours": 9.0,
  "isConfirmed": false,
  "isWeekendWork": false,
  "createdAt": "2026-03-09T00:00:00Z"
}
```

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 401 | - | 인증 실패 |
| 404 | SCH001 | scheduleId에 해당하는 일정 없음 |

---

### 5. 근무 일정 수정

- **Method**: PUT
- **Path**: `/api/schedules/{scheduleId}`
- **역할 제한**: MANAGER (소속 매장), SUPER_ADMIN
- **관련 Use Case**: LMS-SCH-002

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| scheduleId | String (UUID) | 수정 대상 일정 ID |

#### Request Body
```json
{
  "workDate": "2026-03-11",
  "startTime": "10:00",
  "endTime": "19:00"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| workDate | LocalDate (YYYY-MM-DD) | 아니오 | 변경할 근무 날짜 |
| startTime | LocalTime (HH:mm) | 아니오 | 변경할 근무 시작 시간 |
| endTime | LocalTime (HH:mm) | 아니오 | 변경할 근무 종료 시간 |

#### Response (200 OK)
```json
{
  "id": "string (UUID)",
  "employeeId": "string (UUID)",
  "storeId": "string (UUID)",
  "workDate": "2026-03-11",
  "startTime": "10:00",
  "endTime": "19:00",
  "workHours": 9.0,
  "isConfirmed": false,
  "isWeekendWork": false,
  "createdAt": "2026-03-09T00:00:00Z"
}
```

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 400 | - | 검증 실패 (endTime이 startTime 이전) |
| 401 | - | 인증 실패 |
| 403 | SCH005 | MANAGER가 소속 매장이 아닌 일정 수정 시도 |
| 404 | SCH001 | scheduleId에 해당하는 일정 없음 |
| 409 | SCH003 | 확정된 일정 수정 시도 |

---

### 6. 근무 일정 삭제

- **Method**: DELETE
- **Path**: `/api/schedules/{scheduleId}`
- **역할 제한**: MANAGER (소속 매장), SUPER_ADMIN
- **관련 Use Case**: LMS-SCH-003

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| scheduleId | String (UUID) | 삭제 대상 일정 ID |

#### Response (204 No Content)
응답 바디 없음

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 401 | - | 인증 실패 |
| 403 | SCH005 | MANAGER가 소속 매장이 아닌 일정 삭제 시도 |
| 404 | SCH001 | scheduleId에 해당하는 일정 없음 |

---

## 응답 모델

### WorkScheduleResponse
| 필드 | 타입 | Nullable | 설명 |
|------|------|----------|------|
| id | String (UUID) | 아니오 | 일정 ID |
| employeeId | String (UUID) | 아니오 | 근로자 ID |
| storeId | String (UUID) | 아니오 | 매장 ID |
| workDate | LocalDate (YYYY-MM-DD) | 아니오 | 근무 날짜 |
| startTime | LocalTime (HH:mm) | 아니오 | 근무 시작 시간 |
| endTime | LocalTime (HH:mm) | 아니오 | 근무 종료 시간 |
| workHours | Double | 아니오 | 근무 시간 (endTime - startTime, 소수점 1자리) |
| isConfirmed | Boolean | 아니오 | 확정 여부 (기본값 false) |
| isWeekendWork | Boolean | 아니오 | 주말 근무 여부 |
| createdAt | Instant (ISO-8601) | 아니오 | 생성 시점 |

### WorkScheduleListResponse
| 필드 | 타입 | 설명 |
|------|------|------|
| schedules | List<WorkScheduleResponse> | 근무 일정 목록 |
| totalCount | Int | 총 건수 |
