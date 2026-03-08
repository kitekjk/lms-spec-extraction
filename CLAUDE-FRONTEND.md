# LMS Frontend - Spec-Driven Development

## 프로젝트 개요
LMS Backend API를 소비하여 매장 직원에게 출퇴근, 스케줄, 휴가, 급여 UI를 제공하는 프론트엔드 서비스.

## Backend 연동
- Backend repo: lms-backend
- API Base: /api/v1/
- 인증: JWT Bearer Token
- **API Spec 참조**: lms-backend/docs/specs/{도메인}/LMS-API-*.md

## Spec 위치
```
docs/specs/
├── frontend-definition.md       # 프론트엔드 서비스 정의
├── frontend-architecture.md     # React/Next.js 아키텍처 규칙
├── frontend-naming-guide.md     # 컴포넌트/훅/페이지 네이밍
├── screens/                     # 화면 Spec
└── e2e/                         # E2E 테스트 시나리오 (agent-browser용)
```

## Spec 먼저 원칙
- 새 화면: 화면 Spec + E2E 테스트 Spec 먼저 → 코드 생성
- 기존 수정: Spec 먼저 업데이트 → 코드 수정
- Backend API Spec이 변경되면 관련 화면 Spec도 업데이트

## 코드 생성 시
1. 관련 화면 Spec과 Backend API Spec 먼저 읽기
2. frontend-architecture.md 규칙 따르기
3. frontend-naming-guide.md 컨벤션 따르기
4. **모든 인터랙티브 요소에 data-testid 속성 추가** (agent-browser E2E용)
5. **semantic HTML + ARIA 라벨 사용** (접근성 + 테스트 안정성)
6. Backend API 에러 응답({ code, message, details }) 처리 반영

## E2E 테스트 생성 시
1. e2e/ Spec의 Given-When-Then을 agent-browser 스크립트로 변환
2. TC-FE-ID를 테스트 파일에 주석으로 마킹
3. agent-browser snapshot -i로 요소 발견 → @ref 기반 인터랙션

## 기술 스택
- React / Next.js (App Router) / TypeScript
- Tailwind CSS
- Zustand (클라이언트 상태) + React Query (서버 상태)
- React Hook Form + Zod (폼 검증)
- Vitest + React Testing Library (Unit/Integration)
- agent-browser (E2E)

## 커맨드
- /generate-specs → Frontend Spec 전체 생성
- /validate-specs → `python scripts/spec_lint.py docs/specs/`
- /run-e2e → agent-browser 기반 E2E 테스트 실행
