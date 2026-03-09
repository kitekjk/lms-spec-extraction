# POLICY-AUTH-001 인증인가

## 기본 정보
- type: policy
- id: POLICY-AUTH-001
- last-updated: 2026-03-09

## 정책 규칙

### 1. 인증 방식
1. JWT(JSON Web Token) 기반 Stateless 인증을 사용한다.
2. Access Token 만료 시간은 3,600,000ms (1시간)이다.
3. Refresh Token 만료 시간은 604,800,000ms (7일)이다.
4. JWT 서명 알고리즘은 HMAC-SHA256 (HS256)이다.
5. 비밀번호는 BCrypt로 암호화하여 저장한다.

### 2. 로그인/로그아웃
1. 로그인 API는 `POST /api/auth/login`이며 이메일과 비밀번호를 요구한다.
2. 로그인 성공 시 accessToken, refreshToken, tokenType("Bearer")을 응답한다.
3. 비활성화된 사용자(`is_active = false`)는 로그인할 수 없다 (에러코드: AUTH002).
4. 인증 실패 시 에러코드 AUTH001을 반환한다.
5. 모든 인증된 API 요청은 Authorization 헤더에 `Bearer {accessToken}` 형식으로 토큰을 전달한다.

### 3. 역할 기반 접근 제어 (RBAC)
1. 시스템은 3개의 역할을 정의한다: SUPER_ADMIN, MANAGER, EMPLOYEE.
2. SUPER_ADMIN은 모든 매장과 모든 사용자에 대한 전체 권한을 갖는다.
3. MANAGER는 자신이 소속된 매장의 근로자만 관리할 수 있다 (에러코드: EMP003, SCH005).
4. EMPLOYEE는 자신의 정보 조회, 출퇴근 처리, 휴가 신청만 가능하다.
5. 역할별 접근 권한은 @PreAuthorize 어노테이션으로 메서드 레벨에서 제어한다.

### 4. 역할별 API 접근 권한
| API | SUPER_ADMIN | MANAGER | EMPLOYEE |
|-----|-------------|---------|----------|
| 매장 등록/수정/삭제 | O | X | X |
| 매장 목록 조회 | 전체 매장 | 소속 매장 | 소속 매장 |
| 근로자 등록/수정/비활성화 | 전체 매장 | 소속 매장 | X |
| 근로자 목록 조회 | 전체 매장 | 소속 매장 | 본인만 |
| 근무 일정 등록/수정 | 전체 매장 | 소속 매장 | X |
| 근무 일정 조회 | 전체 매장 | 소속 매장 | 본인만 |
| 출퇴근 처리 (check-in/out) | X | X | 본인만 |
| 출퇴근 기록 수정 | 전체 매장 | 소속 매장 | X |
| 출퇴근 기록 조회 | 전체 매장 | 소속 매장 | 본인만 |
| 휴가 신청 | X | X | 본인만 |
| 휴가 승인/반려 | 전체 매장 | 소속 매장 | X |
| 급여 정책 관리 | O | X | X |
| 급여 산정 결과 조회 | 전체 매장 | 소속 매장 | 본인만 |

### 5. 토큰 검증 규칙
1. 유효하지 않은 토큰은 에러코드 TOKEN001을 반환한다.
2. 토큰에 해당하는 사용자가 존재하지 않으면 에러코드 TOKEN002를 반환한다.
3. 토큰에 해당하는 사용자가 비활성 상태이면 에러코드 TOKEN003을 반환한다.
4. JWT 필터는 UsernamePasswordAuthenticationFilter 이전에 실행된다.

### 6. 사용자 등록 규칙
1. 이메일은 시스템 전체에서 고유해야 한다 (에러코드: REG001).
2. 역할은 SUPER_ADMIN, MANAGER, EMPLOYEE 중 하나여야 한다 (에러코드: REG002).
3. 신규 사용자의 is_active 기본값은 true이다.
4. last_login_at은 최초 등록 시 NULL이다.

### 7. 세션 정책
1. 서버는 세션을 생성하지 않는다 (SessionCreationPolicy.STATELESS).
2. CSRF 보호는 비활성화한다 (JWT 사용으로 불필요).

## 적용 대상
- 모든 도메인: 인증된 사용자만 API에 접근 가능
- 사용자(User) 도메인: 로그인, 회원가입, 토큰 갱신
- 근로자(Employee) 도메인: 매장 소속 기반 접근 제어
- 근무일정(WorkSchedule) 도메인: 매니저의 소속 매장 제한
- 출퇴근(Attendance) 도메인: 본인 출퇴근만 처리
- 휴가(Leave) 도메인: 본인 신청, 매니저 승인
- 급여(Payroll) 도메인: 정책 관리는 SUPER_ADMIN, 조회는 역할별 제한
