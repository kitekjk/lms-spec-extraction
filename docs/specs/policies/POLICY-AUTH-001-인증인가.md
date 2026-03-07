# POLICY-AUTH-001: 인증 인가

## 기본 정보
- type: policy
- category: auth
- owner: LMS팀
- last_updated: 2026-03-08

## 관련 상위 정책
(없음 - 향후 전사 보안 정책 연결)

## 정책 규칙

### 인증
- JWT 기반 무상태(Stateless) 인증
- Access Token 유효기간: 3,600,000ms (1시간)
- Refresh Token 유효기간: 604,800,000ms (7일)
- 비밀번호 암호화: BCrypt
- 비활성 사용자(isActive=false) 로그인 불가
- 로그인 성공 시 lastLoginAt 업데이트

### 인가 (역할별 권한)
- SUPER_ADMIN: 전체 시스템 접근 가능
- MANAGER: 소속 매장 범위 내 관리 기능 (일정, 출퇴근, 휴가 관리)
- EMPLOYEE: 자기 자신의 데이터 조회 및 출퇴근/휴가 신청

### 공개 엔드포인트
- `/api/auth/**` (로그인, 회원가입, 토큰 갱신)
- `/swagger-ui/**`, `/v3/api-docs/**`
- `/health`
- 그 외 모든 엔드포인트는 인증 필요

### 회원가입 규칙
- SUPER_ADMIN만 회원가입 API 호출 가능
- User.create()로 SUPER_ADMIN 역할 생성 불가 (reconstruct로만 가능)
- 이메일 중복 불가

## 적용 대상
- LMS-USER-001 (로그인)
- LMS-USER-002 (회원가입)
- 모든 API 엔드포인트 (인증 필수)
