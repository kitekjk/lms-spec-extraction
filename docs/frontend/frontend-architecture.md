# LMS Frontend - 아키텍처 규칙

## 기본 정보
- type: frontend_architecture
- framework: Flutter 3.x
- language: Dart
- architecture: Feature-based Clean Architecture
- state-management: Riverpod (StateNotifier + Provider)
- http-client: Dio
- routing: GoRouter

---

## 디렉토리 규칙

### 최상위 구조
```
lib/
├── main.dart                    # 앱 진입점 (EnvConfig 로드, 날짜 초기화, ProviderScope)
├── app.dart                     # MaterialApp.router 설정 (테마, 라우터)
├── core/                        # 앱 전체 공통 인프라
│   ├── api/                     # HTTP 통신 계층
│   ├── config/                  # 환경/테마 설정
│   ├── exception/               # 예외 계층
│   ├── providers/               # 전역 Provider
│   ├── router/                  # 라우팅 설정
│   └── storage/                 # 보안 저장소
├── features/                    # 기능별 모듈 (Feature-based)
│   ├── admin/                   # 관리자 전용 기능
│   │   ├── auth/                # 관리자 인증
│   │   ├── attendance/          # 출퇴근 관리
│   │   ├── dashboard/           # 대시보드
│   │   ├── employee/            # 근로자 관리
│   │   ├── leave/               # 휴가 관리
│   │   ├── payroll/             # 급여 관리
│   │   ├── schedule/            # 일정 관리
│   │   └── store/               # 매장 관리
│   ├── auth/                    # 근로자 인증
│   ├── attendance/              # 근로자 출퇴근
│   ├── home/                    # 근로자 홈
│   ├── leave/                   # 근로자 휴가
│   ├── payroll/                 # 근로자 급여
│   └── schedule/                # 근로자 일정
└── shared/                      # 공유 위젯
    └── widgets/                 # 재사용 UI 컴포넌트
```

### Feature 내부 구조 (Clean Architecture 레이어)
각 Feature 모듈은 다음 3개 레이어로 구성된다.

```
features/{feature}/
├── data/
│   ├── models/                  # DTO (Request/Response) - toJson/fromJson
│   └── services/                # API 서비스 (Dio 호출)
├── domain/
│   └── models/                  # 도메인 모델, 상태(State), enum
└── presentation/
    ├── providers/               # Riverpod Provider/StateNotifier
    ├── screens/                 # 화면 (Screen) 위젯
    └── widgets/                 # 화면 전용 위젯 (Dialog 등)
```

### 레이어 의존 방향
```
presentation → domain → data
         ↓
       core (api, storage, config)
```

- `presentation`은 `domain`과 `data`에 의존 가능
- `domain`은 `data`에 의존 가능
- `data`는 `core/api`, `core/exception`에 의존
- Feature 간 직접 의존 금지 (core 또는 shared를 통해서만 공유)
- 예외: `admin/auth`의 Provider를 `shared/widgets`에서 참조 (AdminAppBar, AdminSidebar)

### 관리자(Admin) vs 근로자(Employee) 분리
- `features/admin/` 하위에 관리자 전용 기능 배치
- `features/` 루트에 근로자 전용 기능 배치
- 같은 도메인이라도 관리자/근로자 화면은 별도 Feature로 분리
  - 예: `features/attendance/` (근로자 출퇴근) vs `features/admin/attendance/` (관리자 출퇴근 관리)
- 각 Feature는 독립적인 data/domain/presentation 레이어를 가짐

---

## API 연동 규칙

### 1. Dio 인스턴스 관리

#### 전역 Provider 방식 (`core/providers/dio_provider.dart`)
```dart
final dioProvider = Provider<Dio>((ref) {
  return ApiClient().dio;
});
```
- `ApiClient`가 Dio 인스턴스를 생성하고 `ApiInterceptor`, `LogInterceptor`를 등록
- Feature의 API Service Provider에서 `dioProvider`를 `ref.watch`하여 주입

#### Feature 내 Provider 방식 (`features/auth/presentation/providers/auth_provider.dart`)
```dart
final dioProvider = Provider<Dio>((ref) {
  return ApiClient().dio;
});
```
- 일부 Feature는 자체 dioProvider를 정의 (auth 등)
- 신규 Feature는 `core/providers/dio_provider.dart`의 전역 Provider 사용을 권장

### 2. API Service 패턴

#### 표준 API Service 구조
```dart
class XxxApiService {
  final Dio dio;
  XxxApiService(this.dio);

  Future<Model> getXxx() async {
    try {
      final response = await dio.get(ApiEndpoints.xxx);
      return Model.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      rethrow; // 또는 throw ErrorHandler.handleError(e);
    }
  }
}
```

- API Service는 `Dio`를 생성자 주입 받음
- 엔드포인트는 `ApiEndpoints` 클래스의 상수/메서드 사용
- 에러 처리: `ErrorHandler.handleError(e)`로 `ApiException` 변환 또는 `rethrow`
- 응답 데이터는 `Model.fromJson()`으로 변환

#### API Service Provider
```dart
final xxxApiServiceProvider = Provider<XxxApiService>((ref) {
  final dio = ref.watch(dioProvider);
  return XxxApiService(dio);
});
```

### 3. 상태 관리 패턴 (Riverpod)

#### 읽기 전용 데이터: FutureProvider
```dart
final xxxListProvider = FutureProvider<List<Model>>((ref) async {
  final apiService = ref.watch(xxxApiServiceProvider);
  return await apiService.getAll();
});

// 파라미터 있는 경우
final xxxProvider = FutureProvider.family<Model, String>((ref, id) async {
  final apiService = ref.watch(xxxApiServiceProvider);
  return await apiService.getById(id);
});
```

#### 쓰기 작업: StateNotifier + StateNotifierProvider
```dart
class XxxNotifier extends StateNotifier<AsyncValue<void>> {
  final XxxApiService _apiService;
  final Ref _ref;

  XxxNotifier(this._apiService, this._ref) : super(const AsyncValue.data(null));

  Future<void> createXxx({...}) async {
    state = const AsyncValue.loading();
    try {
      await _apiService.createXxx(...);
      state = const AsyncValue.data(null);
      _ref.invalidate(xxxListProvider);  // 목록 갱신
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
}
```

#### 인증 상태: StateNotifier + 커스텀 State 클래스
```dart
class AuthState {
  final UserInfo? user;
  final bool isAuthenticated;
  final bool isLoading;
  final String? error;
  // copyWith 패턴
}

class AuthNotifier extends StateNotifier<AuthState> {
  // login, logout, checkAuthStatus
}
```

- State 클래스는 `copyWith` 메서드를 가짐
- AdminAuthState는 `factory` 생성자로 상태 전환 (initial, loading, authenticated, error, unauthenticated)

### 4. 인터셉터 동작 (ApiInterceptor)

#### 요청 인터셉터 (onRequest)
1. `SecureStorage`에서 `access_token` 읽기
2. 토큰이 존재하면 `Authorization: Bearer {token}` 헤더 추가

#### 에러 인터셉터 (onError) - 401 자동 갱신
1. 401 응답 수신
2. `SecureStorage`에서 `refresh_token` 읽기
3. `{baseUrl}/auth/refresh`로 POST 요청 (`refreshToken` 전송)
4. 새 `accessToken` 수신 후 SecureStorage에 저장
5. 원래 요청에 새 토큰 설정 후 재시도
6. 갱신 실패 시 `SecureStorage.deleteAll()` (자동 로그아웃)

### 5. 모델 직렬화 규칙

#### Request 모델
```dart
class XxxRequest {
  final String field;
  XxxRequest({required this.field});
  Map<String, dynamic> toJson() => {'field': field};
}
```

#### Response/Domain 모델
```dart
class XxxModel {
  final String id;
  final String name;

  XxxModel({required this.id, required this.name});

  factory XxxModel.fromJson(Map<String, dynamic> json) {
    return XxxModel(
      id: json['id'] as String,
      name: json['name'] as String,
    );
  }

  Map<String, dynamic> toJson() => {'id': id, 'name': name};
}
```

- JSON 키는 camelCase (백엔드 응답과 동일)
- DateTime은 `DateTime.parse(json['field'] as String)`, 직렬화는 `toIso8601String()`
- nullable 필드는 `json['field'] as Type?`

### 6. 엔드포인트 관리 규칙

- 모든 API 경로는 `ApiEndpoints` 클래스에서 중앙 관리
- 정적 경로: `static const String xxx = '/path'`
- 동적 경로: `static String xxxById(String id) => '/path/$id'`
- Feature의 API Service에서 직접 문자열 경로 사용 금지

---

## 라우팅 규칙

### GoRouter 설정
- 초기 경로: `/login` (RouteNames.login)
- 모든 라우트 경로는 `RouteNames` 클래스에서 상수로 관리
- 에러 페이지: "페이지를 찾을 수 없습니다: {uri}" 표시

### 라우트 구조
- 근로자 라우트: `/login`, `/home`, `/attendance`, `/schedule`, `/leave`, `/payroll`
- 관리자 라우트: `/admin/login`, `/admin/dashboard`, `/admin/stores`, `/admin/employees`, `/admin/schedules`, `/admin/attendance`, `/admin/leaves`, `/admin/payroll`
- 중첩 라우트: `/leave/request`, `/payroll/:id`, `/admin/stores/new`, `/admin/stores/:storeId/edit` 등

### 네비게이션 방식
- 화면 전환: `context.go(route)` (선언적 이동)
- 파라미터: `state.pathParameters['id']` (경로 파라미터)

---

## UI/레이아웃 규칙

### 테마 설정 (ThemeConfig)
- Material Design 3 (`useMaterial3: true`)
- 기본 색상: `Color(0xFF2196F3)` (Blue)
- Light/Dark 테마 모두 지원
- 버튼: 최소 높이 48px, 둥근 모서리 8px, 전체 너비
- 입력 필드: `OutlineInputBorder`, 둥근 모서리 8px, filled
- AppBar: 중앙 정렬, elevation 0

### 반응형 레이아웃 (AdminLayout)
- 분기 기준: `constraints.maxWidth < 768`
- 모바일 (< 768px): Drawer로 사이드바 표시
- 데스크톱 (>= 768px): 좌측 고정 사이드바 (250px) + 우측 콘텐츠
- 콘텐츠 영역 패딩: 24px (all)

### 관리자 사이드바 메뉴
| 아이콘 | 메뉴명 | 라우트 |
|--------|--------|--------|
| `dashboard` | 대시보드 | `/admin/dashboard` |
| `store` | 매장 관리 | `/admin/stores` |
| `people` | 근로자 관리 | `/admin/employees` |
| `calendar_today` | 근무 일정 | `/admin/schedules` |
| `access_time` | 출퇴근 기록 | `/admin/attendance` |
| `beach_access` | 휴가 관리 | `/admin/leaves` |
| `attach_money` | 급여 관리 | `/admin/payroll` |
| `logout` | 로그아웃 | (로그아웃 후 `/admin/login`으로 이동) |

- 현재 경로와 일치하는 메뉴 항목은 시각적으로 강조 (bold, primary color, 배경 하이라이트)
- 모바일에서 메뉴 선택 시 Drawer 자동 닫힘

### 관리자 앱바 (AdminAppBar)
- ConsumerWidget (Riverpod 연동)
- 사용자 이메일 표시 (fontSize: 12)
- 역할 표시: SUPER_ADMIN -> "슈퍼 관리자", 그 외 -> "매니저" (fontSize: 10, bold)
- 우측에 `account_circle` 아이콘 (size: 32)

---

## 접근성 규칙

### 위젯 식별자
- 테스트 대상 위젯에 `Key` 지정 (예: `Key('login_button')`)
- 리스트 항목에 고유 Key 부여

### 의미론적 구조
- `Scaffold` 기반 화면 구성
- `AppBar`로 화면 제목 명시
- `Drawer`로 네비게이션 메뉴 접근 가능 (모바일)
- 버튼에 명확한 텍스트 라벨 사용

### 한국어 지원
- 날짜 포맷: `ko_KR` 로케일 초기화 (`initializeDateFormatting('ko_KR')`)
- 에러 메시지: 한국어로 표시 (예: "연결 시간이 초과되었습니다.", "서버에 연결할 수 없습니다.")
- 역할 표시: 한국어 (슈퍼 관리자, 매니저)
- 404 페이지: "페이지를 찾을 수 없습니다: {uri}"

---

## 보안 규칙

### 토큰 저장
- `flutter_secure_storage` 사용 (플랫폼별 암호화)
- Access Token, Refresh Token, 사용자 정보를 안전하게 저장
- 로그아웃 또는 토큰 갱신 실패 시 `deleteAll()`로 모든 데이터 삭제

### 관리자 접근 제어
- `AdminAuthService.login()`에서 역할 검증 (`user.isAdmin` 확인)
- 관리자가 아닌 사용자가 로그인 시도 시 "관리자 권한이 없습니다." 예외 발생
- `AdminUser.isAdmin`: `isSuperAdmin || isManager` 조건으로 판단

### 요청 헤더
- `Content-Type: application/json`
- `Accept: application/json`
- `Authorization: Bearer {token}` (인터셉터가 자동 추가)

---

## 환경별 빌드

### .env 파일 구조
```
.env.development    # 개발 환경 (기본)
.env.staging        # 스테이징 환경
.env.production     # 프로덕션 환경
```

### 환경 변수
```
API_BASE_URL=http://localhost:8080/api
API_TIMEOUT=30000
LOG_LEVEL=debug
STORAGE_ENCRYPTION_KEY=...
```

### 디버그 로깅
- `EnvConfig.logLevel == 'debug'`일 때 Dio `LogInterceptor` 활성화
- 요청/응답 body 모두 출력

---

## 에셋 관리
```
assets/
├── images/          # 이미지 파일
└── icons/           # 아이콘 파일
```
- `pubspec.yaml`에서 에셋 경로 등록
- SVG: `flutter_svg` 패키지 사용
- 네트워크 이미지: `cached_network_image` 패키지 사용

---

## 테스트 규칙

### 단위 테스트
- `mockito` 패키지로 의존성 모킹
- Provider 테스트: `ProviderContainer` 사용

### E2E 테스트
- `patrol` 패키지 사용
- `integration_test` SDK 포함

### 코드 품질
- `flutter_lints` 패키지로 린팅
- `build_runner`로 코드 생성 (`freezed`, `json_serializable`, `retrofit_generator`)
