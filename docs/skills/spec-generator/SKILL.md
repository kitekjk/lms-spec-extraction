# Spec Generator Skill

## 목적
기존 소스코드와 문서를 분석하여 Harness Engineering 표준에 맞는 Spec 문서를 자동 생성한다.
생성된 Spec은 향후 소스코드를 제거하고 AI가 처음부터 재개발할 때의 입력이 된다.

## 사용법
```
프로젝트 루트에서:
  "이 프로젝트의 Spec 문서를 생성해줘"
  "docs/specs/ 디렉토리에 전체 Spec을 만들어줘"

특정 도메인만:
  "attendance 도메인의 Spec을 생성해줘"
  "스케줄 관리 API의 Spec을 만들어줘"
```

## 분석 순서

### 1단계: 기존 문서 먼저 읽기
코드를 분석하기 전에 기존 문서를 먼저 읽어 프로젝트의 전체 맥락을 파악한다.
읽는 순서:
1. **README.md** → 프로젝트 개요, 도메인 모델 목록, 설계 결정 사항
2. **docs/ARCHITECTURE.md** → 아키텍처 구조, 계층 간 의존성 규칙
3. **docs/DEMO_SCENARIOS.md** → 역할별 시나리오 → Use Case의 기본 흐름/대안 흐름 추출
4. **docs/LOCAL_MYSQL_SETUP.md** → DB 설정, 초기 데이터 구조
5. **.taskmaster/docs/prd.md** (있으면) → 원본 요구사항, 기능 목록
6. **.aiassistant/rules/guidelines.md** → 코드 작성 가이드라인 추출

이 문서들에서 추출한 정보가 Spec의 "개요", "비즈니스 규칙", "선행 조건"의 기반이 된다.

### 2단계: 프로젝트 구조 파악
이 프로젝트는 **멀티모듈 구조**이다. src/main/kotlin 하위가 아니라 루트 레벨에 모듈이 있다:
```
lms-demo/
├── domain/          # 도메인 레이어 (순수 Kotlin)
│   └── src/main/kotlin/com/lms/domain/
│       ├── model/       # Aggregate Root, Entity, Value Object
│       ├── service/     # Domain Service
│       ├── common/      # DomainContext 등
│       └── exception/   # 도메인 예외
├── application/     # 애플리케이션 레이어
│   └── src/main/kotlin/com/lms/application/
├── infrastructure/  # 인프라 레이어
│   └── src/main/kotlin/com/lms/infrastructure/
│       ├── persistence/ # JPA Entity, Mapper, Repository
│       ├── config/      # 설정
│       └── security/    # JWT, Security
├── interfaces/      # 프레젠테이션 레이어
│   └── src/main/kotlin/com/lms/interfaces/
│       └── web/         # REST Controller, DTO
└── build.gradle.kts # 루트 빌드 설정
```

파악 순서:
1. 루트 build.gradle.kts + settings.gradle.kts → 모듈 목록, 기술 스택
2. domain/src/.../model/ 하위 패키지 → 도메인(Aggregate) 목록 추출
3. infrastructure/.../config/ → DB, Security, 외부 연동 설정
4. interfaces/.../web/ → API 엔드포인트 확인

### 3단계: 도메인별 심층 분석
각 도메인(user, employee, store, schedule, attendance, leave, payroll 등) 대상으로:

1. **domain/model/{도메인}/** → Aggregate Root, Entity, Value Object, Enum
   - 모델 구조, 필드, 검증 규칙(init/require/check) 추출
   - Value Object의 제약 조건 추출 (예: Email 형식 검증)
   - Enum의 상태 목록과 전이 규칙 추출
   - DomainContext 사용 패턴 확인

2. **domain/service/** → Domain Service
   - 여러 Aggregate에 걸치는 비즈니스 로직 추출

3. **application/{도메인}/** → UseCase, Application Service
   - 유스케이스별 비즈니스 흐름 추출
   - 트랜잭션 경계, 이벤트 발행 패턴 추출
   - 에러 처리/예외 흐름 추출

4. **interfaces/web/{도메인}/** → Controller, DTO
   - API 엔드포인트, HTTP Method, 경로 추출
   - 요청/응답 DTO 구조 추출
   - @PreAuthorize → 권한 규칙 추출
   - @Valid → 요청 검증 규칙 추출

5. **infrastructure/persistence/{도메인}/** → JPA Entity, Repository
   - DB 스키마 구조 (컬럼, 관계) 추출
   - 커스텀 쿼리 → 조회 조건, 비즈니스 의미 추출
   - Mapper → 도메인 모델 ↔ JPA Entity 매핑 규칙 추출

6. **infrastructure/security/** → 인증/인가 규칙 추출

### 4단계: Spec 문서 생성
분석 결과를 아래 템플릿에 맞춰 docs/specs/ 에 생성한다.
**기존 문서(1단계)의 내용과 코드 분석(2~3단계) 결과를 교차 검증**하여 빠진 규칙이 없는지 확인한다.

---

## Spec 템플릿

### 서비스 정의 (프로젝트당 1개)

```markdown
# SERVICE-{ID}: {서비스명}

## 기본 정보
- type: service_definition
- domain: {도메인}
- owner: {팀명}
- tech_stack: {기술 스택}
- last_updated: {날짜}

## 서비스 목적과 범위
{README, ARCHITECTURE.md, PRD에서 추출한 프로젝트 목적}

## 핵심 모델
{domain/model/ 의 각 Aggregate를 분석하여 나열}
- **{모델명}**: {역할}. {주요 필드와 Value Object 요약}

## 내부 규칙
{Entity의 init/require/check, Enum 상태 전이, DomainContext 패턴 등}
- {규칙 1}

## 외부 계약
{다른 서비스와의 API 호출, 이벤트 발행/수신}
- **{연계 대상}**: {방식과 내용}

## 소유 데이터
{이 서비스의 truth owner 데이터 vs 조회만 하는 데이터}

## 아키텍처 규칙
{ARCHITECTURE.md에서 추출한 계층 간 의존성 규칙, 설계 원칙}
- domain 레이어는 외부 라이브러리 의존성 없음 (순수 Kotlin)
- 의존성 방향: domain ← application ← interfaces/infrastructure
- {기타 설계 결정 사항}
```

### Use Case (주요 기능당 1개)

```markdown
# {서비스}-{ID}: {Use Case 명}

## 기본 정보
- type: use_case
- domain: {도메인}
- service: {서비스}
- priority: {high/medium/low}

## 관련 정책
- {상위 정책/규칙 참조}

## 관련 Spec
- {관련된 다른 Spec 참조}

## 개요
{이 Use Case가 하는 일 한 문장 요약}

## 선행 조건
{DEMO_SCENARIOS.md와 코드에서 추출한 전제 조건}

## 기본 흐름
{Application Service/UseCase 코드의 로직을 단계별로 기술}
{DEMO_SCENARIOS.md의 시나리오가 있으면 교차 검증}
1. {단계 1}
2. {단계 2}

## 대안 흐름
{코드의 if/when 분기, 예외 처리에서 추출}
- {조건}: {처리 방식}

## 검증 조건
{Entity의 require/check, Service의 검증 로직에서 추출}
{반드시 자동 테스트 가능한 명확한 형태로}
- {조건: 비교 연산자 포함}

## 비즈니스 규칙
{하드코딩된 상수, 정책적 판단, DomainContext 관련 규칙}
- {규칙 1}

## 관련 이벤트
- 발행: {이벤트}
- 수신: {이벤트}
```

### API Spec (엔드포인트 그룹별)

```markdown
# {서비스}-API-{ID}: {API 그룹명}

## 기본 정보
- type: api_spec
- domain: {도메인}
- service: {서비스}
- base_path: {기본 경로}

## 관련 Spec
- {관련 Use Case Spec}

## 인증/인가
{Security 설정에서 추출한 인증 방식, 역할 기반 접근 제어}

## 엔드포인트 목록

### {HTTP Method} {path}
- 설명: {기능 설명}
- 권한: {@PreAuthorize에서 추출}
- 요청: {DTO 필드, @Valid 제약 조건}
- 응답: {응답 DTO 구조, 상태 코드별 설명}
- 검증: {요청 검증 규칙}

## 공통 규칙
{에러 응답 형식, 페이지네이션, API 버전 규칙 등}
```

### Boilerplate Spec (프로젝트 구조 재현용)

```markdown
# SPEC-REPO-{ID}: {프로젝트명} 프로젝트 구조

## 기본 정보
- type: boilerplate_spec
- domain: {도메인}

## 기술 스택
{build.gradle.kts에서 추출}

## 프로젝트 구조
{실제 멀티모듈 구조를 그대로 기술}

## 모듈별 의존성
{settings.gradle.kts, 각 모듈의 build.gradle.kts에서 추출}

## 설정 파일
{application.yml 주요 설정, 프로파일별 차이}

## 인프라 구성
{docker-compose.yml에서 추출: DB, 메시지 큐 등}

## 초기 데이터
{data.sql 또는 초기화 코드에서 추출: 기본 사용자, 매장, 정책 데이터}

## 검증 조건
- 멀티모듈 빌드가 성공하는가
- domain 모듈에 외부 프레임워크 의존성이 없는가
- 의존성 방향이 올바른가 (domain ← application ← interfaces/infrastructure)
- 헬스체크 엔드포인트가 동작하는가
```

---

## 분석 시 주의사항

### 이 프로젝트의 특수 패턴

**DomainContext 패턴**:
모든 도메인 메서드가 DomainContext를 첫 번째 인자로 받는다. Spec에 이 패턴을 명시해야 AI가 재개발 시 동일하게 구현한다.

**Value Object (inline class)**:
UserId, Email, Password 등이 @JvmInline value class로 정의되어 있다. 각 VO의 init 블록 검증 규칙을 빠짐없이 추출한다.

**멀티모듈 의존성**:
domain은 순수 Kotlin(Spring 의존성 없음), infrastructure가 JPA Entity와 Mapper를 포함한다. 이 분리 규칙을 Boilerplate Spec에 반드시 명시한다.

**JPA Entity ↔ Domain Model 매핑**:
infrastructure/persistence/{도메인}/mapper/ 에 Mapper가 있다. 이 매핑 규칙도 Spec에 포함해야 AI가 동일한 분리를 재현한다.

### 코드에서 규칙 추출하는 방법

**domain/model/ Entity에서**:
- `init { require(...) }` → 검증 조건
- `fun someMethod(context: DomainContext, ...)` → Use Case 흐름의 단계
- `companion object { fun create(...) }` → 생성 규칙
- Enum 클래스 → 상태 정의, 허용 전이

**application/ Service에서**:
- `@Transactional` → 트랜잭션 경계
- if/when 분기 → 비즈니스 규칙, 대안 흐름
- throw 문 → 예외 흐름
- 다른 Repository/Service 호출 → 의존 관계

**interfaces/web/ Controller에서**:
- `@RequestMapping` → API 경로
- `@PreAuthorize("hasRole('ADMIN')")` → 권한 규칙
- `@Valid` + DTO 필드 어노테이션 → 요청 검증

**infrastructure/ 에서**:
- JPA Entity → DB 스키마 (컬럼명, 타입, nullable)
- Mapper → 도메인 ↔ JPA 변환 규칙
- Repository → 커스텀 쿼리의 비즈니스 의미
- Security Config → 인증 방식, 경로별 접근 제어

### 규칙의 명확성 확보
- 코드의 실제 값을 사용: ❌ "적절한 형식" → ✅ "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
- 상수를 구체적으로: ❌ "일정 기간 내" → ✅ "30일 이내"
- 역할을 명시적으로: ❌ "권한 필요" → ✅ "ADMIN 또는 MANAGER 역할 보유"

### 기존 문서와 코드의 교차 검증
- DEMO_SCENARIOS.md에 있지만 코드에 없는 기능 → "## 알려진 미구현" 섹션에 기록
- 코드에 있지만 DEMO_SCENARIOS.md에 없는 기능 → Spec에 포함하되 표시
- PRD에 있지만 구현되지 않은 기능 → "## 향후 구현 예정" 섹션에 기록

---

## 출력 구조

```
docs/specs/
├── SERVICE-LMS-001-서비스정의.md
├── LMS-USER-001-로그인.md
├── LMS-USER-002-회원가입.md
├── LMS-EMPLOYEE-001-근로자등록.md
├── LMS-EMPLOYEE-002-근로자수정.md
├── LMS-STORE-001-매장관리.md
├── LMS-SCHEDULE-001-근무일정생성.md
├── LMS-SCHEDULE-002-근무일정변경.md
├── LMS-ATTENDANCE-001-출퇴근기록.md
├── LMS-ATTENDANCE-002-출퇴근수정.md
├── LMS-LEAVE-001-휴가신청.md
├── LMS-LEAVE-002-휴가승인.md
├── LMS-PAYROLL-001-급여산정.md
├── LMS-PAYROLL-002-급여정책관리.md
├── LMS-API-001-인증API.md
├── LMS-API-002-근로자API.md
├── LMS-API-003-매장API.md
├── LMS-API-004-스케줄API.md
├── LMS-API-005-출퇴근API.md
├── LMS-API-006-휴가API.md
├── LMS-API-007-급여API.md
└── SPEC-REPO-LMS-001-프로젝트구조.md
```

## 생성 후 검증

Spec 생성이 완료되면 다음을 확인한다:
1. README의 도메인 모델 목록(User, Employee, Store, WorkSchedule, AttendanceRecord, LeaveRequest, Payroll, PayrollPolicy)이 모두 Spec에 반영되었는가
2. DEMO_SCENARIOS.md의 시나리오가 Use Case Spec에 반영되었는가
3. 모든 Controller 엔드포인트가 API Spec에 포함되어 있는가
4. 검증 조건이 모호하지 않고 테스트 가능한 형태인가
5. DomainContext 패턴, Value Object 규칙이 명시되어 있는가
6. Boilerplate Spec에 멀티모듈 구조와 의존성 방향이 정확히 기술되어 있는가
7. `python scripts/spec_lint.py docs/specs/` 실행 시 ERROR가 0개인가

검증 실패 시 해당 Spec을 보완하고, 보완 내역을 사용자에게 보고한다.
