# LMS-API-SCHEDULE-001: 스케줄 API

## 기본 정보
- type: api_spec
- domain: schedule
- service: LMS
- base_path: /api/schedules

## 관련 Spec
- [LMS-SCHEDULE-001-근무일정생성](LMS-SCHEDULE-001-근무일정생성.md)
- [LMS-SCHEDULE-002-근무일정변경](LMS-SCHEDULE-002-근무일정변경.md)

## 인증/인가
- JWT Bearer Token 필수
- 생성/수정/삭제: MANAGER 또는 SUPER_ADMIN
- 조회: EMPLOYEE, MANAGER, SUPER_ADMIN

## 엔드포인트 목록

### POST /api/schedules
- 설명: 근무 일정 생성
- 권한: MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "employeeId": "employee-uuid",
    "storeId": "store-uuid",
    "workDate": "2026-03-10",
    "startTime": "09:00",
    "endTime": "18:00"
  }
  ```
  - 모든 필드 필수
  - startTime < endTime
- 응답 (201): WorkScheduleResponse
- 응답 (400): DuplicateWorkScheduleException
- 응답 (400): EmployeeNotBelongToStoreException
- 응답 (404): EmployeeNotFoundException, StoreNotFoundException

### GET /api/schedules
- 설명: 일정 목록 조회 (필터링)
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 쿼리 파라미터:
  - employeeId (선택): 특정 근로자 일정
  - storeId (선택): 특정 매장 일정
  - startDate (선택, ISO DATE): 기간 시작
  - endDate (선택, ISO DATE): 기간 종료
- 조회 우선순위:
  1. storeId + startDate + endDate → 매장+기간 조회
  2. employeeId → 근로자별 조회
  3. storeId → 매장별 조회
- 응답 (200):
  ```json
  {
    "schedules": [...],
    "totalCount": 10
  }
  ```

### GET /api/schedules/my-schedule
- 설명: 본인 일정 조회
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 응답 (200): WorkScheduleListResponse

### GET /api/schedules/{scheduleId}
- 설명: 일정 상세 조회
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 응답 (200): WorkScheduleResponse
- 응답 (404): WorkScheduleNotFoundException

### PUT /api/schedules/{scheduleId}
- 설명: 일정 수정
- 권한: MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "workDate": "2026-03-11",
    "startTime": "10:00",
    "endTime": "19:00"
  }
  ```
  - 모든 필드 선택 (제공된 필드만 변경)
- 응답 (200): WorkScheduleResponse
- 응답 (400): 확정된 일정 변경 시도 시 에러
- 응답 (404): WorkScheduleNotFoundException

### DELETE /api/schedules/{scheduleId}
- 설명: 일정 삭제
- 권한: MANAGER, SUPER_ADMIN
- 응답 (204): No Content
- 응답 (404): WorkScheduleNotFoundException

## 공통 규칙
- 에러 응답: `{ "code": "SCH001", "message": "..." }`
- 하위호환: POLICY-NFR-001 하위호환 규칙 적용
