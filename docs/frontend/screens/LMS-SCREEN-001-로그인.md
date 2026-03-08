# LMS-SCREEN-001: 로그인

## 기본 정보
- type: screen_spec
- 화면명: 로그인
- 라우트: `/login`, `/admin/login`
- 대상 사용자: 직원(EMPLOYEE), 관리자(MANAGER, SUPER_ADMIN)

## 관련 Backend Spec
- LMS-API-USER-001 (인증API)

## 화면 목적
직원 및 관리자가 이메일과 비밀번호를 입력하여 시스템에 로그인한다. 직원 로그인 화면과 관리자 로그인 화면이 분리되어 있으며, 직원 로그인 화면에서 관리자 로그인 화면으로 이동할 수 있다.

## 화면 구성 요소

### 직원 로그인 폼
- 표시 데이터: 앱 로고(Icons.business), 타이틀 "LMS 근태 관리", 이메일 입력 필드, 비밀번호 입력 필드(마스킹 토글), 로그인 버튼, 에러 메시지 영역, 관리자 로그인 링크
- Backend API: POST /api/auth/login
  - 참조 Spec: LMS-API-USER-001
  - 요청 파라미터: `{ "email": "string", "password": "string" }`
  - 응답 매핑: accessToken/refreshToken → 로컬 저장, userInfo → authProvider 상태 업데이트
- 빈 상태: 초기 상태에서 입력 필드가 비어 있음
- 에러 상태: SnackBar 빨간색 배경으로 에러 메시지 표시, 에러 컨테이너(빨간 테두리)에 에러 상세 표시
- 유효성 검증:
  - 이메일: 필수, 이메일 형식 (`^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$`)
  - 비밀번호: 필수, 최소 6자
- 성공 시 이동: `/home`

### 관리자 로그인 폼
- 표시 데이터: 관리자 아이콘(Icons.admin_panel_settings), 타이틀 "관리자 로그인", 서브타이틀 "LMS Admin Dashboard", 이메일 입력 필드, 비밀번호 입력 필드(마스킹 토글), 로그인 버튼, 에러 메시지 영역
- Backend API: POST /api/auth/login
  - 참조 Spec: LMS-API-USER-001
  - 요청 파라미터: `{ "email": "string", "password": "string" }`
  - 응답 매핑: accessToken/refreshToken → 로컬 저장, userInfo → adminAuthProvider 상태 업데이트, role 검증(SUPER_ADMIN 또는 MANAGER만 허용)
- 빈 상태: 초기 상태에서 입력 필드가 비어 있음
- 에러 상태: SnackBar 빨간색 배경으로 에러 메시지 표시, 에러 컨테이너(빨간 테두리)에 에러 상세 표시, 권한 없음 시 "관리자 권한이 없습니다" 에러
- 유효성 검증:
  - 이메일: 필수, `@` 포함
  - 비밀번호: 필수, 최소 4자
- 성공 시 이동: `/admin/dashboard`

## 사용자 흐름

1. 사용자가 앱을 실행하면 직원 로그인 화면(`/login`)이 표시된다
2. 이메일과 비밀번호를 입력한다
3. 유효성 검증 통과 시 로그인 API 호출
4. 로그인 성공 시 홈 화면(`/home`)으로 이동
5. 로그인 실패 시 에러 메시지 표시
6. "관리자로 로그인" 링크를 누르면 관리자 로그인 화면(`/admin/login`)으로 이동
7. 관리자 로그인 성공 시 대시보드(`/admin/dashboard`)로 이동
