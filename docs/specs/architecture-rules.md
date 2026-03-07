# 아키텍처 규칙

## 기본 정보
- type: architecture_rules

## 아키텍처 패턴
DDD + Clean Architecture. 멀티모듈 구조로 계층을 물리적으로 분리한다.

## 레이어 정의와 책임

### domain (도메인 레이어)
- **책임**: Aggregate Root, Entity, Value Object, Domain Service, Repository 인터페이스
- **제약**: 순수 Kotlin만. Spring, JPA 등 외부 프레임워크 의존성 없음
- **패키지 규칙**: model/{도메인명}/ 하위에 Aggregate 단위로 구성
- **build.gradle.kts**: 외부 라이브러리 의존성 없음 (Kotlin stdlib만)

### application (애플리케이션 레이어)
- **책임**: UseCase/Application Service (AppService)
- **제약**: domain에만 의존. infrastructure 의존 금지
- **build.gradle.kts**: `implementation(project(":domain"))`, spring-context, spring-tx, validation, security-crypto
- **규칙**:
  - 클래스 이름: `{행위}AppService`
  - 하나의 공개 메서드만 노출 (단일 책임 원칙)
  - 클래스 레벨 `@Service`, `@Transactional`
  - AppService 간 직접 참조 금지
  - 비즈니스 로직은 도메인에 위임, 오케스트레이션만 수행

### infrastructure (인프라 레이어)
- **책임**: JPA Entity, Repository 구현체, Mapper, Security, 외부 API 어댑터
- **제약**: domain에 의존 가능. application에는 의존하지 않음
- **build.gradle.kts**: `implementation(project(":domain"))`, Spring Data JPA, Spring Web, Spring Security, JJWT, MySQL
- **규칙**:
  - JPA Entity와 Domain Model은 반드시 분리
  - Mapper 클래스로 상호 변환
  - Enum은 `AttributeConverter`로 변환 (`@Enumerated` 사용 금지)
  - `@Converter(autoApply = true)` 사용

### interfaces (프레젠테이션 레이어)
- **책임**: REST Controller, DTO (Request/Response)
- **제약**: application에 의존. domain/infrastructure 직접 참조 가능 (모듈 의존성)
- **build.gradle.kts**: `implementation(project(":domain"))`, `implementation(project(":application"))`, `implementation(project(":infrastructure"))`, Spring Boot 플러그인, Spring Web, Security, Jackson, SpringDoc
- **규칙**:
  - Controller는 AppService만 호출
  - DTO ↔ Command 변환
  - 비즈니스 로직 금지
  - `@PreAuthorize`로 권한 제어

## 의존성 방향 (절대 규칙)
```
domain ← application ← interfaces
domain ← application ← infrastructure
interfaces와 infrastructure는 서로 의존하지 않는다
```

## 도메인 모델 규칙
- 새 도메인 추가 시 `domain/model/{도메인명}/` 패키지 생성
- Aggregate Root는 `companion object { fun create(...) }` 패턴으로 생성
- 모든 도메인 메서드는 첫 번째 인자로 `DomainContext`
- Value Object는 `@JvmInline value class`, `init` 블록에서 검증
- `data class`는 불변 원칙, `copy()`로 상태 변경
- 삭제는 soft delete 원칙 (isActive=false)
- 상태 변경은 이력을 남김 (AuditLog)

## DomainContext
```kotlin
interface DomainContext {
    val serviceName: String
    val userId: String
    val userName: String
    val roleId: String
    val requestId: String    // UUID
    val requestedAt: Instant
    val clientIp: String
}
```
- 모든 도메인 비즈니스 메서드의 첫 번째 인자
- infrastructure의 `HttpDomainContext`에서 HTTP 요청 기반으로 생성
- `DomainContextInterceptor` + `DomainContextArgumentResolver`로 Controller에 주입

## 인프라 규칙

### JPA Entity
- `BaseEntity` 상속: `@CreatedDate createdAt`, `@LastModifiedDate updatedAt`, `createdBy`, `updatedBy`
- `@EntityListeners(AuditingEntityListener::class)`
- `@EnableJpaAuditing` 설정

### Mapper
- `infrastructure/persistence/{도메인}/mapper/` 경로
- `toDomain()`: JPA Entity → Domain Model
- `toEntity()`: Domain Model → JPA Entity

### Repository
- 인터페이스: `domain/model/{도메인}/` 하위
- 구현체: `infrastructure/persistence/{도메인}/`
- Spring Data JPA Repository를 내부적으로 사용

## 예외 처리
- 도메인 예외: `DomainException(code: String, message: String)` 추상 클래스 상속
- 각 도메인별 구체 예외 클래스 정의 (AuthException, EmployeeException 등)
- 에러 코드: `{도메인약어}{번호}` (예: AUTH001, LEAVE003)
- Controller 레벨에서 `@ControllerAdvice(GlobalExceptionHandler)`로 공통 처리
