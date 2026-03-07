# Spec Generator Skill

## 목적
기존 소스코드와 문서를 분석하여 Harness Engineering 표준에 맞는 Spec 문서를 자동 생성한다.
생성된 Spec은 향후 소스코드를 제거하고 AI가 처음부터 재개발할 때의 입력이 된다.

## 사용법
```
프로젝트 루트에서:
  "이 프로젝트의 Spec 문서를 생성해줘"

특정 도메인만:
  "attendance 도메인의 Spec을 생성해줘"

정책만:
  "출퇴근 관련 정책 Spec을 생성해줘"
```

---

## 분석 순서

### 1단계: 기존 문서 먼저 읽기
코드를 분석하기 전에 기존 문서를 먼저 읽어 프로젝트의 전체 맥락을 파악한다.

읽는 순서:
1. **README.md** → 프로젝트 개요, 도메인 모델 목록, 설계 결정 사항
2. **docs/ARCHITECTURE.md** → 아키텍처 구조, 계층 간 의존성 규칙
3. **docs/DEMO_SCENARIOS.md** → 역할별 시나리오 → Use Case 흐름, 테스트 시나리오 추출
4. **docs/LOCAL_MYSQL_SETUP.md** → DB 설정, 초기 데이터 구조
5. **.aiassistant/rules/guideline.md** → 코딩 컨벤션 → naming-guide에 반영
6. **.taskmaster/docs/prd.md** (있으면) → 원본 요구사항

### 2단계: 프로젝트 구조 파악
이 프로젝트는 **멀티모듈 Clean Architecture** 구조이다.

파악 순서:
1. settings.gradle.kts → 모듈 목록
2. 루트 + 각 모듈의 build.gradle.kts → 기술 스택, 모듈 간 의존성
3. domain/src/.../model/ 하위 패키지 → 도메인(Aggregate) 목록
4. infrastructure/.../config/ → DB, Security, 외부 연동 설정
5. interfaces/.../web/ → API 엔드포인트

### 3단계: 도메인별 심층 분석
각 도메인 대상으로:

1. **domain/model/{도메인}/** → Aggregate Root, Entity, Value Object, Enum
   - 필드별 타입/제약조건을 **개별 항목으로** 추출
   - Value Object의 init 블록 검증 규칙
   - Enum 상태 목록과 전이 규칙
   - DomainContext 사용 패턴

2. **domain/service/** → Domain Service (여러 Aggregate 걸치는 로직)

3. **application/{도메인}/** → UseCase, Application Service
   - 비즈니스 흐름 (함수명 제외, 흐름만)
   - 트랜잭션 경계, 에러 처리
   - 주 모델/참조 모델 판별

4. **interfaces/web/{도메인}/** → Controller, DTO
   - API 엔드포인트, @PreAuthorize 권한, @Valid 검증

5. **infrastructure/persistence/{도메인}/** → JPA Entity, Repository, Mapper

6. **infrastructure/security/** → 인증/인가 규칙

7. **기존 테스트 코드** (src/test/)
   - Given-When-Then 패턴으로 변환
   - 테스트 레벨(Unit/Integration/E2E) 판별

8. **비기능 요구사항 추출**
   - 응답시간 관련 코드 (타임아웃 설정, 캐시 등)
   - 동시성 제어 (락, @Version 등)
   - 트랜잭션 범위 (@Transactional 경계)
   - 보안 설정 (경로별 접근 제어, CORS 등)

### 4단계: Spec 문서 생성
분석 결과를 아래 템플릿에 맞춰 생성한다.
**기존 문서(1단계)와 코드(2~3단계)를 교차 검증**하여 빠진 규칙이 없는지 확인한다.

---

## 출력 디렉토리 구조

```
docs/specs/
├── service-definition.md
├── architecture-rules.md
├── naming-guide.md
├── infra-config.md
├── init-data.md
│
├── policies/
│   ├── POLICY-AUTH-001-인증인가.md
│   ├── POLICY-ATTENDANCE-001-출퇴근.md
│   ├── POLICY-SCHEDULE-001-근무일정.md
│   ├── POLICY-LEAVE-001-휴가.md
│   ├── POLICY-PAYROLL-001-급여.md
│   └── POLICY-NFR-001-비기능요구사항.md
│
├── user/
│   ├── LMS-USER-001-로그인.md
│   ├── LMS-USER-002-회원가입.md
│   └── LMS-API-USER-001-인증API.md
├── employee/
│   ├── LMS-EMPLOYEE-001-근로자등록.md
│   ├── LMS-EMPLOYEE-002-근로자수정.md
│   └── LMS-API-EMPLOYEE-001-근로자API.md
├── store/
│   ├── LMS-STORE-001-매장관리.md
│   └── LMS-API-STORE-001-매장API.md
├── schedule/
│   ├── LMS-SCHEDULE-001-근무일정생성.md
│   ├── LMS-SCHEDULE-002-근무일정변경.md
│   └── LMS-API-SCHEDULE-001-스케줄API.md
├── attendance/
│   ├── LMS-ATTENDANCE-001-출퇴근기록.md
│   ├── LMS-ATTENDANCE-002-출퇴근수정.md
│   └── LMS-API-ATTENDANCE-001-출퇴근API.md
├── leave/
│   ├── LMS-LEAVE-001-휴가신청.md
│   ├── LMS-LEAVE-002-휴가승인.md
│   └── LMS-API-LEAVE-001-휴가API.md
└── payroll/
    ├── LMS-PAYROLL-001-급여산정.md
    ├── LMS-PAYROLL-002-급여정책관리.md
    └── LMS-API-PAYROLL-001-급여API.md
```

---

## Spec 템플릿

### 서비스 정의 (service-definition.md)

```markdown
# LMS - 서비스 정의

## 기본 정보
- type: service_definition
- domain: lms
- owner: {팀명}
- last_updated: {날짜}

## 서비스 목적과 범위
{README, ARCHITECTURE.md, PRD에서 추출}

## 기술 스택
- Language: Kotlin 2.1.x
- Framework: Spring Boot 3.5.x
- JDK: 21
- Build: Gradle (Kotlin DSL)
- DB: MySQL 8.x + Spring Data JPA (Hibernate 6.x)
- Security: Spring Security 6.x + JWT
- Test: JUnit 5 + MockK + Testcontainers
- API Docs: SpringDoc OpenAPI
- Code Style: Spotless + ktlint

## 핵심 모델
{필드는 개별 항목으로 기술}

### User (사용자)
- **역할**: 인증/인가 관심사
- **주요 필드**:
  - id: UserId (VO, 비어있을 수 없음)
  - email: Email (VO, 이메일 형식 검증)
  - password: Password (VO, 암호화 저장)
  - role: Role (Enum: ADMIN, MANAGER, EMPLOYEE)
  - isActive: Boolean (비활성 사용자 로그인 불가)
  - lastLoginAt: Instant

### Employee (근로자)
...{동일 형식으로 전체 모델}

## 외부 계약

### 현재 연계
- (없음 - 현재 단독 서비스)

### 향후 연계 예정
- **급여지급 시스템**: 월별 근무이력 전달 (발행 예정)
- **HR 시스템**: 직원 마스터 정보 수신 (수신 예정)
- **ERP**: 매장 정보 동기화 (수신 예정)

## 소유 데이터
- 출퇴근 기록: LMS가 truth owner
- 근무 일정: LMS가 truth owner
- 직원 기본정보: LMS가 truth owner (향후 HR에서 수신 가능)
- 매장 정보: LMS가 truth owner (향후 ERP에서 수신 가능)
```

### 아키텍처 규칙 (architecture-rules.md)

```markdown
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

### application (애플리케이션 레이어)
- **책임**: UseCase/Application Service
- **제약**: domain에만 의존

### infrastructure (인프라 레이어)
- **책임**: JPA Entity, Repository 구현체, Mapper, Security, 외부 API
- **제약**: domain, application에 의존 가능

### interfaces (프레젠테이션 레이어)
- **책임**: REST Controller, DTO
- **제약**: application에 의존

## 의존성 방향 (절대 규칙)
domain ← application ← interfaces
domain ← application ← infrastructure
interfaces와 infrastructure는 서로 의존하지 않는다

## 도메인 모델 규칙
- 새 도메인 추가 시 domain/model/{도메인명}/ 패키지 생성
- Aggregate Root는 companion object { fun create(...) } 패턴
- 모든 도메인 메서드는 첫 번째 인자로 DomainContext
- Value Object는 @JvmInline value class, init에서 검증
- 삭제는 soft delete 원칙
- 상태 변경은 이력을 남김

## 인프라 규칙
- JPA Entity와 Domain Model은 반드시 분리
- Mapper는 infrastructure/persistence/{도메인}/mapper/
- Repository 인터페이스는 domain, 구현체는 infrastructure
```

### 네이밍 가이드 (naming-guide.md)

```markdown
# 네이밍 가이드

## 기본 정보
- type: naming_guide

## 패키지
- com.lms.domain.model.{도메인명}
- com.lms.application.{도메인명}
- com.lms.infrastructure.persistence.{도메인명}
- com.lms.interfaces.web.{도메인명}

## 클래스
- Aggregate Root: {도메인명}
- Value Object: @JvmInline value class {의미명}
- JPA Entity: {도메인명}JpaEntity
- Mapper: {도메인명}Mapper
- Repository 인터페이스: {도메인명}Repository (domain)
- Repository 구현체: {도메인명}RepositoryImpl (infrastructure)
- Application Service: {도메인명}Service 또는 {행위}UseCase
- Controller: {도메인명}Controller
- DTO: {행위}Request, {행위}Response

## API 경로
- /api/v1/{리소스-복수형}
- /api/v1/{리소스-복수형}/{id}
- /api/v1/{리소스-복수형}/{id}/{행위}

## 테스트 클래스
- Unit: {클래스명}Test
- Integration: {도메인명}IntegrationTest
- E2E: {도메인명}E2ETest
- @Tag("TC-{ID}")로 Spec 테스트 시나리오와 매핑

## 이벤트 토픽 (향후)
- lms.{도메인}.{aggregate}.{event}

## 기타
- 변수/함수: camelCase
- 상수: UPPER_SNAKE_CASE
- DB 테이블/컬럼: snake_case
```

### 인프라 설정 (infra-config.md)

```markdown
# 인프라 설정

## 기본 정보
- type: infra_config

## 데이터베이스
- DBMS: MySQL 8.x, utf8mb4
- 접속 정보: 환경변수로 관리

## 프로파일별 설정
- **local**: DDL create-drop, 초기 데이터, Swagger 활성화
- **dev**: DDL update
- **prod**: DDL validate, Swagger 비활성화

## 컨테이너 구성
- MySQL: 포트 3306

## 보안 설정
- JWT 기반, 비밀키는 환경변수
- 비밀번호: BCrypt
```

### 초기 데이터 (init-data.md)

```markdown
# 초기 데이터 정의

## 기본 정보
- type: init_data
- 적용 프로파일: local

## 기본 매장
- 강남점, 홍대점, 신촌점

## 기본 사용자
| 역할 | 이메일 | 비밀번호 | 설명 |
|------|--------|----------|------|
| ADMIN | admin@lms.com | password123 | 관리자 |
| MANAGER | manager.gangnam@lms.com | password123 | 강남점 매니저 |
| EMPLOYEE | employee1.gangnam@lms.com | password123 | 강남점 직원 |

## 급여 정책
{코드에서 추출한 배율값}

## 규칙
- local에서만 자동 생성, 재시작 시 초기화, BCrypt 암호화
```

### 비기능 요구사항 정책 (policies/POLICY-NFR-001-비기능요구사항.md)

```markdown
# POLICY-NFR-001: 비기능 요구사항

## 기본 정보
- type: policy
- category: nfr
- owner: {팀명}
- last_updated: {날짜}

## 관련 상위 정책
{현재 없음. 향후 전사 NFR 정책 연결}

## 응답 시간
- 단건 조회 API: 200ms 이내 (p95)
- 목록 조회 API: 500ms 이내 (p95, 100건 기준)
- 생성/수정 API: 300ms 이내 (p95)

## 동시성
- 같은 리소스에 대한 동시 수정 요청 시 낙관적 락으로 충돌 감지
- 충돌 시 409 Conflict 반환

## 데이터 정합성
- 트랜잭션 실패 시 전체 롤백 (부분 변경 없음)
- 여러 Aggregate 변경이 필요한 경우 같은 트랜잭션으로 처리

## 보안
- 인증되지 않은 요청: 401 Unauthorized
- 권한 없는 요청: 403 Forbidden
- 타 매장 데이터 접근 불가 (매장 격리)
- 민감 정보(비밀번호 등) 로그 출력 금지

## 하위호환
- 기존 API 엔드포인트의 요청/응답 형식 변경 금지
- 필드 추가는 허용, 삭제/타입변경은 금지
- 하위호환을 깨야 할 경우 새 API 버전 생성 필수

## 적용 대상
- 모든 Use Case에 공통 적용
```

### 정책 (policies/ — 기능별)

```markdown
# POLICY-{카테고리}-{번호}: {정책명}

## 기본 정보
- type: policy
- category: {auth/attendance/schedule/leave/payroll}
- owner: {팀명}
- last_updated: {날짜}

## 관련 상위 정책
{현재 없음. 향후 전사 정책 연결 시 링크}

## 정책 규칙
- {규칙: 반드시 수치/조건 포함}

## 적용 대상
- {Use Case ID} ({Use Case 명})
```

### Use Case ({도메인}/)

```markdown
# {서비스}-{ID}: {Use Case 명}

## 기본 정보
- type: use_case
- domain: {도메인}
- service: {서비스}
- priority: {high/medium/low}

## 관련 정책
- {정책 ID} ({적용되는 구체적 규칙})
- POLICY-NFR-001 (비기능 요구사항: 공통 적용)

## 관련 Spec
- {Spec ID} ({Spec명})

## 관련 모델

### 주 모델 (Aggregate Root)
- **{모델명}**: {역할}
  - 사용하는 주요 필드: {필드 목록}
  - 상태 변경: {상태 전이}

### 참조 모델
- **{모델명}**: {참조 목적}
  - 참조하는 필드: {필드 목록}

## 개요
{한 문장 요약}

## 선행 조건
- {조건}

## 기본 흐름
{비즈니스 흐름만. 함수명/변수명 제외}
1. {단계}

## 대안 흐름
- {조건}: {처리}

## 예외 흐름
- {에러 조건}: {에러 처리}

## 검증 조건
{자동 테스트 가능한 명확한 형태}
- {조건: 비교 연산자 포함}

## 비즈니스 규칙
- {규칙}

## 비기능 요구사항
{POLICY-NFR-001 공통 규칙 외에 이 Use Case에 특화된 NFR}
{특화된 NFR이 없으면 "공통 NFR 정책(POLICY-NFR-001) 적용"으로 기술}

### 동시성
- {예: 같은 직원의 동시 출근 요청 시 1건만 성공}

### 데이터 정합성
- {예: 연차 차감과 휴가 생성은 같은 트랜잭션}

## 테스트 시나리오
{ID 형식: TC-{도메인약어}-{UseCase번호}-{시나리오번호}}
{테스트 레벨: Unit / Integration / E2E}
{AI 코드 생성 시 @Tag("TC-xxx")로 마킹}

### TC-{도메인}-{번호}-01: {정상 케이스} (Integration)
- Given: {사전 조건}
- When: {실행 행위}
- Then: {기대 결과}

### TC-{도메인}-{번호}-02: {대안 흐름 케이스} (Integration)
- Given: {사전 조건}
- When: {실행 행위}
- Then: {기대 결과}

### TC-{도메인}-{번호}-03: {권한 검증} (E2E)
- Given: {권한 없는 사용자}
- When: {API 호출}
- Then: {403 Forbidden}

### TC-{도메인}-{번호}-04: {예외 케이스} (Integration)
- Given: {예외 조건}
- When: {실행}
- Then: {에러, 상태 변경 없음}

### TC-{도메인}-{번호}-05: {도메인 규칙} (Unit)
- Given: {도메인 객체 상태}
- When: {도메인 메서드}
- Then: {검증 조건 충족}

### TC-{도메인}-{번호}-06: {동시성 검증} (Integration)
- Given: {동시 요청 조건}
- When: {동시에 동일 행위 요청}
- Then: {1건만 성공 또는 409 Conflict}

### TC-{도메인}-{번호}-07: {응답 시간 검증} (Integration)
- Given: {일반적인 데이터 상태}
- When: {API 호출}
- Then: {응답 시간 <= POLICY-NFR-001 기준}

## 관련 이벤트
- 발행: {이벤트} (향후)
- 수신: {이벤트} (향후)
```

### API Spec ({도메인}/)

```markdown
# {서비스}-API-{ID}: {API 그룹명}

## 기본 정보
- type: api_spec
- domain: {도메인}
- service: {서비스}
- base_path: {기본 경로}

## 관련 Spec
- {관련 Use Case ID}

## 인증/인가
- JWT Bearer Token
- {엔드포인트별 권한}

## 엔드포인트 목록

### {HTTP Method} {path}
- 설명: {기능}
- 권한: {역할}
- 요청: {필드, 검증}
- 응답 (200): {성공}
- 응답 (4xx): {실패}

## 공통 규칙
- 에러 응답: { code, message, details }
- 하위호환: POLICY-NFR-001 하위호환 규칙 적용
```

---

## 테스트 시나리오 작성 가이드

### 테스트 케이스 ID 규칙
- 형식: TC-{도메인약어}-{UseCase번호}-{시나리오번호}
- 도메인 약어: USER, EMP, STORE, SCH, ATT, LEAVE, PAY

### 테스트 레벨 판별 기준
- **Unit**: 도메인 모델 검증, Value Object 제약, 상태 전이
- **Integration**: Use Case 전체 흐름 (DB 포함), 트랜잭션, 동시성
- **E2E**: API 호출 → 응답 검증, 권한, 에러 형식, 응답 시간

### 시나리오 도출 방법
- 기본 흐름 정상 실행 → 정상 케이스 (Integration)
- 대안 흐름 각 분기 → 대안 케이스 (Integration)
- 예외 흐름 각 throw → 에러 케이스 (Integration)
- @PreAuthorize 역할 조합 → 권한 케이스 (E2E)
- Entity init/require → 도메인 규칙 (Unit)
- **비기능 요구사항 → 동시성/응답시간/정합성 케이스 (Integration/E2E)**
- DEMO_SCENARIOS.md 시나리오 → 통합/E2E 케이스

### AI 코드 생성 시 규칙
```kotlin
@Tag("TC-ATT-001-01")
@DisplayName("정상 출근 기록 생성")
@Test
fun `정상 출근 기록 생성`() {
    // Given: ...
    // When: ...
    // Then: ...
}
```

---

## 분석 시 주의사항

### 이 프로젝트의 특수 패턴
- **DomainContext**: 모든 도메인 메서드의 첫 번째 인자
- **Value Object**: @JvmInline value class, init 검증
- **JPA Entity ↔ Domain Model 분리**: Mapper 규칙은 architecture-rules.md

### 규칙의 명확성
- ❌ "적절한 형식" → ✅ 코드의 실제 정규식
- ❌ "일정 기간 내" → ✅ "30일 이내"
- ❌ "빠른 응답" → ✅ "200ms 이내 (p95)"
- ❌ "checkIn() 호출" → ✅ "출퇴근 기록을 생성한다"

### 기존 문서와 코드의 교차 검증
- DEMO_SCENARIOS.md에 있지만 코드에 없는 기능 → "## 알려진 미구현"
- 코드에 있지만 문서에 없는 기능 → Spec에 포함하되 표시
- PRD에 있지만 미구현 → "## 향후 구현 예정"

---

## 생성 후 검증

1. README의 모든 도메인 모델이 service-definition.md에 필드별로 기술되어 있는가
2. DEMO_SCENARIOS.md의 시나리오가 Use Case에 반영되어 있는가
3. 모든 Controller 엔드포인트가 API Spec에 포함되어 있는가
4. 모든 Use Case에 주 모델과 참조 모델이 명시되어 있는가
5. 검증 조건이 테스트 가능한 형태인가
6. **모든 Use Case에 최소 3개 이상 테스트 시나리오(정상/대안/예외)가 있는가**
7. **모든 테스트 시나리오에 TC-ID가 부여되고 레벨이 지정되어 있는가**
8. **비기능 요구사항 정책(POLICY-NFR-001)이 작성되어 있는가**
9. **Use Case에 특화된 NFR이 있으면 "## 비기능 요구사항" 섹션에 기술되어 있는가**
10. 정책 Spec이 코드의 실제 상수/규칙과 일치하는가
11. `python scripts/spec_lint.py docs/specs/` 실행 시 ERROR가 0개인가
