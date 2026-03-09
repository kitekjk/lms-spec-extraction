# LMS-E2E-001: 로그인흐름

## 기본 정보
- type: e2e_test_spec
- tool: agent-browser
- 관련 화면: LMS-SCREEN-001

## 관련 Backend Spec
- LMS-API-USER-001 (로그인 API)
- LMS-USER-001 (사용자 인증 Use Case)

## 테스트 데이터 준비 방법
- init-data.md 기본 데이터 활용
- 테스트 전용 시딩 API: POST /api/v1/test/seed
- 사용 계정: manager.gangnam@lms.com (MANAGER), employee1.gangnam@lms.com (EMPLOYEE), admin@lms.com (SUPER_ADMIN)
- 비밀번호: password123

## 테스트 시나리오

### TC-FE-001-01: MANAGER 계정 정상 로그인 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 사용자 6명 등록 상태
  - 로그인 페이지(/login) 접속 상태
- When:
  - 이메일 입력란에 "manager.gangnam@lms.com" 입력
  - 비밀번호 입력란에 "password123" 입력
  - "로그인" 버튼 클릭
- Then:
  - /dashboard 페이지로 이동
  - 대시보드 페이지 텍스트 표시 확인
  - 사이드바에 "박수진" 이름 텍스트 표시

### TC-FE-001-02: 빈 입력값으로 로그인 시도 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 사용자 등록 상태
  - 로그인 페이지(/login) 접속 상태
- When:
  - 이메일/비밀번호 입력 없이 "로그인" 버튼 클릭
- Then:
  - "이메일을 입력해주세요." 메시지 표시
  - "비밀번호를 입력해주세요." 메시지 표시
  - /login 페이지에 그대로 유지 (이동 미발생)

### TC-FE-001-03: 잘못된 비밀번호로 로그인 시도 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 사용자 등록 상태
  - 로그인 페이지(/login) 접속 상태
- When:
  - 이메일 입력란에 "manager.gangnam@lms.com" 입력
  - 비밀번호 입력란에 "wrongpassword" 입력
  - "로그인" 버튼 클릭
- Then:
  - "이메일 또는 비밀번호가 올바르지 않습니다." 에러 메시지 표시
  - /login 페이지에 그대로 유지 (이동 미발생)
  - 비밀번호 입력란 초기화

### TC-FE-001-04: 비활성화된 계정으로 로그인 시도 (E2E)
- Given:
  - Backend 데이터: is_active=false 상태의 사용자 계정 (시딩 API로 생성)
  - 로그인 페이지(/login) 접속 상태
- When:
  - 이메일 입력란에 비활성화 계정 이메일 입력
  - 비밀번호 입력란에 "password123" 입력
  - "로그인" 버튼 클릭
- Then:
  - "비활성화된 계정입니다. 관리자에게 문의하세요." 에러 메시지 표시
  - /login 페이지에 그대로 유지 (이동 미발생)

### TC-FE-001-05: 서버 오류(500) 시 로그인 동작 (E2E)
- Given:
  - Backend API 응답: 500 (서버 내부 오류)
- When:
  - 이메일 입력란에 "manager.gangnam@lms.com" 입력
  - 비밀번호 입력란에 "password123" 입력
  - "로그인" 버튼 클릭
- Then:
  - "서버 오류가 발생했습니다. 다시 시도해주세요." 에러 메시지 표시
  - 재시도 버튼 표시
  - /login 페이지에 그대로 유지 (이동 미발생)
