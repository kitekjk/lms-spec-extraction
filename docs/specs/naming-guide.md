# 네이밍 가이드

## 기본 정보
- type: naming_guide

## 패키지
- `com.lms.domain.model.{도메인명}` - Aggregate Root, Entity, Value Object, Repository 인터페이스
- `com.lms.domain.service` - Domain Service (여러 Aggregate 걸치는 로직)
- `com.lms.domain.exception` - Domain Exception
- `com.lms.domain.common` - DomainContext 등 공통
- `com.lms.application.{도메인명}` - Application Service
- `com.lms.application.{도메인명}.dto` - Command, Result DTO
- `com.lms.infrastructure.persistence.{도메인명}` - JPA Entity, Repository 구현체
- `com.lms.infrastructure.persistence.{도메인명}.mapper` - Entity ↔ Domain Mapper
- `com.lms.infrastructure.persistence.{도메인명}.converter` - JPA AttributeConverter
- `com.lms.infrastructure.security` - 인증/인가
- `com.lms.infrastructure.security.jwt` - JWT 관련
- `com.lms.infrastructure.config` - 설정 클래스
- `com.lms.infrastructure.context` - DomainContext 구현
- `com.lms.interfaces.web.controller` - REST Controller
- `com.lms.interfaces.web.dto` - Request/Response DTO
- `com.lms.interfaces.web.exception` - GlobalExceptionHandler

## 클래스
- Aggregate Root: `{도메인명}` (예: User, Employee, Store)
- Value Object: `@JvmInline value class {의미명}` (예: UserId, Email, StoreName)
- Value Object (복합): `data class {의미명}` (예: AttendanceTime, WorkTime, LeavePeriod)
- JPA Entity: `{도메인명}Entity` (예: UserEntity, EmployeeEntity)
- Mapper: `{도메인명}Mapper` (예: UserMapper, EmployeeMapper)
- Repository 인터페이스: `{도메인명}Repository` (domain 모듈)
- Repository 구현체: `{도메인명}RepositoryImpl` (infrastructure 모듈)
- Spring Data JPA: `{도메인명}JpaRepository` 또는 `Jpa{도메인명}Repository`
- Application Service: `{행위}{도메인명}AppService` (예: CreateEmployeeAppService)
- Controller: `{도메인명}Controller` (예: EmployeeController)
- Request DTO: `{도메인명}{행위}Request` (예: StoreCreateRequest)
- Response DTO: `{도메인명}Response`, `{도메인명}ListResponse`
- Command: `{행위}{도메인명}Command` (예: CreateStoreCommand)
- Result: `{도메인명}Result` (예: StoreResult)
- Domain Exception: `{도메인명}Exception.kt` 내부에 구체 클래스 정의
- AttributeConverter: `{Enum명}Converter` (예: RoleConverter, LeaveStatusConverter)
- EntityListener: `{도메인명}EntityListener` (예: AttendanceRecordEntityListener)

## API 경로
- `/api/auth` - 인증 (로그인, 회원가입, 토큰 갱신)
- `/api/employees` - 근로자
- `/api/stores` - 매장
- `/api/schedules` - 근무 일정
- `/api/attendance` - 출퇴근
- `/api/leaves` - 휴가
- `/api/payroll` - 급여
- `/api/payroll-policies` - 급여 정책

## 테스트 클래스
- Unit: `{클래스명}Test`
- Integration: `{Controller명}Test` (예: AttendanceControllerTest)
- @Tag("TC-{도메인약어}-{UseCase번호}-{시나리오번호}")로 Spec 테스트 시나리오와 매핑
- 도메인 약어: USER, EMP, STORE, SCH, ATT, LEAVE, PAY

## 이벤트 토픽 (향후)
- `lms.{도메인}.{aggregate}.{event}`

## 기타
- 변수/함수: camelCase
- 상수: UPPER_SNAKE_CASE (예: LATE_TOLERANCE_MINUTES)
- DB 테이블/컬럼: snake_case
- Enum: sealed class 또는 enum class, 코드에서 AttributeConverter로 변환
- Kotlin 관용적 스타일: val 우선, null-safety, data class, sealed class
