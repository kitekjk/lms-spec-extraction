# LMS-ATTENDANCE-001: 출퇴근 기록

## 기본 정보
- type: use_case
- domain: attendance
- service: LMS
- priority: high

## 관련 정책
- POLICY-ATTENDANCE-001 (동일 날짜 중복 출근 불가, 출근 없이 퇴근 불가, 지각 허용 10분)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-ATTENDANCE-001-출퇴근API](LMS-API-ATTENDANCE-001-출퇴근API.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **AttendanceRecord**: 생성/변경 대상
  - 사용하는 주요 필드: employeeId, attendanceDate, attendanceTime, status
  - 상태 변경: 출근(PENDING) → 퇴근(NORMAL)

### 참조 모델
- **WorkSchedule**: 상태 평가 기준 (선택)
  - 참조하는 필드: workTime (startTime, endTime)

## 개요
근로자가 출근 또는 퇴근을 기록한다.

## 선행 조건
- 요청자가 EMPLOYEE, MANAGER 또는 SUPER_ADMIN 역할이어야 한다

## 기본 흐름

### 출근
1. 오늘 날짜를 기준으로 해당 Employee의 출퇴근 기록 존재 여부를 확인한다
2. AttendanceRecord.checkIn(context, employeeId, workScheduleId, checkInTime)을 호출한다
3. 생성된 AttendanceRecord를 저장하고 결과를 반환한다

### 퇴근
1. 오늘 날짜를 기준으로 해당 Employee의 출퇴근 기록을 조회한다
2. 이미 퇴근 처리되었는지 확인한다
3. AttendanceRecord.checkOut(context, checkOutTime)을 호출한다
4. 수정된 AttendanceRecord를 저장하고 결과를 반환한다

## 대안 흐름
- 동일 날짜에 이미 출근한 경우: `AlreadyCheckedInException` 발생
- 출근 기록이 없는데 퇴근 시도: `NotCheckedInException` 발생
- 이미 퇴근한 기록에 재퇴근 시도: `AlreadyCheckedOutException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 정상 출근 시 AttendanceRecord가 PENDING 상태로 생성되어야 한다
- 정상 퇴근 시 status가 NORMAL로 변경되어야 한다
- 동일 날짜 중복 출근 시 AlreadyCheckedInException이 발생해야 한다
- 출근 기록 없이 퇴근 시 NotCheckedInException이 발생해야 한다
- 이미 퇴근한 기록에 재퇴근 시 AlreadyCheckedOutException이 발생해야 한다
- 퇴근 시간은 출근 시간 이후여야 한다
- checkOutTime != null이면 isCompleted()가 true를 반환해야 한다

## 비즈니스 규칙
- 출근 시 workScheduleId는 선택값 (일정 없이도 출근 가능)
- 출근 시 초기 상태: PENDING
- 퇴근 시 상태: NORMAL (evaluateStatus 호출 전)
- AttendanceTime.checkOut()에서 중복 퇴근 검증 (checkOutTime == null 확인)
- 지각/조퇴 판정은 evaluateStatus(workSchedule)로 별도 수행

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용. 추가 특화 사항:

### 동시성
- 같은 직원의 동시 출근 요청 시 1건만 성공해야 한다

### 데이터 정합성
- 출근/퇴근 기록은 원자적으로 저장되어야 한다

## 테스트 시나리오

### TC-ATT-001-01: 정상 출근 (Integration)
- Given: 해당 Employee의 오늘 출퇴근 기록이 없다
- When: 출근을 기록한다
- Then: PENDING 상태의 AttendanceRecord가 생성된다

### TC-ATT-001-02: 정상 퇴근 (Integration)
- Given: 해당 Employee가 오늘 출근 처리되어 있다 (PENDING)
- When: 퇴근을 기록한다
- Then: status가 NORMAL로 변경되고 checkOutTime이 기록된다

### TC-ATT-001-03: 중복 출근 (Integration)
- Given: 해당 Employee가 오늘 이미 출근했다
- When: 다시 출근을 시도한다
- Then: AlreadyCheckedInException이 발생한다

### TC-ATT-001-04: 출근 없이 퇴근 (Integration)
- Given: 해당 Employee의 오늘 출근 기록이 없다
- When: 퇴근을 시도한다
- Then: NotCheckedInException이 발생한다

### TC-ATT-001-05: 이미 퇴근 후 재퇴근 (Integration)
- Given: 해당 Employee가 이미 퇴근했다
- When: 다시 퇴근을 시도한다
- Then: AlreadyCheckedOutException이 발생한다

### TC-ATT-001-06: AttendanceTime 검증 (Unit)
- Given: checkInTime이 checkOutTime 이후인 AttendanceTime
- When: AttendanceTime을 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-ATT-001-07: 동시 출근 요청 (Integration)
- Given: 출근 기록이 없는 Employee
- When: 동시에 2건의 출근 요청을 보낸다
- Then: 1건만 성공하고 나머지는 실패한다

## 관련 이벤트
- 발행: 없음
- 수신: 없음
