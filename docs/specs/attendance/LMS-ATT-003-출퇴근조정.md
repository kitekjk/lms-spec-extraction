# LMS-ATT-003: 출퇴근조정

## 기본 정보
- type: use_case
- domain: attendance

## 관련 Spec
- LMS-API-ATT-001 (출퇴근API)
- LMS-ATT-001 (출근)
- LMS-ATT-002 (퇴근)

## 개요
관리자가 출퇴근 기록의 시간을 수정사유와 함께 조정한다.

## 관련 모델
- 주 모델: AttendanceRecord (Aggregate Root)
- 참조 모델: AttendanceTime

## 선행 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 권한을 보유해야 한다
- 조정 대상 출퇴근 기록이 존재해야 한다

## 기본 흐름
1. 관리자가 출퇴근 기록 ID와 수정된 출근시간, 퇴근시간(선택), 수정사유를 입력하여 조정을 요청한다
2. 시스템은 출퇴근 기록을 조회한다
3. 시스템은 수정된 시간으로 AttendanceTime을 생성한다
4. 시스템은 출퇴근 기록을 업데이트한다 (수정 사유를 note에 저장)
5. 시스템은 수정된 기록을 저장하고 결과를 반환한다 (AuditLog 자동 생성)

## 대안 흐름
- adjustedCheckOutTime이 null인 경우: 출근시간만 수정한다

## 예외 흐름
- 출퇴근 기록을 찾을 수 없는 경우: AttendanceNotFoundException (ATT001) 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-ATTENDANCE-001-출퇴근 참조

## 검증 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 권한을 보유해야 한다
- 조정 대상 출퇴근 기록이 존재해야 한다
- 조정된 출근시간이 퇴근시간보다 늦을 수 없다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-ATT-003-01: 출퇴근 시간 정상 조정 (Unit)
- Given: 출퇴근 기록이 존재하고, MANAGER 또는 SUPER_ADMIN이 인증된 상태
- When: 수정된 출근시간 08:30, 퇴근시간 17:30, 수정사유 "단말기 오류로 인한 시간 조정"으로 조정을 요청
- Then: AttendanceTime이 수정되고, note에 수정 사유가 저장됨

### TC-ATT-003-02: 출근시간만 조정 (Unit)
- Given: 출퇴근 기록이 존재하고, adjustedCheckOutTime이 null
- When: 수정된 출근시간만 제공하여 조정을 요청
- Then: 출근시간만 수정되고, 기존 퇴근시간은 유지됨

### TC-ATT-003-03: 존재하지 않는 출퇴근 기록 조정 시도 (Unit)
- Given: 존재하지 않는 attendanceId
- When: 해당 출퇴근 기록의 조정을 요청
- Then: AttendanceNotFoundException (ATT001) 발생 - "출퇴근 기록을 찾을 수 없습니다."

### TC-ATT-003-04: 조정 후 출근시간이 퇴근시간보다 늦은 경우 (Unit)
- Given: 출퇴근 기록이 존재
- When: 수정된 출근시간 18:00, 퇴근시간 09:00으로 조정을 요청
- Then: "출근 시간은 퇴근 시간보다 늦을 수 없습니다." 에러 발생

### TC-ATT-003-05: EMPLOYEE 권한으로 출퇴근 조정 시도 (E2E)
- Given: EMPLOYEE 역할의 사용자가 인증된 상태
- When: 출퇴근 조정을 요청
- Then: 403 Forbidden 응답

### TC-ATT-003-06: 조정 시 AuditLog 생성 확인 (Integration)
- Given: 출퇴근 기록이 존재하고, SUPER_ADMIN이 인증된 상태
- When: 출퇴근 시간 조정을 수행
- Then: 조정 내역이 AuditLog에 자동으로 기록됨
