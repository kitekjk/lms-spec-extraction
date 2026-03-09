# Frontend 아키텍처 규칙

## 기본 정보
- type: frontend_architecture

## 디렉토리 규칙

```
src/
├── app/                    # Next.js App Router 페이지
│   ├── (auth)/             # 인증 불필요 레이아웃 그룹
│   │   └── login/          # /login
│   ├── (protected)/        # 인증 필요 레이아웃 그룹
│   │   ├── dashboard/      # /dashboard
│   │   ├── attendance/     # /attendance
│   │   ├── schedule/       # /schedule
│   │   ├── leave/          # /leave
│   │   └── payroll/        # /payroll
│   ├── layout.tsx          # 루트 레이아웃
│   └── page.tsx            # / → /login 리다이렉트
├── components/             # 재사용 컴포넌트
│   ├── ui/                 # 기본 UI 컴포넌트 (Button, Input, Card, Badge, Table)
│   ├── layout/             # 레이아웃 컴포넌트 (Header, Sidebar, Navigation)
│   ├── forms/              # 폼 컴포넌트 (LoginForm, LeaveRequestForm)
│   └── feedback/           # 피드백 컴포넌트 (ErrorMessage, EmptyState, LoadingSpinner)
├── hooks/                  # 커스텀 훅
│   ├── useAuth.ts          # 인증 상태 관리
│   ├── useAttendance.ts    # 출퇴근 React Query 훅
│   ├── useSchedule.ts      # 스케줄 React Query 훅
│   ├── useLeave.ts         # 휴가 React Query 훅
│   └── usePayroll.ts       # 급여 React Query 훅
├── lib/                    # 유틸리티 및 API 클라이언트
│   ├── api/                # API 클라이언트 (도메인별 분리)
│   │   ├── client.ts       # Axios 인스턴스 (인터셉터 포함)
│   │   ├── auth.ts         # POST /api/auth/login, /api/auth/refresh
│   │   ├── attendance.ts   # /api/attendance/*
│   │   ├── schedule.ts     # /api/schedules/*
│   │   ├── leave.ts        # /api/leave-requests/*
│   │   ├── payroll.ts      # /api/payrolls/*
│   │   └── employee.ts     # /api/employees/*
│   ├── utils/              # 날짜 포맷, 금액 포맷, 유효성 검증 유틸리티
│   └── constants.ts        # 상수 (역할 코드, 상태 코드, 에러 메시지, 빈 상태 메시지)
├── stores/                 # Zustand 스토어
│   └── authStore.ts        # 인증 상태 (accessToken, refreshToken, user, role)
└── types/                  # TypeScript 타입 정의
    ├── auth.ts             # LoginRequest, LoginResponse, TokenResponse
    ├── attendance.ts       # AttendanceRecord, CheckInRequest, CheckOutRequest
    ├── schedule.ts         # WorkSchedule, CreateScheduleRequest
    ├── leave.ts            # LeaveRequest, CreateLeaveRequest
    ├── payroll.ts          # Payroll, PayrollPolicy
    ├── employee.ts         # Employee, EmployeeType
    └── common.ts           # ApiError, PaginatedResponse
```

## API 연동 규칙

### API 클라이언트
- Axios 인스턴스에 baseURL: /api, Content-Type: application/json 설정
- 요청 인터셉터: Zustand authStore에서 accessToken을 읽어 Authorization 헤더에 Bearer {token} 추가
- 응답 인터셉터: 401 응답 시 refreshToken으로 토큰 갱신 시도, 실패 시 /login으로 리다이렉트
- 응답 인터셉터: 에러 응답 body를 { code, message, details } 형태로 파싱

### React Query 사용 규칙
- 조회(GET)는 useQuery 사용, queryKey는 [도메인, ...파라미터] 형태
- 변경(POST/PUT/DELETE)은 useMutation 사용, 성공 시 관련 queryKey를 invalidate
- staleTime: 30초 (기본값), 출퇴근 관련 데이터는 10초
- 에러 발생 시 retry: 1회 (네트워크 오류만), 4xx 에러는 retry 하지 않음

### TypeScript 타입 규칙
- Backend DTO와 1:1 대응하는 타입을 types/ 디렉토리에 정의
- API 응답 타입은 Backend 응답 구조 그대로 사용
- camelCase 변환은 API 클라이언트 레벨에서 처리하지 않음 (Backend가 camelCase 응답)

## 인증/인가 규칙

### 토큰 관리
- accessToken, refreshToken은 Zustand authStore에 저장 (메모리)
- 브라우저 새로고침 대응: refreshToken을 localStorage에 보관 (키: "lms_refresh_token")
- accessToken 만료(1시간) 전 자동 갱신: 만료 5분 전 POST /api/auth/refresh 호출

### 라우트 보호
- (protected) 레이아웃 그룹: 인증되지 않은 사용자는 /login으로 리다이렉트
- 역할별 접근 제어: EMPLOYEE가 MANAGER 전용 기능에 접근 시 403 페이지 표시
- /login: 이미 인증된 사용자는 /dashboard로 리다이렉트

## 접근성 (필수)
- 모든 인터랙티브 요소에 data-testid 속성 부여 (E2E 테스트용)
- semantic HTML 사용: button, input, form, table, nav, main, header
- ARIA 라벨 필수: aria-label, aria-describedby, role 속성
- 키보드 네비게이션 지원: Tab 순서, Enter/Space로 버튼 활성화
- 포커스 관리: 모달 열림 시 포커스 트랩, 닫힘 시 원래 요소로 복귀

## 반응형 규칙
- 모바일(< 768px): 단일 컬럼, 햄버거 메뉴
- 태블릿(768px ~ 1024px): 2컬럼, 축소된 사이드바
- 데스크톱(> 1024px): 전체 사이드바 + 메인 콘텐츠

## 비기능 요구사항
- 초기 로딩(LCP): 2초 이내
- 인터랙션 반응(FID): 100ms 이내
- 번들 사이즈: 초기 로드 200KB 이내 (gzip 기준)
- 코드 스플리팅: 라우트 단위 dynamic import
