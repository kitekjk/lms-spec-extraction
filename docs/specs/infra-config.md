# LMS Backend - 인프라 설정

## 기본 정보
- type: infra_config

## 데이터베이스

### MySQL 설정
- 이미지: `mysql:8.0`
- 컨테이너명: `lms-demo-mysql`
- 포트: `3306:3306`
- 데이터베이스명: `lms_demo`
- 문자셋: `utf8mb4`
- Collation: `utf8mb4_unicode_ci`
- 인증 플러그인: `mysql_native_password`
- 볼륨: `mysql_data:/var/lib/mysql` (로컬 드라이버)
- 헬스체크: `mysqladmin ping` (10초 간격, 5초 타임아웃, 5회 재시도)

### 커넥션 풀 (HikariCP)
| 속성 | 값 | 설명 |
|------|-----|------|
| maximum-pool-size | 10 | 최대 커넥션 수 |
| minimum-idle | 5 | 최소 유휴 커넥션 수 |
| connection-timeout | 30,000ms | 연결 획득 타임아웃 (30초) |
| idle-timeout | 600,000ms | 유휴 커넥션 타임아웃 (10분) |
| max-lifetime | 1,800,000ms | 커넥션 최대 수명 (30분) |

### JDBC URL
- 기본: `jdbc:mysql://localhost:3306/lms_demo?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true`
- 드라이버: `com.mysql.cj.jdbc.Driver`

### JPA/Hibernate 설정
| 속성 | 값 |
|------|-----|
| dialect | `org.hibernate.dialect.MySQLDialect` |
| batch_size | 20 |
| order_inserts | true |
| order_updates | true |
| use_sql_comments | true |
| open-in-view | false |
| defer-datasource-initialization | true |

## 보안

### JWT 설정
| 속성 | 값 | 환경 변수 |
|------|-----|----------|
| secret-key | 개발용 기본값 제공 (프로덕션에서 반드시 변경) | `JWT_SECRET_KEY` |
| access-token-expiration | 3,600,000ms (1시간) | - |
| refresh-token-expiration | 604,800,000ms (7일) | - |

- 서명 알고리즘: HMAC-SHA (HS256)
- 시크릿 키: 256비트 이상 필수
- 비밀번호 암호화: BCrypt

### Spring Security
- CSRF: 비활성화 (JWT Stateless)
- 세션 정책: STATELESS
- 메서드 보안: `@EnableMethodSecurity(prePostEnabled = true)`
- CORS: 모든 오리진 허용 (Preflight 캐시 3,600초)

## 프로파일별 설정

### local (로컬 개발)
```yaml
spring:
  datasource:
    username: lms
    password: lms1234
  jpa:
    hibernate:
      ddl-auto: create-drop    # 서버 시작 시 생성, 종료 시 삭제
    show-sql: true
  sql:
    init:
      mode: always             # data.sql 항상 실행
```
- DemoDataInitializer 실행: 강남점 3주치 근무 일정 자동 생성 (1주 전 ~ 2주 후, 월~금)
- 로깅: DEBUG (com.lms), TRACE (SQL 파라미터)

### dev (개발 서버)
```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: update         # 스키마 자동 반영
    show-sql: true
  sql:
    init:
      mode: never              # 초기 데이터 미로드
```
- 로깅: DEBUG (com.lms), INFO (Security)

### prod (프로덕션)
```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate       # 스키마 검증만
    show-sql: false
  sql:
    init:
      mode: never
```
- 로깅: INFO (com.lms), WARN (root, Security, Hibernate)

## API 문서

### Springdoc OpenAPI
| 속성 | 값 |
|------|-----|
| API 문서 경로 | `/api-docs` |
| Swagger UI 경로 | `/swagger-ui.html` |
| Content-Type | `application/json` |
| 태그 정렬 | 알파벳순 |
| 작업 정렬 | HTTP 메서드순 |
| 요청 시간 표시 | 활성화 |

### 서버 목록
| 환경 | URL |
|------|-----|
| 로컬 개발 | `http://localhost:8080` |
| 프로덕션 | `https://api.lms.com` |

## 서버 설정
| 속성 | 값 |
|------|-----|
| 포트 | 8080 |
| 에러 메시지 포함 | always |
| 바인딩 에러 포함 | always |
| 스택 트레이스 포함 | on_param |
| 예외 클래스명 포함 | false |

## Jackson 설정
| 속성 | 값 |
|------|-----|
| 타임존 | Asia/Seoul |
| 날짜 직렬화 | ISO 형식 (timestamps 비활성화) |
| 알 수 없는 속성 처리 | 무시 (fail-on-unknown-properties: false) |

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DB_PASSWORD` | 데이터베이스 비밀번호 | `changeme` |
| `JWT_SECRET_KEY` | JWT 서명 키 (256비트 이상) | 개발용 기본값 |
| `SPRING_PROFILES_ACTIVE` | 활성 프로파일 | `local` |

## Docker Compose 서비스

### mysql
| 속성 | 값 |
|------|-----|
| 이미지 | mysql:8.0 |
| 컨테이너명 | lms-demo-mysql |
| 재시작 정책 | unless-stopped |
| MYSQL_ROOT_PASSWORD | changeme |
| MYSQL_DATABASE | lms_demo |
| MYSQL_USER | lms |
| MYSQL_PASSWORD | lms1234 |

## 기술 스택 버전 (gradle/libs.versions.toml)

| 항목 | 버전 |
|------|------|
| Kotlin | 2.1.0 |
| Spring Boot | 3.5.9 |
| Spring Dependency Management | 1.1.7 |
| MySQL Connector | 8.3.0 |
| H2 (테스트) | 2.2.224 |
| Hibernate | 6.4.1.Final |
| JJWT | 0.12.5 |
| Jakarta Validation | 3.0.2 |
| Jackson | 2.16.1 |
| JUnit 5 | 5.10.1 |
| MockK | 1.13.9 |
| Spring MockK | 4.0.2 |
| Kotest | 5.8.0 |
| Springdoc OpenAPI | 2.7.0 |
| Spotless | 7.0.2 |
| ktlint | 1.5.0 |
