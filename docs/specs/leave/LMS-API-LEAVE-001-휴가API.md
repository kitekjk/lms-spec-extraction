# LMS-API-LEAVE-001 휴가 API

## 기본 정보
- type: api_spec
- id: LMS-API-LEAVE-001
- domain: leave
- last-updated: 2026-03-09

## 관련 Spec
- LMS-LEAVE-001-휴가신청
- LMS-LEAVE-002-휴가승인
- LMS-LEAVE-003-휴가반려
- LMS-LEAVE-004-휴가취소
- LMS-LEAVE-005-휴가조회

## 엔드포인트 목록

### POST /api/leaves — 휴가 신청
- **Method**: POST
- **Path**: `/api/leaves`
- **Auth**: Bearer Token (EMPLOYEE, MANAGER, SUPER_ADMIN)
- **Request Body**:
```json
{
  "leaveType": "ANNUAL",
  "startDate": "2026-04-01",
  "endDate": "2026-04-03",
  "reason": "개인 사유"
}
```
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| leaveType | String (Enum) | Y | 휴가 유형. ANNUAL, SICK, PERSONAL, MATERNITY, PATERNITY, BEREAVEMENT, UNPAID |
| startDate | String (LocalDate, yyyy-MM-dd) | Y | 휴가 시작일 |
| endDate | String (LocalDate, yyyy-MM-dd) | Y | 휴가 종료일 |
| reason | String | N | 신청 사유 |

- **Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "employeeId": "660e8400-e29b-41d4-a716-446655440001",
  "leaveType": "ANNUAL",
  "startDate": "2026-04-01",
  "endDate": "2026-04-03",
  "requestedDays": 3,
  "reason": "개인 사유",
  "status": "PENDING",
  "rejectionReason": null,
  "approvedBy": null,
  "approvedAt": null,
  "createdAt": "2026-03-09T10:00:00Z"
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 400 | (Bean Validation) | 필수 필드 누락 또는 형식 오류 |
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 409 | LEAVE002 | 잔여 연차 부족 |
| 409 | LEAVE003 | 승인된 휴가와 기간 중복 |
| 409 | LEAVE006 | 과거 날짜 신청 불가 |
| 409 | LEAVE007 | 유효하지 않은 휴가 기간 (시작일 > 종료일) |

---

### GET /api/leaves/my-leaves — 본인 휴가 내역 조회
- **Method**: GET
- **Path**: `/api/leaves/my-leaves`
- **Auth**: Bearer Token (EMPLOYEE, MANAGER, SUPER_ADMIN)
- **Request Parameters**: 없음
- **Response** (200 OK):
```json
{
  "requests": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "employeeId": "660e8400-e29b-41d4-a716-446655440001",
      "leaveType": "ANNUAL",
      "startDate": "2026-04-01",
      "endDate": "2026-04-03",
      "requestedDays": 3,
      "reason": "개인 사유",
      "status": "APPROVED",
      "rejectionReason": null,
      "approvedBy": "770e8400-e29b-41d4-a716-446655440002",
      "approvedAt": "2026-03-10T09:00:00Z",
      "createdAt": "2026-03-09T10:00:00Z"
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

### GET /api/leaves?storeId={storeId} — 매장별 휴가 목록 조회
- **Method**: GET
- **Path**: `/api/leaves`
- **Auth**: Bearer Token (MANAGER, SUPER_ADMIN)
- **Request Parameters**:

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| storeId | String (UUID) | Y | 조회 대상 매장 ID |

- **Response** (200 OK):
```json
{
  "requests": [ /* LeaveRequestResponse 배열 */ ],
  "totalCount": 5
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 400 | (요청 검증) | storeId 누락 |
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | EMPLOYEE 접근 또는 MANAGER의 타 매장 접근 |

---

### GET /api/leaves/pending — 승인 대기 휴가 목록 조회
- **Method**: GET
- **Path**: `/api/leaves/pending`
- **Auth**: Bearer Token (MANAGER, SUPER_ADMIN)
- **Request Parameters**: 없음
- **Response** (200 OK):
```json
{
  "requests": [ /* PENDING 상태의 LeaveRequestResponse 배열 */ ],
  "totalCount": 2
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | EMPLOYEE 접근 불가 |

---

### PATCH /api/leaves/{leaveId}/approve — 휴가 승인
- **Method**: PATCH
- **Path**: `/api/leaves/{leaveId}/approve`
- **Auth**: Bearer Token (MANAGER, SUPER_ADMIN)
- **Path Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| leaveId | String (UUID) | 승인 대상 휴가 신청 ID |

- **Request Body**: 없음
- **Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "employeeId": "660e8400-e29b-41d4-a716-446655440001",
  "leaveType": "ANNUAL",
  "startDate": "2026-04-01",
  "endDate": "2026-04-03",
  "requestedDays": 3,
  "reason": "개인 사유",
  "status": "APPROVED",
  "rejectionReason": null,
  "approvedBy": "770e8400-e29b-41d4-a716-446655440002",
  "approvedAt": "2026-03-10T09:00:00Z",
  "createdAt": "2026-03-09T10:00:00Z"
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | EMPLOYEE 접근 또는 MANAGER의 타 매장 접근 |
| 404 | LEAVE001 | 휴가 신청을 찾을 수 없음 |
| 409 | LEAVE005 | PENDING 상태가 아닌 휴가 승인 시도 |

---

### PATCH /api/leaves/{leaveId}/reject — 휴가 반려
- **Method**: PATCH
- **Path**: `/api/leaves/{leaveId}/reject`
- **Auth**: Bearer Token (MANAGER, SUPER_ADMIN)
- **Path Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| leaveId | String (UUID) | 반려 대상 휴가 신청 ID |

- **Request Body**:
```json
{
  "rejectionReason": "인원 부족으로 해당 기간 휴가 불가"
}
```
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| rejectionReason | String | Y | 반려 사유 (빈 문자열 불가) |

- **Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "employeeId": "660e8400-e29b-41d4-a716-446655440001",
  "leaveType": "ANNUAL",
  "startDate": "2026-04-01",
  "endDate": "2026-04-03",
  "requestedDays": 3,
  "reason": "개인 사유",
  "status": "REJECTED",
  "rejectionReason": "인원 부족으로 해당 기간 휴가 불가",
  "approvedBy": "770e8400-e29b-41d4-a716-446655440002",
  "approvedAt": "2026-03-10T09:00:00Z",
  "createdAt": "2026-03-09T10:00:00Z"
}
```
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 400 | (Bean Validation) | rejectionReason 빈 문자열 또는 누락 |
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 403 | (권한 없음) | EMPLOYEE 접근 또는 MANAGER의 타 매장 접근 |
| 404 | LEAVE001 | 휴가 신청을 찾을 수 없음 |
| 409 | LEAVE005 | PENDING 상태가 아닌 휴가 반려 시도 |

---

### DELETE /api/leaves/{leaveId} — 휴가 취소
- **Method**: DELETE
- **Path**: `/api/leaves/{leaveId}`
- **Auth**: Bearer Token (EMPLOYEE, MANAGER, SUPER_ADMIN)
- **Path Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| leaveId | String (UUID) | 취소 대상 휴가 신청 ID |

- **Request Body**: 없음
- **Response** (204 No Content): 본문 없음
- **Error Codes**:

| HTTP 상태 | 에러코드 | 설명 |
|-----------|---------|------|
| 401 | (인증 실패) | 토큰 없음 또는 만료 |
| 404 | LEAVE001 | 휴가 신청을 찾을 수 없음 |
| 409 | LEAVE004 | REJECTED 또는 CANCELLED 상태에서 취소 시도 |
