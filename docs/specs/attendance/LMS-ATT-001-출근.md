# LMS-ATT-001: 출근

## 기본 정보
- type: use_case
- domain: attendance

## 관련 Spec
- LMS-API-ATT-001 (출퇴근API)
- LMS-ATT-002 (퇴근)

## 개요
근로자가 출근 체크를 요청하여 당일 출근 기록을 생성한다.

## 관련 모델
- 주 모델: AttendanceRecord (Aggregate Root)
- 참조 모델: Employee (employeeId 참조), WorkSchedule (workScheduleId 참조), AttendanceTime, AttendanceStatus

## 선행 조건
- 인증된 사용자여야 한다 (EMPLOYEE, MANAGER, SUPER_ADMIN)
- 당일 출근 기록이 없어야 한다

## 기본 흐름
1. 근로자가 출근 체크를 요청한다 (workScheduleId 선택적 제공)
2. 시스템은 현재 로그인한 사용자의 ID를 employeeId로 사용한다
3. 시스템은 당일 해당 근로자의 출근 기록이 이미 존재하는지 확인한다
4. 시스템은 새로운 AttendanceRecord를 생성한다 (checkIn)
   - attendanceDate: 현재 날짜
   - checkInTime: 현재 시간
   - status: PENDING (퇴근 대기 중)
   - checkOutTime: null
5. 시스템은 출근 기록을 저장하고 결과를 반환한다

## 대안 흐름
- workScheduleId가 제공된 경우: 해당 근무 일정과 연결하여 출근 기록을 생성한다
- workScheduleId가 null인 경우: 근무 일정 없이 출근 기록을 생성한다

## 예외 흐름
- 이미 당일 출근 기록이 존재하는 경우: AlreadyCheckedInException (ATT002) 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-ATTENDANCE-001-출퇴근 참조

## 검증 조건
- 인증된 사용자여야 한다
- 당일 해당 근로자의 출근 기록이 없어야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-ATT-001-01: 정상 출근 (Unit)
- Given: 활성 상태의 근로자가 존재하고, 당일 출근 기록이 없음
- When: 근로자가 출근 처리를 요청
- Then: AttendanceRecord가 생성되고, status=PENDING, checkInTime=현재시간, checkOutTime=null로 설정됨

### TC-ATT-001-02: 근무 일정 연결 출근 (Unit)
- Given: 활성 상태의 근로자가 존재하고, 당일 근무 일정(workScheduleId)이 있음
- When: workScheduleId를 포함하여 출근 처리를 요청
- Then: AttendanceRecord가 생성되고, workScheduleId가 연결됨

### TC-ATT-001-03: 근무 일정 없이 출근 (Unit)
- Given: 활성 상태의 근로자가 존재하고, workScheduleId가 null
- When: workScheduleId 없이 출근 처리를 요청
- Then: AttendanceRecord가 생성되고, workScheduleId=null로 설정됨

### TC-ATT-001-04: 이미 출근한 상태에서 재출근 시도 (Unit)
- Given: 해당 날짜에 이미 출근 기록이 존재
- When: 동일 날짜에 다시 출근 처리를 요청
- Then: AlreadyCheckedInException (ATT002) 발생 - "이미 출근 처리되었습니다."

### TC-ATT-001-05: 동시 출근 요청 (Integration)
- Given: 동일 근로자에 대한 두 개의 동시 출근 요청
- When: 두 요청이 동시에 처리됨
- Then: 하나만 성공하고 나머지는 AlreadyCheckedInException (ATT002) 발생

### TC-ATT-001-06: 출근 날짜 자동 설정 확인 (Unit)
- Given: 시스템 타임존이 Asia/Seoul이고, 현재 시간이 2026-03-09 08:55
- When: 출근 처리를 요청
- Then: attendanceDate가 2026-03-09(LocalDate)로 설정됨

### TC-ATT-001-07: 출근 API 인증 필수 확인 (E2E)
- Given: 인증 토큰 없이 요청
- When: POST /api/attendances/check-in 을 호출
- Then: 401 Unauthorized 응답
