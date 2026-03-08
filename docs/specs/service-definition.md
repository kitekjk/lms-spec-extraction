# LMS Backend - 서비스 정의

## 기본 정보
- type: service_definition
- name: LMS (Labor Management System)
- modules: domain, application, infrastructure, interfaces
- group: com.example.lms
- version: 0.0.1-SNAPSHOT

## 서비스 목적과 범위

매장 직원의 출퇴근 기록, 업무 스케줄, 휴가, 급여를 통합 관리하는 노동관리 백엔드 서비스.

---

## 공통 모델

### DomainContext
도메인 계층의 모든 비즈니스 메서드에 첫 번째 인자로 전달되는 요청 메타데이터 인터페이스.

| 필드 | 타입 | 설명 | 비고 |
|------|------|------|------|
| serviceName | String | 요청 도메인/서비스명 | |
| userId | String | 요청 사용자 ID | |
| userName | String | 요청 사용자 이름 | |
| roleId | String | 역할 ID (Role enum의 name) | |
| requestId | String | 요청 추적용 UUID | 기본값: 랜덤 UUID |
| requestedAt | Instant | 요청 시각 | 기본값: 현재 시각 |
| clientIp | String | 클라이언트 IP | |

- 기본 구현체: `DomainContextBase` (data class)
- 시스템 내부 작업용 팩토리: `DomainContextBase.system(serviceName)` - userId="SYSTEM", clientIp="127.0.0.1"

---

## 핵심 모델

### User (Aggregate Root)
인증 및 인가 정보를 관리하는 사용자 Aggregate.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | UserId | 사용자 식별자 | UUID 기반, 비어있을 수 없음 |
| email | Email | 이메일 주소 | 이메일 정규식 검증 (`^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$`) |
| password | Password | 인코딩된 비밀번호 | 비어있을 수 없음 |
| role | Role | 사용자 역할 | SUPER_ADMIN, MANAGER, EMPLOYEE |
| isActive | Boolean | 활성화 상태 | 생성 시 true |
| createdAt | Instant | 생성 시각 | context.requestedAt |
| lastLoginAt | Instant? | 마지막 로그인 시각 | nullable, 생성 시 null |

**비즈니스 규칙:**
- SUPER_ADMIN 역할은 `create()`로 생성 불가 (시스템에서만 생성 가능)
- 로그인 시 isActive가 true여야 함
- 비활성화/활성화 시 현재 상태와 반대여야 함

**Value Objects:**
- `UserId`: @JvmInline value class, UUID 기반, `generate()`, `from(String)`
- `Email`: @JvmInline value class, 이메일 정규식 검증
- `Password`: @JvmInline value class, encodedValue 필드, 비어있을 수 없음
- `Role`: enum class - SUPER_ADMIN("슈퍼 관리자"), MANAGER("매니저"), EMPLOYEE("근로자")

**Repository:**
- `save(user)`, `findById(userId)`, `findByEmail(email)`, `existsByEmail(email)`, `delete(userId)`

---

### Employee (Aggregate Root)
근로자 정보를 관리하는 Aggregate. User와 1:1 관계.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | EmployeeId | 근로자 식별자 | UUID 기반, 비어있을 수 없음 |
| userId | UserId | 연결된 사용자 ID | User 1:1 참조 |
| name | EmployeeName | 근로자 이름 | 비어있을 수 없음, 최대 100자 |
| employeeType | EmployeeType | 근로자 유형 | REGULAR, IRREGULAR, PART_TIME |
| storeId | StoreId? | 배정 매장 ID | nullable |
| remainingLeave | RemainingLeave | 잔여 연차 | BigDecimal, 0 이상 |
| isActive | Boolean | 활성화 상태 | 생성 시 true |
| createdAt | Instant | 생성 시각 | context.requestedAt |

**비즈니스 규칙:**
- 생성 시 직급별 초기 연차: REGULAR=15일, IRREGULAR=11일, PART_TIME=0일
- 연차 차감 시 잔여 연차 >= 차감일수 필요
- 연차 복구 시 복구일수 > 0

**Value Objects:**
- `EmployeeId`: @JvmInline value class, UUID 기반
- `EmployeeName`: @JvmInline value class, 비어있을 수 없음, 최대 100자
- `EmployeeType`: enum class - REGULAR("정규직"), IRREGULAR("계약직"), PART_TIME("아르바이트")
- `RemainingLeave`: @JvmInline value class, BigDecimal 기반, 0 이상, deduct/add 메서드 제공

**Repository:**
- `save`, `findById`, `findByUserId`, `findByStoreId`, `findActiveByStoreId`, `findByStoreIdAndActive`, `findByActive`, `findAll`, `delete`

---

### Store (Aggregate Root)
매장 정보를 관리하는 Aggregate.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | StoreId | 매장 식별자 | UUID 기반, 비어있을 수 없음 |
| name | StoreName | 매장 이름 | 비어있을 수 없음, 최대 100자 |
| location | StoreLocation | 매장 위치 | 비어있을 수 없음, 최대 200자 |
| createdAt | Instant | 생성 시각 | context.requestedAt |

**Value Objects:**
- `StoreId`: @JvmInline value class, UUID 기반
- `StoreName`: @JvmInline value class, 비어있을 수 없음, 최대 100자
- `StoreLocation`: @JvmInline value class, 비어있을 수 없음, 최대 200자

**Repository:**
- `save`, `findById`, `findByName`, `findAll`, `delete`

---

### AttendanceRecord (Aggregate Root)
근로자의 출퇴근 기록을 관리하는 Aggregate.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | AttendanceRecordId | 출퇴근 기록 식별자 | UUID 기반, 비어있을 수 없음 |
| employeeId | EmployeeId | 근로자 ID | Employee 참조 |
| workScheduleId | WorkScheduleId? | 근무 일정 ID | nullable |
| attendanceDate | LocalDate | 출근 날짜 | 출근 시간 기준 자동 계산 |
| attendanceTime | AttendanceTime | 출퇴근 시간 | checkInTime 필수, checkOutTime nullable |
| status | AttendanceStatus | 출퇴근 상태 | NORMAL, LATE, EARLY_LEAVE, ABSENT, PENDING |
| note | String? | 메모 | nullable |
| createdAt | Instant | 생성 시각 | context.requestedAt |

**비즈니스 규칙:**
- 출근 체크 시 status = PENDING
- 퇴근 체크 시 기본 status = NORMAL
- 지각 허용 시간: 10분 (LATE_TOLERANCE_MINUTES)
- 상태 평가: 퇴근 처리 완료 후만 가능
- 상태 판정 기준: 스케줄 대비 실제 출퇴근 시간 비교 (지각/조퇴/정상)

**Value Objects:**
- `AttendanceRecordId`: @JvmInline value class, UUID 기반
- `AttendanceTime`: data class
  - checkInTime: Instant (필수)
  - checkOutTime: Instant? (nullable)
  - 제약: checkOutTime이 있으면 checkInTime <= checkOutTime
  - 근무 시간 계산: Duration 기반 (분 -> 시간)
- `AttendanceStatus`: enum class - NORMAL("정상 출근"), LATE("지각"), EARLY_LEAVE("조퇴"), ABSENT("결근"), PENDING("퇴근 대기 중")

**Repository:**
- `save`, `findById`, `findByEmployeeId`, `findByEmployeeIdAndDate`, `findByEmployeeIdAndDateRange`, `findPendingByEmployeeId`, `delete`

---

### WorkSchedule (Aggregate Root)
근로자의 근무 일정을 관리하는 Aggregate.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | WorkScheduleId | 근무 일정 식별자 | UUID 기반, 비어있을 수 없음 |
| employeeId | EmployeeId | 근로자 ID | Employee 참조 |
| storeId | StoreId | 매장 ID | Store 참조 |
| workDate | WorkDate | 근무 날짜 | LocalDate 래핑 |
| workTime | WorkTime | 근무 시간 | 시작/종료 시간 |
| isConfirmed | Boolean | 확정 여부 | 생성 시 false |
| createdAt | Instant | 생성 시각 | context.requestedAt |

**비즈니스 규칙:**
- 확정된 일정은 시간/날짜 변경 불가
- 이미 확정된 일정은 재확정 불가
- 확정되지 않은 일정은 확정 취소 불가

**Value Objects:**
- `WorkScheduleId`: @JvmInline value class, UUID 기반
- `WorkDate`: @JvmInline value class, LocalDate 래핑, 주말 판단(토/일) 지원
- `WorkTime`: data class
  - startTime: LocalTime
  - endTime: LocalTime
  - 제약: startTime <= endTime
  - 표준 근무 시간: 09:00~18:00
  - 근무 시간 계산: Duration 기반

**Repository:**
- `save`, `findById`, `findByEmployeeId`, `findByStoreId`, `findByEmployeeIdAndWorkDate`, `findByEmployeeIdAndDateRange`, `findByStoreIdAndDateRange`, `delete`

---

### LeaveRequest (Aggregate Root)
근로자의 휴가 신청 및 승인 프로세스를 관리하는 Aggregate.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | LeaveRequestId | 휴가 신청 식별자 | UUID 기반, 비어있을 수 없음 |
| employeeId | EmployeeId | 근로자 ID | Employee 참조 |
| leaveType | LeaveType | 휴가 유형 | ANNUAL, SICK, PERSONAL, MATERNITY, PATERNITY, BEREAVEMENT, UNPAID |
| leavePeriod | LeavePeriod | 휴가 기간 | startDate <= endDate |
| status | LeaveStatus | 신청 상태 | PENDING, APPROVED, REJECTED, CANCELLED |
| reason | String? | 사유 | nullable |
| approvedBy | UserId? | 승인자 ID | nullable |
| approvedAt | Instant? | 승인 시각 | nullable |
| rejectionReason | String? | 거부 사유 | nullable, 거부 시 필수(비어있을 수 없음) |
| createdAt | Instant | 생성 시각 | context.requestedAt |

**비즈니스 규칙:**
- 생성 시 status = PENDING
- 승인: PENDING 상태에서만 가능
- 거부: PENDING 상태에서만 가능, 거부 사유 필수
- 취소: PENDING 또는 APPROVED 상태에서만 가능
- 모든 휴가 유형은 승인 필요 (requiresApproval = true)
- 기간 겹침 확인 지원

**Value Objects:**
- `LeaveRequestId`: @JvmInline value class, UUID 기반
- `LeaveType`: enum class - ANNUAL("연차"), SICK("병가"), PERSONAL("개인 사유"), MATERNITY("출산 휴가"), PATERNITY("육아 휴가"), BEREAVEMENT("경조사"), UNPAID("무급 휴가"), 모두 requiresApproval=true
- `LeaveStatus`: enum class - PENDING("승인 대기"), APPROVED("승인됨"), REJECTED("거부됨"), CANCELLED("취소됨")
- `LeavePeriod`: data class
  - startDate: LocalDate
  - endDate: LocalDate
  - 제약: startDate <= endDate
  - 일수 계산: endDate - startDate + 1 (시작일/종료일 포함)
  - 기간 포함/겹침 확인 지원

**Repository:**
- `save`, `findById`, `findByEmployeeId`, `findByEmployeeIdAndStatus`, `findByEmployeeIdAndDateRange`, `findPendingRequests`, `delete`

---

### Payroll (Aggregate Root)
근로자의 급여 정보 및 계산을 관리하는 Aggregate.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | PayrollId | 급여 식별자 | UUID 기반, 비어있을 수 없음 |
| employeeId | EmployeeId | 근로자 ID | Employee 참조 |
| period | PayrollPeriod | 급여 기간 | YYYY-MM 형식 |
| amount | PayrollAmount | 급여 금액 | 기본급/초과근무수당/공제액 |
| calculatedAt | Instant | 계산 시각 | |
| isPaid | Boolean | 지급 여부 | 생성 시 false |
| paidAt | Instant? | 지급 시각 | nullable |
| createdAt | Instant | 생성 시각 | context.requestedAt |

**비즈니스 규칙:**
- 지급 완료된 급여는 수정/재계산 불가
- 초과근무수당 추가 시 계산 시각 갱신

**Value Objects:**
- `PayrollId`: @JvmInline value class, UUID 기반
- `PayrollPeriod`: @JvmInline value class, YYYY-MM 형식 정규식 검증, YearMonth 변환 지원
- `PayrollAmount`: data class
  - baseAmount: BigDecimal (0 이상)
  - overtimeAmount: BigDecimal (0 이상)
  - deductions: BigDecimal (기본값 0, 0 이상)
  - 총액 계산: (기본급 + 초과근무수당 - 공제액), 소수점 2자리 HALF_UP

**Repository:**
- `save`, `findById`, `findByEmployeeId`, `findByEmployeeIdAndPeriod`, `findByPeriod`, `findUnpaidByEmployeeId`, `delete`

---

### PayrollDetail (Entity)
일별 근무 유형별 급여 계산 내역. Payroll에 종속.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | PayrollDetailId | 급여 상세 식별자 | UUID 기반 |
| payrollId | PayrollId | 소속 급여 ID | Payroll 참조 |
| workDate | LocalDate | 근무 날짜 | |
| workType | WorkType | 근무 유형 | WEEKDAY, NIGHT, WEEKEND, HOLIDAY |
| hours | BigDecimal | 근무 시간 | 0 이상 |
| hourlyRate | BigDecimal | 시급 | 0 초과 |
| multiplier | BigDecimal | 가산율 | 0 이상 |
| amount | BigDecimal | 계산 금액 | hours * hourlyRate * multiplier |

**Value Objects/Enums:**
- `PayrollDetailId`: @JvmInline value class, UUID 기반
- `WorkType`: enum class - WEEKDAY(평일), NIGHT(야간 22:00~06:00), WEEKEND(주말), HOLIDAY(공휴일)

**Repository:**
- `save`, `saveAll`, `findById`, `findByPayrollId`, `deleteByPayrollId`

---

### PayrollPolicy (Aggregate Root)
급여 가산율 정책을 관리하는 Aggregate.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | PayrollPolicyId | 정책 식별자 | UUID 기반, 비어있을 수 없음 |
| policyType | PolicyType | 정책 유형 | 7개 유형 |
| multiplier | PolicyMultiplier | 가산율 | 0 이상 10 이하 |
| effectivePeriod | PolicyEffectivePeriod | 유효 기간 | 시작일 필수, 종료일 nullable |
| description | String? | 설명 | nullable |
| createdAt | Instant | 생성 시각 | context.requestedAt |

**비즈니스 규칙:**
- 유효하지 않은 정책은 배율 변경 불가
- 종료일은 시작일 이후여야 함

**Value Objects/Enums:**
- `PayrollPolicyId`: @JvmInline value class, UUID 기반
- `PolicyType`: enum class - OVERTIME_WEEKDAY("평일 초과근무"), OVERTIME_WEEKEND("주말 초과근무"), OVERTIME_HOLIDAY("공휴일 초과근무"), NIGHT_SHIFT("야간 근무"), HOLIDAY_WORK("휴일 근무"), BONUS("보너스"), ALLOWANCE("수당")
- `PolicyMultiplier`: @JvmInline value class, BigDecimal, 0~10 범위, 기본 배율: standard=1.5, weekend=2.0, holiday=2.5
- `PolicyEffectivePeriod`: data class
  - effectiveFrom: LocalDate (필수)
  - effectiveTo: LocalDate? (nullable, null이면 무기한)
  - 제약: effectiveTo != null이면 effectiveFrom <= effectiveTo

**Repository:**
- `save`, `findById`, `findByPolicyType`, `findEffectivePolicies(date)`, `findCurrentlyEffectivePolicies`, `delete`

---

### PayrollBatchHistory (Aggregate Root)
급여 배치 실행 이력을 관리하는 Aggregate.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | PayrollBatchHistoryId | 배치 이력 식별자 | UUID 기반 |
| period | PayrollPeriod | 대상 급여 기간 | YYYY-MM |
| storeId | StoreId? | 대상 매장 ID | nullable (전체 매장인 경우 null) |
| status | BatchStatus | 배치 상태 | RUNNING, COMPLETED, PARTIAL_SUCCESS, FAILED |
| totalCount | Int | 총 대상 수 | |
| successCount | Int | 성공 수 | |
| failureCount | Int | 실패 수 | |
| startedAt | Instant | 시작 시각 | |
| completedAt | Instant? | 완료 시각 | nullable |
| errorMessage | String? | 오류 메시지 | nullable |
| createdAt | Instant | 생성 시각 | context.requestedAt |

**비즈니스 규칙:**
- 실행 중(RUNNING)인 배치만 완료/실패 처리 가능
- 실패 0건이면 COMPLETED, 그 외 PARTIAL_SUCCESS

**Value Objects/Enums:**
- `PayrollBatchHistoryId`: @JvmInline value class, UUID 기반, private constructor
- `BatchStatus`: enum class - RUNNING, COMPLETED, PARTIAL_SUCCESS, FAILED

**Repository:**
- `save`, `findById`, `findAll(startDate?, endDate?)`, `findByStoreId`, `findByPeriod`

---

### AuditLog (Aggregate Root)
시스템 내 중요 데이터 변경 이력을 추적하는 Aggregate.

| 필드 | 타입 | 설명 | 제약조건 |
|------|------|------|----------|
| id | AuditLogId | 감사로그 식별자 | UUID 기반 |
| entityType | EntityType | 대상 엔티티 타입 | sealed class |
| entityId | String | 대상 엔티티 ID | |
| actionType | ActionType | 액션 타입 | sealed class |
| performedBy | String | 수행자 ID | context.userId |
| performedByName | String | 수행자 이름 | context.userName |
| performedAt | Instant | 수행 시각 | context.requestedAt |
| oldValue | String? | 변경 전 값 (JSON) | nullable |
| newValue | String? | 변경 후 값 (JSON) | nullable |
| reason | String? | 변경 사유 | nullable |
| clientIp | String? | 클라이언트 IP | context.clientIp |

**비즈니스 규칙:**
- 생성 전용 (변경/삭제 메서드 없음, 불변 로그)

**Value Objects:**
- `AuditLogId`: @JvmInline value class, UUID 기반
- `ActionType`: sealed class - Create, Update, Delete, Activate, Deactivate (각각 value 필드: "CREATE", "UPDATE", "DELETE", "ACTIVATE", "DEACTIVATE")
- `EntityType`: sealed class - AttendanceRecord, Employee, Store, User, WorkSchedule, LeaveRequest, Payroll (각각 value 필드)

**Repository:**
- `save`, `findById`, `findByEntityTypeAndEntityId`, `findByPerformedBy`, `findByDateRange`, `findByEntityTypeAndDateRange`

---

### TokenProvider (도메인 인터페이스)
토큰 생성 및 검증을 위한 인터페이스. 구현은 infrastructure 계층.

| 메서드 | 파라미터 | 반환 | 설명 |
|--------|----------|------|------|
| generateAccessToken | employeeId: String, role: String, storeId: String? | String | Access Token 생성 |
| generateRefreshToken | employeeId: String | String | Refresh Token 생성 |
| validateToken | token: String | Boolean | 토큰 유효성 검증 |
| extractEmployeeId | token: String | String | employeeId 추출 |
| extractRole | token: String | String? | role 추출 |
| extractStoreId | token: String | String? | storeId 추출 |

---

## 도메인 서비스

### LeavePolicyService
직급별 연차 정책을 관리하고 휴가 신청 가능 여부를 검증하는 도메인 서비스.

**역할:**
- 직급별 기본 연차 일수 조회 (REGULAR=15, IRREGULAR=11, PART_TIME=0)
- 근로자 등록 시 초기 연차 설정
- 휴가 신청 가능 여부 검증 (파트타임은 항상 가능, 정규/비정규는 잔여 연차 확인)

**의존 모델:** EmployeeType, RemainingLeave

---

### PayrollCalculationEngine
출퇴근 기록과 정책을 기반으로 급여를 계산하는 도메인 서비스.

**역할:**
- 출퇴근 기록 기반 일별 급여 계산
- 근무 유형 판단 (우선순위: 공휴일 > 주말 > 야간 > 평일)
- 야간 근무 판단 (22:00~06:00)
- 정책 기반 가산율 적용
- 기본급/초과근무수당 분리 계산
- 승인된 휴가 날짜 제외

**의존 모델:** AttendanceRecord, LeaveRequest, PayrollPolicy, PayrollDetail, WorkType, PolicyType

**내부 DTO:**
- `PayrollCalculationResult`: baseAmount, overtimeAmount, totalAmount, details
- `PayrollDetailData`: workDate, workType, hours, hourlyRate, multiplier, amount

---

## 외부 계약

- MySQL 8.x (데이터베이스)
- JWT (인증 토큰)

---

## 소유 데이터

- users: 사용자 인증/인가 정보
- employees: 근로자 정보
- stores: 매장 정보
- attendance_records: 출퇴근 기록
- work_schedules: 근무 일정
- leave_requests: 휴가 신청
- payrolls: 급여 정보
- payroll_details: 급여 상세 내역
- payroll_policies: 급여 정책
- payroll_batch_histories: 급여 배치 이력
- audit_logs: 감사 로그

---

## 도메인 예외 체계

### 기본 구조
- `DomainException` (abstract class): code, message, cause
- 모든 도메인 예외는 DomainException을 상속
- 에러 코드는 `ErrorCode` object에서 중앙 관리

### 에러 코드 목록

| 코드 | 예외 클래스 | 설명 |
|------|-------------|------|
| AUTH001 | AuthenticationFailedException | 인증 실패 |
| AUTH002 | InactiveUserException | 비활성화된 사용자 |
| TOKEN001 | - | 유효하지 않은 토큰 |
| TOKEN002 | - | 사용자 없음 |
| TOKEN003 | - | 토큰 사용자 비활성 |
| REG001 | DuplicateEmailException | 이메일 중복 |
| REG002 | InvalidRoleException | 유효하지 않은 역할 |
| STORE001 | StoreNotFoundException | 매장 없음 |
| STORE002 | DuplicateStoreNameException | 매장명 중복 |
| EMP001 | EmployeeNotFoundException | 근로자 없음 |
| EMP002 | DuplicateEmployeeUserException | 근로자-사용자 중복 |
| EMP003 | UnauthorizedStoreAccessException | 매장 접근 권한 없음 |
| EMP004 | NoEmployeesFoundException | 근로자 목록 없음 |
| ATT001 | AttendanceNotFoundException | 출퇴근 기록 없음 |
| ATT002 | AlreadyCheckedInException | 중복 출근 |
| ATT003 | NotCheckedInException | 출근 기록 없음 |
| ATT004 | AlreadyCheckedOutException | 중복 퇴근 |
| SCH001 | ScheduleNotFoundException | 일정 없음 |
| SCH002 | DuplicateScheduleException | 일정 중복 |
| SCH003 | ConfirmedScheduleCannotBeModifiedException | 확정 일정 수정 불가 |
| SCH004 | EmployeeNotBelongToStoreException | 근로자 매장 불일치 |
| SCH005 | ManagerCanOnlyManageOwnStoreException | 매니저 매장 제한 |
| LEAVE001 | LeaveRequestNotFoundException | 휴가 신청 없음 |
| LEAVE002 | InsufficientLeaveBalanceException | 연차 부족 |
| LEAVE003 | LeaveRequestDateOverlapException | 휴가 기간 중복 |
| LEAVE004 | LeaveRequestCannotBeCancelledException | 취소 불가 상태 |
| LEAVE005 | LeaveRequestCannotBeProcessedException | 승인/반려 불가 상태 |
| LEAVE006 | PastDateLeaveRequestException | 과거 날짜 신청 |
| LEAVE007 | InvalidLeaveDateRangeException | 유효하지 않은 날짜 범위 |
| PAYROLL001 | PayrollNotFoundException | 급여 없음 |
| PAYROLL002 | PayrollAlreadyCalculatedException | 급여 이미 계산됨 |
| PAYROLL003 | NoAttendanceRecordsFoundException | 출퇴근 기록 없음 |
| PAYROLL_POLICY001 | PayrollPolicyNotFoundException | 정책 없음 |
| PAYROLL_POLICY002 | PayrollPolicyPeriodOverlapException | 정책 기간 중복 |
| PAYROLL_POLICY003 | InvalidPolicyPeriodException | 유효하지 않은 정책 기간 |
| PAYROLL_POLICY004 | InactivePolicyCannotBeModifiedException | 비활성 정책 수정 불가 |
