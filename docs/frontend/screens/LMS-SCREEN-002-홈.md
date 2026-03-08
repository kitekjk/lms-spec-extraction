# LMS-SCREEN-002: 홈

## 기본 정보
- type: screen_spec
- 화면명: 홈
- 라우트: `/home`
- 대상 사용자: 직원(EMPLOYEE)

## 관련 Backend Spec
- LMS-API-USER-001 (인증API)

## 화면 목적
로그인한 직원에게 사용자 정보를 표시하고, 주요 기능(출퇴근 체크, 근무 일정, 휴가 신청, 급여 조회)으로 이동할 수 있는 메뉴 그리드를 제공한다.

## 화면 구성 요소

### 사용자 정보 카드
- 표시 데이터: 사용자 아이콘, 이메일(user.email), 역할(user.role)
- Backend API: GET /api/auth/me
  - 참조 Spec: LMS-API-USER-001
  - 요청 파라미터: 없음 (인증 토큰으로 사용자 식별)
  - 응답 매핑: userInfo.email → 이메일 표시, userInfo.role → 역할 표시
- 빈 상태: "사용자 정보가 없습니다"
- 에러 상태: 카드가 표시되지 않음

### 메뉴 그리드
- 표시 데이터: 2x2 그리드 형태의 메뉴 카드 4개
  - 출퇴근 체크 (Icons.access_time, 파란색) → `/attendance`
  - 근무 일정 (Icons.calendar_today, 초록색) → `/schedule`
  - 휴가 신청 (Icons.beach_access, 주황색) → `/leave`
  - 급여 조회 (Icons.attach_money, 보라색) → `/payroll`
- Backend API: POST /api/auth/logout
  - 참조 Spec: LMS-API-USER-001
  - 요청 파라미터: 없음
  - 응답 매핑: 로그아웃 성공 시 로컬 토큰 삭제 후 `/login`으로 이동
- 빈 상태: "메뉴가 없습니다"
- 에러 상태: 해당 없음 (정적 메뉴)

## 사용자 흐름

1. 로그인 성공 후 홈 화면이 표시된다
2. 사용자 정보 카드에서 현재 로그인한 사용자의 이메일과 역할을 확인한다
3. 메뉴 카드를 탭하여 각 기능 화면으로 이동한다
4. AppBar의 로그아웃 아이콘을 눌러 로그아웃하고 로그인 화면으로 돌아간다
