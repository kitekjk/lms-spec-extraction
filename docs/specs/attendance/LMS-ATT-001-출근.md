# LMS-ATT-001 출근

## 기본 정보
- type: use_case
- domain: attendance
- id: LMS-ATT-001

## 관련 정책
- POLICY-AUTH-001 (인증/인가)
- POLICY-NFR-001 (비기능 요구사항)
- POLICY-ATTENDANCE-001 (출퇴근)

## 관련 Spec
- LMS-API-ATT-001

## 관련 모델
- 주 모델: AttendanceRecord
- 참조 모델: Employee, WorkSchedule

## 개요
인증된 근로자(EMPLOYEE, MANAGER, SUPER_ADMIN)가 당일 출근을 기록한다. 출근 시각은 서버 시간(Asia/Seoul) 기준으로 자동 기록되며, 출근 직후 출퇴근 상태는 PENDING(퇴근 대기 중)으로 설정된다. 동일 날짜에 이미 출근 기록이 존재하면 중복 출근이 불가하다.

## 기본 흐름
1. 근로자가 JWT 인증 토큰과 함께 출근 체크 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증하여 인증된 사용자인지 확인한다.
3. 시스템이 인증된 userId로부터 employeeId를 조회한다.
4. 시스템이 동일 근로자의 당일(Asia/Seoul 기준) 출근 기록 존재 여부를 확인한다.
5. 당일 출근 기록이 없으면, 서버 시간(Asia/Seoul)을 출근 시각(checkInTime)으로 설정한다.
6. AttendanceRecord를 생성한다 (상태: PENDING, attendanceDate: 당일).
7. 요청에 workScheduleId가 포함된 경우, 해당 WorkSchedule과 연결한다.
8. 생성된 AttendanceRecord를 저장하고 201 Created 응답을 반환한다.

## 대안 흐름
- **AF-1: 동일 날짜 중복 출근** - 당일 출근 기록이 이미 존재하면 에러코드 ATT002와 HTTP 409 Conflict를 반환한다.
- **AF-2: 인증 실패** - JWT 토큰이 없거나 만료된 경우 HTTP 401 Unauthorized를 반환한다.
- **AF-3: workScheduleId 미제공** - workScheduleId 없이 요청하면 workScheduleId를 null로 설정하고 정상 처리한다.
- **AF-4: 잘못된 workScheduleId** - 존재하지 않는 workScheduleId가 전달되면 HTTP 404 Not Found를 반환한다.

## 검증 조건
- 출근 기록 생성 후 status는 반드시 PENDING이어야 한다.
- attendanceDate는 서버 시간(Asia/Seoul) 기준 당일 날짜(LocalDate)와 일치해야 한다.
- checkInTime은 서버 시간(Instant)으로 자동 설정되어야 한다.
- checkOutTime은 null이어야 한다.
- 동일 employeeId + 동일 attendanceDate 조합으로 2건 이상 출근 기록을 생성할 수 없다.
- workScheduleId는 요청에 포함된 경우에만 설정되고, 미포함 시 null이다.

## 비기능 요구사항
- POLICY-NFR-001 참조
- API 응답 시간: 500ms 이내
- 동시 출근 요청(동일 근로자) 시 중복 생성 방지 (데이터 무결성)

## 테스트 시나리오

### TC-ATT-001-01: 정상 출근 기록 생성 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자가 인증된 상태이고, 당일 출근 기록이 없다.
- **When**: workScheduleId "sch-001"과 함께 출근 체크 요청을 전송한다.
- **Then**: AttendanceRecord가 생성되고, status는 PENDING, workScheduleId는 "sch-001", checkOutTime은 null, attendanceDate는 당일 날짜이다.

### TC-ATT-001-02: 중복 출근 시 에러 반환 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자의 당일 출근 기록이 이미 존재한다.
- **When**: 출근 체크 요청을 전송한다.
- **Then**: 에러코드 ATT002와 함께 예외가 발생하고, 새로운 출근 기록은 생성되지 않는다.

### TC-ATT-001-03: workScheduleId 없이 출근 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자가 인증된 상태이고, 당일 출근 기록이 없다.
- **When**: workScheduleId 없이 출근 체크 요청을 전송한다.
- **Then**: AttendanceRecord가 생성되고, workScheduleId는 null이다.

### TC-ATT-001-04: 출근 API 정상 응답 검증 (Integration)
- **Given**: 인증된 EMPLOYEE 역할의 사용자가 존재하고, 당일 출근 기록이 없다.
- **When**: POST /api/attendance/check-in 요청을 전송한다.
- **Then**: HTTP 201 Created 응답과 함께 AttendanceRecordResponse가 반환되고, status는 "PENDING"이다.

### TC-ATT-001-05: 인증 없이 출근 시도 (E2E)
- **Given**: JWT 토큰 없이 요청을 전송한다.
- **When**: POST /api/attendance/check-in 요청을 전송한다.
- **Then**: HTTP 401 Unauthorized 응답이 반환된다.

### TC-ATT-001-06: 동시 출근 요청 시 중복 방지 (Integration)
- **Given**: employeeId가 "emp-001"인 근로자가 인증된 상태이고, 당일 출근 기록이 없다.
- **When**: 동일 근로자에 대해 2건의 출근 요청을 동시에 전송한다.
- **Then**: 1건만 성공(HTTP 201)하고, 나머지 1건은 에러코드 ATT002와 HTTP 409로 실패한다.
