# POLICY-NFR-001: 비기능 요구사항

## 기본 정보
- type: policy
- domain: cross-cutting
- related-specs: [architecture-rules.md, infra-config.md]

## 정책 규칙

### RULE-001: API 하위호환 유지
- 조건: 기존 API 변경 시
- 결과: 하위호환성을 반드시 유지. 기존 클라이언트(lms-frontend)가 영향받지 않도록 함
- 위반 시: 변경 전 Frontend repo에 영향 공유 필요
- 근거: `CLAUDE.md` - "기존 API 하위호환 유지 (POLICY-NFR-001)"

### RULE-002: 인증 보안 요구사항
- 조건: 인증/인가 관련 구현 시
- 결과:
  - JWT 토큰 서명에 256비트 이상 HMAC-SHA 키 사용
  - Access Token 만료: 1시간 (3,600,000ms)
  - Refresh Token 만료: 7일 (604,800,000ms)
  - 비밀번호 저장: BCrypt 해싱
  - CSRF 비활성화 (JWT Stateless 방식이므로)
  - 세션 사용 금지 (Stateless)
- 근거: `SecurityConfig.kt`, `JwtProperties.kt`

### RULE-003: 데이터베이스 연결 관리
- 조건: 데이터베이스 커넥션 풀 설정
- 결과:
  - 최대 풀 크기: 10
  - 최소 유휴 연결: 5
  - 연결 타임아웃: 30,000ms (30초)
  - 유휴 타임아웃: 600,000ms (10분)
  - 최대 수명: 1,800,000ms (30분)
- 근거: `application.yml` - `spring.datasource.hikari`

### RULE-004: JPA/Hibernate 배치 설정
- 조건: 대량 데이터 처리 시
- 결과:
  - JDBC 배치 크기: 20
  - INSERT 순서 정렬: 활성화 (`order_inserts: true`)
  - UPDATE 순서 정렬: 활성화 (`order_updates: true`)
  - Open-in-View: 비활성화 (`open-in-view: false`)
- 근거: `application.yml` - `spring.jpa.properties.hibernate`

### RULE-005: 프로파일별 스키마 관리
- 조건: 환경별 DDL 전략
- 결과:
  | 프로파일 | ddl-auto | SQL 초기화 | 설명 |
  |----------|----------|-----------|------|
  | local | `create-drop` | `always` | 서버 시작 시 테이블 생성, 종료 시 삭제. data.sql 항상 실행 |
  | dev | `update` | `never` | 스키마 변경사항 자동 반영. 초기 데이터 미로드 |
  | prod | `validate` | `never` | 스키마 검증만 수행. 초기 데이터 미로드 |
  | default | `validate` | `never` | 프로덕션 안전 기본값 |
- 근거: `application.yml`, `application-local.yml`, `application-dev.yml`, `application-prod.yml`

### RULE-006: 로깅 수준
- 조건: 환경별 로깅 설정
- 결과:
  | 패키지 | local | dev | prod |
  |--------|-------|-----|------|
  | root | INFO | INFO | WARN |
  | com.lms | DEBUG | DEBUG | INFO |
  | Spring Security | DEBUG | INFO | WARN |
  | Hibernate SQL | DEBUG | DEBUG | WARN |
  | BasicBinder (파라미터) | TRACE | - | - |
- 근거: `application.yml`, `application-*.yml`

### RULE-007: 문자 인코딩
- 조건: 데이터베이스 및 API 통신
- 결과:
  - MySQL 문자셋: `utf8mb4`
  - MySQL Collation: `utf8mb4_unicode_ci`
  - Jackson 타임존: `Asia/Seoul`
  - 날짜 직렬화: ISO 형식 (`write-dates-as-timestamps: false`)
  - 알 수 없는 속성 무시: `fail-on-unknown-properties: false`
- 근거: `docker-compose.yml`, `application.yml` - `spring.jackson`

### RULE-008: 에러 응답 정책
- 조건: API 에러 응답 시
- 결과:
  - 에러 메시지 포함: `include-message: always`
  - 바인딩 에러 포함: `include-binding-errors: always`
  - 스택 트레이스: 파라미터 지정 시에만 포함 (`include-stacktrace: on_param`)
  - 예외 클래스명: 미포함 (`include-exception: false`)
  - 모든 도메인 예외는 `DomainException` 추상 클래스를 상속하며 `code` (에러 코드)와 `message`를 포함
- 근거: `application.yml` - `server.error`, `DomainException.kt`

### RULE-009: API 문서화
- 조건: API 문서 자동 생성
- 결과:
  - OpenAPI 3.0 (Springdoc) 사용
  - API 문서 경로: `/api-docs`
  - Swagger UI 경로: `/swagger-ui.html`
  - 기본 Content-Type: `application/json`
  - JWT Bearer Authentication 스키마 등록
  - 서버 목록: 로컬(`http://localhost:8080`), 프로덕션(`https://api.lms.com`)
- 근거: `OpenApiConfig.kt`, `application.yml` - `springdoc`

### RULE-010: 서버 포트
- 조건: 서버 기본 포트
- 결과: `8080`
- 근거: `application.yml` - `server.port: 8080`

### RULE-011: 도메인 서비스 의존성 관리
- 조건: 순수 도메인 서비스의 Spring Bean 등록
- 결과: 도메인 서비스(`LeavePolicyService`, `PayrollCalculationEngine`)는 Spring 어노테이션 없이 순수 Kotlin 클래스로 구현하고, `DomainServiceConfig`에서 `@Bean`으로 등록
- 근거: `DomainServiceConfig.kt`

### RULE-012: DomainContext 주입
- 조건: 도메인 계층에서 요청 컨텍스트(인증 사용자 정보, 매장 ID 등)를 참조할 때
- 결과: `DomainContextInterceptor`와 `DomainContextArgumentResolver`를 통해 `/api/**` 경로에 자동 주입
- 근거: `WebMvcConfig.kt`

### RULE-013: 스케줄링
- 조건: 배치/스케줄 작업을 등록하여 주기적으로 실행할 때
- 결과: Spring `@EnableScheduling` 활성화. `@Scheduled` 어노테이션 사용 가능
- 근거: `SchedulingConfig.kt`

### RULE-014: JPA Auditing
- 조건: 엔티티의 생성/수정 시간 관리
- 결과: `@EnableJpaAuditing` 활성화. `createdAt`, `updatedAt` 자동 관리
- 근거: `JpaConfig.kt`

## 기술 스택 버전

| 항목 | 버전 |
|------|------|
| Kotlin | 2.1.0 |
| Spring Boot | 3.5.9 |
| Spring Dependency Management | 1.1.7 |
| MySQL Connector | 8.3.0 |
| Hibernate | 6.4.1.Final |
| JJWT | 0.12.5 |
| Jakarta Validation | 3.0.2 |
| JUnit 5 | 5.10.1 |
| MockK | 1.13.9 |
| Kotest | 5.8.0 |
| Springdoc OpenAPI | 2.7.0 |
| Spotless | 7.0.2 |
| ktlint | 1.5.0 |

## 적용 대상

- 전체 Use Case
- 전체 API Spec
