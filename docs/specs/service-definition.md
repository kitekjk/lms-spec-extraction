# LMS - 서비스 정의

## 기본 정보
- type: service_definition
- domain: lms
- owner: LMS팀
- last_updated: 2026-03-08

## 서비스 목적과 범위
LMS(Labor Management System)는 매장 근로자의 출퇴근 기록, 업무 스케줄, 휴가, 급여 산정을 관리하는 시스템이다.
정규직(REGULAR), 비정규직(IRREGULAR), 파트타임(PART_TIME) 근로자를 대상으로 하며,
매장 단위로 근로자를 관리한다.

## 기술 스택
- Language: Kotlin 2.1.0
- Framework: Spring Boot 3.5.9
- JDK: 17
- Build: Gradle 8.5 (Kotlin DSL)
- DB: MySQL 8.3.0 + Spring Data JPA (Hibernate 6.4.1)
- Security: Spring Security 6.x + JWT (JJWT 0.12.5)
- Test: JUnit 5.10.1 + MockK 1.13.9 + Kotest 5.8.0
- API Docs: SpringDoc OpenAPI 2.7.0
- Code Style: Spotless + ktlint
- Dependency Management: Gradle Version Catalog (gradle/libs.versions.toml)

## 핵심 모델

### User (사용자)
- **역할**: 인증/인가 관심사
- **주요 필드**:
  - id: UserId (VO, @JvmInline value class, 비어있을 수 없음)
  - email: Email (VO, 이메일 형식 검증, 정규식: `^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$`)
  - password: Password (VO, 비어있을 수 없음, 암호화 저장)
  - role: Role (Enum: SUPER_ADMIN, MANAGER, EMPLOYEE)
  - isActive: Boolean (기본값 true, 비활성 사용자 로그인 불가)
  - createdAt: Instant
  - lastLoginAt: Instant? (nullable)
- **생성 규칙**: User.create()로 SUPER_ADMIN 역할 생성 불가 (require 검증)
- **비즈니스 메서드**:
  - login(context): 활성 상태 검증, lastLoginAt 업데이트
  - deactivate(context): isActive=false로 변경

### Employee (근로자)
- **역할**: 근로자 정보 및 연차 관리
- **주요 필드**:
  - id: EmployeeId (VO, @JvmInline value class, 비어있을 수 없음)
  - userId: UserId (User와 1:1 관계)
  - name: EmployeeName (VO, 비어있을 수 없음, 최대 100자)
  - employeeType: EmployeeType (Enum: REGULAR, IRREGULAR, PART_TIME)
  - storeId: StoreId? (nullable, 매장 미배정 가능)
  - remainingLeave: RemainingLeave (VO, BigDecimal, 0 이상)
  - isActive: Boolean (기본값 true)
  - createdAt: Instant
- **생성 시 연차 자동 설정**:
  - REGULAR: 15.0일
  - IRREGULAR: 11.0일
  - PART_TIME: 0.0일
- **비즈니스 메서드**:
  - deductLeave(context, days): 연차 차감 (잔여 연차 >= 차감일수 검증)
  - restoreLeave(context, days): 연차 복원
  - update(context, name, employeeType, storeId): 정보 수정
  - deactivate(context): 비활성화

### Store (매장)
- **역할**: 매장 정보 관리
- **주요 필드**:
  - id: StoreId (VO, @JvmInline value class, 비어있을 수 없음)
  - name: StoreName (VO, 비어있을 수 없음, 최대 100자)
  - location: StoreLocation (VO, 비어있을 수 없음, 최대 200자)
  - createdAt: Instant
- **비즈니스 메서드**:
  - update(context, name, location): 매장 정보 수정

### WorkSchedule (근무 일정)
- **역할**: 근로자별 일정 관리
- **주요 필드**:
  - id: WorkScheduleId (VO)
  - employeeId: EmployeeId
  - storeId: StoreId
  - workDate: WorkDate (VO, LocalDate, 주말 판별 가능)
  - workTime: WorkTime (VO, startTime/endTime, startTime < endTime 검증)
  - isConfirmed: Boolean (기본값 false)
  - createdAt: Instant
- **비즈니스 규칙**:
  - 하나의 Employee는 하나의 날짜에 하나의 WorkSchedule만 가질 수 있다
  - 확정(isConfirmed=true)된 일정은 시간/날짜 변경 불가
  - WorkTime.standard(): 09:00~18:00
- **비즈니스 메서드**:
  - confirm(context): 확정 처리
  - unconfirm(context): 확정 해제
  - changeWorkTime(context, newWorkTime): 시간 변경 (미확정만)
  - changeWorkDate(context, newWorkDate): 날짜 변경 (미확정만)
  - calculateWorkHours(): 근무 시간 계산

### AttendanceRecord (출퇴근 기록)
- **역할**: 출퇴근 시간 기록 및 상태 관리
- **주요 필드**:
  - id: AttendanceRecordId (VO)
  - employeeId: EmployeeId
  - workScheduleId: WorkScheduleId? (nullable)
  - attendanceDate: LocalDate
  - attendanceTime: AttendanceTime (VO, checkInTime: Instant, checkOutTime: Instant?)
  - status: AttendanceStatus (Enum: NORMAL, LATE, EARLY_LEAVE, ABSENT, PENDING)
  - note: String? (수정 사유)
  - createdAt: Instant
- **상수**: LATE_TOLERANCE_MINUTES = 10 (지각 판정 기준 10분)
- **비즈니스 메서드**:
  - checkOut(context, checkOutTime): 퇴근 기록 (중복 퇴근 불가)
  - evaluateStatus(context, workSchedule): 상태 평가 (NORMAL/LATE/EARLY_LEAVE)
  - markAsAbsent(context): 결근 처리

### LeaveRequest (휴가 신청)
- **역할**: 휴가 신청/승인/거절/취소
- **주요 필드**:
  - id: LeaveRequestId (VO)
  - employeeId: EmployeeId
  - leaveType: LeaveType (Enum: ANNUAL, SICK, PERSONAL, MATERNITY, PATERNITY, BEREAVEMENT, UNPAID)
  - leavePeriod: LeavePeriod (VO, startDate/endDate, startDate <= endDate)
  - status: LeaveStatus (Enum: PENDING, APPROVED, REJECTED, CANCELLED)
  - reason: String?
  - approvedBy: UserId?
  - approvedAt: Instant?
  - rejectionReason: String?
  - createdAt: Instant
- **상태 전이**:
  - PENDING → APPROVED (승인)
  - PENDING → REJECTED (거절)
  - PENDING → CANCELLED (취소)
  - APPROVED → CANCELLED (취소)
- **비즈니스 규칙**:
  - 모든 LeaveType은 requiresApproval=true
  - 휴가 일수 = endDate - startDate + 1 (양 끝 포함)
  - LeavePeriod.overlapsWith()로 기간 중복 판정

### Payroll (급여)
- **역할**: 월별 급여 계산 결과 저장
- **주요 필드**:
  - id: PayrollId (VO)
  - employeeId: EmployeeId
  - period: PayrollPeriod (VO, YYYY-MM 형식, 정규식 검증)
  - amount: PayrollAmount (VO, baseAmount/overtimeAmount/deductions, 각각 >= 0)
  - calculatedAt: Instant
  - isPaid: Boolean (기본값 false)
  - paidAt: Instant?
  - createdAt: Instant
- **비즈니스 규칙**:
  - 지급 완료(isPaid=true)된 급여는 수정 불가
  - totalAmount = (baseAmount + overtimeAmount - deductions).setScale(2, HALF_UP)

### PayrollDetail (급여 상세)
- **역할**: 일별 급여 계산 내역
- **주요 필드**:
  - id: PayrollDetailId (VO)
  - payrollId: PayrollId
  - workDate: LocalDate
  - workType: WorkType (Enum: WEEKDAY, NIGHT, WEEKEND, HOLIDAY)
  - hours: BigDecimal (>= 0)
  - hourlyRate: BigDecimal (> 0)
  - multiplier: BigDecimal (>= 0)
  - amount: BigDecimal (= hours × hourlyRate × multiplier, scale 2, HALF_UP)

### PayrollPolicy (급여 정책)
- **역할**: 근무유형별 가산율 정의
- **주요 필드**:
  - id: PayrollPolicyId (VO)
  - policyType: PolicyType (Enum: OVERTIME_WEEKDAY, OVERTIME_WEEKEND, OVERTIME_HOLIDAY, NIGHT_SHIFT, HOLIDAY_WORK, BONUS, ALLOWANCE)
  - multiplier: PolicyMultiplier (VO, BigDecimal, 0 이상 10 이하)
  - effectivePeriod: PolicyEffectivePeriod (VO, effectiveFrom/effectiveTo)
  - description: String?
  - createdAt: Instant
- **사전 정의 가산율**:
  - PolicyMultiplier.standard(): 1.5 (평일 초과근무)
  - PolicyMultiplier.weekend(): 2.0 (주말/야간)
  - PolicyMultiplier.holiday(): 2.5 (공휴일)

### PayrollBatchHistory (배치 이력)
- **역할**: 급여 일괄 계산 실행 이력
- **주요 필드**:
  - id: PayrollBatchHistoryId
  - period: PayrollPeriod
  - storeId: StoreId? (null이면 전체 매장)
  - status: BatchStatus (Enum: RUNNING, COMPLETED, PARTIAL_SUCCESS, FAILED)
  - totalCount / successCount / failureCount: Int
  - startedAt / completedAt: Instant
  - errorMessage: String?

### AuditLog (감사 로그)
- **역할**: 엔티티 변경 이력 추적
- **주요 필드**:
  - id: AuditLogId (VO)
  - entityType: EntityType (sealed class: ATTENDANCE_RECORD, EMPLOYEE, STORE, USER, WORK_SCHEDULE, LEAVE_REQUEST, PAYROLL)
  - entityId: String
  - actionType: ActionType (sealed class: CREATE, UPDATE, DELETE, ACTIVATE, DEACTIVATE)
  - performedBy / performedByName: String
  - performedAt: Instant
  - oldValue / newValue: String? (JSON)
  - reason / clientIp: String?

## 도메인 서비스

### LeavePolicyService
- **역할**: 근로자 유형별 연차 정책 관리
- **규칙**:
  - REGULAR: 15일/년
  - IRREGULAR: 11일/년
  - PART_TIME: 0일 (무급 휴가만 가능)
- **메서드**: getAnnualLeaveByEmployeeType, initializeEmployeeLeave, canRequestLeave, validateLeaveRequest

### PayrollCalculationEngine
- **역할**: 출퇴근 기록 기반 급여 계산
- **근무유형 판정** (우선순위):
  1. HOLIDAY: 공휴일 (1월 1일, 12월 25일)
  2. WEEKEND: 토요일 또는 일요일
  3. NIGHT: 22:00 ~ 06:00
  4. WEEKDAY: 위에 해당하지 않는 경우
- **계산 흐름**:
  1. 승인된 휴가 날짜 추출
  2. 완료된 출퇴근 기록만 필터링 (checkOutTime 존재)
  3. 휴가 날짜 제외
  4. 일별 근무유형 판정 및 가산율 적용
  5. baseAmount (WEEKDAY) / overtimeAmount (비WEEKDAY) 분리
- **가산율 기본값** (정책 없는 경우): 1.0

## 외부 계약

### 현재 연계
- (없음 - 현재 단독 서비스)

### 향후 연계 예정
- **급여지급 시스템**: 월별 근무이력 전달 (발행 예정)
- **HR 시스템**: 직원 마스터 정보 수신 (수신 예정)
- **ERP**: 매장 정보 동기화 (수신 예정)

## 소유 데이터
- 출퇴근 기록: LMS가 truth owner
- 근무 일정: LMS가 truth owner
- 직원 기본정보: LMS가 truth owner (향후 HR에서 수신 가능)
- 매장 정보: LMS가 truth owner (향후 ERP에서 수신 가능)
