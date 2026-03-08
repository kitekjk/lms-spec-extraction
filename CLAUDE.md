# LMS Backend - Spec-Driven Development

## 프로젝트 개요
매장 직원의 출퇴근 기록, 업무 스케줄, 휴일 관리 백엔드 서비스.
DDD + Clean Architecture 기반 멀티모듈 Spring Boot 프로젝트.
Frontend repo(lms-frontend)가 이 서비스의 API를 소비한다.

## Spec 위치
```
docs/specs/
├── service-definition.md       # 서비스 정의
├── architecture-rules.md       # 아키텍처 규칙
├── naming-guide.md             # 네이밍 컨벤션
├── infra-config.md             # 인프라 설정
├── init-data.md                # 초기 데이터
├── policies/                   # 정책 (공통 규칙 + NFR)
└── {도메인}/                    # Use Case + API Spec
```

## Spec 먼저 원칙
- 새 기능: Spec 먼저 → 코드 생성
- 기존 수정: Spec 먼저 업데이트 → 코드 수정
- Spec 없이 코드 생성 요청 → Spec 작성 먼저 제안

## Spec 작성 시
1. 기존 Spec과 중복/충돌 검토
2. 관련 정책 링크 포함
3. 주 모델 + 참조 모델 명시
4. 검증 조건은 테스트 가능한 형태
5. 함수명/변수명 제외 (naming-guide.md 참조)
6. 테스트 시나리오: Given-When-Then + TC-ID + 레벨
7. 비기능 요구사항(NFR) 확인
8. **API Spec 변경 시 Frontend repo에 영향 공유 필요**

## 코드 생성 시
1. 관련 Spec 먼저 읽기
2. architecture-rules.md 레이어/의존성 규칙 따르기
3. naming-guide.md 컨벤션 따르기
4. 테스트 시나리오 → @Tag("TC-xxx") 마킹 테스트 코드 생성
5. NFR 테스트 포함 (동시성, 응답시간)
6. 대상 도메인 외 코드 수정 금지
7. **기존 API 하위호환 유지** (POLICY-NFR-001)

## 기술 스택
- Kotlin 2.1.x / Spring Boot 3.5.x / JDK 21
- MySQL 8.x + Spring Data JPA
- Spring Security 6.x + JWT
- JUnit 5 + MockK + Testcontainers
- Spotless + ktlint

## 커맨드
- /generate-specs → Agent Teams로 전체 Spec 생성 (SKILL.md 참조)
- /generate-spec [도메인] → 특정 도메인 Spec 생성
- /validate-specs → `python scripts/spec_lint.py docs/specs/`
