# Spec Generator Skill

## 목적
기존 소스코드와 문서를 분석하여 Harness Engineering 표준에 맞는 Spec 문서를 자동 생성한다.
**Backend와 Frontend를 별도 repo로 분리**하여 Spec을 생성하며, Frontend Spec은 Backend의 Use Case/API Spec을 참조한다.

## 사용법
```
"이 프로젝트의 Spec을 생성해줘"           # Agent Teams로 전체 생성
"backend Spec만 생성해줘"                 # 백엔드만
"frontend Spec만 생성해줘"                # 프론트엔드만
"attendance 도메인의 Spec을 생성해줘"      # 특정 도메인
```

---

## Agent Teams 구성

Spec 생성은 **Agent Teams**로 병렬 수행한다. Lead가 조율하고 4개 Teammate가 각자 영역을 담당한다.

### Team Lead (오케스트레이터)
- 전체 Spec 생성 워크플로우 조율
- Teammate 간 결과물 교차 검증
- Backend ↔ Frontend Spec 간 참조 링크 정합성 확인
- 최종 린터 실행 및 결과 보고

### Teammate 1: 도메인 분석가
- **담당**: service-definition.md, architecture-rules.md, naming-guide.md
- **분석 대상**: domain/model/, README.md, docs/ARCHITECTURE.md
- **핵심 책임**: 도메인 모델(필드별 상세), 아키텍처 규칙, 네이밍 가이드
- **협업**: **정책/규칙 추출가(Teammate 3)와 긴밀히 협의** — 도메인 모델의 검증 규칙이 정책과 일치하는지, 비즈니스 규칙이 빠짐없이 정책에 반영되었는지 상호 검증

### Teammate 2: API/흐름 분석가
- **담당**: Use Case Spec, API Spec (Backend + Frontend)
- **분석 대상**: application/, interfaces/web/, 기존 docs/DEMO_SCENARIOS.md
- **핵심 책임**: Use Case 흐름(함수명 제외), API 엔드포인트, 주 모델/참조 모델
- **추가 책임**: Frontend Spec 생성 — 화면 흐름, 컴포넌트, Backend API 연동
- **협업**: 도메인 분석가에게 모델 상세 확인, 정책 추출가에게 비즈니스 규칙 확인

### Teammate 3: 정책/규칙 추출가
- **담당**: policies/ 디렉토리 전체 (기능 정책 + NFR)
- **분석 대상**: Entity init/require, Service 분기 로직, Security Config, 상수값
- **핵심 책임**: 코드의 실제 규칙을 정책 Spec으로 추출. 모호한 표현 없이 구체적 수치로
- **협업**: **도메인 분석가(Teammate 1)와 긴밀히 협의** — 모델의 검증 규칙이 정책에 정확히 반영되었는지, 정책에는 있지만 코드에 구현되지 않은 규칙이 있는지 상호 검증
- **추가 담당**: infra-config.md, init-data.md

### Teammate 4: 테스트 시나리오 작성가
- **담당**: 모든 Use Case의 "## 테스트 시나리오" 섹션 + Frontend 테스트 시나리오
- **분석 대상**: 기존 테스트 코드(src/test/), Use Case Spec, 정책 Spec
- **핵심 책임**:
  - 기존 테스트 코드에서 Given-When-Then 패턴 추출
  - **기존에 없는 예외/엣지 케이스를 추가 발굴** (경계값, 동시성, 권한 조합 등)
  - TC-ID 부여, 테스트 레벨(Unit/Integration/E2E) 지정
  - NFR 테스트 시나리오 (응답시간, 동시성, 정합성) 추가
  - **Frontend E2E 테스트 시나리오** (agent-browser 기반)
- **협업**: API/흐름 분석가에게 대안/예외 흐름 확인, 정책 추출가에게 규칙 경계값 확인

### Teammate 간 협업 규칙
- **도메인 분석가 ↔ 정책 추출가**: 가장 빈번한 소통. 모델 규칙과 정책의 일치 여부를 반복 검증
- **API/흐름 분석가 → 테스트 시나리오 작성가**: Use Case 완성 후 테스트 시나리오 작성 시작
- **정책 추출가 → 테스트 시나리오 작성가**: 정책의 경계값을 테스트 케이스로 변환
- **Lead**: 모든 Spec 완성 후 Backend ↔ Frontend 참조 링크 정합성 최종 확인

---

## 출력 디렉토리 구조

### Backend Repo (lms-backend/)
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
│   └── ...
├── store/
│   └── ...
├── schedule/
│   └── ...
├── attendance/
│   └── ...
├── leave/
│   └── ...
└── payroll/
    └── ...
```

### Frontend Repo (lms-frontend/)
```
docs/specs/
├── frontend-definition.md              # 프론트엔드 서비스 정의
├── frontend-architecture.md            # React/Next.js 아키텍처 규칙
├── frontend-naming-guide.md            # 컴포넌트/페이지/훅 네이밍
│
├── screens/                            # 화면 Spec
│   ├── LMS-SCREEN-001-로그인.md
│   ├── LMS-SCREEN-002-대시보드.md
│   ├── LMS-SCREEN-003-출퇴근.md
│   ├── LMS-SCREEN-004-스케줄.md
│   ├── LMS-SCREEN-005-휴가관리.md
│   └── LMS-SCREEN-006-급여조회.md
│
└── e2e/                                # E2E 테스트 시나리오 (agent-browser용)
    ├── LMS-E2E-001-로그인흐름.md
    ├── LMS-E2E-002-출퇴근흐름.md
    ├── LMS-E2E-003-스케줄관리흐름.md
    └── LMS-E2E-004-휴가신청흐름.md
```

---

## Spec 템플릿 — Backend

(기존과 동일: service-definition, architecture-rules, naming-guide, infra-config, init-data, policies, Use Case, API Spec)

### Use Case 템플릿 (변경 없음, 핵심 재확인)

Use Case에는 반드시 다음이 포함된다:
- **관련 모델**: 주 모델(Aggregate Root) + 참조 모델
- **비기능 요구사항**: POLICY-NFR-001 참조 또는 특화 NFR
- **테스트 시나리오**: TC-ID, Given-When-Then, 테스트 레벨(Unit/Integration/E2E)
  - 최소 3개 (정상/대안/예외)
  - 기존 테스트 코드에 없는 엣지 케이스도 추가 발굴

---

## Spec 템플릿 — Frontend

### 프론트엔드 서비스 정의 (frontend-definition.md)

```markdown
# LMS Frontend - 서비스 정의

## 기본 정보
- type: frontend_definition
- framework: React / Next.js (App Router)
- language: TypeScript
- styling: Tailwind CSS
- state: Zustand 또는 React Query
- test: Vitest + React Testing Library + agent-browser (E2E)

## 서비스 목적
LMS Backend API를 소비하여 매장 직원에게 출퇴근, 스케줄, 휴가, 급여 관련 UI를 제공한다.

## Backend API 연동
- Backend repo: lms-backend
- API Base URL: /api/v1/
- 인증: JWT Bearer Token (Backend POLICY-AUTH-001 참조)
- API Spec 참조: lms-backend/docs/specs/{도메인}/LMS-API-*.md

## 화면 목록
{각 화면과 연결된 Backend Use Case 명시}
- 로그인: LMS-USER-001, LMS-API-USER-001
- 대시보드: LMS-ATTENDANCE-001, LMS-SCHEDULE-001
- 출퇴근: LMS-ATTENDANCE-001, LMS-ATTENDANCE-002, LMS-API-ATTENDANCE-001
- ...
```

### 프론트엔드 아키텍처 규칙 (frontend-architecture.md)

```markdown
# Frontend 아키텍처 규칙

## 기본 정보
- type: frontend_architecture

## 디렉토리 규칙
- app/ → Next.js App Router 페이지
- components/ → 재사용 컴포넌트
- hooks/ → 커스텀 훅 (API 호출, 상태 관리)
- lib/ → API 클라이언트, 유틸리티
- types/ → TypeScript 타입 정의 (Backend DTO와 일치)

## 상태 관리 규칙
- 서버 상태: React Query (Backend API 캐싱)
- 클라이언트 상태: Zustand (UI 상태)
- 폼 상태: React Hook Form + Zod 검증

## API 연동 규칙
- Backend API Spec(LMS-API-*.md)에 정의된 요청/응답 타입을 TypeScript로 정의
- API 클라이언트는 lib/api/ 에 도메인별로 분리
- 에러 처리는 Backend 에러 응답 형식({ code, message, details })에 맞춤

## 접근성
- 모든 인터랙티브 요소에 ARIA 라벨 필수 (agent-browser 테스트를 위해)
- semantic HTML 사용 (button, input, form 등)
- data-testid 속성 추가 (E2E 테스트 안정성)
```

### 화면 Spec (screens/)

```markdown
# LMS-SCREEN-{번호}: {화면명}

## 기본 정보
- type: screen_spec
- route: {Next.js 라우트 경로}

## 관련 Backend Spec
- {Backend Use Case ID} ({Use Case 명})
- {Backend API Spec ID} ({API 명})

## 화면 목적
{이 화면이 사용자에게 제공하는 기능 한 문장}

## 접근 권한
{어떤 역할이 이 화면에 접근 가능한지}
- {ADMIN / MANAGER / EMPLOYEE}

## 화면 구성 요소
{주요 UI 요소. 컴포넌트명은 제외, 기능 관점으로 기술}
- {요소 1}: {역할, 표시 데이터}
- {요소 2}: {역할, 사용자 인터랙션}

## 사용자 흐름
{이 화면에서 사용자가 수행하는 주요 흐름}
1. {단계}
2. {단계}

## API 호출
{이 화면에서 호출하는 Backend API 목록}
- {HTTP Method} {path}: {목적}

## 상태 관리
{이 화면에서 관리하는 상태}
- 서버 상태: {React Query로 캐싱하는 데이터}
- 클라이언트 상태: {UI 상태 - 모달, 필터 등}

## 검증 조건
{폼 입력 검증, UI 상태 검증}
- {조건}

## 비기능 요구사항
- 초기 로딩: 2초 이내
- 인터랙션 반응: 100ms 이내
- 오프라인 시: 적절한 에러 메시지 표시
```

### Frontend E2E 테스트 시나리오 (e2e/)

```markdown
# LMS-E2E-{번호}: {E2E 흐름명}

## 기본 정보
- type: e2e_test_spec
- tool: agent-browser
- 관련 화면: LMS-SCREEN-{번호}

## 관련 Backend Spec
- {Backend Use Case ID}

## 테스트 시나리오
{agent-browser 명령으로 변환 가능한 형태로 기술}
{ID 형식: TC-FE-{흐름번호}-{시나리오번호}}

### TC-FE-001-01: 정상 로그인 (E2E)
- Given: 로그인 페이지 열림
- When:
  - 이메일 입력란에 "admin@lms.com" 입력
  - 비밀번호 입력란에 "password123" 입력
  - 로그인 버튼 클릭
- Then:
  - 대시보드 페이지로 이동
  - 환영 메시지 표시

### TC-FE-001-02: 잘못된 비밀번호 (E2E)
- Given: 로그인 페이지 열림
- When:
  - 이메일 입력란에 "admin@lms.com" 입력
  - 비밀번호 입력란에 "wrong" 입력
  - 로그인 버튼 클릭
- Then:
  - 에러 메시지 "이메일 또는 비밀번호가 올바르지 않습니다" 표시
  - 로그인 페이지 유지

### TC-FE-001-03: 이메일 미입력 (E2E)
- Given: 로그인 페이지 열림
- When:
  - 비밀번호만 입력
  - 로그인 버튼 클릭
- Then:
  - 이메일 필드에 검증 에러 표시

## agent-browser 실행 예시
{AI가 테스트 코드 생성 시 참고할 agent-browser 명령 패턴}
```bash
agent-browser open http://localhost:3000/login
agent-browser snapshot -i
agent-browser fill @email "admin@lms.com"
agent-browser fill @password "password123"
agent-browser click @login-button
agent-browser wait --url "**/dashboard"
agent-browser snapshot -i
# 대시보드 요소 확인
```
```

---

## 테스트 시나리오 작성 가이드

### TC-ID 규칙
- Backend: TC-{도메인약어}-{UseCase번호}-{시나리오번호} (예: TC-ATT-001-01)
- Frontend E2E: TC-FE-{흐름번호}-{시나리오번호} (예: TC-FE-001-01)
- 도메인 약어: USER, EMP, STORE, SCH, ATT, LEAVE, PAY

### 테스트 레벨
- **Unit**: 도메인 모델 검증, Value Object, 상태 전이
- **Integration**: Use Case 흐름 (DB 포함), 트랜잭션, 동시성
- **E2E (Backend)**: API 호출 → 응답 검증, 권한, 에러 형식
- **E2E (Frontend)**: agent-browser로 브라우저 테스트 — 화면 렌더링, 폼 입력, 페이지 전환

### 엣지 케이스 발굴 (Teammate 4 핵심 책임)
기존 테스트에 없는 케이스를 적극 추가한다:
- **경계값**: 최소/최대값, 빈 문자열, 0, 음수
- **동시성**: 같은 리소스에 대한 동시 요청
- **권한 조합**: 각 역할(ADMIN/MANAGER/EMPLOYEE) × 각 API
- **상태 전이 불가**: 이미 완료된 것을 다시 변경 시도
- **타 매장 데이터 접근**: 매장 격리 규칙 위반 시도
- **대량 데이터**: 목록 조회 시 100건, 1000건
- **네트워크 오류**: Frontend에서 API 타임아웃/실패 시 UI 동작

### AI 코드 생성 시 규칙
- Backend: `@Tag("TC-ATT-001-01")` 마킹
- Frontend: `test('TC-FE-001-01: 정상 로그인', ...)` 또는 agent-browser 스크립트에 TC-ID 주석

---

## 분석 순서

### 1단계: 기존 문서 읽기
1. README.md
2. docs/ARCHITECTURE.md
3. docs/DEMO_SCENARIOS.md → Use Case 흐름 + 테스트 시나리오 추출
4. docs/LOCAL_MYSQL_SETUP.md
5. .aiassistant/rules/guideline.md → naming-guide에 반영
6. .taskmaster/docs/prd.md (있으면)

### 2단계: 프로젝트 구조 파악 (멀티모듈)
1. settings.gradle.kts → 모듈 목록
2. build.gradle.kts → 기술 스택, 의존성
3. domain/src/.../model/ → 도메인 목록
4. interfaces/.../web/ → API 엔드포인트
5. lms_mobile_web/ → 기존 Frontend 화면/라우트 파악

### 3단계: 도메인별 심층 분석
(기존과 동일: domain/model, application, interfaces, infrastructure, security, 기존 테스트 코드)
+ **Frontend 화면 분석**: lms_mobile_web/의 라우트, 화면 구성, API 호출 패턴

### 4단계: Agent Teams로 Spec 생성
Lead가 Teammate 1~4에게 병렬 작업 할당, 결과물 교차 검증

---

## 생성 후 검증

### Backend Spec
1. 모든 도메인 모델이 필드별로 기술되어 있는가
2. 모든 Use Case에 주 모델/참조 모델이 있는가
3. 모든 Controller 엔드포인트가 API Spec에 있는가
4. 모든 Use Case에 테스트 시나리오 3개 이상 + TC-ID + 레벨 지정
5. NFR 정책(POLICY-NFR-001)이 있고 Use Case에 참조되어 있는가
6. `python scripts/spec_lint.py docs/specs/` ERROR 0개

### Frontend Spec
7. 모든 화면이 Backend Use Case/API Spec과 연결되어 있는가
8. 모든 화면 Spec에 API 호출 목록이 있는가
9. E2E 테스트 시나리오가 agent-browser 명령으로 변환 가능한 형태인가
10. Frontend E2E 테스트에 TC-FE-ID가 부여되어 있는가

### 교차 검증
11. Backend API Spec에 있는 엔드포인트가 Frontend 화면의 API 호출과 일치하는가
12. Backend 에러 응답이 Frontend 화면의 에러 처리와 일치하는가
