# LMS-API-ATT-001 출퇴근 API

## 기본 정보
- type: api_spec
- domain: attendance
- id: LMS-API-ATT-001

## 관련 정책
- POLICY-AUTH-001 (인증/인가)
- POLICY-NFR-001 (비기능 요구사항)
- POLICY-ATTENDANCE-001 (출퇴근)

## 관련 Spec
- LMS-ATT-001 (출근)
- LMS-ATT-002 (퇴근)
- LMS-ATT-003 (출퇴근조정)
- LMS-ATT-004 (출퇴근조회)

## 개요
출퇴근(Attendance) 도메인의 REST API 명세이다. 출근 체크, 퇴근 체크, 본인 기록 조회, 매장별 기록 조회, 출퇴근 기록 수정 5개 엔드포인트를 제공한다. 모든 엔드포인트는 JWT Bearer Token 인증이 필수이며, 역할(EMPLOYEE, MANAGER, SUPER_ADMIN)에 따라 접근 권한이 제한된다.

## 공통 사항

### 인증
- 모든 엔드포인트는 `Authorization: Bearer {accessToken}` 헤더 필수
- Content-Type: `application/json`
- Base Path: `/api/attendance`

### 공통 에러 응답
| HTTP 상태 코드 | 에러코드 | 설명 |
|---------------|---------|------|
| 400 | - | 요청 데이터 검증 실패 (@NotNull, @NotBlank 위반) |
| 401 | - | JWT 토큰 없음 또는 만료 |
| 403 | - | 역할 기반 접근 권한 부족 |
| 404 | ATT001 | 출퇴근 기록을 찾을 수 없음 |
| 409 | ATT002 | 이미 출근 처리됨 (동일 날짜 중복 출근) |
| 409 | ATT003 | 출근 기록 없음 (퇴근 처리 불가) |
| 409 | ATT004 | 이미 퇴근 처리됨 (동일 날짜 중복 퇴근) |
| 500 | - | 서버 내부 오류 |

## 엔드포인트 목록

### 1. 출근 체크

- **Method**: POST
- **Path**: `/api/attendance/check-in`
- **역할 제한**: EMPLOYEE, MANAGER, SUPER_ADMIN
- **관련 Use Case**: LMS-ATT-001

#### Request Body
```json
{
  "workScheduleId": "string (UUID, 선택)"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| workScheduleId | String (UUID) | 아니오 | 연결할 근무 일정 ID |

#### Response (201 Created)
```json
{
  "id": "string (UUID)",
  "employeeId": "string (UUID)",
  "workScheduleId": "string (UUID) | null",
  "attendanceDate": "2026-03-09",
  "checkInTime": "2026-03-09T00:00:00Z",
  "checkOutTime": null,
  "actualWorkHours": null,
  "status": "PENDING",
  "note": null,
  "createdAt": "2026-03-09T00:00:00Z"
}
```

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 409 | ATT002 | 동일 날짜에 이미 출근 기록 존재 |
| 401 | - | 인증 실패 |

---

### 2. 퇴근 체크

- **Method**: POST
- **Path**: `/api/attendance/check-out`
- **역할 제한**: EMPLOYEE, MANAGER, SUPER_ADMIN
- **관련 Use Case**: LMS-ATT-002

#### Request Body
```json
{
  "note": "string (선택)"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| note | String | 아니오 | 퇴근 시 메모 |

#### Response (200 OK)
```json
{
  "id": "string (UUID)",
  "employeeId": "string (UUID)",
  "workScheduleId": "string (UUID) | null",
  "attendanceDate": "2026-03-09",
  "checkInTime": "2026-03-09T00:00:00Z",
  "checkOutTime": "2026-03-09T09:00:00Z",
  "actualWorkHours": 8.0,
  "status": "NORMAL",
  "note": null,
  "createdAt": "2026-03-09T00:00:00Z"
}
```

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 409 | ATT003 | 당일 출근 기록 없음 |
| 409 | ATT004 | 이미 퇴근 처리됨 |
| 401 | - | 인증 실패 |

---

### 3. 본인 출퇴근 기록 조회

- **Method**: GET
- **Path**: `/api/attendance/my-records`
- **역할 제한**: EMPLOYEE, MANAGER, SUPER_ADMIN
- **관련 Use Case**: LMS-ATT-004

#### Query Parameters
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| startDate | LocalDate (YYYY-MM-DD) | 아니오 | 조회 시작 날짜 |
| endDate | LocalDate (YYYY-MM-DD) | 아니오 | 조회 종료 날짜 |

#### Response (200 OK)
```json
{
  "records": [
    {
      "id": "string (UUID)",
      "employeeId": "string (UUID)",
      "workScheduleId": "string (UUID) | null",
      "attendanceDate": "2026-03-09",
      "checkInTime": "2026-03-09T00:00:00Z",
      "checkOutTime": "2026-03-09T09:00:00Z",
      "actualWorkHours": 8.0,
      "status": "NORMAL",
      "note": null,
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

### 4. 매장별 출퇴근 기록 조회

- **Method**: GET
- **Path**: `/api/attendance/records`
- **역할 제한**: MANAGER (소속 매장), SUPER_ADMIN
- **관련 Use Case**: LMS-ATT-004

#### Query Parameters
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| storeId | String (UUID) | 예 | 매장 ID |
| startDate | LocalDate (YYYY-MM-DD) | 아니오 | 조회 시작 날짜 |
| endDate | LocalDate (YYYY-MM-DD) | 아니오 | 조회 종료 날짜 |

#### Response (200 OK)
```json
{
  "records": [
    {
      "id": "string (UUID)",
      "employeeId": "string (UUID)",
      "workScheduleId": "string (UUID) | null",
      "attendanceDate": "2026-03-09",
      "checkInTime": "2026-03-09T00:00:00Z",
      "checkOutTime": "2026-03-09T09:00:00Z",
      "actualWorkHours": 8.0,
      "status": "NORMAL",
      "note": null,
      "createdAt": "2026-03-09T00:00:00Z"
    }
  ],
  "totalCount": 1
}
```

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 400 | - | storeId 파라미터 누락 |
| 401 | - | 인증 실패 |
| 403 | - | EMPLOYEE 역할이 접근하거나, MANAGER가 타 매장 조회 시도 |

---

### 5. 출퇴근 기록 수정 (관리자용)

- **Method**: PUT
- **Path**: `/api/attendance/records/{recordId}`
- **역할 제한**: MANAGER (소속 매장), SUPER_ADMIN
- **관련 Use Case**: LMS-ATT-003

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| recordId | String (UUID) | 수정 대상 출퇴근 기록 ID |

#### Request Body
```json
{
  "adjustedCheckInTime": "2026-03-09T00:00:00Z",
  "adjustedCheckOutTime": "2026-03-09T09:00:00Z",
  "reason": "출근 시각 오류 정정"
}
```

| 필드 | 타입 | 필수 | 검증 조건 | 설명 |
|------|------|------|----------|------|
| adjustedCheckInTime | Instant (ISO-8601) | 예 | @NotNull | 수정된 출근 시각 |
| adjustedCheckOutTime | Instant (ISO-8601) | 아니오 | - | 수정된 퇴근 시각 |
| reason | String | 예 | @NotBlank, 빈 문자열 불가 | 수정 사유 |

#### Response (200 OK)
```json
{
  "id": "string (UUID)",
  "employeeId": "string (UUID)",
  "workScheduleId": "string (UUID) | null",
  "attendanceDate": "2026-03-09",
  "checkInTime": "2026-03-09T00:00:00Z",
  "checkOutTime": "2026-03-09T09:00:00Z",
  "actualWorkHours": 9.0,
  "status": "NORMAL",
  "note": "출근 시각 오류 정정",
  "createdAt": "2026-03-09T00:00:00Z"
}
```

#### 에러 응답
| HTTP 상태 코드 | 에러코드 | 조건 |
|---------------|---------|------|
| 400 | - | adjustedCheckInTime이 null이거나, reason이 빈 문자열 |
| 401 | - | 인증 실패 |
| 403 | - | EMPLOYEE 역할이 접근하거나, MANAGER가 타 매장 기록 수정 시도 |
| 404 | ATT001 | recordId에 해당하는 기록 없음 |

---

## 응답 모델

### AttendanceRecordResponse
| 필드 | 타입 | Nullable | 설명 |
|------|------|----------|------|
| id | String (UUID) | 아니오 | 출퇴근 기록 ID |
| employeeId | String (UUID) | 아니오 | 근로자 ID |
| workScheduleId | String (UUID) | 예 | 연결된 근무 일정 ID |
| attendanceDate | LocalDate (YYYY-MM-DD) | 아니오 | 출근 날짜 |
| checkInTime | Instant (ISO-8601) | 아니오 | 출근 시각 |
| checkOutTime | Instant (ISO-8601) | 예 | 퇴근 시각 (미퇴근 시 null) |
| actualWorkHours | Double | 예 | 실제 근무 시간 (소수점 2자리, 미퇴근 시 null) |
| status | String (Enum) | 아니오 | NORMAL, LATE, EARLY_LEAVE, ABSENT, PENDING |
| note | String | 예 | 메모 (수정 사유 등) |
| createdAt | Instant (ISO-8601) | 아니오 | 생성 시점 |

### AttendanceRecordListResponse
| 필드 | 타입 | 설명 |
|------|------|------|
| records | List<AttendanceRecordResponse> | 출퇴근 기록 목록 |
| totalCount | Int | 총 건수 |

### AttendanceStatus (Enum)
| 값 | 설명 |
|----|------|
| NORMAL | 정상 출퇴근 |
| LATE | 지각 (근무 시작 시간 + 10분 초과 출근) |
| EARLY_LEAVE | 조퇴 (근무 종료 시간 이전 퇴근) |
| ABSENT | 결근 (출근 기록 없음) |
| PENDING | 퇴근 대기 중 (출근 후 퇴근 전) |
