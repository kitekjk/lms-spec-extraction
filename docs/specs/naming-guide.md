# LMS Backend - 네이밍 가이드

## 기본 정보
- type: naming_guide
- service: lms-backend
- language: Kotlin 2.1.x

## 패키지

### 루트 패키지
```
com.lms.domain          # domain 모듈
com.lms.application     # application 모듈
com.lms.infrastructure  # infrastructure 모듈
com.lms.interfaces      # interfaces 모듈
```

### domain 모듈 패키지

| 패키지 경로 | 용도 |
|------------|------|
| `com.lms.domain.common` | 공통 도메인 객체 (DomainContext) |
| `com.lms.domain.exception` | 도메인 예외 클래스 |
| `com.lms.domain.model.{도메인}` | Aggregate Root, Entity, Value Object, Repository Interface, Enum |
| `com.lms.domain.service` | Domain Service (교차 Aggregate 로직) |

도메인별 패키지명:

| 도메인 | 패키지명 |
|--------|---------|
| 사용자 | `model.user` |
| 근로자 | `model.employee` |
| 매장 | `model.store` |
| 출퇴근 | `model.attendance` |
| 근무일정 | `model.schedule` |
| 휴가 | `model.leave` |
| 급여 | `model.payroll` |
| 감사로그 | `model.auditlog` |
| 인증 | `model.auth` |

### application 모듈 패키지

| 패키지 경로 | 용도 |
|------------|------|
| `com.lms.application.{도메인}` | 해당 도메인의 AppService, Command, Result 클래스 |

도메인별 패키지명:

| 도메인 | 패키지명 |
|--------|---------|
| 인증 | `auth` |
| 근로자 | `employee` |
| 매장 | `store` |
| 출퇴근 | `attendance` |
| 근무일정 | `schedule` |
| 휴가 | `leave` |
| 급여/급여정책 | `payroll` |

### infrastructure 모듈 패키지

| 패키지 경로 | 용도 |
|------------|------|
| `com.lms.infrastructure.persistence` | JPA Entity, Spring Data Repository, Repository 구현체 |
| `com.lms.infrastructure.security` | JWT, Security Filter, SecurityUtils |
| `com.lms.infrastructure.config` | 기술 설정 (DB, CORS, Jackson, Properties) |

### interfaces 모듈 패키지

| 패키지 경로 | 용도 |
|------------|------|
| `com.lms.interfaces.web.controller` | REST Controller |
| `com.lms.interfaces.web.dto` | Request/Response DTO |
| `com.lms.interfaces` | Spring Boot 진입점 (`LmsApplication.kt`) |

## 클래스

### Aggregate Root / Entity

| 분류 | 패턴 | 예시 |
|------|------|------|
| Aggregate Root | `{도메인명}` (단수형) | `User`, `Employee`, `Store`, `AttendanceRecord`, `WorkSchedule`, `LeaveRequest`, `Payroll`, `PayrollPolicy`, `AuditLog` |

### Value Object

| 분류 | 패턴 | 예시 |
|------|------|------|
| 식별자 | `{AggregateRoot}Id` | `UserId`, `EmployeeId`, `StoreId`, `AttendanceRecordId`, `WorkScheduleId`, `LeaveRequestId`, `PayrollId`, `PayrollPolicyId`, `AuditLogId`, `PayrollDetailId` |
| 도메인 값 | `{의미있는이름}` | `Email`, `Password`, `EmployeeName`, `RemainingLeave`, `StoreName`, `StoreLocation`, `AttendanceTime`, `WorkDate`, `WorkTime`, `LeavePeriod`, `PayrollAmount`, `PayrollPeriod`, `PolicyMultiplier`, `PolicyEffectivePeriod` |

### Enum

| 분류 | 패턴 | 예시 |
|------|------|------|
| 역할 | `Role` | SUPER_ADMIN, MANAGER, EMPLOYEE |
| 유형 | `{도메인}Type` | `EmployeeType`, `LeaveType`, `PolicyType`, `WorkType` |
| 상태 | `{도메인}Status` | `AttendanceStatus`, `LeaveStatus` |
| 감사 | `ActionType`, `EntityType` | CREATE, UPDATE, DELETE / USER, EMPLOYEE, STORE |

### Domain Exception

| 분류 | 패턴 | 예시 |
|------|------|------|
| 기반 클래스 | `DomainException` | - |
| 도메인별 | `{도메인명}Exception` | `AttendanceException`, `AuthException`, `EmployeeException`, `LeaveException`, `PayrollException`, `PayrollPolicyException`, `RegistrationException`, `StoreException`, `WorkScheduleException` |
| 에러 코드 | `ErrorCode` (Enum) | - |

### Domain Service

| 분류 | 패턴 | 예시 |
|------|------|------|
| Domain Service | `{비즈니스행위}Service` | `LeavePolicyService`, `PayrollCalculationEngine` |

### Repository Interface (domain)

| 분류 | 패턴 | 예시 |
|------|------|------|
| Repository | `{AggregateRoot}Repository` | `UserRepository`, `EmployeeRepository`, `StoreRepository`, `AttendanceRecordRepository`, `WorkScheduleRepository`, `LeaveRequestRepository`, `PayrollRepository`, `PayrollPolicyRepository`, `PayrollDetailRepository`, `PayrollBatchHistoryRepository`, `AuditLogRepository` |

### Application Service

| 분류 | 패턴 | 예시 |
|------|------|------|
| AppService | `{동사}{대상}AppService` | `CreateEmployeeAppService`, `GetEmployeeAppService`, `UpdateEmployeeAppService`, `DeactivateEmployeeAppService`, `CheckInAppService`, `CheckOutAppService`, `ApproveLeaveRequestAppService`, `CalculatePayrollAppService`, `ExecutePayrollBatchAppService`, `LoginAppService`, `RegisterAppService` |
| Command | `{동사}{대상}Command` | `CreateEmployeeCommand`, `CheckInCommand`, `ApproveLeaveRequestCommand` |
| Result | `{동사}{대상}Result` 또는 `{대상}Result` | `CreateEmployeeResult`, `LoginResult` |

### Infrastructure 클래스

| 분류 | 패턴 | 예시 |
|------|------|------|
| JPA Entity | `Jpa{AggregateRoot}` | `JpaUser`, `JpaEmployee`, `JpaStore` |
| Spring Data Repository | `SpringData{AggregateRoot}Repository` | `SpringDataUserRepository`, `SpringDataEmployeeRepository` |
| Repository 구현체 | `{AggregateRoot}RepositoryImpl` | `UserRepositoryImpl`, `EmployeeRepositoryImpl` |
| Security | 기능 기반 이름 | `JwtTokenProvider`, `JwtAuthenticationFilter`, `SecurityUtils`, `SecurityConfig` |
| Config | `{기능}Config` 또는 `{기능}Properties` | `JwtProperties`, `WebConfig`, `CorsConfig` |

### Interfaces 클래스

| 분류 | 패턴 | 예시 |
|------|------|------|
| Controller | `{도메인}Controller` | `AuthController`, `EmployeeController`, `StoreController`, `AttendanceController`, `WorkScheduleController`, `LeaveRequestController`, `PayrollController`, `PayrollPolicyController`, `HealthController` |
| Request DTO | `{동사}{대상}Request` | `CreateEmployeeRequest`, `LoginRequest`, `CheckInRequest` |
| Response DTO | `{대상}Response` | `EmployeeResponse`, `LoginResponse`, `AttendanceRecordResponse` |

## API 경로

### 기본 규칙
- 모든 API 경로는 `/api` 프리픽스로 시작
- 리소스명은 소문자 복수형 (kebab-case)
- 행위가 포함된 경로는 동사를 하위 경로로 사용

### 경로 패턴

| 패턴 | 의미 | 예시 |
|------|------|------|
| `GET /api/{resources}` | 목록 조회 | `GET /api/employees` |
| `GET /api/{resources}/{id}` | 단건 조회 | `GET /api/employees/{id}` |
| `POST /api/{resources}` | 생성 | `POST /api/employees` |
| `PUT /api/{resources}/{id}` | 수정 | `PUT /api/employees/{id}` |
| `DELETE /api/{resources}/{id}` | 삭제/비활성화 | `DELETE /api/employees/{id}` |
| `PUT /api/{resources}/{id}/{action}` | 상태 변경 | `PUT /api/leave-requests/{id}/approve` |
| `POST /api/{resources}/{action}` | 특수 행위 | `POST /api/attendance/check-in` |

### 리소스별 경로

| 리소스 | Base Path | 비고 |
|--------|-----------|------|
| 인증 | `/api/auth` | login, register, refresh |
| 매장 | `/api/stores` | CRUD |
| 근로자 | `/api/employees` | CRUD + 비활성화 |
| 근무일정 | `/api/schedules` | CRUD |
| 출퇴근 | `/api/attendance` | check-in, check-out, adjust |
| 휴가 | `/api/leave-requests` | CRUD + approve, reject, cancel |
| 급여 | `/api/payrolls` | 조회 + calculate, batch |
| 급여정책 | `/api/payroll-policies` | CRUD |
| 헬스체크 | `/api/health` | 서버 상태 확인 |

### 쿼리 파라미터 네이밍

| 용도 | 파라미터 | 예시 |
|------|---------|------|
| 매장 필터 | `storeId` | `GET /api/employees?storeId={id}` |
| 근로자 필터 | `employeeId` | `GET /api/schedules?employeeId={id}` |
| 날짜 필터 | `date`, `startDate`, `endDate` | `GET /api/schedules?startDate=2026-03-01&endDate=2026-03-31` |
| 기간 필터 | `period` | `GET /api/payrolls?period=2026-03` |
| 상태 필터 | `status` | `GET /api/leave-requests?status=PENDING` |
| 페이징 | `page`, `size` | `GET /api/employees?page=0&size=20` |
| 정렬 | `sort` | `GET /api/employees?sort=createdAt,desc` |

### JSON 필드 네이밍
- camelCase 사용 (Jackson 기본 설정)
- 날짜/시간: ISO 8601 형식 (`2026-03-09T09:00:00Z`)
- 금액: 문자열이 아닌 숫자 타입 (`"amount": 1500000.00`)
- Boolean: `is` 프리픽스 (`"isActive": true`, `"isPaid": false`)
- Enum: UPPER_SNAKE_CASE 문자열 (`"status": "PENDING"`, `"role": "SUPER_ADMIN"`)

### HTTP 헤더
- 인증: `Authorization: Bearer {accessToken}`
- Content-Type: `Content-Type: application/json`
- Accept: `Accept: application/json`
