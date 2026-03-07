# 인프라 설정

## 기본 정보
- type: infra_config

## 데이터베이스
- DBMS: MySQL 8.3.0, utf8mb4, utf8mb4_unicode_ci
- 접속 정보: 환경변수로 관리 (.env)
- 기본 접속: localhost:3306/lms_demo, lms/lms1234
- JDBC URL 필수 파라미터: `useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true`

## 프로파일별 설정

### local/dev
- DDL: `create-drop` (재시작 시 스키마 재생성)
- 초기 데이터: `data.sql` 자동 로드
- Swagger UI: `http://localhost:8080/swagger-ui.html` 활성화
- 로깅: DEBUG 레벨, SQL 출력 (`show-sql: true`)
- HikariCP: 기본 풀 크기

### prod
- DDL: `validate` (스키마 자동 변경 없음)
- Swagger: 비활성화
- 로깅: WARN/INFO 레벨, SQL 출력 안 함
- HikariCP: 확장된 풀 크기
- 접속 정보: 환경변수 (DB_URL, DB_USERNAME, DB_PASSWORD)

## 보안 설정

### JWT 설정
- 비밀키: 환경변수 `JWT_SECRET_KEY` (256-bit)
- Access Token 만료: 3,600,000ms (1시간)
- Refresh Token 만료: 604,800,000ms (7일)
- 설정 클래스: `JwtProperties` (`@ConfigurationProperties(prefix = "jwt")`)

### Spring Security
- 무상태 세션 (SessionCreationPolicy.STATELESS)
- BCrypt 비밀번호 암호화
- CORS 활성화
- CSRF 비활성화
- 공개 엔드포인트: `/api/auth/**`, `/swagger-ui/**`, `/v3/api-docs/**`, `/health`
- 그 외 인증 필요
- JwtAuthenticationFilter: OncePerRequestFilter로 JWT 검증
- `@PreAuthorize` 메서드 레벨 권한 제어 (`@EnableMethodSecurity`)

### 역할 (Role)
- SUPER_ADMIN: 전체 시스템 관리, 매장/근로자/정책 관리
- MANAGER: 소속 매장 근로자/일정/출퇴근/휴가 관리
- EMPLOYEE: 자신의 출퇴근, 일정 조회, 휴가 신청

## 컨테이너 구성 (docker-compose.yml)
- MySQL 8.3.0: 포트 3306, lms_demo 데이터베이스
- Volume: mysql-data (데이터 영속화)

## JPA 설정
- `@EnableJpaAuditing`: 자동 감사 필드 (createdAt, updatedAt)
- Hibernate: `open-in-view: false`
- 네이밍 전략: SpringPhysicalNamingStrategy (snake_case)
- BaseEntity: createdAt, updatedAt, createdBy, updatedBy

## 스케줄링
- `@EnableScheduling`
- PayrollBatchScheduler: `cron = "0 0 1 L * ?"` (매월 마지막 날 01:00)

## API 문서 (SpringDoc OpenAPI)
- 설정 클래스: `OpenApiConfig`
- Security Scheme: Bearer Authentication
- Swagger UI 경로: `/swagger-ui.html`
