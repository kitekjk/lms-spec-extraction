# LMS Backend - 네이밍 가이드

## 기본 정보
- type: naming_guide
- language: Kotlin
- style: Kotlin idiomatic (camelCase, PascalCase)

---

## 패키지 네이밍

| 레이어 | 패키지 패턴 | 예시 |
|--------|-------------|------|
| domain/model | `com.lms.domain.model.{aggregate}` | `com.lms.domain.model.user`, `com.lms.domain.model.payroll` |
| domain/service | `com.lms.domain.service` | `com.lms.domain.service` |
| domain/exception | `com.lms.domain.exception` | `com.lms.domain.exception` |
| domain/common | `com.lms.domain.common` | `com.lms.domain.common` |
| application | `com.lms.application.{context}` | `com.lms.application.user` |
| infrastructure/persistence | `com.lms.infrastructure.persistence.{aggregate}` | `com.lms.infrastructure.persistence.user` |
| infrastructure/security | `com.lms.infrastructure.security` | `com.lms.infrastructure.security` |
| infrastructure/config | `com.lms.infrastructure.config` | `com.lms.infrastructure.config` |
| interfaces/web | `com.lms.interfaces.web.controller` | `com.lms.interfaces.web.controller` |
| interfaces/dto | `com.lms.interfaces.web.dto` | `com.lms.interfaces.web.dto` |

**규칙:**
- 패키지명은 소문자, 단수형 사용
- Aggregate 이름을 서브패키지 구분자로 사용: `user`, `employee`, `store`, `attendance`, `schedule`, `leave`, `payroll`, `auditlog`, `auth`

---

## 클래스 네이밍

### Aggregate Root / Entity
- PascalCase, 도메인 개념 명사
- `data class` + `private constructor`

| 패턴 | 예시 |
|------|------|
| `{DomainConcept}` | `User`, `Employee`, `Store`, `AttendanceRecord`, `WorkSchedule`, `LeaveRequest`, `Payroll`, `PayrollPolicy`, `PayrollBatchHistory`, `AuditLog`, `PayrollDetail` |

### Value Object (ID)
- `{AggregateRoot}Id` 패턴
- `@JvmInline value class`

| 패턴 | 예시 |
|------|------|
| `{AggregateRoot}Id` | `UserId`, `EmployeeId`, `StoreId`, `AttendanceRecordId`, `WorkScheduleId`, `LeaveRequestId`, `PayrollId`, `PayrollPolicyId`, `PayrollDetailId`, `PayrollBatchHistoryId`, `AuditLogId` |

### Value Object (일반)
- 도메인 의미를 반영하는 명사
- `@JvmInline value class` 또는 `data class`

| 패턴 | 예시 | 구현 |
|------|------|------|
| 단일 값 래핑 | `Email`, `Password`, `EmployeeName`, `StoreName`, `StoreLocation`, `RemainingLeave`, `PayrollPeriod`, `PolicyMultiplier` | `@JvmInline value class` |
| 복합 값 | `AttendanceTime`, `WorkTime`, `LeavePeriod`, `PayrollAmount`, `PolicyEffectivePeriod` | `data class` |

### Enum / Sealed Class
- PascalCase, 도메인 개념 반영

| 패턴 | 예시 | 구현 |
|------|------|------|
| `{Domain}Type` | `EmployeeType`, `LeaveType`, `PolicyType`, `WorkType` | `enum class` |
| `{Domain}Status` | `AttendanceStatus`, `LeaveStatus`, `BatchStatus` | `enum class` |
| `{Domain}` | `Role` | `enum class` |
| 다형성 필요 시 | `ActionType`, `EntityType` | `sealed class` |

### Repository 인터페이스
- `{AggregateRoot}Repository` 패턴
- domain 모듈에 `interface`로 정의

| 패턴 | 예시 |
|------|------|
| `{AggregateRoot}Repository` | `UserRepository`, `EmployeeRepository`, `StoreRepository`, `AttendanceRecordRepository`, `WorkScheduleRepository`, `LeaveRequestRepository`, `PayrollRepository`, `PayrollPolicyRepository`, `PayrollDetailRepository`, `PayrollBatchHistoryRepository`, `AuditLogRepository` |

### Repository 구현체
- `{AggregateRoot}RepositoryImpl` 패턴
- infrastructure 모듈에 위치

| 패턴 | 예시 |
|------|------|
| `{AggregateRoot}RepositoryImpl` | `UserRepositoryImpl`, `EmployeeRepositoryImpl` |

### Domain Service
- `{Domain}PolicyService` 또는 `{Domain}Engine` 패턴
- domain/service에 위치

| 패턴 | 예시 |
|------|------|
| `{Domain}PolicyService` | `LeavePolicyService` |
| `{Domain}CalculationEngine` | `PayrollCalculationEngine` |

### Application Service
- `{UseCase}AppService` 패턴
- 하나의 public 메서드 보유

| 패턴 | 예시 |
|------|------|
| `{Action}{Domain}AppService` | `PlaceOrderAppService` (예시), `CreateEmployeeAppService` |

### REST Controller
- `{Domain}Controller` 패턴
- interfaces/web/controller에 위치

| 패턴 | 예시 |
|------|------|
| `{Domain}Controller` | `OrderController` (예시), `UserController` |

### DTO
- `{Action}{Domain}Request` / `{Action}{Domain}Response` 패턴
- interfaces/web/dto에 위치

| 패턴 | 예시 |
|------|------|
| `{UseCase}Request` | `PlaceOrderRequest` (예시) |
| `{UseCase}Response` | `OrderResponse` (예시) |

### Application Layer DTO
- `{UseCase}Command` / `{UseCase}Result` 패턴

| 패턴 | 예시 |
|------|------|
| `{UseCase}Command` | `PlaceOrderCommand` (예시) |
| `{UseCase}Result` | `OrderResult` (예시) |

### Exception
- `{상황}Exception` 패턴
- DomainException을 상속

| 패턴 | 예시 |
|------|------|
| `{Entity}NotFoundException` | `AttendanceNotFoundException`, `PayrollNotFoundException`, `LeaveRequestNotFoundException`, `PayrollPolicyNotFoundException` |
| `{상황}Exception` | `AlreadyCheckedInException`, `NotCheckedInException`, `InsufficientLeaveBalanceException`, `PayrollAlreadyCalculatedException` |
| `Duplicate{Field}Exception` | `DuplicateEmailException`, `DuplicateStoreNameException` |
| `Invalid{Concept}Exception` | `InvalidRoleException`, `InvalidLeaveDateRangeException`, `InvalidPolicyPeriodException` |

### Configuration
- `{Feature}Properties` / `{Feature}Config` 패턴

| 패턴 | 예시 |
|------|------|
| `{Feature}Properties` | `JwtProperties` |
| `{Feature}Config` | `JpaConfig` |

### Converter (JPA)
- `{Enum}Converter` 패턴
- `@Converter(autoApply = true)`

| 패턴 | 예시 |
|------|------|
| `{Enum}Converter` | `RoleConverter` |

---

## 파일 네이밍 컨벤션

### 파일명 = 클래스명
- 1파일 1클래스 원칙
- 파일명은 PascalCase

| 파일명 | 내용 |
|--------|------|
| `User.kt` | User Aggregate Root |
| `UserId.kt` | UserId Value Object |
| `UserRepository.kt` | UserRepository 인터페이스 |
| `LeavePolicyService.kt` | LeavePolicyService 도메인 서비스 |
| `ErrorCode.kt` | ErrorCode 상수 object |
| `DomainException.kt` | DomainException abstract class |
| `AttendanceException.kt` | 출퇴근 관련 예외 모음 (동일 도메인 예외 그룹핑 허용) |

### 예외: 관련 클래스 그룹핑
- 동일 도메인의 예외 클래스는 하나의 파일에 그룹핑 가능
- 예: `AttendanceException.kt`에 `AttendanceNotFoundException`, `AlreadyCheckedInException`, `NotCheckedInException`, `AlreadyCheckedOutException` 포함
- 예: `PayrollBatchHistory.kt`에 `PayrollBatchHistory`, `BatchStatus`, `PayrollBatchHistoryId` 포함

---

## ID 타입 컨벤션

- 모든 Aggregate Root의 식별자는 전용 Value Object 사용
- `@JvmInline value class`로 구현
- 내부 값 타입: `String` (UUID 문자열)
- 표준 팩토리 메서드:
  - `generate()`: UUID 기반 새 ID 생성
  - `from(value: String)`: 문자열에서 복원
- `init` 블록에서 `require(value.isNotBlank())` 검증 (일부 ID는 private constructor 사용)

```
패턴:
@JvmInline
value class {Name}Id(val value: String) {
    init {
        require(value.isNotBlank()) { "{Name}Id는 비어있을 수 없습니다." }
    }
    companion object {
        fun generate(): {Name}Id = {Name}Id(UUID.randomUUID().toString())
        fun from(value: String): {Name}Id = {Name}Id(value)
    }
}
```

---

## Value Object 컨벤션

### 단일 값 래핑 (Inline Value Class)
- `@JvmInline value class` 사용
- `init` 블록에서 유효성 검증
- 한국어 에러 메시지

```
패턴:
@JvmInline
value class {Name}(val value: {Type}) {
    init {
        require(검증조건) { "한국어 에러 메시지" }
    }
}
```

### 복합 값 (Data Class)
- `data class` 사용
- `init` 블록에서 필드 간 관계 검증
- 비즈니스 메서드 포함 가능

```
패턴:
data class {Name}(val field1: Type1, val field2: Type2) {
    init {
        require(field1과 field2의 관계 검증) { "한국어 에러 메시지" }
    }
    fun businessMethod(): ReturnType { ... }
}
```

### 팩토리 메서드 네이밍
| 메서드 | 용도 | 예시 |
|--------|------|------|
| `create(context, ...)` | Aggregate 신규 생성 | `User.create(context, email, password, role)` |
| `reconstruct(...)` | Repository 조회 결과 복원 | `User.reconstruct(id, email, ...)` |
| `generate()` | ID 자동 생성 | `UserId.generate()` |
| `from(value)` | 단일 값에서 생성 | `UserId.from("...")`, `PayrollPeriod.from(yearMonth)` |
| `of(...)` | 복수 인자에서 생성 | `PayrollPeriod.of(year, month)` |
| `standard()` | 기본값 생성 | `WorkTime.standard()`, `PolicyMultiplier.standard()` |
| `fromBase(value)` | 특정 필드만으로 생성 | `PayrollAmount.fromBase(baseAmount)` |
| `indefinite(startDate)` | 무기한 생성 | `PolicyEffectivePeriod.indefinite(startDate)` |
| `start(context, ...)` | 프로세스 시작 | `PayrollBatchHistory.start(context, period, ...)` |
| `checkIn(context, ...)` | 도메인 행위 기반 생성 | `AttendanceRecord.checkIn(context, ...)` |
| `system(serviceName)` | 시스템 내부용 생성 | `DomainContextBase.system("batch")` |

### 에러 메시지 컨벤션
- 한국어 사용
- 구체적인 값 포함: `"잔여 연차가 부족합니다. 현재: $value, 요청: $days"`
- `require()` 함수 사용 (Kotlin 표준)

---

## 메서드 네이밍 (도메인 행위)

| 패턴 | 용도 | 예시 도메인 |
|------|------|-------------|
| `create` | 신규 생성 (Companion) | 모든 Aggregate |
| `reconstruct` | 재구성 (Companion) | 모든 Aggregate |
| `login` | 로그인 처리 | User |
| `deactivate` / `activate` | 비활성화/활성화 | User, Employee |
| `changePassword` | 비밀번호 변경 | User |
| `deductLeave` / `restoreLeave` | 연차 차감/복구 | Employee |
| `assignStore` | 매장 배정 | Employee |
| `changeType` | 유형 변경 | Employee |
| `checkIn` / `checkOut` | 출퇴근 체크 | AttendanceRecord |
| `evaluateStatus` | 상태 평가 | AttendanceRecord |
| `markAsAbsent` | 결근 처리 | AttendanceRecord |
| `updateNote` | 메모 수정 | AttendanceRecord |
| `confirm` / `unconfirm` | 확정/확정취소 | WorkSchedule |
| `changeWorkTime` / `changeWorkDate` | 시간/날짜 변경 | WorkSchedule |
| `approve` / `reject` / `cancel` | 승인/거부/취소 | LeaveRequest |
| `markAsPaid` | 지급 완료 | Payroll |
| `addOvertime` / `addDeduction` | 초과근무수당/공제 추가 | Payroll |
| `recalculate` | 재계산 | Payroll, PayrollDetail |
| `terminate` | 종료 | PayrollPolicy |
| `updateMultiplier` | 배율 변경 | PayrollPolicy |
| `complete` / `fail` | 완료/실패 처리 | PayrollBatchHistory |
| `calculateWorkHours` | 근무 시간 계산 | WorkSchedule, AttendanceTime |
| `calculateLeaveDays` | 휴가 일수 계산 | LeaveRequest |
| `calculateTotal` | 총액 계산 | PayrollAmount |
| `isEffectiveOn` / `isCurrentlyEffective` | 유효 기간 확인 | PayrollPolicy, PolicyEffectivePeriod |
| `overlapsWith` | 기간 겹침 확인 | LeaveRequest, LeavePeriod |
| `contains` | 포함 여부 확인 | LeavePeriod, WorkTime |
| `deduct` / `add` | 값 차감/추가 | RemainingLeave |

---

## Enum 값 네이밍

- UPPER_SNAKE_CASE 사용
- `description` 필드로 한국어 설명 포함

| Enum | 값 패턴 |
|------|---------|
| Role | `SUPER_ADMIN`, `MANAGER`, `EMPLOYEE` |
| EmployeeType | `REGULAR`, `IRREGULAR`, `PART_TIME` |
| AttendanceStatus | `NORMAL`, `LATE`, `EARLY_LEAVE`, `ABSENT`, `PENDING` |
| LeaveType | `ANNUAL`, `SICK`, `PERSONAL`, `MATERNITY`, `PATERNITY`, `BEREAVEMENT`, `UNPAID` |
| LeaveStatus | `PENDING`, `APPROVED`, `REJECTED`, `CANCELLED` |
| PolicyType | `OVERTIME_WEEKDAY`, `OVERTIME_WEEKEND`, `OVERTIME_HOLIDAY`, `NIGHT_SHIFT`, `HOLIDAY_WORK`, `BONUS`, `ALLOWANCE` |
| WorkType | `WEEKDAY`, `NIGHT`, `WEEKEND`, `HOLIDAY` |
| BatchStatus | `RUNNING`, `COMPLETED`, `PARTIAL_SUCCESS`, `FAILED` |

---

## API 경로

| 규칙 | 설명 | 예시 |
|------|------|------|
| 기본 경로 | `/api/{resource}` | `/api/employees`, `/api/stores` |
| 케이스 | kebab-case | `/api/work-schedules`, `/api/leave-requests` |
| 복수형 | 리소스명은 복수 명사 | `/api/employees` (O), `/api/employee` (X) |
| 중첩 리소스 | `/api/{parent}/{parentId}/{child}` | `/api/stores/{storeId}/employees` |
| 행위 | 동사 대신 리소스 + HTTP Method | `POST /api/attendance-records` (출근 체크) |
| 인증 | `/api/auth/{action}` | `/api/auth/login`, `/api/auth/refresh` |

---

## 에러 코드 네이밍

- 접두사: 도메인 약어 (AUTH, REG, STORE, EMP, ATT, SCH, LEAVE, PAYROLL, PAYROLL_POLICY, TOKEN)
- 번호: 3자리 순번
- `ErrorCode` object에서 `const val`로 중앙 관리

```
패턴: {DOMAIN_PREFIX}{NNN}
예시: AUTH001, EMP003, LEAVE007, PAYROLL_POLICY002
```
