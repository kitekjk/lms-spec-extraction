# LMS Frontend - 네이밍 가이드

## 기본 정보
- type: frontend_naming_guide
- language: Dart
- framework: Flutter

---

## 파일 네이밍

### 규칙: snake_case
모든 Dart 파일은 `snake_case.dart` 형식을 따른다.

### 파일 유형별 접미사 패턴

| 유형 | 접미사 패턴 | 실제 예시 |
|------|-----------|----------|
| Screen (화면) | `_screen.dart` | `login_screen.dart`, `home_screen.dart`, `check_in_out_screen.dart` |
| Widget (위젯) | `_widget.dart`, `_dialog.dart` | `attendance_summary_widget.dart`, `leave_detail_dialog.dart` |
| 레이아웃 | `_layout.dart`, `_sidebar.dart`, `_app_bar.dart` | `admin_layout.dart`, `admin_sidebar.dart`, `admin_app_bar.dart` |
| API Service | `_service.dart`, `_api_service.dart` | `auth_service.dart`, `store_api_service.dart` |
| Provider | `_provider.dart` | `auth_provider.dart`, `store_provider.dart`, `dio_provider.dart` |
| Model (도메인) | 도메인명 그대로 | `store.dart`, `employee.dart`, `work_schedule.dart` |
| Model (DTO) | `_request.dart`, `_response.dart` | `login_request.dart`, `login_response.dart` |
| State | `_state.dart` | `attendance_state.dart`, `admin_auth_state.dart`, `leave_state.dart` |
| Status/Type (enum) | `_status.dart`, `_type.dart` | `attendance_status.dart`, `leave_status.dart`, `leave_type.dart` |
| Config | `_config.dart` | `env_config.dart`, `theme_config.dart` |
| Exception | `_exception.dart`, `_handler.dart` | `api_exception.dart`, `error_handler.dart` |
| Router | `_router.dart`, `_names.dart` | `app_router.dart`, `route_names.dart` |
| Storage | `_storage.dart`, `_keys.dart` | `secure_storage.dart`, `storage_keys.dart` |

### 관리자 vs 근로자 파일 구분
- 관리자 전용 파일: `admin_` 접두사 사용 (예: `admin_login_screen.dart`, `admin_dashboard_screen.dart`, `admin_auth_service.dart`)
- 근로자 전용 파일: 접두사 없음 (예: `login_screen.dart`, `home_screen.dart`, `auth_service.dart`)
- 관리자 화면용 API Service: `_api_service.dart` 접미사 (예: `store_api_service.dart`, `employee_api_service.dart`)
- 근로자 화면용 API Service: `_service.dart` 접미사 (예: `auth_service.dart`, `attendance_service.dart`)

---

## 클래스 네이밍

### 규칙: PascalCase

### 클래스 유형별 패턴

| 유형 | 패턴 | 실제 예시 |
|------|------|----------|
| Screen | `{Feature}Screen` | `LoginScreen`, `HomeScreen`, `CheckInOutScreen` |
| Admin Screen | `{Admin}{Feature}Screen` / `{Feature}{Action}Screen` | `AdminLoginScreen`, `AdminDashboardScreen`, `StoreListScreen`, `StoreFormScreen` |
| Widget | `{Feature}{Role}Widget` | `AttendanceSummaryWidget`, `RecentActivitiesWidget` |
| Dialog | `{Feature}{Action}Dialog` | `AttendanceAdjustDialog`, `LeaveDetailDialog`, `ScheduleFormDialog` |
| Layout | `{Scope}Layout` | `AdminLayout` |
| AppBar | `{Scope}AppBar` | `AdminAppBar` |
| Sidebar | `{Scope}Sidebar` | `AdminSidebar` |
| API Service | `{Feature}Service` / `{Feature}ApiService` | `AuthService`, `StoreApiService`, `EmployeeApiService` |
| Admin Service | `Admin{Feature}Service` / `{Feature}ApiService` | `AdminAuthService`, `StoreApiService` |
| StateNotifier | `{Feature}Notifier` | `AuthNotifier`, `StoreNotifier` |
| State | `{Feature}State` | `AuthState`, `AdminAuthState`, `AttendanceState` |
| Model (도메인) | 도메인명 | `Store`, `Employee`, `WorkSchedule`, `AdminUser`, `UserInfo` |
| Model (DTO) | `{Action}Request` / `{Action}Response` | `LoginRequest`, `LoginResponse` |
| Config | `{Target}Config` | `EnvConfig`, `ThemeConfig` |
| Exception | `{Type}Exception` | `ApiException`, `UnauthorizedException`, `NetworkException` |
| Handler | `{Target}Handler` | `ErrorHandler` |
| Storage | `{Type}Storage` | `SecureStorage` |
| Keys 상수 | `{Target}Keys` | `StorageKeys` |
| Endpoints 상수 | `Api{Target}` | `ApiEndpoints` |
| Route 상수 | `RouteNames` | `RouteNames` |
| API Client | `ApiClient` | `ApiClient` |
| Interceptor | `ApiInterceptor` | `ApiInterceptor` |

---

## 변수/필드 네이밍

### 규칙: camelCase

### 패턴

| 유형 | 패턴 | 실제 예시 |
|------|------|----------|
| private 인스턴스 | `_camelCase` | `_dio`, `_storage`, `_apiService`, `_ref`, `_instance` |
| public 인스턴스 | `camelCase` | `dio`, `user`, `isAuthenticated`, `isLoading` |
| 상수 (static const) | `camelCase` | `accessToken`, `refreshToken`, `userId` |
| boolean | `is{Adjective}` / `has{Noun}` | `isActive`, `isAuthenticated`, `isLoading`, `isAdmin`, `isSuperAdmin` |
| nullable | `{name}?` | `user`, `error`, `storeId`, `storeName` |
| callback | `on{Event}` | `onTap` |

### JSON 키 (API 통신)
- camelCase 사용 (백엔드와 동일)
- 예: `accessToken`, `refreshToken`, `userInfo`, `userId`, `createdAt`

---

## Provider 네이밍

### 규칙: camelCase + Provider/Notifier 접미사

| 유형 | 패턴 | 실제 예시 |
|------|------|----------|
| 읽기 전용 (단건) | `{feature}Provider` | `storeProvider`, `dioProvider`, `secureStorageProvider` |
| 읽기 전용 (목록) | `{feature}sProvider` | `storesProvider` |
| 쓰기 (Notifier) | `{feature}NotifierProvider` | `storeNotifierProvider` |
| 인증 상태 | `{scope}AuthProvider` | `authProvider`, `adminAuthProvider` |
| API Service | `{feature}ApiServiceProvider` / `{feature}ServiceProvider` | `storeApiServiceProvider`, `authServiceProvider` |
| 파라미터 있는 | `FutureProvider.family` | `storeProvider = FutureProvider.family<Store, String>` |

---

## 라우트 네이밍

### 경로(Path): kebab-case + 슬래시 구분

| 유형 | 패턴 | 실제 예시 |
|------|------|----------|
| 근로자 루트 | `/{feature}` | `/login`, `/home`, `/attendance`, `/schedule`, `/leave`, `/payroll` |
| 근로자 하위 | `/{feature}/{sub}` | `/attendance/records`, `/leave/request` |
| 근로자 동적 | `/{feature}/:id` | `/payroll/:id` |
| 관리자 루트 | `/admin/{feature}` | `/admin/login`, `/admin/dashboard`, `/admin/stores` |
| 관리자 생성 | `/admin/{feature}/new` | `/admin/stores/new`, `/admin/employees/new` |
| 관리자 수정 | `/admin/{feature}/:{id}/edit` | `/admin/stores/:storeId/edit`, `/admin/employees/:employeeId/edit` |

### RouteNames 상수: camelCase

| 상수명 | 경로 |
|--------|------|
| `login` | `/login` |
| `home` | `/home` |
| `attendance` | `/attendance` |
| `attendanceRecords` | `/attendance/records` |
| `schedule` | `/schedule` |
| `leave` | `/leave` |
| `leaveRequest` | `/leave/request` |
| `payroll` | `/payroll` |
| `payrollDetail` | `/payroll/:id` |
| `adminLogin` | `/admin/login` |
| `adminDashboard` | `/admin/dashboard` |
| `adminStores` | `/admin/stores` |
| `adminEmployees` | `/admin/employees` |
| `adminSchedules` | `/admin/schedules` |
| `adminAttendance` | `/admin/attendance` |
| `adminLeaves` | `/admin/leaves` |
| `adminPayroll` | `/admin/payroll` |

### GoRouter name 속성: camelCase (RouteNames와 동일 패턴)
- `name: 'login'`, `name: 'adminDashboard'`, `name: 'adminStoreCreate'`, `name: 'adminStoreEdit'`

---

## 메서드 네이밍

### 규칙: camelCase

### API Service 메서드
| 패턴 | 실제 예시 |
|------|----------|
| `get{Entity}` / `getAll{Entity}s` | `getStore(id)`, `getAllStores()` |
| `create{Entity}` | `createStore(name, location)` |
| `update{Entity}` | `updateStore(id, name, location)` |
| `delete{Entity}` | `deleteStore(id)` |
| `login` / `logout` | `login(request)`, `logout()` |
| `refreshToken` | `refreshToken(refreshToken)` |
| `getCurrentUser` | `getCurrentUser()` |

### StateNotifier 메서드
| 패턴 | 실제 예시 |
|------|----------|
| `create{Entity}` | `createStore(name, location)` |
| `update{Entity}` | `updateStore(id, name, location)` |
| `delete{Entity}` | `deleteStore(id)` |
| `login` / `logout` | `login(email, password)`, `logout()` |
| `clearError` | `clearError()` |
| `_check{State}` | `_checkAuthStatus()` |

### 위젯 내부 메서드
| 패턴 | 실제 예시 |
|------|----------|
| `_build{Component}` | `_buildMenuItem(context, ...)` |

---

## 엔드포인트 상수 네이밍

### 규칙: camelCase

| 패턴 | 실제 예시 |
|------|----------|
| 정적 경로 (리소스) | `stores`, `employees`, `schedules`, `leaves`, `payrolls` |
| 정적 경로 (액션) | `login`, `logout`, `refresh`, `checkIn`, `checkOut` |
| 정적 경로 (내 데이터) | `myAttendance`, `mySchedule`, `myLeaveRequests`, `myPayroll` |
| 정적 경로 (상태별) | `pendingLeaves` |
| 정적 경로 (배치) | `calculatePayroll`, `payrollBatch`, `payrollBatchHistory` |
| 동적 경로 (ID) | `storeById(id)`, `employeeById(id)`, `scheduleById(id)` |
| 동적 경로 (액션) | `approveLeave(id)`, `rejectLeave(id)`, `employeeDeactivate(id)` |

---

## Exception 클래스 네이밍

### 규칙: PascalCase + Exception 접미사

| HTTP 상태 | 클래스명 | 코드 상수 |
|-----------|---------|----------|
| (추상) | `ApiException` | - |
| 401 | `UnauthorizedException` | `UNAUTHORIZED` |
| 403 | `ForbiddenException` | `FORBIDDEN` |
| 404 | `NotFoundException` | `NOT_FOUND` |
| 409 | `ConflictException` | `CONFLICT` |
| 422 | `ValidationException` | `VALIDATION_ERROR` |
| 500 | `ServerException` | `SERVER_ERROR` |
| Network | `NetworkException` | `NETWORK_ERROR` |

- 에러 코드는 `UPPER_SNAKE_CASE`

---

## 디렉토리 네이밍

### 규칙: snake_case (단수형)

| 실제 예시 |
|----------|
| `core/api/`, `core/config/`, `core/exception/`, `core/providers/`, `core/router/`, `core/storage/` |
| `features/auth/`, `features/attendance/`, `features/home/`, `features/leave/`, `features/payroll/`, `features/schedule/` |
| `features/admin/auth/`, `features/admin/attendance/`, `features/admin/dashboard/`, `features/admin/employee/`, `features/admin/leave/`, `features/admin/payroll/`, `features/admin/schedule/`, `features/admin/store/` |
| `data/models/`, `data/services/` |
| `domain/models/` |
| `presentation/providers/`, `presentation/screens/`, `presentation/widgets/` |
| `shared/widgets/` |

---

## 기타 네이밍 규칙

### 앱 타이틀
- `'LMS 근태 관리'` (MaterialApp.router의 title)

### 한국어 메시지
- 에러 메시지: 한국어 문장형 (예: `'연결 시간이 초과되었습니다.'`)
- 사이드바 메뉴: 한국어 명사형 (예: `'대시보드'`, `'매장 관리'`, `'근로자 관리'`)
- 역할 표시: `'슈퍼 관리자'`, `'매니저'`

### import 패턴
- 패키지 import: `package:lms_mobile_web/{path}`
- Flutter SDK: `package:flutter/material.dart`
- 외부 패키지: `package:{package_name}/{file}.dart`
