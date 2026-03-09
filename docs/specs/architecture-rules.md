# LMS Backend - 아키텍처 규칙

## 기본 정보
- type: architecture_rules
- service: lms-backend
- architecture: DDD + Clean Architecture
- build: Gradle 멀티모듈 (Kotlin DSL)

## 레이어 정의와 책임

### 모듈 구조

```
lms-demo/
├── domain/           # 순수 비즈니스 로직
├── application/      # 유스케이스 오케스트레이션
├── infrastructure/   # 기술 구현체
└── interfaces/       # 외부 인터페이스 (REST API, 진입점)
```

### domain 모듈

**책임:** Aggregate Root, Entity, Value Object, Domain Service, Repository Interface, Domain Event, Domain Exception 정의

**허용:**
- 순수 Kotlin 코드 (kotlin-stdlib, kotlin-reflect만 의존)
- data class를 사용한 불변 Aggregate Root
- private constructor + companion object의 `create()` / `reconstruct()` 팩토리 패턴
- DomainContext를 통한 요청 컨텍스트 전달
- `@JvmInline value class`를 사용한 식별자/값 래핑

**금지:**
- Spring Framework 의존 (`@Service`, `@Component`, `@Transactional` 등)
- JPA 어노테이션 (`@Entity`, `@Table`, `@Column` 등)
- 외부 라이브러리 의존 (Jackson, JJWT 등)
- infrastructure/interfaces 모듈 참조

**패키지 구조:**
```
com.lms.domain/
├── common/           # DomainContext 등 공통 객체
├── exception/        # 도메인 예외 (DomainException 상속)
├── model/
│   ├── user/         # User AR + UserId, Email, Password, Role
│   ├── employee/     # Employee AR + EmployeeId, EmployeeName, EmployeeType, RemainingLeave
│   ├── store/        # Store AR + StoreId, StoreName, StoreLocation
│   ├── attendance/   # AttendanceRecord AR + AttendanceRecordId, AttendanceTime, AttendanceStatus
│   ├── schedule/     # WorkSchedule AR + WorkScheduleId, WorkDate, WorkTime
│   ├── leave/        # LeaveRequest AR + LeaveRequestId, LeaveType, LeaveStatus, LeavePeriod
│   ├── payroll/      # Payroll AR, PayrollPolicy AR + 관련 VO/Enum
│   ├── auditlog/     # AuditLog AR + AuditLogId, EntityType, ActionType
│   └── auth/         # TokenProvider 인터페이스
└── service/          # Domain Service (LeavePolicyService, PayrollCalculationEngine)
```

### application 모듈

**책임:** 유스케이스 실행, 트랜잭션 경계 관리, 도메인 객체 오케스트레이션

**허용:**
- domain 모듈 의존
- Spring Context (`@Service`, `@Transactional`)
- Spring Validation (`spring-boot-starter-validation`)
- Spring Security Crypto (`spring-security-crypto`) - 비밀번호 인코딩
- Command/Result DTO 정의

**금지:**
- infrastructure/interfaces 모듈 참조
- JPA 어노테이션 직접 사용
- HTTP 요청/응답 객체 참조
- 외부 API 클라이언트 직접 호출

**패턴:** 하나의 AppService 클래스는 하나의 public `execute()` 메서드만 보유 (단일 유스케이스 원칙)

```kotlin
@Service
@Transactional
class CreateEmployeeAppService(
    private val employeeRepository: EmployeeRepository,
    private val userRepository: UserRepository
) {
    fun execute(command: CreateEmployeeCommand): CreateEmployeeResult {
        // 1. Repository에서 조회
        // 2. Domain 로직 실행
        // 3. Repository에 저장
        // 4. Result 반환
    }
}
```

**패키지 구조:**
```
com.lms.application/
├── auth/       # LoginAppService, RegisterAppService, RefreshTokenAppService
├── employee/   # CreateEmployeeAppService, GetEmployeeAppService, ...
├── store/      # CreateStoreAppService, GetStoreAppService, ...
├── attendance/ # CheckInAppService, CheckOutAppService, ...
├── schedule/   # CreateWorkScheduleAppService, ...
├── leave/      # CreateLeaveRequestAppService, ApproveLeaveRequestAppService, ...
└── payroll/    # CalculatePayrollAppService, ExecutePayrollBatchAppService, ...
```

### infrastructure 모듈

**책임:** domain에서 정의한 인터페이스의 기술 구현, JPA Entity/Repository, Security 설정, JWT 토큰 처리, 외부 시스템 연동

**허용:**
- domain 모듈 의존
- Spring Boot Starter (Web, Data JPA, Security)
- JPA 어노테이션, Hibernate
- JJWT 라이브러리
- MySQL Connector
- Springdoc OpenAPI
- 테스트: Spring Boot Test, MockK, Kotest Extensions

**금지:**
- application 모듈 참조
- interfaces 모듈 참조
- 비즈니스 로직 포함 (데이터 변환/매핑만 허용)

**패키지 구조:**
```
com.lms.infrastructure/
├── persistence/    # JPA Entity, Spring Data Repository, Repository 구현체
├── security/       # JWT 토큰 제공자, Security Filter, SecurityUtils
└── config/         # 기술 설정 (DB, Jackson, CORS 등)
```

**JPA Entity 매핑 규칙:**
- JPA Entity 클래스명: `Jpa{AggregateRoot}` (예: `JpaUser`, `JpaEmployee`)
- Repository 구현체: `{AggregateRoot}RepositoryImpl` (domain의 Repository 인터페이스 구현)
- Spring Data 인터페이스: `SpringData{AggregateRoot}Repository`
- Domain 모델 <-> JPA Entity 변환은 Repository 구현체 내부에서 수행

### interfaces 모듈

**책임:** REST 컨트롤러, Request/Response DTO, Spring Boot 진입점

**허용:**
- domain, application, infrastructure 모듈 의존
- Spring Web (`@RestController`, `@RequestMapping`)
- Spring Security (`@PreAuthorize`)
- Spring Validation (`@Valid`, `@NotBlank`)
- Jackson (JSON 직렬화/역직렬화)
- Springdoc OpenAPI
- Request DTO -> Command 변환
- Result -> Response DTO 변환

**금지:**
- 비즈니스 로직 포함
- Repository 직접 호출
- Domain 모델을 HTTP 응답으로 직접 반환

**패키지 구조:**
```
com.lms.interfaces/
├── web/
│   ├── controller/   # REST Controller
│   └── dto/          # Request/Response DTO
└── LmsApplication.kt  # @SpringBootApplication 진입점
```

**Controller 패턴:**
```kotlin
@RestController
@RequestMapping("/api/employees")
class EmployeeController(
    private val createEmployeeAppService: CreateEmployeeAppService,
    private val getEmployeeAppService: GetEmployeeAppService
) {
    @PostMapping
    @PreAuthorize("hasAnyRole('SUPER_ADMIN', 'MANAGER')")
    fun create(@Valid @RequestBody request: CreateEmployeeRequest): ResponseEntity<EmployeeResponse> {
        val command = request.toCommand()
        val result = createEmployeeAppService.execute(command)
        return ResponseEntity.status(HttpStatus.CREATED).body(EmployeeResponse.from(result))
    }
}
```

## 의존성 방향

### 모듈 간 의존 규칙 (바깥에서 안으로만 의존)

```
interfaces → application → domain ← infrastructure
                             ↑
                    infrastructure (구현 제공)
```

| 모듈 | 의존 가능 | 의존 불가 |
|------|----------|----------|
| domain | 없음 (순수 Kotlin) | application, infrastructure, interfaces |
| application | domain | infrastructure, interfaces |
| infrastructure | domain | application, interfaces |
| interfaces | domain, application, infrastructure | - |

### Gradle 의존성

```kotlin
// domain/build.gradle.kts
dependencies {
    // 순수 Kotlin만 (kotlin-stdlib, kotlin-reflect는 root에서 상속)
}

// application/build.gradle.kts
dependencies {
    implementation(project(":domain"))
    implementation("org.springframework:spring-context")
    implementation("org.springframework:spring-tx")
}

// infrastructure/build.gradle.kts
dependencies {
    implementation(project(":domain"))
    implementation(libs.spring.boot.starter.data.jpa)
    implementation(libs.spring.boot.starter.security)
    // ...
}

// interfaces/build.gradle.kts
dependencies {
    implementation(project(":domain"))
    implementation(project(":application"))
    implementation(project(":infrastructure"))
    implementation(libs.spring.boot.starter.web)
    // ...
}
```

### 의존성 역전 패턴

domain에서 인터페이스를 정의하고, infrastructure에서 구현한다:

```
domain:  interface UserRepository { fun findByEmail(email: Email): User? }
           ↑ (의존)
infrastructure:  class UserRepositoryImpl(
                     private val springDataRepo: SpringDataUserRepository
                 ) : UserRepository { ... }
```

## 도메인 모델 설계 규칙

### Aggregate Root 생성 패턴
- `private constructor` + `companion object` 팩토리
- `create()`: 새 인스턴스 생성 (비즈니스 검증 포함)
- `reconstruct()`: 기존 데이터 복원 (Repository에서 사용, 검증 최소화)
- 모든 명령 메서드는 `DomainContext`를 첫 번째 파라미터로 수신
- 상태 변경은 `copy()`를 통한 불변 객체 반환

### Value Object 규칙
- `data class` 또는 `@JvmInline value class` 사용
- `init {}` 블록에서 유효성 검증 수행
- 불변 (모든 필드 `val`)
- ID 타입: `@JvmInline value class {Name}Id(val value: String)`에 `generate()` companion 메서드

### Enum 규칙
- 한국어 `description` 프로퍼티 필수
- 도메인 행위가 있는 경우 메서드 추가 (예: `LeaveType.requiresApproval`)

### Repository Interface 규칙
- domain 모듈에 인터페이스 정의
- Aggregate Root 단위로 1개의 Repository
- 반환 타입은 domain 모델 (JPA Entity 노출 금지)

## 테스트 전략

### 테스트 프레임워크
- JUnit 5 Platform
- Kotest (StringSpec, BehaviorSpec)
- MockK (모킹)
- Kotest Extensions Spring (통합 테스트)
- H2 Database (인터페이스 모듈 테스트)
- Testcontainers (인프라 통합 테스트, MySQL)

### 테스트 레벨

| 레벨 | 대상 모듈 | Spring 컨텍스트 | DB |
|------|----------|----------------|-----|
| Unit | domain | 불필요 | 불필요 |
| Unit | application | MockK로 Repository Mock | 불필요 |
| Integration | infrastructure | `@DataJpaTest` | H2 또는 Testcontainers |
| Integration | interfaces | `@SpringBootTest` | H2 |
| E2E | 전체 | `@SpringBootTest(webEnvironment = RANDOM_PORT)` | Testcontainers MySQL |

### 테스트 명명
- Kotest StringSpec: 한글 테스트 이름 사용
- `@Tag("TC-{도메인}-{번호}")` 형식으로 TC-ID 마킹

## 코드 품질 규칙

### Spotless + ktlint
- max_line_length: 120
- wildcard imports 허용 (`ktlint_standard_no-wildcard-imports: disabled`)
- trailing comma 비활성화
- filename 규칙 비활성화

### 빌드 설정
- JVM Target: 17
- `-Xjsr305=strict`: JSR-305 null-safety 어노테이션 strict 모드

## 횡단 관심사

### 인증/인가
- Spring Security 6.x + JWT
- `@PreAuthorize` 어노테이션으로 Controller 메서드 단위 역할 제어
- `SecurityUtils` 유틸리티로 프로그래밍 방식 권한 검증 (`isSuperAdmin()`, `isManager()`, `belongsToStore()`, `isCurrentUser()`)
- MANAGER는 소속 매장 데이터만 접근 (`SecurityUtils.belongsToStore(storeId)`)
- EMPLOYEE는 본인 데이터만 접근 (`SecurityUtils.isCurrentUser(employeeId)`)

### 감사 로그
- AuditLog Aggregate로 데이터 변경 이력 기록
- DomainContext에서 수행자 정보 및 클라이언트 IP 추출
- 변경 전/후 값을 JSON 형식으로 저장

### 에러 처리
- `DomainException` 기반 도메인 예외 계층
- 도메인별 전용 Exception 클래스 (AttendanceException, LeaveException 등)
- `ErrorCode` Enum으로 에러 코드 체계 관리
- `@RestControllerAdvice`에서 예외 -> HTTP 응답 변환

### 트랜잭션
- Application Service에서 `@Transactional`로 트랜잭션 경계 설정
- 읽기 전용 조회: `@Transactional(readOnly = true)`
- Domain 모듈에는 트랜잭션 어노테이션 금지
