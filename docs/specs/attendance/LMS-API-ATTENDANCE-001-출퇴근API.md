# LMS-API-ATTENDANCE-001: 출퇴근 API

## 기본 정보
- type: api_spec
- domain: attendance
- service: LMS
- base_path: /api/attendance

## 관련 Spec
- [LMS-ATTENDANCE-001-출퇴근기록](LMS-ATTENDANCE-001-출퇴근기록.md)
- [LMS-ATTENDANCE-002-출퇴근수정](LMS-ATTENDANCE-002-출퇴근수정.md)

## 인증/인가
- JWT Bearer Token 필수
- 출근/퇴근: EMPLOYEE, MANAGER, SUPER_ADMIN
- 기록 조회 (my-records): EMPLOYEE, MANAGER, SUPER_ADMIN
- 매장별 조회: MANAGER, SUPER_ADMIN
- 기록 수정: MANAGER, SUPER_ADMIN

## 엔드포인트 목록

### POST /api/attendance/check-in
- 설명: 출근 기록
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "employeeId": "employee-uuid",
    "workScheduleId": "schedule-uuid"
  }
  ```
  - employeeId: 필수
  - workScheduleId: 선택 (일정 없이도 출근 가능)
- 응답 (201): AttendanceRecordResponse
- 응답 (400): AlreadyCheckedInException

### POST /api/attendance/check-out
- 설명: 퇴근 기록
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "employeeId": "employee-uuid"
  }
  ```
- 응답 (200): AttendanceRecordResponse
- 응답 (400): NotCheckedInException, AlreadyCheckedOutException

### GET /api/attendance/my-records
- 설명: 본인 출퇴근 기록 조회
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 쿼리 파라미터:
  - startDate (선택, ISO DATE)
  - endDate (선택, ISO DATE)
- 응답 (200):
  ```json
  {
    "records": [...],
    "totalCount": 20
  }
  ```

### GET /api/attendance/records
- 설명: 매장별 출퇴근 기록 조회
- 권한: MANAGER, SUPER_ADMIN
- 쿼리 파라미터:
  - storeId (필수)
  - startDate (선택, ISO DATE)
  - endDate (선택, ISO DATE)
- 응답 (200): AttendanceRecordListResponse

### PUT /api/attendance/records/{recordId}
- 설명: 출퇴근 기록 수정 (조정)
- 권한: MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "adjustedCheckInTime": "2026-03-08T08:55:00Z",
    "adjustedCheckOutTime": "2026-03-08T18:05:00Z",
    "reason": "시스템 오류로 인한 시간 조정"
  }
  ```
  - adjustedCheckInTime: 필수
  - adjustedCheckOutTime: 선택
  - reason: 필수
- 응답 (200): AttendanceRecordResponse
- 응답 (404): AttendanceNotFoundException

## 공통 규칙
- 에러 응답: `{ "code": "ATT001", "message": "..." }`
- 하위호환: POLICY-NFR-001 하위호환 규칙 적용
