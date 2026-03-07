# LMS-ATTENDANCE-002: 출퇴근 기록 수정

## 기본 정보
- type: use_case
- domain: attendance
- service: LMS
- priority: medium

## 관련 정책
- POLICY-ATTENDANCE-001 (MANAGER 또는 SUPER_ADMIN만 수정, 수정 사유 필수, AuditLog 자동 생성)
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- [service-definition](../service-definition.md)
- [LMS-API-ATTENDANCE-001-출퇴근API](LMS-API-ATTENDANCE-001-출퇴근API.md)
- [LMS-ATTENDANCE-001-출퇴근기록](LMS-ATTENDANCE-001-출퇴근기록.md)

## 관련 모델

### 주 모델 (Aggregate Root)
- **AttendanceRecord**: 수정 대상
  - 사용하는 주요 필드: attendanceTime, note
  - 상태 변경: checkInTime/checkOutTime 조정, note 기록

### 참조 모델
- **AuditLog**: 변경 이력 자동 생성
  - 참조하는 필드: entityType, entityId, oldValue, newValue, reason

## 개요
관리자가 근로자의 출퇴근 기록을 수정(조정)한다.

## 선행 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 역할이어야 한다
- 수정 대상 AttendanceRecord가 존재해야 한다

## 기본 흐름
1. recordId로 AttendanceRecord를 조회한다
2. 조정된 출근시간과 퇴근시간으로 새 AttendanceTime을 생성한다
3. 수정 사유를 note에 기록하며 AttendanceRecord를 copy한다
4. 수정된 AttendanceRecord를 저장한다
5. EntityListener가 자동으로 AuditLog를 생성한다

## 대안 흐름
- AttendanceRecord가 존재하지 않는 경우: `AttendanceNotFoundException` 발생

## 예외 흐름
- 없음

## 검증 조건
- 수정 후 checkInTime이 adjustedCheckInTime으로 변경되어야 한다
- 수정 후 checkOutTime이 adjustedCheckOutTime으로 변경되어야 한다
- 수정 사유가 note에 기록되어야 한다
- 존재하지 않는 기록 수정 시 AttendanceNotFoundException이 발생해야 한다
- adjustedCheckInTime이 adjustedCheckOutTime 이후일 수 없다
- 수정 시 AuditLog가 자동 생성되어야 한다

## 비즈니스 규칙
- 출퇴근 수정 시 변경 전 값은 AuditLog의 oldValue(JSON)에 저장된다
- 변경 후 값은 AuditLog의 newValue(JSON)에 저장된다
- 수정 사유(reason)는 필수이다
- adjustedCheckOutTime은 선택값이다 (출근시간만 수정 가능)

## 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001) 적용. 추가 특화 사항:

### 감사 추적
- 모든 출퇴근 수정은 AuditLog로 자동 기록된다
- EntityListener 패턴을 사용한다

### 데이터 정합성
- 출퇴근 수정과 AuditLog 생성은 같은 트랜잭션에서 처리된다

## 테스트 시나리오

### TC-ATT-002-01: 정상 출퇴근 수정 (Integration)
- Given: 출퇴근 기록이 존재한다
- When: 조정된 출근/퇴근 시간과 사유를 입력하여 수정한다
- Then: checkInTime/checkOutTime이 변경되고 note가 기록된다

### TC-ATT-002-02: 출근시간만 수정 (Integration)
- Given: 출퇴근 기록이 존재한다
- When: adjustedCheckOutTime=null로 수정한다
- Then: checkInTime만 변경되고 checkOutTime은 기존 값 유지

### TC-ATT-002-03: 존재하지 않는 기록 수정 (Integration)
- Given: 존재하지 않는 recordId가 주어진다
- When: 수정을 시도한다
- Then: AttendanceNotFoundException이 발생한다

### TC-ATT-002-04: AuditLog 자동 생성 (Integration)
- Given: 출퇴근 기록이 존재한다
- When: 수정을 수행한다
- Then: AuditLog가 생성되고 oldValue/newValue/reason이 기록된다

### TC-ATT-002-05: 시간 순서 검증 (Unit)
- Given: adjustedCheckInTime이 adjustedCheckOutTime 이후이다
- When: AttendanceTime을 생성한다
- Then: IllegalArgumentException이 발생한다

### TC-ATT-002-06: 권한 검증 - EMPLOYEE 접근 (E2E)
- Given: EMPLOYEE 역할로 로그인한 상태이다
- When: 출퇴근 수정 API를 호출한다
- Then: 403 Forbidden이 반환된다

## 관련 이벤트
- 발행: AuditLog 생성 (EntityListener를 통해 자동)
- 수신: 없음
