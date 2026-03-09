# LMS-SCREEN-001: 로그인

## 기본 정보
- type: screen_spec
- route: /login

## 관련 Backend Spec
- LMS-API-USER-001 (로그인 API)
- LMS-USER-001 (사용자 인증 Use Case)

## 화면 목적
사용자가 이메일과 비밀번호를 입력하여 시스템에 로그인하고, JWT 토큰을 발급받아 인증된 상태로 전환한다.

## 접근 권한
- 전체 (비인증 사용자)

## 화면 구성 요소

### 로그인 폼
- 표시 데이터: 이메일 입력 필드, 비밀번호 입력 필드, 로그인 버튼
- Backend API: POST /api/auth/login
  - 참조 Spec: LMS-API-USER-001
  - 요청 파라미터: { email: string, password: string }
  - 응답 매핑: accessToken -> authStore.accessToken, refreshToken -> authStore.refreshToken, role -> authStore.role
- 빈 상태: 해당 없음 (폼 초기 상태는 빈 입력 필드)
- 에러 상태: "이메일 또는 비밀번호가 올바르지 않습니다." (AUTH001), "비활성화된 계정입니다. 관리자에게 문의하세요." (AUTH002)

### 에러 메시지 영역
- 표시 데이터: 인증 실패 시 에러 메시지 텍스트 (빨간색, 폼 상단)
- Backend API: POST /api/auth/login (에러 응답 시)
  - 참조 Spec: LMS-API-USER-001
  - 응답 매핑: error.message -> 에러 메시지 텍스트
- 빈 상태: 에러 없을 시 미표시
- 에러 상태: "서버 오류가 발생했습니다. 다시 시도해주세요." (500 응답 시) + 재시도 버튼 표시

### 로딩 상태 오버레이
- 표시 데이터: 로그인 요청 중 버튼 비활성화 + 스피너 표시
- Backend API: POST /api/auth/login (요청 진행 중)
  - 참조 Spec: LMS-API-USER-001
  - 응답 매핑: isLoading -> 버튼 disabled 상태 + 스피너 표시
- 빈 상태: 요청 미진행 시 미표시
- 에러 상태: 요청 실패 시 로딩 해제, 에러 메시지 표시

## 사용자 흐름
1. 사용자가 /login 페이지에 접속한다
2. 이메일 입력 필드에 이메일 주소를 입력한다 (예: manager.gangnam@lms.com)
3. 비밀번호 입력 필드에 비밀번호를 입력한다 (예: password123)
4. "로그인" 버튼을 클릭한다
5. 로그인 성공 시: accessToken과 refreshToken을 authStore에 저장하고 /dashboard로 이동한다
6. 로그인 실패 시: 에러 메시지 영역에 실패 사유를 표시한다
7. 이미 인증된 상태로 /login 접속 시: /dashboard로 자동 리다이렉트한다

## 검증 조건
- 이메일 필드: 빈 값이면 "이메일을 입력해주세요." 표시
- 이메일 필드: 이메일 형식이 아니면 "올바른 이메일 형식을 입력해주세요." 표시
- 비밀번호 필드: 빈 값이면 "비밀번호를 입력해주세요." 표시
- 로그인 버튼: 이메일/비밀번호가 모두 입력되어야 활성화
- 로그인 버튼: 요청 진행 중에는 비활성화 (중복 요청 방지)

## 비기능 요구사항
- 초기 로딩: 2초 이내
- 인터랙션 반응: 100ms 이내
- API 실패 시: 에러 메시지 표시 + 재시도 버튼
- 비밀번호 입력: type="password"로 마스킹 처리
- Enter 키로 폼 제출 가능
