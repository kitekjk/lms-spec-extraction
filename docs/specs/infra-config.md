# 인프라 설정

## 기본 정보
- type: infra_config
- last-updated: 2026-03-09

## 데이터베이스

### MySQL 설정
| 항목 | 값 |
|------|-----|
| 엔진 | MySQL 8.0 |
| 문자셋 | utf8mb4 |
| 정렬(Collation) | utf8mb4_unicode_ci |
| 인증 플러그인 | mysql_native_password |
| 데이터베이스명 | lms_demo |

### 접속 정보 (프로파일별)

| 프로파일 | Host | Port | Username | Password | 비고 |
|----------|------|------|----------|----------|------|
| local | localhost | 3306 | lms | lms1234 | 로컬 개발용 |
| default | localhost | 3306 | root | ${DB_PASSWORD:changeme} | 환경변수 우선 |
| prod | 환경변수 | 환경변수 | 환경변수 | 환경변수 | 환경변수 필수 |

### JDBC URL 파라미터
```
useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true
```

### HikariCP 커넥션 풀 설정
| 항목 | 값 | 설명 |
|------|-----|------|
| maximum-pool-size | 10 | 최대 커넥션 수 |
| minimum-idle | 5 | 최소 유휴 커넥션 |
| connection-timeout | 30000ms (30초) | 커넥션 획득 대기 시간 |
| idle-timeout | 600000ms (10분) | 유휴 커넥션 유지 시간 |
| max-lifetime | 1800000ms (30분) | 커넥션 최대 수명 |

### JPA/Hibernate 설정

| 프로파일 | ddl-auto | show-sql | sql.init.mode | 설명 |
|----------|----------|----------|---------------|------|
| local | create-drop | true | always | 서버 시작 시 테이블 생성, 종료 시 삭제, data.sql 매번 실행 |
| dev | update | true | never | 스키마 변경사항 자동 반영, 초기 데이터 로드 안 함 |
| prod | validate | false | never | 스키마 검증만 수행, SQL 출력 안 함 |

### Hibernate 배치 설정
| 항목 | 값 |
|------|-----|
| batch_size | 20 |
| order_inserts | true |
| order_updates | true |
| dialect | org.hibernate.dialect.MySQLDialect |
| open-in-view | false |

## 서버 설정

### 기본 설정
| 항목 | 값 |
|------|-----|
| 서버 포트 | 8080 |
| 애플리케이션 이름 | lms-demo |
| 기본 프로파일 | local |

### 에러 응답 설정
| 항목 | 값 |
|------|-----|
| include-message | always |
| include-binding-errors | always |
| include-stacktrace | on_param |
| include-exception | false |

### Jackson 직렬화 설정
| 항목 | 값 |
|------|-----|
| write-dates-as-timestamps | false (ISO-8601 형식 사용) |
| fail-on-unknown-properties | false |
| time-zone | Asia/Seoul |

## 인증/보안 설정

### JWT 설정
| 항목 | 값 |
|------|-----|
| 알고리즘 | HS256 (HMAC-SHA256) |
| Access Token 만료 | 3600000ms (1시간) |
| Refresh Token 만료 | 604800000ms (7일) |
| Secret Key (개발) | 환경변수 JWT_SECRET_KEY, 미설정 시 개발용 기본값 사용 |
| Secret Key (운영) | 환경변수 JWT_SECRET_KEY 필수 설정 |

### Spring Security 설정
| 항목 | 값 |
|------|-----|
| 세션 정책 | STATELESS (세션 미사용) |
| CSRF | 비활성화 (JWT 사용) |
| 비밀번호 암호화 | BCryptPasswordEncoder |
| Method Security | @PreAuthorize, @PostAuthorize 활성화 |

### CORS 설정
| 항목 | 값 |
|------|-----|
| allowedOriginPatterns | * (전체 허용) |
| allowedMethods | GET, POST, PUT, DELETE, PATCH, OPTIONS |
| allowedHeaders | * |
| exposedHeaders | Authorization |
| allowCredentials | true |
| maxAge | 3600초 (1시간) |

### 인증 제외 경로
- `/api/auth/**` - 인증 API
- `/health` - 헬스체크
- `/actuator/health` - 액추에이터 헬스체크
- `/swagger-ui/**`, `/swagger-ui.html` - Swagger UI
- `/api-docs/**`, `/v3/api-docs/**` - API 문서
- `OPTIONS /**` - CORS preflight 요청

## API 문서 설정 (Springdoc OpenAPI)
| 항목 | 값 |
|------|-----|
| API Docs 경로 | /api-docs |
| Swagger UI 경로 | /swagger-ui.html |
| 기본 Content-Type | application/json |
| 태그 정렬 | 알파벳순 |
| 오퍼레이션 정렬 | HTTP 메서드순 |
| doc-expansion | none (접혀있는 상태) |

## Docker 설정

### docker-compose.yml
| 항목 | 값 |
|------|-----|
| 이미지 | mysql:8.0 |
| 컨테이너명 | lms-demo-mysql |
| 외부 포트 | 3306 |
| MYSQL_ROOT_PASSWORD | changeme |
| MYSQL_DATABASE | lms_demo |
| MYSQL_USER | lms |
| MYSQL_PASSWORD | lms1234 |
| 볼륨 | mysql_data (named volume) |
| 헬스체크 간격 | 10초, 타임아웃 5초, 재시도 5회 |
| 재시작 정책 | unless-stopped |

## 멀티모듈 구조
| 모듈 | 설명 |
|------|------|
| domain | 도메인 모델, 비즈니스 규칙 (순수 Kotlin, Spring 의존성 없음) |
| application | 유스케이스, 애플리케이션 서비스 |
| infrastructure | JPA 엔티티, 리포지토리 구현, Security 설정 |
| interfaces | REST 컨트롤러, DTO, application.yml, data.sql |

## 코드 품질 설정

### Spotless + ktlint
| 항목 | 값 |
|------|-----|
| 대상 | **/*.kt |
| 제외 | **/build/**/*.kt |
| max_line_length | 120 |
| no-wildcard-imports | disabled |
| trailing-comma-on-call-site | disabled |
| trailing-comma-on-declaration-site | disabled |
| filename | disabled |

## 로깅 설정 (프로파일별)

### local / dev
| 로거 | 레벨 |
|------|------|
| root | INFO |
| com.lms | DEBUG |
| org.springframework.security | DEBUG (local) / INFO (dev) |
| org.hibernate.SQL | DEBUG |
| org.hibernate.type.descriptor.sql.BasicBinder | TRACE (local only) |

### prod
| 로거 | 레벨 |
|------|------|
| root | WARN |
| com.lms | INFO |
| org.springframework.security | WARN |
| org.hibernate.SQL | WARN |
