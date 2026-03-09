# LMS-LEAVE-001 휴가신청

## 기본 정보
- type: use_case
- id: LMS-LEAVE-001
- domain: leave
- last-updated: 2026-03-09

## 관련 정책
- POLICY-LEAVE-001: 휴가 유형, 직급별 연차 정책, 신청 규칙, 에러 코드
- POLICY-NFR-001: API 하위호환성, 변경 이력 추적

## 관련 Spec
- LMS-LEAVE-005-휴가조회 (신청 후 조회)
- LMS-API-LEAVE-001-휴가API (POST /api/leaves)

## 관련 모델
- **주 모델**: `LeaveRequest` (Aggregate Root)
- 참조 모델: `Employee` (잔여 연차 확인), `LeavePeriod` (Value Object), `LeaveType` (Enum), `LeaveStatus` (Enum)

## 개요
근로자(EMPLOYEE, MANAGER, SUPER_ADMIN)가 휴가를 신청한다. 신청 시 휴가 유형, 시작일, 종료일, 사유를 입력하며, 시스템은 잔여 연차 확인, 기간 겹침 검증, 날짜 유효성 검증을 수행한 후 PENDING 상태의 LeaveRequest를 생성한다.

## 기본 흐름
1. 사용자가 휴가 유형(LeaveType), 시작일(LocalDate), 종료일(LocalDate), 사유(String, 선택)를 입력한다.
2. 시스템이 시작일이 현재 날짜 이후인지 검증한다. 과거 날짜이면 에러코드 LEAVE006을 반환한다.
3. 시스템이 시작일이 종료일 이전 또는 동일한지 검증한다. 시작일이 종료일보다 이후이면 에러코드 LEAVE007을 반환한다.
4. 시스템이 요청자의 Employee 정보를 조회한다. 조회 실패 시 HTTP 404를 반환한다.
5. 시스템이 근로자 유형(EmployeeType)을 확인한다.
   - PART_TIME인 경우: 잔여 연차 확인을 건너뛴다 (UNPAID 휴가만 신청 가능).
   - REGULAR 또는 IRREGULAR인 경우: 잔여 연차(remainingLeave)가 신청 일수(시작일~종료일 일수) 이상인지 검증한다. 부족하면 에러코드 LEAVE002를 반환한다.
6. 시스템이 해당 근로자의 기존 승인된(APPROVED) 휴가와 기간 겹침 여부를 확인한다. 겹치면 에러코드 LEAVE003을 반환한다.
7. 시스템이 PENDING 상태의 LeaveRequest를 생성하고 저장한다.
8. 시스템이 생성된 LeaveRequest 정보를 반환한다 (HTTP 201).

## 대안 흐름
- **AF-1**: 아르바이트(PART_TIME) 근로자가 UNPAID 외 다른 유형의 휴가를 신청한 경우 → 에러코드 LEAVE002를 반환한다 (잔여 연차 0일).
- **AF-2**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.
- **AF-3**: 요청 본문의 필수 필드(leaveType, startDate, endDate)가 누락된 경우 → HTTP 400을 반환한다.

## 검증 조건
- startDate는 오늘 날짜(LocalDate.now()) 이후여야 한다 (startDate >= 오늘). 위반 시 LEAVE006 / HTTP 409
- startDate는 endDate 이전이거나 동일해야 한다 (startDate <= endDate). 위반 시 LEAVE007 / HTTP 409
- REGULAR, IRREGULAR 근로자의 잔여 연차(remainingLeave)는 신청 일수(startDate~endDate 일수) 이상이어야 한다. 위반 시 LEAVE002 / HTTP 409
- 신청 기간은 해당 근로자의 기존 APPROVED 상태 휴가 기간과 겹치지 않아야 한다. 위반 시 LEAVE003 / HTTP 409
- leaveType, startDate, endDate는 NOT NULL이어야 한다. 위반 시 HTTP 400

## 비기능 요구사항
- **POLICY-NFR-001 §1**: API 요청/응답 구조의 하위호환을 유지한다.
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.
- **POLICY-NFR-001 §3**: 휴가 신청 생성 시 AuditLog에 기록한다 (EntityType: LEAVE_REQUEST, ActionType: CREATE).

## 테스트 시나리오

### TC-LEAVE-001-01: 정규직 근로자 연차 신청 성공
- **레벨**: Unit
- **Given**: 정규직(REGULAR) 근로자의 잔여 연차가 10일이고, 기존 승인된 휴가와 겹치지 않는 기간이 존재한다.
- **When**: 해당 근로자가 2026-04-01 ~ 2026-04-03 (3일) ANNUAL 유형 휴가를 신청한다.
- **Then**: PENDING 상태의 LeaveRequest가 생성되고, HTTP 201이 반환된다. requestedDays는 3이다.

### TC-LEAVE-001-02: 잔여 연차 부족 시 신청 실패
- **레벨**: Unit
- **Given**: 계약직(IRREGULAR) 근로자의 잔여 연차가 2일이다.
- **When**: 해당 근로자가 2026-04-01 ~ 2026-04-05 (5일) ANNUAL 유형 휴가를 신청한다.
- **Then**: 에러코드 LEAVE002가 반환되고, LeaveRequest가 생성되지 않는다. HTTP 409가 반환된다.

### TC-LEAVE-001-03: 과거 날짜 신청 시 실패
- **레벨**: Unit
- **Given**: 현재 날짜가 2026-03-09이다.
- **When**: 근로자가 2026-03-01 ~ 2026-03-03 ANNUAL 유형 휴가를 신청한다.
- **Then**: 에러코드 LEAVE006이 반환되고, LeaveRequest가 생성되지 않는다. HTTP 409가 반환된다.

### TC-LEAVE-001-04: 승인된 휴가와 기간 중복 시 신청 실패
- **레벨**: Integration
- **Given**: 근로자에게 2026-04-01 ~ 2026-04-05 기간의 APPROVED 상태 휴가가 존재한다.
- **When**: 해당 근로자가 2026-04-03 ~ 2026-04-07 ANNUAL 유형 휴가를 신청한다.
- **Then**: 에러코드 LEAVE003이 반환되고, LeaveRequest가 생성되지 않는다. HTTP 409가 반환된다.

### TC-LEAVE-001-05: 아르바이트 근로자 무급 휴가 신청 성공
- **레벨**: Unit
- **Given**: 아르바이트(PART_TIME) 근로자 (잔여 연차 0일).
- **When**: 해당 근로자가 2026-04-01 ~ 2026-04-01 (1일) UNPAID 유형 휴가를 신청한다.
- **Then**: PENDING 상태의 LeaveRequest가 생성되고, HTTP 201이 반환된다.
