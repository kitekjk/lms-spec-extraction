# Spec Generator - 빠른 시작 가이드

## 이게 뭔가요?

기존 소스코드와 문서에서 Spec을 자동 생성하는 Claude Code 스킬입니다.
생성된 Spec은 Harness Engineering의 입력이 됩니다:
**소스코드 삭제 → Spec만 남김 → AI가 Spec 기반으로 재개발**

## 파일 구성

```
lms-spec-extraction/              (lms-demo 복사본)
├── CLAUDE.md                      ← 교체
├── docs/
│   ├── ARCHITECTURE.md            ← 기존 유지 (참조)
│   ├── DEMO_SCENARIOS.md          ← 기존 유지 (참조)
│   ├── LOCAL_MYSQL_SETUP.md       ← 기존 유지 (참조)
│   ├── skills/
│   │   └── spec-generator/
│   │       └── SKILL.md           ← 새로 추가
│   └── specs/                     ← Spec 생성 위치
│       ├── service-definition.md
│       ├── architecture-rules.md
│       ├── naming-guide.md
│       ├── infra-config.md
│       ├── init-data.md
│       ├── policies/              ← 기능 정책 + NFR 정책
│       └── {도메인}/               ← Use Case + API Spec
└── scripts/
    └── spec_lint.py               ← 새로 추가
```

## 설치

```bash
# 1. 복사본 생성
git clone https://github.com/kitekjk/lms-demo.git lms-spec-extraction
cd lms-spec-extraction

# 2. 기존 AI 관련 파일 정리
rm -rf .taskmaster .claude
# .aiassistant/rules/guideline.md는 유지 (참조용)

# 3. 새 파일 배치
cp (다운로드경로)/CLAUDE.md ./CLAUDE.md
mkdir -p docs/skills/spec-generator
cp (다운로드경로)/SKILL.md docs/skills/spec-generator/SKILL.md
mkdir -p scripts
cp (다운로드경로)/spec_lint.py scripts/spec_lint.py
mkdir -p docs/specs/policies
```

## 실행

```bash
cd lms-spec-extraction
claude
> 이 프로젝트의 Spec 문서를 생성해줘
```

## 검증

```bash
python scripts/spec_lint.py docs/specs/
```

## 생성되는 Spec

| 파일 | 내용 |
|------|------|
| service-definition.md | 서비스 정의, 핵심 모델(필드별 상세), 외부 계약 |
| architecture-rules.md | 레이어 책임, 의존성 방향, 도메인 모델 규칙 |
| naming-guide.md | 네이밍 컨벤션 (패키지/클래스/API/테스트) |
| infra-config.md | DB, Docker, 프로파일 |
| init-data.md | 초기 사용자, 매장, 정책 데이터 |
| policies/POLICY-NFR-001 | **비기능 요구사항 (응답시간, 동시성, 보안, 하위호환)** |
| policies/*.md | 인증, 출퇴근, 일정, 휴가, 급여 정책 |
| {도메인}/*.md | Use Case(테스트 시나리오+NFR 포함) + API Spec |

## 핵심 특징

### 테스트 시나리오 추적
Use Case Spec에 TC-ID가 부여되고, AI가 @Tag로 마킹합니다:
```kotlin
@Tag("TC-ATT-001-01")
@Test
fun `정상 출근 기록 생성`() { ... }
```

### 비기능 요구사항
공통 NFR 정책(POLICY-NFR-001)과 Use Case별 특화 NFR이 Spec에 포함됩니다.
동시성, 응답시간, 데이터 정합성, 하위호환 검증이 테스트 시나리오에 포함됩니다.

### 완전 자동화 Harness 워크플로우 (목표)
```
Spec 입력 → AI 코드 생성 → 자동 검증 ──실패→ AI 재시도
                              │
                           전체 통과
                              │
                           자동 머지/배포
```
사람 리뷰 없이, 자동 검증 게이트가 신뢰를 보장합니다:
- 변경 범위 검증 (대상 도메인 외 변경 감지)
- 기존 테스트 전체 통과 (regression 방지)
- 신규 TC-ID 테스트 전체 통과
- API 하위호환 검증
- NFR 검증 (응답시간, 동시성)

## Harness Engineering 시연 절차

1. **Spec 생성**: 기존 코드+문서 → Spec 자동 생성
2. **Spec 검증**: 린터 + 사람 리뷰/보완
3. **코드 제거**: 새 폴더에 docs/specs/ 만 복사
4. **AI 재개발**: "docs/specs/ 기반으로 이 프로젝트를 처음부터 개발해줘"
5. **테스트 검증**: TC-ID 매핑 + NFR 검증
6. **비교**: 원본 vs AI 재생성 코드
