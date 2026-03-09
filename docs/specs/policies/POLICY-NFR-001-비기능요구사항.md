# POLICY-NFR-001 비기능요구사항

## 기본 정보
- type: policy
- id: POLICY-NFR-001
- last-updated: 2026-03-09

## 정책 규칙

### 1. API 하위호환성
1. 기존 API의 URL, HTTP 메서드, 요청/응답 구조를 변경할 때 하위호환을 유지해야 한다.
2. 필드 추가는 허용하되, 기존 필드 삭제 또는 타입 변경은 금지한다.
3. API 변경 시 Frontend repo(lms-frontend)에 영향 범위를 공유해야 한다.
4. 에러 코드(ErrorCode)는 한번 정의되면 의미를 변경하지 않는다.

### 2. 데이터 무결성
1. 급여 데이터는 트랜잭션 내에서 원자적으로 처리되어야 한다.
2. 급여 금액 계산은 BigDecimal을 사용하며, 소수점 2자리 HALF_UP 반올림을 적용한다.
3. 출퇴근 기록 수정 시 변경 이력을 AuditLog에 기록한다.
4. AuditLog는 엔티티 타입(EntityType), 행위 타입(ActionType), 변경 전/후 값을 포함한다.

### 3. 변경 이력 추적
1. 감사 대상 엔티티의 모든 수정은 AuditLog에 기록해야 한다.
2. AuditLog에는 수행자(userId), 엔티티 타입, 엔티티 ID, 행위 타입, 변경 내용을 포함한다.
3. AuditLog는 삭제할 수 없다 (append-only).

### 4. 멀티 매장 지원
1. 모든 데이터 조회는 매장(storeId) 기반으로 격리되어야 한다.
2. MANAGER는 소속 매장의 데이터만 접근 가능하다.
3. 매장 간 데이터가 혼합되지 않도록 쿼리 레벨에서 storeId 필터링을 강제한다.
4. SUPER_ADMIN만 전체 매장 데이터에 접근할 수 있다.

### 5. 성능 요구사항
1. 일반 API 응답 시간은 500ms 이내를 목표로 한다.
2. 급여 산정 배치는 매장당 100명 근로자 기준 10초 이내에 완료되어야 한다.
3. HikariCP 커넥션 풀: 최대 10개, 최소 유휴 5개, 커넥션 타임아웃 30초.
4. Hibernate 배치 사이즈: 20 (INSERT/UPDATE 배치 처리).

### 6. 보안 요구사항
1. 비밀번호는 BCrypt로 암호화하여 저장한다 (평문 저장 금지).
2. JWT Secret Key는 운영 환경에서 반드시 환경변수(JWT_SECRET_KEY)로 설정한다.
3. 운영 환경에서 개발용 기본 Secret Key 사용을 금지한다.
4. DB 비밀번호는 환경변수(DB_PASSWORD)로 관리한다.
5. CORS allowedOriginPatterns는 운영 환경에서 구체적인 도메인으로 제한해야 한다.
6. Swagger UI는 운영 환경에서 비활성화를 권장한다.

### 7. 코드 품질
1. ktlint를 사용하여 코드 스타일을 통일한다.
2. 최대 줄 길이는 120자이다.
3. Spotless 플러그인으로 포맷팅을 자동화한다.
4. 도메인 레이어(domain 모듈)는 Spring Framework에 의존하지 않는다 (순수 Kotlin).
5. JVM 타겟은 17이다.
6. Kotlin 컴파일러 옵션: -Xjsr305=strict (null-safety 강화).

### 8. 테스트 요구사항
1. 단위 테스트는 JUnit 5 + Kotest + MockK를 사용한다.
2. 통합 테스트는 Testcontainers를 사용하여 실제 MySQL 환경에서 검증한다.
3. 테스트 시나리오는 Given-When-Then 형식으로 작성하고 @Tag("TC-xxx")를 부여한다.
4. 비기능 요구사항(동시성, 응답시간) 테스트를 포함한다.
5. 테스트 프로파일(`application-test.yml`)은 별도로 관리한다.

### 9. 아키텍처 규칙
1. DDD + Clean Architecture 기반 4-모듈 구조를 유지한다: domain, application, infrastructure, interfaces.
2. 의존성 방향: interfaces -> application -> domain, infrastructure -> domain.
3. domain 모듈은 다른 모듈을 의존하지 않는다.
4. 대상 도메인 외 코드 수정을 금지한다 (도메인 경계 보호).
5. open-in-view는 false로 설정한다 (지연 로딩 문제 방지).

### 10. 확장성 고려사항
1. 외부 급여/회계 시스템 연동을 위한 인터페이스 확장을 고려한다.
2. 위치 기반 출퇴근(GPS, Beacon) 확장을 고려한다.
3. 공휴일 판정은 향후 외부 API 또는 별도 공휴일 테이블로 확장한다.
4. BI 대시보드 및 HR 관리 시스템 확장을 고려한다.

## 적용 대상
- 전체 도메인: API 하위호환성, 보안, 성능, 코드 품질 규칙
- 급여(Payroll) 도메인: 데이터 무결성, BigDecimal 정밀도
- 출퇴근(Attendance) 도메인: 변경 이력 추적 (AuditLog)
- 전체 조회 API: 멀티 매장 격리
- 전체 모듈: 아키텍처 규칙 및 의존성 방향
