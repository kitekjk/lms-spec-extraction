# LMS-ATT-002 퇴근

## 기본 정보
- type: use_case
- domain: attendance
- id: LMS-ATT-002

## 관련 정책
- POLICY-AUTH-001 (인증/인가)
- POLICY-NFR-001 (비기능 요구사항)
- POLICY-ATTENDANCE-001 (출퇴근)

## 관련 Spec
- LMS-API-ATT-001
- LMS-ATT-001 (출근)

## 관련 모델
- 주 모델: AttendanceRecord
- 참조 모델: WorkSchedule

## 개요
출근 기록이 있는 근로자(EMPLOYEE, MANAGER, SUPER_ADMIN)가 당일 퇴근을 기록한다. 퇴근 시각은 서버 시간(Asia/Seoul) 기준으로 자동 기록되며, 퇴근 처리 후 연결된 WorkSchedule이 있으면 출퇴근 상태(NORMAL, LATE, EARLY_LEAVE)를 자동 평가한다. 출근 기록 없이 퇴근하거나, 이미 퇴근한 기록에 대해 중복 퇴근할 수 없다.

## 기본 흐름
1. 근로자가 JWT 인증 토큰과 함께 퇴근 체크 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증하여 인증된 사용자인지 확인한다.
3. 시스템이 인증된 userId로부터 employeeId를 조회한다.
4. 시스템이 해당 근로자의 당일(Asia/Seoul 기준) 출근 기록을 조회한다.
5. 출근 기록이 존재하고 퇴근이 처리되지 않은 상태(PENDING)인지 확인한다.
6. 서버 시간(Asia/Seoul)을 퇴근 시각(checkOutTime)으로 설정한다.
7. AttendanceRecord의 checkOut 메서드를 호출하여 퇴근을 처리한다.
8. workScheduleId가 연결되어 있으면, 해당 WorkSchedule의 시작/종료 시간과 실제 출퇴근 시간을 비교하여 상태를 평가한다.
9. 업데이트된 AttendanceRecord를 저장하고 200 OK 응답을 반환한다.

## 대안 흐름
- **AF-1: 출근 기록 없음** - 당일 출근 기록이 존재하지 않으면 에러코드 ATT003과 HTTP 409 Conflict를 반환한다.
- **AF-2: 이미 퇴근 처리됨** - 당일 출근 기록에 이미 checkOutTime이 설정되어 있으면 에러코드 ATT004와 HTTP 409 Conflict를 반환한다.
- **AF-3: 인증 실패** - JWT 토큰이 없거나 만료된 경우 HTTP 401 Unauthorized를 반환한다.
- **AF-4: WorkSchedule 미연결** - workScheduleId가 null인 경우, 상태 평가를 건너뛰고 기본 상태 NORMAL로 설정한다.

## 검증 조건
- 퇴근 처리 후 checkOutTime은 null이 아니어야 한다.
- 퇴근 처리 후 status는 PENDING이 아니어야 한다 (NORMAL, LATE, EARLY_LEAVE 중 하나).
- 출근 시각보다 퇴근 시각이 이후여야 한다.
- WorkSchedule이 연결된 경우, 상태 평가 규칙은 다음과 같다:
  - 출근 시각이 근무 시작 시간 + 10분 이내이고 퇴근 시각이 근무 종료 시간 이후이면: NORMAL
  - 출근 시각이 근무 시작 시간 + 10분 초과이면: LATE
  - 퇴근 시각이 근무 종료 시간 이전이면: EARLY_LEAVE
- 실제 근무 시간(actualWorkHours)은 (checkOutTime - checkInTime)을 시간 단위로 소수점 2자리까지 계산한다.

## 비기능 요구사항
- POLICY-NFR-001 참조
- API 응답 시간: 500ms 이내
- 트랜잭션 내에서 출퇴근 기록 업데이트와 상태 평가가 원자적으로 처리되어야 한다.

## 테스트 시나리오

### TC-ATT-002-01: 정상 퇴근 처리 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자의 당일 출근 기록이 PENDING 상태로 존재하고, workScheduleId "sch-001"이 연결되어 있으며, 근무 시간은 09:00~18:00이다.
- **When**: 17:30에 퇴근 체크 요청을 전송한다.
- **Then**: checkOutTime이 설정되고, status는 EARLY_LEAVE이며, actualWorkHours가 계산된다.

### TC-ATT-002-02: 출근 기록 없이 퇴근 시도 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자의 당일 출근 기록이 존재하지 않는다.
- **When**: 퇴근 체크 요청을 전송한다.
- **Then**: 에러코드 ATT003과 함께 예외가 발생한다.

### TC-ATT-002-03: 중복 퇴근 시도 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자의 당일 출퇴근 기록에 이미 checkOutTime이 설정되어 있다.
- **When**: 퇴근 체크 요청을 전송한다.
- **Then**: 에러코드 ATT004와 함께 예외가 발생한다.

### TC-ATT-002-04: 지각 상태 평가 (Unit)
- **Given**: 근무 시작 시간이 09:00인 WorkSchedule이 연결되어 있고, 출근 시각이 09:15이다.
- **When**: 18:30에 퇴근 체크 요청을 전송한다.
- **Then**: status는 LATE로 평가된다 (지각 허용 시간 10분 초과).

### TC-ATT-002-05: 정상 상태 평가 (지각 허용 범위 내) (Unit)
- **Given**: 근무 시작 시간이 09:00인 WorkSchedule이 연결되어 있고, 출근 시각이 09:08이다.
- **When**: 18:30에 퇴근 체크 요청을 전송한다.
- **Then**: status는 NORMAL로 평가된다 (지각 허용 시간 10분 이내).

### TC-ATT-002-06: 퇴근 API 정상 응답 검증 (Integration)
- **Given**: 인증된 EMPLOYEE 역할의 사용자가 존재하고, 당일 출근 기록이 PENDING 상태이다.
- **When**: POST /api/attendance/check-out 요청을 전송한다.
- **Then**: HTTP 200 OK 응답과 함께 AttendanceRecordResponse가 반환되고, checkOutTime이 null이 아니다.

### TC-ATT-002-07: 인증 없이 퇴근 시도 (E2E)
- **Given**: JWT 토큰 없이 요청을 전송한다.
- **When**: POST /api/attendance/check-out 요청을 전송한다.
- **Then**: HTTP 401 Unauthorized 응답이 반환된다.
