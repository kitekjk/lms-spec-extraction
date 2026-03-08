# LMS Backend - 아키텍처 규칙

## 기본 정보
- type: architecture_rules
- pattern: DDD (Domain-Driven Design) + Clean Architecture
- build: Gradle Kotlin DSL + Version Catalog
- rootProject: lms-demo
- group: com.example.lms

---

## 모듈 구조

```
lms-demo/
├── domain/              # 순수 비즈니스 로직 (외부 의존 없음)
│   └── src/main/kotlin/com/lms/domain/
│       ├── common/      # 공용 인터페이스 (DomainContext)
│       ├── model/       # Aggregate별 서브패키지
│       │   ├── user/
│       │   ├── employee/
│       │   ├── store/
│       │   ├── attendance/
│       │   ├── schedule/
│       │   ├── leave/
│       │   ├── payroll/
│       │   ├── auditlog/
│       │   └── auth/
│       ├── service/     # 도메인 서비스 (복수 Aggregate 로직)
│       └── exception/   # 도메인 예외
│
├── application/         # UseCase 및 오케스트레이션
│   └── src/main/kotlin/com/lms/application/
│       └── {context}/   # 도메인 컨텍스트별 AppService
│
├── infrastructure/      # 기술 구현체
│   └── src/main/kotlin/com/lms/infrastructure/
│       ├── persistence/ # JPA Repository 구현체
│       ├── security/    # JWT, 인증 필터
│       └── config/      # 기술 설정 (DB, Cache 등)
│
└── interfaces/          # 외부 인터페이스 (REST API)
    └── src/main/kotlin/com/lms/interfaces/
        ├── web/
        │   ├── controller/  # REST Controller
        │   └── dto/         # Request/Response DTO
        └── LmsApplication.kt  # Spring Boot Entry Point
```

---

## 의존성 방향

### 의존 방향 (실제 build.gradle.kts 기반)

```
interfaces → application, infrastructure, domain
infrastructure → domain
application → domain
domain → (없음, 순수 Kotlin)
```

| 모듈 | 의존하는 프로젝트 모듈 | 허용되는 외부 의존 |
|------|------------------------|--------------------|
| domain | 없음 | Kotlin stdlib, Kotlin reflect만 |
| application | `:domain` | Spring Context, Spring TX, Spring Security Crypto, Spring Validation |
| infrastructure | `:domain` | Spring Data JPA, Spring Web, Spring Security, JWT(jjwt), MySQL, Springdoc OpenAPI |
| interfaces | `:domain`, `:application`, `:infrastructure` | Spring Web, Spring Security, Spring Validation, JWT, Jackson, Springdoc OpenAPI, H2(test) |

### 금지 규칙
- domain -> Spring, JPA, 외부 프레임워크 의존 금지
- application -> infrastructure 의존 금지
- application -> application (AppService 간 상호 참조) 금지
- interfaces -> 비즈니스 로직 작성 금지

---

## 레이어 정의와 책임

### domain

**목적:** 순수 비즈니스 로직과 도메인 모델

**규칙:**
- 순수 Kotlin 코드만 사용 (Spring, JPA 등 외부 라이브러리 금지)
- Aggregate Root 내에 비즈니스 로직 캡슐화
- 여러 Aggregate에 걸친 로직은 도메인 서비스(`domain/service/`)에 위치
- Repository는 인터페이스만 정의 (구현은 infrastructure에서)
- 모든 비즈니스 메서드의 첫 번째 인자는 `DomainContext`
- Aggregate Root와 Entity는 `data class`로 선언, `private constructor` + `create()`/`reconstruct()` 팩토리 메서드 패턴
- 상태 변경은 `copy()`를 통한 불변 객체 반환
- 예외는 `DomainException`을 상속한 구체 클래스 사용 (DomainException 직접 사용 금지)

**Gradle 플러그인:** `kotlin.jvm`만 적용

**의존성:** Kotlin stdlib, Kotlin reflect (root subprojects에서 상속)

---

### application

**목적:** UseCase 단위 오케스트레이션, 트랜잭션 경계

**규칙:**
- UseCase 단위로 AppService 클래스 정의
- 클래스 이름에 `AppService` postfix 사용
- 클래스에 `@Service`, `@Transactional` 선언 (메서드가 아닌 클래스 레벨)
- 하나의 public 메서드만 제공 (단일 책임 원칙)
- AppService 간 상호 참조 금지
- 비즈니스 로직은 도메인에 위임, 오케스트레이션 역할만 수행
- 인터페이스 없이 class로 직접 선언
- domain 모듈만 의존 (infrastructure 직접 의존 금지)

**Gradle 플러그인:** `kotlin.jvm`, `kotlin.spring`, `spring.dependency.management`

**의존성:** `:domain`, Spring Context, Spring TX, Spring Security Crypto, Spring Validation

---

### infrastructure

**목적:** 기술 구현체 (DB, 외부 API, 보안 등)

**규칙:**
- domain에 정의된 Repository 인터페이스 구현
- JPA Entity는 infrastructure 전용 (domain 모델과 분리)
- Enum 타입은 `@Enumerated` 금지, `AttributeConverter` 사용 (`@Converter(autoApply = true)`)
- 생성일시/수정일시는 JPA Auditing(`@CreatedDate`, `@LastModifiedDate`) 사용
- BaseEntity를 상속하여 공통 타임스탬프 관리
- `TokenProvider` 인터페이스의 JWT 구현체 위치
- Spring Security 설정 및 필터 위치

**Gradle 플러그인:** `kotlin.jvm`, `kotlin.spring`, `kotlin.jpa`, `spring.dependency.management`

**의존성:** `:domain`, Spring Data JPA, Spring Web, Spring Security, JWT(jjwt), MySQL, Springdoc OpenAPI

---

### interfaces

**목적:** 외부 요청 수신 및 응답 (REST API)

**규칙:**
- REST Controller는 AppService만 호출
- DTO <-> Command 변환만 수행
- 비즈니스 로직 작성 금지
- Spring Boot Application Entry Point 위치
- `spring-boot` 플러그인이 적용되는 유일한 모듈

**Gradle 플러그인:** `kotlin.jvm`, `kotlin.spring`, `spring.boot`, `spring.dependency.management`

**의존성:** `:domain`, `:application`, `:infrastructure`, Spring Web, Spring Security, Spring Validation, JWT, Jackson, Springdoc OpenAPI, H2(test)

---

## DDD 패턴

### Aggregate Root
- 일관성 경계(Consistency Boundary)의 진입점
- `data class` + `private constructor`
- `create()`: 새로운 인스턴스 생성 (DomainContext 필수)
- `reconstruct()`: Repository 조회 시 재구성
- 상태 변경 메서드: `copy()`로 불변 반환
- 현재 프로젝트의 Aggregate Root: User, Employee, Store, AttendanceRecord, WorkSchedule, LeaveRequest, Payroll, PayrollPolicy, PayrollBatchHistory, AuditLog

### Entity
- 식별자가 있고 변경 가능한 객체
- Aggregate Root에 종속
- 현재 프로젝트의 Entity: PayrollDetail (PayrollId로 Payroll에 종속)

### Value Object
- 불변, 식별자 없음, 값 기반 동등성
- `@JvmInline value class` 또는 `data class`로 구현
- `init` 블록에서 유효성 검증
- 팩토리 메서드 제공: `generate()`, `from()`, `of()`, `standard()` 등
- 현재 프로젝트의 주요 VO: UserId, Email, Password, EmployeeId, EmployeeName, RemainingLeave, StoreId, StoreName, StoreLocation, AttendanceRecordId, AttendanceTime, WorkScheduleId, WorkDate, WorkTime, LeaveRequestId, LeavePeriod, PayrollId, PayrollAmount, PayrollPeriod, PayrollDetailId, PayrollPolicyId, PolicyMultiplier, PolicyEffectivePeriod, PayrollBatchHistoryId, AuditLogId

### Sealed Class
- enum 대신 sealed class 사용이 권장됨
- 현재 프로젝트에서 sealed class로 구현: ActionType, EntityType

### Repository
- 도메인 계층에 인터페이스 정의
- infrastructure 계층에서 구현
- 컬렉션과 유사한 추상화 제공

### Domain Service
- 복수 Aggregate 간 도메인 규칙
- Stateless
- `domain/service/`에 위치
- Spring 의존성 없음 (순수 Kotlin)
- 현재: LeavePolicyService, PayrollCalculationEngine

### Application Service (AppService)
- UseCase 1개당 AppService 1개
- 트랜잭션 경계 관리 (클래스 레벨 @Transactional)
- 도메인 객체와 Repository 호출만 수행

---

## 데이터 흐름

```
HTTP Request
    |
[REST Controller] (interfaces)
    | DTO -> Command 변환
[Application Service] (application) @Transactional
    | 오케스트레이션
[Domain Service] (domain) <- 비즈니스 로직
    | 상태 변경
[Aggregate Root] (domain) <- 상태 + 규칙
    | 영속화
[Repository Interface] (domain) -> [Repository Impl] (infrastructure) <- JPA
    |
Database
```

---

## 빌드 설정

### Version Catalog (`gradle/libs.versions.toml`)
- Kotlin 2.1.0
- Spring Boot 3.5.9
- Spring Dependency Management 1.1.7
- MySQL Connector 8.3.0
- H2 2.2.224
- Hibernate 6.4.1.Final
- JJWT 0.12.5
- Jakarta Validation 3.0.2
- Kotest 5.8.0
- MockK 1.13.9
- Spotless 7.0.2
- ktlint 1.5.0
- Springdoc OpenAPI 2.7.0

### 코드 품질
- Spotless + ktlint 적용 (모든 서브프로젝트)
- max_line_length: 120
- 비활성화된 ktlint 규칙: no-wildcard-imports, trailing-comma-on-call-site, trailing-comma-on-declaration-site, filename
- JVM Target: 17
- `-Xjsr305=strict` 컴파일러 옵션

### 테스트
- JUnit Platform 사용
- Kotest (Runner, Assertions, Property)
- MockK
- Spring MockK (integration test)
- Given-When-Then 패턴
- `shouldBe`, `shouldNotBe`, `shouldThrow` 매처 사용

---

## 설정 파일 구조

### application.yml 프로파일
- **dev**: 로컬 DB, `ddl-auto: update`, DEBUG 로깅, `show-sql: true`
- **prod**: 환경변수 기반, `ddl-auto: validate`, WARN 로깅, `show-sql: false`

### 환경 변수
- `DB_URL`, `DB_USERNAME`, `DB_PASSWORD`
- `JWT_SECRET_KEY`
- `SPRING_PROFILES_ACTIVE`

### JwtProperties
- `jwt.secretKey`: 비밀키
- `jwt.accessTokenExpiration`: Access Token 만료 시간 (기본 3600000ms = 1시간)
- `jwt.refreshTokenExpiration`: Refresh Token 만료 시간 (기본 604800000ms = 7일)
