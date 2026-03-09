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

Spec 생성은 **Agent Teams**로 병렬 수행한다.

### Team Lead (오케스트레이터)
- 전체 워크플로우 조율
- Teammate 간 결과물 교차 검증
- Backend ↔ Frontend Spec 참조 링크 정합성 확인
- 최종 린터 실행

### Teammate 1: 도메인 분석가
- **담당**: service-definition.md, architecture-rules.md, naming-guide.md
- **분석 대상**: domain/model/, README.md, docs/ARCHITECTURE.md
- **협업**: **정책/규칙 추출가(Teammate 3)와 긴밀히 협의** — 모델 검증 규칙과 정책 일치 여부 상호 검증

### Teammate 2: API/흐름 분석가
- **담당**: Use Case Spec, API Spec, **Frontend 화면 Spec**
- **분석 대상**: application/, interfaces/web/, docs/DEMO_SCENARIOS.md, 기존 Flutter 화면 구조
- **핵심 책임**: Use Case 흐름, API 엔드포인트, 화면 구성 요소별 Backend API 매핑

### Teammate 3: 정책/규칙 추출가
- **담당**: policies/, infra-config.md, init-data.md
- **분석 대상**: Entity init/require, Service 분기, Security Config, 상수값
- **협업**: **도메인 분석가(Teammate 1)와 긴밀히 협의**

### Teammate 4: 테스트 시나리오 작성가
- **담당**: 모든 테스트 시나리오 (Backend TC-ID + Frontend TC-FE-ID)
- **핵심 책임**:
  - 기존 테스트 코드에서 패턴 추출 + **엣지 케이스 추가 발굴**
  - **E2E 테스트에 데이터 시딩(Given) + 화면 조회 검증(Then) 포함**
  - NFR 테스트 (응답시간, 동시성)

### Teammate 간 협업 규칙
- 도메인 분석가 ↔ 정책 추출가: 모델↔정책 일치 여부 반복 검증
- API/흐름 분석가 → 테스트 작성가: Use Case + 화면 Spec 완성 후 테스트 작성
- 정책 추출가 → 테스트 작성가: 정책 경계값을 테스트 케이스로 변환
- Lead: Backend ↔ Frontend 참조 링크 + 화면 구성 요소별 API 매핑 최종 검증

### Spec 유형별 AI 전략

Spec 유형마다 AI 개입 수준이 다르다. 사람 주도 항목은 AI가 초안을 만들되 사람이 반드시 검증/수정한다.

| Spec 유형 | AI 전략 | 이유 |
|-----------|---------|------|
| 정책 (policies/) | **사람 주도** | 비즈니스 판단, 조직 규칙 결정 |
| 아키텍처 규칙 | **사람 주도** | 설계 의사결정, 장기 영향 |
| 서비스 정의, 핵심 모델 | **협업** (AI 초안 → 사람 검증) | 모델 구조는 AI 추출, 의미/판단은 사람 |
| Use Case 흐름 | **AI 주도** | 코드에서 기계적 추출 가능 |
| API Spec | **AI 주도** | Controller에서 기계적 추출 |
| 테스트 시나리오 | **AI 주도 + 사람 보강** | AI가 기존 변환, 사람이 엣지 케이스 추가 |
| Frontend 화면 Spec | **협업** | 기존 화면 추출 + UX 판단 |
| Frontend E2E | **AI 주도** | Given-When-Then 기계적 생성 |

### Teammate별 컨텍스트 범위

각 Teammate가 로드하는 파일 범위를 제한하여 컨텍스트 윈도우를 효율적으로 사용한다.

**Teammate 1 (도메인 분석가):**
- 읽기: domain/**, README.md, docs/ARCHITECTURE.md
- 읽지 않기: infrastructure/**, interfaces/**, src/test/**

**Teammate 2 (API/흐름 분석가):**
- 읽기: application/**, interfaces/**, docs/DEMO_SCENARIOS.md, lms_mobile_web/
- 읽지 않기: infrastructure/persistence/**, domain/model/** (모델 상세는 Teammate 1에게 확인)

**Teammate 3 (정책 추출가):**
- 읽기: domain/**/model/** (검증 로직만), infrastructure/config/**, infrastructure/security/**, 상수 파일
- 읽지 않기: application/**, interfaces/**

**Teammate 4 (테스트 작성가):**
- 읽기: src/test/**, 다른 Teammate가 생성한 Spec (완성 후)
- 읽지 않기: infrastructure/**

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
├── policies/
│   ├── POLICY-AUTH-001-인증인가.md
│   ├── POLICY-ATTENDANCE-001-출퇴근.md
│   ├── POLICY-SCHEDULE-001-근무일정.md
│   ├── POLICY-LEAVE-001-휴가.md
│   ├── POLICY-PAYROLL-001-급여.md
│   └── POLICY-NFR-001-비기능요구사항.md
├── user/
│   └── ...
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
├── frontend-definition.md
├── frontend-architecture.md
├── frontend-naming-guide.md
├── screens/
│   ├── LMS-SCREEN-001-로그인.md
│   ├── LMS-SCREEN-002-대시보드.md
│   ├── LMS-SCREEN-003-출퇴근.md
│   ├── LMS-SCREEN-004-스케줄.md
│   ├── LMS-SCREEN-005-휴가관리.md
│   └── LMS-SCREEN-006-급여조회.md
└── e2e/
    ├── LMS-E2E-001-로그인흐름.md
    ├── LMS-E2E-002-대시보드조회.md
    ├── LMS-E2E-003-출퇴근흐름.md
    ├── LMS-E2E-004-스케줄관리흐름.md
    └── LMS-E2E-005-휴가신청흐름.md
```

---

## Spec 템플릿 — Backend

(서비스 정의, 아키텍처 규칙, 네이밍 가이드, 인프라 설정, 초기 데이터, 정책, Use Case, API Spec 템플릿은 기존과 동일)

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
- state: Zustand + React Query
- test: Vitest + React Testing Library + agent-browser (E2E)

## Backend API 연동
- Backend repo: lms-backend
- API Base: /api/v1/
- 인증: JWT Bearer Token (POLICY-AUTH-001 참조)
- API Spec 참조: lms-backend/docs/specs/{도메인}/LMS-API-*.md

## 화면 목록
- 로그인: LMS-USER-001, LMS-API-USER-001
- 대시보드: LMS-ATTENDANCE-001, LMS-SCHEDULE-001, LMS-LEAVE-001
- 출퇴근: LMS-ATTENDANCE-001, LMS-API-ATTENDANCE-001
- 스케줄: LMS-SCHEDULE-001, LMS-API-SCHEDULE-001
- 휴가관리: LMS-LEAVE-001, LMS-API-LEAVE-001
- 급여조회: LMS-PAYROLL-001, LMS-API-PAYROLL-001
```

### 프론트엔드 아키텍처 규칙 (frontend-architecture.md)

```markdown
# Frontend 아키텍처 규칙

## 기본 정보
- type: frontend_architecture

## 디렉토리 규칙
- app/ → Next.js App Router 페이지
- components/ → 재사용 컴포넌트
- hooks/ → 커스텀 훅
- lib/ → API 클라이언트, 유틸리티
- types/ → TypeScript 타입 (Backend DTO와 일치)

## API 연동 규칙
- Backend API Spec의 요청/응답 타입을 TypeScript로 정의
- API 클라이언트는 lib/api/ 에 도메인별 분리
- 에러 처리는 Backend 형식({ code, message, details })에 맞춤

## 접근성 (필수 — E2E 테스트를 위해)
- 모든 인터랙티브 요소에 data-testid 속성
- semantic HTML (button, input, form, table)
- ARIA 라벨 필수
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
{한 문장 요약}

## 접근 권한
- {ADMIN / MANAGER / EMPLOYEE}

## 화면 구성 요소
{각 UI 요소가 어떤 Backend API에서 데이터를 받는지 반드시 매핑한다}
{빈 상태(데이터 없음)일 때의 표시도 정의한다}

### {구성 요소 1: 예: 금일 출근 현황 카드}
- 표시 데이터: {어떤 데이터를 어떤 형태로 표시하는지}
- Backend API: {HTTP Method} {path}
  - 참조 Spec: {LMS-API-xxx-ID}
  - 요청 파라미터: {예: ?date=today&storeId=xxx}
  - 응답 매핑: {API 응답의 어떤 필드가 UI의 어떤 부분에 매핑되는지}
- 빈 상태: {데이터 0건일 때 UI 표시. 예: "출근 기록이 없습니다"}
- 에러 상태: {API 실패 시 UI 표시}

### {구성 요소 2: 예: 금일 근무일정 목록}
- 표시 데이터: {직원명, 근무시간, 매장명}
- Backend API: {HTTP Method} {path}
  - 참조 Spec: {LMS-API-xxx-ID}
  - 응답 매핑: {필드 매핑}
- 빈 상태: {예: "등록된 일정이 없습니다"}
- 에러 상태: {예: "일정을 불러올 수 없습니다. 다시 시도해주세요."}

### {구성 요소 3: 예: 휴가 승인 대기 배지}
- 표시 데이터: {승인 대기 건수}
- Backend API: {HTTP Method} {path}
  - 참조 Spec: {LMS-API-xxx-ID}
- 권한: {MANAGER, ADMIN만 표시 — EMPLOYEE에게는 미표시}
- 빈 상태: {배지 미표시 (0건)}

## 사용자 흐름
1. {단계}
2. {단계}

## 검증 조건
- {폼 검증, UI 상태 검증}

## 비기능 요구사항
- 초기 로딩: 2초 이내
- 인터랙션 반응: 100ms 이내
- API 실패 시: 에러 메시지 표시 + 재시도 버튼
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
- {Backend API Spec ID}

## 테스트 데이터 준비 방법
{E2E 테스트 실행 전 Backend 데이터를 어떻게 준비하는지 기술}
- 방법 A: init-data.md 기본 데이터 활용 (local 프로파일)
- 방법 B: 테스트 전용 시딩 API 호출 (POST /api/v1/test/seed)
{각 시나리오의 Given에서 필요한 데이터 상태를 명시한다}

## 테스트 시나리오

### TC-FE-{번호}-01: {정상 조회 — 데이터 있음} (E2E)
- Given:
  - Backend 데이터:
    - {필요한 데이터 상태 명시}
    - {예: 강남점 직원 3명, 오늘 출근 2명, 미출근 1명}
    - {예: 근무일정 3건, 휴가 승인대기 1건}
  - {역할}로 로그인 완료
- When: {화면} 페이지 접속
- Then:
  - {구성 요소 1}: {기대되는 표시 내용}
    - {예: "2/3명 출근" 텍스트 표시}
  - {구성 요소 2}: {기대되는 표시 내용}
    - {예: 일정 3건 목록 표시, 각 항목에 직원명/시간 포함}
  - {구성 요소 3}: {기대되는 표시 내용}
    - {예: 승인 대기 배지 "1" 표시}

### TC-FE-{번호}-02: {빈 데이터 조회} (E2E)
- Given:
  - Backend 데이터:
    - {데이터가 없는 상태. 예: 직원 존재, 출퇴근/일정 없음}
  - {역할}로 로그인 완료
- When: {화면} 페이지 접속
- Then:
  - {구성 요소 1}: {빈 상태 메시지. 예: "출근 기록이 없습니다"}
  - {구성 요소 2}: {빈 상태 메시지. 예: "등록된 일정이 없습니다"}
  - {구성 요소 3}: {미표시}

### TC-FE-{번호}-03: {입력/행위 테스트} (E2E)
- Given:
  - Backend 데이터: {필요한 데이터}
  - {역할}로 로그인 완료
- When:
  - {입력란}에 {값} 입력
  - {버튼} 클릭
- Then:
  - {성공 메시지 또는 화면 전환}
  - {관련 데이터 갱신 확인}

### TC-FE-{번호}-04: {권한별 화면 차이} (E2E)
- Given:
  - Backend 데이터: {동일 데이터}
  - {EMPLOYEE}로 로그인
- When: {화면} 페이지 접속
- Then:
  - {MANAGER 전용 요소}: 미표시
  - {EMPLOYEE 전용 요소}: 표시

### TC-FE-{번호}-05: {API 에러 시 화면 동작} (E2E)
- Given:
  - Backend API 응답: {500 또는 타임아웃}
- When: {화면} 페이지 접속
- Then:
  - 에러 메시지 표시: {예: "데이터를 불러올 수 없습니다"}
  - 재시도 버튼 표시

## agent-browser 실행 예시
```bash
# 데이터 시딩 (테스트 전용)
curl -X POST http://localhost:8080/api/v1/test/seed -d '{"scenario": "dashboard-with-data"}'

# 로그인
agent-browser open http://localhost:3000/login
agent-browser snapshot -i
agent-browser fill @email "manager.gangnam@lms.com"
agent-browser fill @password "password123"
agent-browser click @login-button
agent-browser wait --url "**/dashboard"

# 대시보드 조회 검증
agent-browser snapshot -i
agent-browser get text [data-testid="attendance-summary"]
# 기대: "2/3명 출근"
agent-browser get text [data-testid="schedule-count"]
# 기대: "3건"
agent-browser is visible [data-testid="leave-pending-badge"]
# 기대: true
```
```

---

## 테스트 시나리오 작성 가이드

### TC-ID 규칙
- Backend: TC-{도메인약어}-{UseCase번호}-{시나리오번호}
- Frontend E2E: TC-FE-{흐름번호}-{시나리오번호}

### 테스트 레벨
- Unit: 도메인 모델, Value Object, 상태 전이
- Integration: Use Case 흐름 (DB 포함), 동시성
- E2E (Backend): API 호출 → 응답 검증, 권한
- **E2E (Frontend)**: agent-browser 브라우저 테스트 — **조회 검증 + 입력 검증 + 에러 검증**

### E2E 시나리오 필수 포함 항목
모든 화면의 E2E 테스트에는 최소 다음 5가지를 포함한다:
1. **데이터 있는 상태에서 조회 검증** — 각 구성 요소에 기대 데이터가 올바르게 표시되는지
2. **빈 데이터 상태에서 조회 검증** — 빈 상태 메시지가 올바르게 표시되는지
3. **입력/행위 테스트** — 폼 입력, 버튼 클릭 후 기대 동작
4. **권한별 화면 차이** — 역할에 따라 보이는 요소가 다른지
5. **에러 상태 검증** — API 실패 시 에러 메시지와 재시도 동작

### 엣지 케이스 발굴 (Teammate 4)
- 경계값: 최소/최대값, 빈 문자열, 0, 음수
- 동시성: 같은 리소스 동시 요청
- 권한 조합: ADMIN/MANAGER/EMPLOYEE × 각 화면/API
- 상태 전이 불가: 이미 완료된 것을 재변경
- 타 매장 접근: 매장 격리 위반
- 대량 데이터: 목록 100건, 1000건 시 UI 동작
- 네트워크 오류: API 타임아웃 시 UI 동작

### AI 코드 생성 시 규칙
- Backend: `@Tag("TC-ATT-001-01")` 마킹
- Frontend: `test('TC-FE-001-01: 정상 로그인', ...)` 또는 agent-browser 스크립트에 TC-ID 주석

---

## 분석 순서

### 1단계: 기존 문서 읽기
1. README.md
2. docs/ARCHITECTURE.md
3. docs/DEMO_SCENARIOS.md → Use Case + 테스트 시나리오
4. docs/LOCAL_MYSQL_SETUP.md
5. .aiassistant/rules/guideline.md
6. .taskmaster/docs/prd.md (있으면)

### 2단계: 프로젝트 구조 파악
1. settings.gradle.kts → 모듈 목록
2. build.gradle.kts → 기술 스택
3. domain/src/.../model/ → 도메인 목록
4. interfaces/.../web/ → API 엔드포인트
5. lms_mobile_web/ → **기존 화면 구조, 각 화면에서 호출하는 API 파악**

### 3단계: 도메인별 심층 분석
(domain, application, interfaces, infrastructure, security, 기존 테스트)
+ **Frontend 화면 분석**: 각 화면의 구성 요소와 해당 요소가 호출하는 API 매핑

### 4단계: Agent Teams로 Spec 생성

---

## 생성 후 검증 — 2단계 품질 게이트

Spec 생성 완료 후 **2단계 검증**을 수행한다. 기준 미달이면 Lead가 해당 Teammate에게 재생성을 지시한다.

### Step 1: 구조 검증 (린터 — Pass/Fail)
`python scripts/spec_lint.py docs/specs/`

린터는 **구조적 존재 여부**만 검사한다. 있다/없다의 이진 판정:
- 필수 섹션 존재 여부
- 참조 ID 유효성
- TC-ID 형식 및 최소 개수
- 화면-API 매핑 존재 여부
- Given-When-Then 완전성

**ERROR가 1개라도 있으면 FAIL → 해당 파일 재생성 후 재검사**
WARNING은 Step 2에서 AI가 판단한다.

### Step 2: 결정성 평가 (AI 평가 — 수치화)

린터를 통과한 Spec에 대해 **Lead가 AI로 내용 품질을 평가**한다.
핵심 질문: **"이 Spec만으로 코드를 추측 없이 생성할 수 있는가?"**

Lead는 각 Spec을 읽고 다음 5개 항목을 100점 만점으로 평가한다:

#### 평가 항목

**① 구조 완결성 (20점)**
- 모든 섹션이 실질적 내용을 담고 있는가 (빈 섹션이 아닌가)
- 모델 필드가 타입/제약조건과 함께 기술되어 있는가
- 감점 예: "향후 정의 예정" 같은 미완 표시 -5점/건

**② 모호성 (25점)**
- "적절히 처리", "필요한 경우", "상황에 따라" 같은 모호한 표현이 있는가
- AI가 이 Spec을 읽고 2가지 이상 해석이 가능한 문장이 있는가
- 감점: 모호한 표현 1건당 -5점
- 감점 예: "적절히 에러 처리한다" → 구체적 에러 코드/메시지 필요

**③ 분기 커버리지 (25점)**
- 조건 분기가 명시되었는데 일부 경로의 결과가 정의되지 않은 경우
- if A then X — else는? 가 빠져있는가
- 상태 전이에서 허용되지 않는 전이 시도의 결과가 정의되었는가
- 감점: 미정의 분기 1건당 -5점
- 감점 예: "할인율이 적용된다" → 할인율이 0인 경우? 음수인 경우? 100% 초과인 경우?

**④ 참조 완결성 (15점)**
- 참조된 상위 정책/규칙이 실제로 해당 내용을 포함하는가
- Use Case에서 참조한 모델 필드가 서비스 정의에 존재하는가
- Frontend API 호출이 Backend API Spec에 존재하는가
- 감점: 참조 불일치 1건당 -5점

**⑤ 테스트 도출 가능성 (15점)**
- 각 검증 조건/비즈니스 규칙에서 Given-When-Then을 도출할 수 있는가
- 테스트 시나리오의 Given이 재현 가능한 상태인가 (데이터 시딩 포함)
- Then의 기대 결과가 검증 가능한 형태인가 (구체적 값, 상태, 메시지)
- 감점: 도출 불가능한 규칙 1건당 -3점

#### 통과 기준
- **파일별 80점 이상**
- **전체 평균 80점 이상**
- 어느 항목이든 **개별 항목 50% 미만이면 FAIL** (예: 모호성 12/25 이하)

#### 평가 결과 출력 예시

```
📊 Spec 결정성 평가 리포트
============================================================
파일: LMS-ATT-001-출퇴근기록.md

  ① 구조 완결성:      18/20  (NFR 섹션 수치 기준 1개 누락)
  ② 모호성:           20/25  ("적절히 처리" 1건 발견)
  ③ 분기 커버리지:     15/25  (퇴근 없이 다음날 출근 시 미정의)
  ④ 참조 완결성:      15/15
  ⑤ 테스트 도출 가능성: 13/15  (TC-ATT-001-04 Given 데이터 불충분)

  종합: 81/100  ✅ PASS

  개선 권고:
  - line 34: "적절히 에러를 반환한다" → 에러 코드/메시지 명시 필요
  - 분기 누락: 퇴근 기록 없이 다음날 출근하는 경우의 처리 정의 필요
  - TC-ATT-001-04: Given에 "타 매장 직원" 데이터 시딩 방법 명시 필요
============================================================

파일: LMS-SCREEN-002-대시보드.md

  ① 구조 완결성:      20/20
  ② 모호성:           15/25  ("적절한 형태로 표시" 2건)
  ③ 분기 커버리지:     20/25  (권한별 미표시 요소 1건 미정의)
  ④ 참조 완결성:      15/15
  ⑤ 테스트 도출 가능성: 12/15

  종합: 82/100  ✅ PASS

  개선 권고:
  - line 18: "적절한 형태로 표시" → 구체적 포맷 명시 (예: "N/M명 출근")
  - line 25: "적절한 시간 형식" → "HH:mm" 명시
  - EMPLOYEE 역할일 때 급여 카드 표시 여부 미정의
============================================================

📊 전체 요약
파일                              점수    상태
------------------------------------------------------------
service-definition.md              92    ✅ PASS
architecture-rules.md              88    ✅ PASS
POLICY-AUTH-001.md                  90    ✅ PASS
POLICY-NFR-001.md                  85    ✅ PASS
LMS-ATT-001-출퇴근기록.md           81    ✅ PASS
LMS-API-ATT-001.md                 87    ✅ PASS
LMS-SCREEN-002-대시보드.md          82    ✅ PASS
LMS-E2E-002-대시보드조회.md          84    ✅ PASS
------------------------------------------------------------
전체 평균: 86.1점  ✅ PASS (기준: 80점)
테스트 케이스: Backend 24개, Frontend E2E 12개, 총 36개
```

#### 미달 시 재생성 루프

```
Spec 생성
  │
  ▼
Step 1: 린터 (Pass/Fail) ──FAIL→ 해당 파일 재생성
  │
  PASS
  │
  ▼
Step 2: AI 결정성 평가 ──80점 미달→ 개선 권고와 함께 해당 파일 재생성
  │                              (최대 3회 재시도)
  │                              3회 후에도 미달 시 사람 개입 요청
  80점 이상
  │
  ▼
Spec 확정
```

#### Lead의 평가 프롬프트

Lead는 Step 2 수행 시 각 Spec에 대해 다음 프롬프트를 사용한다:

```
이 Spec을 읽고 다음 5가지 항목을 평가해주세요.
핵심 질문: "이 Spec만으로 코드를 추측 없이 생성할 수 있는가?"

① 구조 완결성 (20점): 모든 섹션에 실질적 내용이 있는가
② 모호성 (25점): 2가지 이상 해석 가능한 표현이 있는가
③ 분기 커버리지 (25점): 모든 조건 분기의 결과가 정의되어 있는가
④ 참조 완결성 (15점): 참조된 문서가 실제로 해당 내용을 포함하는가
⑤ 테스트 도출 가능성 (15점): 각 규칙에서 Given-When-Then을 도출할 수 있는가

각 항목별 점수, 감점 사유, 구체적 개선 권고를 제시해주세요.
개선 권고에는 해당 라인 번호와 수정 방향을 포함해주세요.
```
