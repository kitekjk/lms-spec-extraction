# Spec Generator - 빠른 시작 가이드

## 이게 뭔가요?

기존 LMS 소스코드에서 Backend/Frontend Spec을 자동 생성하는 Claude Code 스킬입니다.
Agent Teams로 병렬 생성하며, 생성된 Spec은 Harness Engineering의 입력이 됩니다.

## 핵심 구조: 2개 Repo

```
lms-backend/                          # Backend (Spring Boot + Kotlin)
├── CLAUDE.md                          ← CLAUDE.md (Backend용)
├── docs/
│   ├── skills/spec-generator/SKILL.md ← 스킬 파일 (공통)
│   └── specs/                         ← Backend Spec
│       ├── service-definition.md
│       ├── architecture-rules.md
│       ├── policies/
│       └── {도메인}/                   ← Use Case + API Spec
└── scripts/spec_lint.py

lms-frontend/                          # Frontend (React + Next.js)
├── CLAUDE.md                          ← CLAUDE-FRONTEND.md → CLAUDE.md로 이름 변경
├── docs/
│   └── specs/
│       ├── frontend-definition.md
│       ├── frontend-architecture.md
│       ├── screens/                   ← 화면 Spec
│       └── e2e/                       ← agent-browser E2E 테스트 시나리오
└── scripts/spec_lint.py
```

## Agent Teams 구성

| Teammate | 담당 | 핵심 협업 |
|----------|------|----------|
| Lead | 전체 조율, 교차 검증 | BE↔FE 참조 정합성 |
| 도메인 분석가 | 서비스정의, 아키텍처, 네이밍 | ↔ 정책 추출가 (모델↔규칙 일치) |
| API/흐름 분석가 | Use Case, API Spec, 화면 Spec | ↔ 테스트 작성가 |
| 정책/규칙 추출가 | policies/, infra, init-data | ↔ 도메인 분석가 (규칙 교차 검증) |
| 테스트 시나리오 작성가 | TC-ID, 엣지 케이스, FE E2E | ↔ 정책 추출가 (경계값) |

## 설치 & 실행

```bash
# 1. 복사본 생성
git clone https://github.com/kitekjk/lms-demo.git lms-spec-extraction
cd lms-spec-extraction

# 2. 정리
rm -rf .taskmaster .claude

# 3. Backend 파일 배치
cp CLAUDE.md ./CLAUDE.md
mkdir -p docs/skills/spec-generator scripts docs/specs/policies
cp SKILL.md docs/skills/spec-generator/
cp spec_lint.py scripts/

# 4. Spec 생성 (Agent Teams)
claude
> 이 프로젝트의 Spec을 생성해줘

# 5. 검증
python scripts/spec_lint.py docs/specs/
```

## Harness Engineering 시연

1. **Spec 생성**: Agent Teams로 BE+FE Spec 병렬 생성
2. **Spec 검증**: 린터 + 사람 리뷰
3. **코드 제거**: 2개 새 repo에 docs/specs/ 만 복사
4. **AI 재개발**: "docs/specs/ 기반으로 개발해줘"
5. **테스트 검증**: Backend TC-ID + Frontend TC-FE-ID 전수 확인
6. **E2E 검증**: agent-browser로 Frontend E2E 자동 테스트
