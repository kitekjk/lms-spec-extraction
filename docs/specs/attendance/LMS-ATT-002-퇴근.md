# LMS-ATT-002: 퇴근

## 기본 정보
- type: use_case
- domain: attendance

## 관련 Spec
- LMS-API-ATT-001 (출퇴근API)
- LMS-ATT-001 (출근)

## 개요
근로자가 퇴근 체크를 요청하여 당일 출근 기록에 퇴근 시간을 기록하고 근무 상태를 평가한다.

## 관련 모델
- 주 모델: AttendanceRecord (Aggregate Root)
- 참조 모델: AttendanceTime, AttendanceStatus

## 선행 조건
- 인증된 사용자여야 한다 (EMPLOYEE, MANAGER, SUPER_ADMIN)
- 당일 출근 기록이 존재해야 한다
- 아직 퇴근하지 않은 상태여야 한다

## 기본 흐름
1. 근로자가 퇴근 체크를 요청한다
2. 시스템은 현재 로그인한 사용자의 ID를 employeeId로 사용한다
3. 시스템은 당일 해당 근로자의 출근 기록을 조회한다
4. 시스템은 이미 퇴근 처리되었는지 확인한다
5. 시스템은 퇴근 시간을 기록한다 (checkOut)
   - checkOutTime: 현재 시간
   - status: NORMAL (기본값, 이후 평가 필요)
6. 시스템은 수정된 출퇴근 기록을 저장하고 결과를 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 당일 출근 기록이 없는 경우: NotCheckedInException (ATT003) 발생
- 이미 퇴근 처리된 경우: AlreadyCheckedOutException (ATT004) 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-ATTENDANCE-001-출퇴근 참조

## 검증 조건
- 인증된 사용자여야 한다
- 당일 출근 기록이 존재해야 한다
- 아직 퇴근 처리되지 않은 상태여야 한다
- 퇴근 시간은 출근 시간보다 이후여야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-ATT-002-01: 정상 퇴근 (Unit)
- Given: 당일 출근 기록이 존재하고, 아직 퇴근하지 않은 상태(status=PENDING)
- When: 퇴근 처리를 요청
- Then: checkOutTime이 현재 시간으로 기록되고, status가 NORMAL로 변경됨

### TC-ATT-002-02: 미출근 상태에서 퇴근 시도 (Unit)
- Given: 당일 출근 기록이 존재하지 않음
- When: 퇴근 처리를 요청
- Then: NotCheckedInException (ATT003) 발생 - "출근 기록이 없습니다."

### TC-ATT-002-03: 이미 퇴근한 상태에서 재퇴근 시도 (Unit)
- Given: 당일 출근 기록이 존재하고, 이미 퇴근 처리(checkOutTime 설정)됨
- When: 다시 퇴근 처리를 요청
- Then: AlreadyCheckedOutException (ATT004) 발생 - "이미 퇴근 처리되었습니다."

### TC-ATT-002-04: 퇴근 시간이 출근 시간보다 이전인 경우 (Unit)
- Given: 출근 시간이 09:00으로 기록됨
- When: 퇴근 시간을 08:00으로 설정하려고 시도
- Then: "퇴근 시간은 출근 시간보다 이전일 수 없습니다." 에러 발생

### TC-ATT-002-05: 퇴근 후 근무 상태 평가 - 정상 (Unit)
- Given: 근무 시작 09:00, 근무 종료 18:00 일정이고, 출근 시간 08:55, 퇴근 시간 18:05
- When: 퇴근 후 evaluateStatus() 실행
- Then: status가 NORMAL로 설정됨

### TC-ATT-002-06: 퇴근 후 근무 상태 평가 - 지각 (Unit)
- Given: 근무 시작 09:00, 근무 종료 18:00 일정이고, 출근 시간 09:15 (10분 초과), 퇴근 시간 17:30
- When: 퇴근 후 evaluateStatus() 실행
- Then: status가 LATE로 설정됨 (지각 허용 시간 10분 초과)

### TC-ATT-002-07: 퇴근 후 근무 상태 평가 - 조퇴 (Unit)
- Given: 근무 시작 09:00, 근무 종료 18:00 일정이고, 출근 시간 09:05 (10분 이내), 퇴근 시간 16:00
- When: 퇴근 후 evaluateStatus() 실행
- Then: status가 EARLY_LEAVE로 설정됨

### TC-ATT-002-08: 지각 경계값 - 정확히 10분 (Unit)
- Given: 근무 시작 09:00 일정이고, 출근 시간이 정확히 09:10
- When: 퇴근 후 evaluateStatus() 실행
- Then: status가 NORMAL로 설정됨 (10분 이내이므로 정상)
