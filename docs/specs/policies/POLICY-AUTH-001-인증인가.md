# POLICY-AUTH-001: 인증/인가 정책

## 기본 정보
- type: policy
- domain: auth
- related-specs: [architecture-rules.md, infra-config.md]

## 정책 규칙

### RULE-001: JWT 기반 Stateless 인증
- 조건: 모든 API 요청 (permitAll 경로 제외)
- 결과: `Authorization: Bearer {accessToken}` 헤더를 통해 인증 수행. 세션을 사용하지 않음 (`SessionCreationPolicy.STATELESS`)
- 근거: `SecurityConfig.kt` - `.sessionManagement { it.sessionCreationPolicy(SessionCreationPolicy.STATELESS) }`

### RULE-002: 인증 제외 경로 (Public Endpoints)
- 조건: 아래 경로로 요청 시
- 결과: 인증 없이 접근 허용 (`permitAll`)
  - `/api/auth/**` - 로그인, 회원가입, 토큰 갱신
  - `/health` - 헬스 체크
  - `/actuator/health` - Actuator 헬스 체크
  - `/swagger-ui/**`, `/swagger-ui.html` - Swagger UI
  - `/api-docs/**`, `/v3/api-docs/**` - API 문서
  - `OPTIONS /**` - CORS preflight 요청
- 근거: `SecurityConfig.kt` - `authorizeHttpRequests` 블록

### RULE-003: 인증 필수 경로
- 조건: RULE-002에 해당하지 않는 모든 요청
- 결과: JWT 토큰 인증 필수. 유효한 토큰이 없으면 401 Unauthorized 응답
- 근거: `SecurityConfig.kt` - `.anyRequest().authenticated()`

### RULE-004: Access Token 구조 및 만료
- 조건: Access Token 생성 시
- 결과: JWT 토큰에 다음 클레임 포함:
  - `subject` (sub): employeeId (근로자 ID)
  - `role`: 사용자 역할 (SUPER_ADMIN, MANAGER, EMPLOYEE)
  - `storeId`: 매장 ID (nullable)
  - `iat`: 발급 시간
  - `exp`: 만료 시간
- 만료 시간: 3,600,000ms (1시간)
- 서명 알고리즘: HMAC-SHA (HS256), 256비트 이상 시크릿 키 필요
- 근거: `JwtTokenProvider.kt` - `generateAccessToken()`, `JwtProperties.kt` - `accessTokenExpiration = 3600000`

### RULE-005: Refresh Token 구조 및 만료
- 조건: Refresh Token 생성 시
- 결과: JWT 토큰에 다음 클레임 포함:
  - `subject` (sub): employeeId
  - `iat`: 발급 시간
  - `exp`: 만료 시간
- 만료 시간: 604,800,000ms (7일)
- 주의: Refresh Token에는 role, storeId 클레임이 포함되지 않음
- 근거: `JwtTokenProvider.kt` - `generateRefreshToken()`, `JwtProperties.kt` - `refreshTokenExpiration = 604800000`

### RULE-006: 토큰 유효성 검증
- 조건: 매 요청마다 `JwtAuthenticationFilter`에서 실행
- 결과:
  - `Authorization` 헤더에서 `Bearer ` 접두어 이후 토큰 추출
  - `Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token)` 으로 검증
  - 유효하면 `SecurityContext`에 인증 정보 설정
  - 유효하지 않으면 (만료, 변조 등) 인증 정보를 설정하지 않고 다음 필터로 전달
- 근거: `JwtAuthenticationFilter.kt` - `doFilterInternal()`

### RULE-007: 역할 기반 접근 제어 (RBAC)
- 조건: 인증된 요청에 대해 역할 확인
- 결과: 3단계 역할 체계 적용
  - `SUPER_ADMIN` ("슈퍼 관리자"): 전체 시스템 관리, 매장 생성, 모든 매장 접근
  - `MANAGER` ("매니저"): 자기 매장의 근무 일정, 휴가 승인 관리
  - `EMPLOYEE` ("근로자"): 본인의 출퇴근, 일정 조회, 휴가 신청
- Spring Security Authority 형식: `ROLE_SUPER_ADMIN`, `ROLE_MANAGER`, `ROLE_EMPLOYEE`
- 메서드 레벨 보안: `@EnableMethodSecurity(prePostEnabled = true)` 활성화 (`@PreAuthorize` 사용 가능)
- 근거: `Role.kt`, `SecurityConfig.kt`, `JwtAuthenticationFilter.kt`

### RULE-008: 비밀번호 암호화
- 조건: 사용자 비밀번호 저장 및 검증 시
- 결과: `BCryptPasswordEncoder` 사용하여 암호화
- 근거: `SecurityConfig.kt` - `fun passwordEncoder(): PasswordEncoder = BCryptPasswordEncoder()`

### RULE-009: 사용자 로드 및 계정 상태 확인
- 조건: 이메일 기반 사용자 조회 시
- 결과:
  - `Email` Value Object로 사용자 조회
  - 사용자 미존재 시: `UsernameNotFoundException` ("사용자를 찾을 수 없습니다: {email}")
  - 비활성 사용자: `accountLocked = true`, `disabled = true` 설정 (로그인 차단)
- 근거: `CustomUserDetailsService.kt` - `loadUserByUsername()`

### RULE-010: CORS 정책
- 조건: 모든 Cross-Origin 요청
- 결과:
  - 허용 오리진 패턴: `*` (모든 오리진)
  - 허용 메서드: GET, POST, PUT, DELETE, PATCH, OPTIONS
  - 허용 헤더: `*` (모든 헤더)
  - 노출 헤더: `Authorization`
  - 자격 증명 허용: `true`
  - Preflight 캐시 시간: 3,600초 (1시간)
- 근거: `SecurityConfig.kt` - `corsConfigurationSource()`

## 에러 코드

| 코드 | 예외 클래스 | 기본 메시지 |
|------|-------------|-------------|
| AUTH001 | `AuthenticationFailedException` | "이메일 또는 비밀번호가 일치하지 않습니다." |
| AUTH002 | `InactiveUserException` | "비활성화된 사용자입니다." |
| TOKEN001 | `InvalidTokenException` | "유효하지 않은 Refresh Token입니다." |
| TOKEN002 | `UserNotFoundException` | "사용자를 찾을 수 없습니다." |
| TOKEN003 | `TokenUserInactiveException` | "비활성화된 사용자입니다." |
| REG001 | `DuplicateEmailException` | "이미 등록된 이메일입니다: {email}" |
| REG002 | `InvalidRoleException` | "유효하지 않은 역할입니다: {role}" |

## 적용 대상

- LMS-USER-001 (로그인)
- LMS-USER-002 (회원가입)
- LMS-USER-003 (토큰갱신)
- 전체 API 인증
