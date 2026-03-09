# LMS Frontend - 서비스 정의

## 기본 정보
- type: frontend_definition
- framework: React / Next.js (App Router)
- language: TypeScript
- styling: Tailwind CSS
- state: Zustand + React Query
- test: Vitest + React Testing Library + agent-browser (E2E)

## 서비스 목적
매장 근로자의 출퇴근 기록, 근무 일정, 휴가 관리, 급여 조회를 위한 웹 프론트엔드 애플리케이션이다. LMS Backend API를 소비하며, 역할(SUPER_ADMIN, MANAGER, EMPLOYEE)에 따라 접근 가능한 화면과 기능이 다르다.

## Backend API 연동
- Backend repo: lms-backend
- API Base: /api
- 인증: JWT Bearer Token (POLICY-AUTH-001 참조)
- Content-Type: application/json
- Access Token 만료: 1시간, Refresh Token 만료: 7일
- 인증 헤더: Authorization: Bearer {accessToken}
- API Spec 참조: lms-backend/docs/specs/{도메인}/LMS-API-*.md

## 사용자 역할

| 역할 | 코드 | Frontend 접근 범위 |
|------|------|-------------------|
| 슈퍼 관리자 | SUPER_ADMIN | 전체 화면, 전체 매장 데이터 |
| 매니저 | MANAGER | 대시보드, 소속 매장 근로자/일정/출퇴근/휴가 관리 |
| 근로자 | EMPLOYEE | 본인 출퇴근, 일정 조회, 휴가 신청, 급여 조회 |

## 화면 목록

| 화면 ID | 화면명 | 라우트 | 관련 Backend Spec |
|---------|--------|--------|------------------|
| LMS-SCREEN-001 | 로그인 | /login | LMS-API-USER-001 |
| LMS-SCREEN-002 | 대시보드 | /dashboard | LMS-API-ATT-001, LMS-API-SCH-001, LMS-API-LEAVE-001 |
| LMS-SCREEN-003 | 출퇴근 | /attendance | LMS-API-ATT-001 |
| LMS-SCREEN-004 | 스케줄 | /schedule | LMS-API-SCH-001 |
| LMS-SCREEN-005 | 휴가관리 | /leave | LMS-API-LEAVE-001 |
| LMS-SCREEN-006 | 급여조회 | /payroll | LMS-API-PAY-001 |

## E2E 테스트 목록

| E2E ID | 흐름명 | 관련 화면 |
|--------|--------|----------|
| LMS-E2E-001 | 로그인흐름 | LMS-SCREEN-001 |
| LMS-E2E-002 | 대시보드조회 | LMS-SCREEN-002 |
| LMS-E2E-003 | 출퇴근흐름 | LMS-SCREEN-003 |
| LMS-E2E-004 | 스케줄관리흐름 | LMS-SCREEN-004 |
| LMS-E2E-005 | 휴가신청흐름 | LMS-SCREEN-005 |

## 에러 처리 규칙
- Backend 에러 응답 형식: { code: string, message: string, details?: object }
- 401 응답: 로그인 페이지로 리다이렉트
- 403 응답: "접근 권한이 없습니다" 메시지 표시
- 404 응답: "요청한 데이터를 찾을 수 없습니다" 메시지 표시
- 500 응답: "서버 오류가 발생했습니다. 다시 시도해주세요." 메시지 + 재시도 버튼
- 네트워크 오류: "네트워크 연결을 확인해주세요." 메시지 + 재시도 버튼
