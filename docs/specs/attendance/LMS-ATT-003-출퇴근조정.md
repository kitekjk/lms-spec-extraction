# LMS-ATT-003 출퇴근조정

## 기본 정보
- type: use_case
- domain: attendance
- id: LMS-ATT-003

## 관련 정책
- POLICY-AUTH-001 (인증/인가)
- POLICY-NFR-001 (비기능 요구사항)
- POLICY-ATTENDANCE-001 (출퇴근)

## 관련 Spec
- LMS-API-ATT-001
- LMS-ATT-001 (출근)
- LMS-ATT-002 (퇴근)

## 관련 모델
- 주 모델: AttendanceRecord
- 참조 모델: AuditLog, Employee, Store

## 개요
MANAGER 또는 SUPER_ADMIN이 근로자의 출퇴근 기록을 수정한다. 수정 대상은 출근 시각(checkInTime)과 퇴근 시각(checkOutTime)이며, 수정 사유(reason)는 필수 입력이다. MANAGER는 자신의 소속 매장 근로자의 기록만 수정할 수 있고, SUPER_ADMIN은 전체 매장의 기록을 수정할 수 있다. 모든 수정 이력은 AuditLog에 기록된다.

## 기본 흐름
1. 관리자가 JWT 인증 토큰과 함께 출퇴근 기록 수정 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증하고 역할(MANAGER 또는 SUPER_ADMIN)을 확인한다.
3. 시스템이 recordId로 AttendanceRecord를 조회한다.
4. MANAGER인 경우, 해당 근로자가 자신의 소속 매장에 속하는지 확인한다.
5. 요청 바디에서 adjustedCheckInTime(필수), adjustedCheckOutTime(선택), reason(필수)을 추출한다.
6. AttendanceRecord의 attendanceTime을 수정된 시간으로 업데이트한다.
7. 수정 사유(reason)를 note 필드에 저장한다.
8. 변경된 AttendanceRecord를 저장한다.
9. EntityListener가 AuditLog에 변경 전/후 값과 수행자 정보를 자동 기록한다.
10. 200 OK 응답과 함께 수정된 AttendanceRecord를 반환한다.

## 대안 흐름
- **AF-1: 기록 없음** - recordId에 해당하는 AttendanceRecord가 존재하지 않으면 에러코드 ATT001과 HTTP 404 Not Found를 반환한다.
- **AF-2: 권한 없음 (EMPLOYEE)** - EMPLOYEE 역할의 사용자가 수정을 시도하면 HTTP 403 Forbidden을 반환한다.
- **AF-3: 소속 매장 불일치 (MANAGER)** - MANAGER가 소속 매장이 아닌 근로자의 기록을 수정하려 하면 HTTP 403 Forbidden을 반환한다.
- **AF-4: 수정 사유 미입력** - reason이 빈 문자열이거나 null이면 HTTP 400 Bad Request를 반환한다.
- **AF-5: adjustedCheckInTime 미입력** - adjustedCheckInTime이 null이면 HTTP 400 Bad Request를 반환한다.
- **AF-6: 인증 실패** - JWT 토큰이 없거나 만료된 경우 HTTP 401 Unauthorized를 반환한다.

## 검증 조건
- 수정 후 note 필드에 수정 사유(reason)가 저장되어야 한다.
- AuditLog에 엔티티 타입(ATTENDANCE_RECORD), 엔티티 ID(recordId), 행위 타입(UPDATE), 변경 전/후 값, 수행자 정보가 기록되어야 한다.
- adjustedCheckInTime은 null이 아니어야 한다 (@NotNull 검증).
- reason은 빈 문자열이 아니어야 한다 (@NotBlank 검증).
- adjustedCheckOutTime이 제공된 경우, adjustedCheckInTime보다 이후 시각이어야 한다.
- EMPLOYEE 역할은 이 기능에 접근할 수 없다.
- MANAGER는 소속 매장 근로자의 기록만 수정 가능하다.

## 비기능 요구사항
- POLICY-NFR-001 참조
- API 응답 시간: 500ms 이내
- 출퇴근 기록 수정과 AuditLog 기록이 동일 트랜잭션 내에서 원자적으로 처리되어야 한다.
- AuditLog는 append-only이며 삭제할 수 없다.

## 테스트 시나리오

### TC-ATT-003-01: 정상 출퇴근 기록 수정 (Unit)
- **Given**: recordId가 "rec-001"인 AttendanceRecord가 존재하고, checkInTime이 09:15, checkOutTime이 18:00이다.
- **When**: SUPER_ADMIN이 adjustedCheckInTime을 09:00, adjustedCheckOutTime을 18:00, reason을 "출근 시각 오류 정정"으로 수정 요청한다.
- **Then**: AttendanceRecord의 checkInTime이 09:00으로, note가 "출근 시각 오류 정정"으로 업데이트된다.

### TC-ATT-003-02: 존재하지 않는 기록 수정 시도 (Unit)
- **Given**: recordId가 "rec-999"인 AttendanceRecord가 존재하지 않는다.
- **When**: SUPER_ADMIN이 수정 요청을 전송한다.
- **Then**: 에러코드 ATT001과 함께 AttendanceNotFoundException이 발생한다.

### TC-ATT-003-03: EMPLOYEE 역할의 수정 시도 (Integration)
- **Given**: EMPLOYEE 역할로 인증된 사용자가 존재한다.
- **When**: PUT /api/attendance/records/{recordId} 요청을 전송한다.
- **Then**: HTTP 403 Forbidden 응답이 반환된다.

### TC-ATT-003-04: 수정 사유 미입력 시 검증 실패 (Integration)
- **Given**: MANAGER 역할로 인증된 사용자가 존재한다.
- **When**: reason을 빈 문자열("")로 설정하여 PUT /api/attendance/records/{recordId} 요청을 전송한다.
- **Then**: HTTP 400 Bad Request 응답이 반환된다.

### TC-ATT-003-05: AuditLog 기록 검증 (Integration)
- **Given**: recordId가 "rec-001"인 AttendanceRecord가 존재한다.
- **When**: SUPER_ADMIN이 adjustedCheckInTime을 09:00으로, reason을 "시간 정정"으로 수정한다.
- **Then**: AuditLog에 entityType이 ATTENDANCE_RECORD, entityId가 "rec-001", actionType이 UPDATE, 변경 전/후 값이 기록된다.

### TC-ATT-003-06: 전체 수정 흐름 E2E 검증 (E2E)
- **Given**: MANAGER 역할의 사용자가 인증되어 있고, 소속 매장의 근로자에 대한 출퇴근 기록이 존재한다.
- **When**: PUT /api/attendance/records/{recordId} 요청을 adjustedCheckInTime, adjustedCheckOutTime, reason과 함께 전송한다.
- **Then**: HTTP 200 OK 응답과 수정된 AttendanceRecordResponse가 반환되고, AuditLog가 생성된다.
