# LMS (Labor Management System) - Spec-Driven Development

## 프로젝트 개요
매장 직원의 출퇴근 기록, 업무 스케줄, 휴일 관리를 담당하는 서비스이다.
DDD + Clean Architecture 기반 멀티모듈 Spring Boot 프로젝트.

## Spec-Driven Development 규칙

### Spec 위치
```
docs/specs/
├── service-definition.md       # 서비스 정의
├── architecture-rules.md       # 아키텍처 규칙
├── naming-guide.md             # 네이밍 컨벤션
├── infra-config.md             # 인프라 설정
├── init-data.md                # 초기/테스트 데이터
├── policies/                   # 정책 (공통 규칙 + NFR)
└── {도메인}/                    # 도메인별 Use Case + API Spec
```

### Spec 먼저 원칙
- 새로운 기능: **Spec 먼저 작성 → 코드 생성**
- 기존 기능 수정: **Spec 먼저 업데이트 → 코드 수정**
- Spec 없이 코드 생성 요청 → Spec 작성을 먼저 제안

### Spec 작성/수정 시
1. 기존 Spec과 중복/충돌 검토
2. 관련 정책(policies/) 링크 포함
3. 주 모델(Aggregate Root)과 참조 모델 명시
4. 검증 조건은 자동 테스트 가능한 형태
5. 함수명/변수명 제외 (naming-guide.md 참조)
6. 테스트 시나리오를 Given-When-Then + TC-ID로 작성
7. 비기능 요구사항(NFR) 확인 — POLICY-NFR-001 공통 + Use Case 특화

### 코드 생성 시
1. 관련 Spec을 먼저 읽는다
2. architecture-rules.md의 레이어/의존성 규칙을 따른다
3. naming-guide.md의 네이밍 컨벤션을 따른다
4. 검증 조건을 테스트 코드로 반영한다
5. 테스트 시나리오를 테스트 코드로 생성하고 **@Tag("TC-xxx")로 마킹**한다
6. 비기능 요구사항(동시성, 응답시간, 정합성)에 대한 테스트도 생성한다
7. Spec에 없는 규칙을 임의로 추가하지 않는다
8. **대상 도메인 외 코드는 수정하지 않는다**

### 테스트 코드 생성 시
1. Spec "## 테스트 시나리오"의 Given-When-Then을 변환
2. 반드시 @Tag("TC-{ID}")를 추가
3. 테스트 레벨별 클래스 배치:
   - Unit → {클래스명}Test
   - Integration → {도메인명}IntegrationTest (Testcontainers 사용)
   - E2E → {도메인명}E2ETest (Testcontainers 사용)
4. NFR 테스트 포함: 동시성, 응답시간, 트랜잭션 정합성

### 코드 리뷰 시
1. 변경 코드가 관련 Spec과 일치하는지
2. 테스트 시나리오가 모두 테스트 코드에 반영되었는지
3. **대상 도메인 외 파일 변경이 없는지**
4. **기존 API 형식이 변경되지 않았는지 (하위호환)**
5. Spec 변경 없이 비즈니스 로직이 변경된 경우 경고

## 기술 스택
- Language: Kotlin 2.1.x
- Framework: Spring Boot 3.5.x
- JDK: 21
- Build: Gradle (Kotlin DSL)
- DB: MySQL 8.x + Spring Data JPA
- Security: Spring Security 6.x + JWT
- Test: JUnit 5 + MockK + Testcontainers
- Code Style: Spotless + ktlint

## 커맨드

### /generate-specs
기존 소스코드와 문서를 분석하여 전체 Spec 생성.
Skill: docs/skills/spec-generator/SKILL.md

### /generate-spec [도메인명]
특정 도메인의 Spec만 생성.

### /validate-specs
`python scripts/spec_lint.py docs/specs/`
