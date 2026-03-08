# LMS Frontend - 서비스 정의

## 기본 정보
- type: frontend_definition
- name: LMS 근태 관리 (모바일/웹)
- package: lms_mobile_web
- version: 1.0.0+1
- framework: Flutter (SDK >=3.0.0 <4.0.0)
- language: Dart
- state-management: Riverpod (flutter_riverpod ^2.5.1)
- routing: GoRouter (go_router ^13.2.0)
- http-client: Dio (dio ^5.4.3)

## 서비스 목적
매장 직원(근로자)의 출퇴근 기록, 근무 일정 조회, 휴가 신청, 급여 확인을 위한 모바일 앱과
관리자(슈퍼 관리자/매니저)의 매장, 근로자, 일정, 출퇴근, 휴가, 급여를 통합 관리하는 웹 어드민을 하나의 Flutter 앱으로 제공한다.

---

## Backend API 연동

### Base URL
- 웹(kIsWeb): `http://localhost:8080/api` (하드코딩)
- 모바일: `.env` 파일의 `API_BASE_URL` (기본값: `http://localhost:8080/api`)

### 환경 설정 (EnvConfig)
| 항목 | 환경 변수 | 웹 기본값 | 모바일 기본값 |
|------|-----------|-----------|---------------|
| API Base URL | `API_BASE_URL` | `http://localhost:8080/api` | `http://localhost:8080/api` |
| API Timeout | `API_TIMEOUT` | 30,000ms | 30,000ms |
| Log Level | `LOG_LEVEL` | `info` | `info` |
| Storage Encryption Key | `STORAGE_ENCRYPTION_KEY` | (빈 문자열) | (빈 문자열) |

- 환경별 .env 파일: `.env.development`, `.env.staging`, `.env.production`
- 웹 환경에서는 .env 파일을 로드하지 않고 기본값 사용

### 인증 방식 (JWT Bearer Token)
- 요청 헤더: `Authorization: Bearer {accessToken}`
- `ApiInterceptor`가 모든 요청에 SecureStorage에서 읽은 accessToken을 자동 첨부
- 401 응답 시 refreshToken으로 `/auth/refresh` 호출하여 토큰 갱신 후 원래 요청 재시도
- 갱신 실패 시 저장된 모든 토큰/사용자 정보 삭제 (자동 로그아웃)

### 토큰 저장소 (SecureStorage)
- `flutter_secure_storage` 사용 (싱글턴 패턴)
- Android: `encryptedSharedPreferences: true`
- iOS: `KeychainAccessibility.first_unlock`

| Storage Key | 용도 |
|-------------|------|
| `access_token` | JWT Access Token |
| `refresh_token` | JWT Refresh Token |
| `user_id` | 사용자 ID |
| `user_email` | 사용자 이메일 |
| `user_role` | 사용자 역할 (SUPER_ADMIN, MANAGER, EMPLOYEE) |
| `store_id` | 매장 ID |
| `store_name` | 매장 이름 |

### API 엔드포인트 목록 (ApiEndpoints)

#### 인증 (Auth)
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `login` | `/auth/login` | 로그인 | UC-AUTH-001 로그인 |
| `register` | `/auth/register` | 회원가입 | UC-AUTH-002 회원가입 |
| `refresh` | `/auth/refresh` | 토큰 갱신 | UC-AUTH-003 토큰 갱신 |
| `logout` | `/auth/logout` | 로그아웃 | UC-AUTH-004 로그아웃 |
| `me` | `/auth/me` | 내 정보 조회 | UC-AUTH-005 내 정보 |

#### 출퇴근 (Attendance) - 근로자용
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `checkIn` | `/attendance/check-in` | 출근 체크 | UC-ATT-001 출근 |
| `checkOut` | `/attendance/check-out` | 퇴근 체크 | UC-ATT-002 퇴근 |
| `myAttendance` | `/attendance/my-records` | 내 출퇴근 기록 | UC-ATT-003 내 기록 조회 |

#### 근무 일정 (Schedule) - 근로자용
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `mySchedule` | `/work-schedules/my-schedules` | 내 근무 일정 | UC-SCH-001 내 일정 조회 |

#### 휴가 (Leave) - 근로자용
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `leaveRequests` | `/leave-requests` | 휴가 신청 | UC-LEAVE-001 휴가 신청 |
| `myLeaveRequests` | `/leave-requests/my-requests` | 내 휴가 내역 | UC-LEAVE-002 내 휴가 조회 |

#### 급여 (Payroll) - 근로자용
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `myPayroll` | `/payroll/my-payroll` | 내 급여 조회 | UC-PAY-001 내 급여 조회 |

#### 매장 관리 (Admin - Store)
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `stores` | `/stores` | 매장 목록/생성 | UC-STORE-001 매장 CRUD |
| `storeById(id)` | `/stores/{id}` | 매장 상세/수정/삭제 | UC-STORE-001 매장 CRUD |

#### 근로자 관리 (Admin - Employee)
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `employees` | `/employees` | 근로자 목록/등록 | UC-EMP-001 근로자 CRUD |
| `employeeById(id)` | `/employees/{id}` | 근로자 상세/수정 | UC-EMP-001 근로자 CRUD |
| `employeeDeactivate(id)` | `/employees/{id}/deactivate` | 근로자 비활성화 | UC-EMP-002 비활성화 |

#### 근무 일정 관리 (Admin - Schedule)
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `schedules` | `/schedules` | 일정 목록/생성 | UC-SCH-002 일정 관리 |
| `scheduleById(id)` | `/schedules/{id}` | 일정 수정/삭제 | UC-SCH-002 일정 관리 |

#### 출퇴근 관리 (Admin - Attendance)
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `attendanceRecords` | `/attendance/records` | 출퇴근 기록 목록 | UC-ATT-004 기록 관리 |
| `attendanceRecordById(id)` | `/attendance/records/{id}` | 기록 수정 | UC-ATT-005 기록 수정 |

#### 휴가 관리 (Admin - Leave)
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `leaves` | `/leaves` | 휴가 목록 | UC-LEAVE-003 휴가 관리 |
| `pendingLeaves` | `/leaves/pending` | 대기 중 휴가 | UC-LEAVE-004 승인 대기 |
| `approveLeave(id)` | `/leaves/{id}/approve` | 휴가 승인 | UC-LEAVE-005 휴가 승인 |
| `rejectLeave(id)` | `/leaves/{id}/reject` | 휴가 거부 | UC-LEAVE-006 휴가 거부 |

#### 급여 관리 (Admin - Payroll)
| 상수명 | 경로 | 용도 | Backend Use Case |
|--------|------|------|------------------|
| `payrolls` | `/payroll` | 급여 목록 | UC-PAY-002 급여 관리 |
| `payrollById(id)` | `/payroll/{id}` | 급여 상세 | UC-PAY-003 급여 상세 |
| `calculatePayroll` | `/payroll/calculate` | 급여 계산 | UC-PAY-004 급여 계산 |
| `payrollBatch` | `/payroll/batch` | 일괄 급여 계산 | UC-PAY-005 일괄 계산 |
| `payrollBatchHistory` | `/payroll/batch-history` | 배치 이력 | UC-PAY-006 배치 이력 |

### 에러 처리 (ErrorHandler)
Dio 예외를 앱 내부 `ApiException` 계층으로 변환한다.

| HTTP 상태 | 예외 클래스 | 코드 | 사용자 메시지 예시 |
|-----------|------------|------|-------------------|
| timeout | `NetworkException` | `NETWORK_ERROR` | 연결 시간이 초과되었습니다. |
| connectionError | `NetworkException` | `NETWORK_ERROR` | 서버에 연결할 수 없습니다. |
| 400 | `ValidationException` | `VALIDATION_ERROR` | (서버 메시지) |
| 401 | `UnauthorizedException` | `UNAUTHORIZED` | (서버 메시지) |
| 403 | `ForbiddenException` | `FORBIDDEN` | (서버 메시지) |
| 404 | `NotFoundException` | `NOT_FOUND` | (서버 메시지) |
| 409 | `ConflictException` | `CONFLICT` | (서버 메시지) |
| 500/502/503 | `ServerException` | `SERVER_ERROR` | (서버 메시지) |

---

## 화면 목록

### 근로자(Employee) 화면

| # | 화면명 | 라우트 경로 | Screen 클래스 | Backend API | 설명 |
|---|--------|-----------|--------------|-------------|------|
| E-01 | 로그인 | `/login` | `LoginScreen` | `POST /auth/login` | 이메일/비밀번호 로그인 |
| E-02 | 홈 | `/home` | `HomeScreen` | `GET /auth/me` | 메인 대시보드 |
| E-03 | 출퇴근 | `/attendance` | `CheckInOutScreen` | `POST /attendance/check-in`, `POST /attendance/check-out` | 출근/퇴근 체크 |
| E-04 | 출퇴근 기록 | `/attendance/records` | `AttendanceRecordsScreen` | `GET /attendance/my-records` | 내 출퇴근 기록 목록 |
| E-05 | 근무 일정 | `/schedule` | `MyScheduleScreen` | `GET /work-schedules/my-schedules` | 내 근무 일정 캘린더 |
| E-06 | 휴가 내역 | `/leave` | `LeaveHistoryScreen` | `GET /leave-requests/my-requests` | 내 휴가 신청 내역 |
| E-07 | 휴가 신청 | `/leave/request` | `LeaveRequestScreen` | `POST /leave-requests` | 새 휴가 신청 |
| E-08 | 급여 목록 | `/payroll` | `PayrollListScreen` | `GET /payroll/my-payroll` | 내 급여 목록 |
| E-09 | 급여 상세 | `/payroll/:id` | `PayrollDetailScreen` | `GET /payroll/{id}` | 급여 상세 정보 |

### 관리자(Admin) 화면

| # | 화면명 | 라우트 경로 | Screen 클래스 | Backend API | 설명 |
|---|--------|-----------|--------------|-------------|------|
| A-01 | 관리자 로그인 | `/admin/login` | `AdminLoginScreen` | `POST /auth/login` | 관리자 전용 로그인 (역할 검증 포함) |
| A-02 | 대시보드 | `/admin/dashboard` | `AdminDashboardScreen` | 복합 API | 출퇴근 요약, 최근 활동 |
| A-03 | 매장 목록 | `/admin/stores` | `StoreListScreen` | `GET /stores` | 매장 목록 조회 |
| A-04 | 매장 생성 | `/admin/stores/new` | `StoreFormScreen` | `POST /stores` | 새 매장 등록 |
| A-05 | 매장 수정 | `/admin/stores/:storeId/edit` | `StoreFormScreen(storeId)` | `PUT /stores/{id}` | 매장 정보 수정 |
| A-06 | 근로자 목록 | `/admin/employees` | `EmployeeListScreen` | `GET /employees` | 근로자 목록 조회 |
| A-07 | 근로자 등록 | `/admin/employees/new` | `EmployeeFormScreen` | `POST /employees` | 새 근로자 등록 |
| A-08 | 근로자 수정 | `/admin/employees/:employeeId/edit` | `EmployeeFormScreen(employeeId)` | `PUT /employees/{id}` | 근로자 정보 수정 |
| A-09 | 근무 일정 | `/admin/schedules` | `ScheduleCalendarScreen` | `GET /schedules`, `POST /schedules` | 근무 일정 캘린더 관리 |
| A-10 | 출퇴근 관리 | `/admin/attendance` | `AttendanceManagementScreen` | `GET /attendance/records` | 전체 출퇴근 기록 관리 |
| A-11 | 휴가 관리 | `/admin/leaves` | `LeaveManagementScreen` | `GET /leaves`, `POST /leaves/{id}/approve`, `POST /leaves/{id}/reject` | 휴가 신청 승인/거부 |
| A-12 | 급여 관리 | `/admin/payroll` | `PayrollManagementScreen` | `GET /payroll`, `POST /payroll/calculate`, `POST /payroll/batch` | 급여 계산 및 관리 |

### 공유 위젯 (Shared Widgets)

| 위젯명 | 클래스명 | 용도 |
|--------|---------|------|
| 관리자 앱바 | `AdminAppBar` | 관리자 화면 상단 바 (사용자 정보 표시, 역할 표시) |
| 관리자 레이아웃 | `AdminLayout` | 반응형 레이아웃 (768px 기준 모바일/데스크톱 분기) |
| 관리자 사이드바 | `AdminSidebar` | 관리자 네비게이션 메뉴 (Drawer 기반) |

### 대시보드 위젯

| 위젯명 | 클래스명 | 용도 |
|--------|---------|------|
| 출퇴근 요약 | `AttendanceSummaryWidget` | 대시보드 출퇴근 현황 요약 카드 |
| 최근 활동 | `RecentActivitiesWidget` | 대시보드 최근 활동 목록 |

### 다이얼로그

| 위젯명 | 클래스명 | 용도 |
|--------|---------|------|
| 출퇴근 조정 | `AttendanceAdjustDialog` | 출퇴근 기록 수동 조정 |
| 휴가 상세 | `LeaveDetailDialog` | 휴가 신청 상세 정보 및 승인/거부 |
| 급여 상세 | `PayrollDetailDialog` | 급여 상세 정보 조회 |
| 일정 폼 | `ScheduleFormDialog` | 근무 일정 등록/수정 폼 |

---

## 주요 의존성

| 카테고리 | 패키지 | 버전 | 용도 |
|---------|--------|------|------|
| 상태 관리 | `flutter_riverpod` | ^2.5.1 | 상태 관리 |
| API 통신 | `dio` | ^5.4.3 | HTTP 클라이언트 |
| API 통신 | `retrofit` | ^4.1.0 | 타입 안전 API 클라이언트 생성 |
| 직렬화 | `json_annotation` | ^4.9.0 | JSON 직렬화 어노테이션 |
| 보안 | `flutter_secure_storage` | ^9.0.0 | 토큰/인증정보 안전 저장 |
| 날짜 | `intl` | ^0.19.0 | 날짜/시간 포맷 (ko_KR) |
| 날짜 | `table_calendar` | ^3.1.2 | 캘린더 UI 위젯 |
| 라우팅 | `go_router` | ^13.2.0 | 선언적 라우팅 |
| UI | `flutter_svg` | ^2.0.10 | SVG 이미지 렌더링 |
| UI | `cached_network_image` | ^3.3.1 | 네트워크 이미지 캐싱 |
| 코드 생성 | `freezed` / `freezed_annotation` | ^2.5.2 / ^2.4.1 | 불변 데이터 클래스 생성 |
| 로깅 | `logger` | ^2.3.0 | 구조화된 로깅 |
| 환경 변수 | `flutter_dotenv` | ^5.1.0 | .env 파일 로딩 |
| 테스팅 | `mockito` | ^5.4.4 | 단위 테스트 모킹 |
| 테스팅 | `patrol` | ^3.14.0 | E2E 테스트 |
| 린팅 | `flutter_lints` | ^6.0.0 | 코드 스타일 검사 |
