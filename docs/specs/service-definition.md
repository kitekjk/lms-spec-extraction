# LMS Backend - 서비스 정의

## 기본 정보
- type: service_definition
- service: lms-backend
- language: Kotlin 2.1.x
- framework: Spring Boot 3.5.x
- jdk: 21
- database: MySQL 8.x
- group: com.example.lms
- artifact: lms-demo

## 서비스 목적과 범위

### 목적
의류/신발 매장 근로자(정규직, 계약직, 아르바이트)의 출퇴근 기록, 근무 일정, 휴가 관리, 급여 산정을 통합 관리하는 백엔드 API 서비스이다.

### 범위

**포함 (In-Scope)**
- 사용자 인증/인가 (JWT 기반 로그인, 역할 기반 접근 제어)
- 매장 등록 및 관리
- 근로자 등록, 매장 배정, 유형 관리
- 근무 일정 생성/수정/확정/삭제
- 출퇴근 체크인/체크아웃 및 상태 평가 (정상, 지각, 조퇴, 결근)
- 휴가 신청/승인/거부/취소 및 연차 차감/복구
- 급여 산정 (기본급 + 초과근무수당 - 공제액) 및 배치 처리
- 급여 정책 관리 (가산율, 유효 기간)
- 감사 로그 (데이터 변경 이력 추적)

**제외 (Out-of-Scope)**
- 프론트엔드 화면 렌더링 (Flutter Web/Mobile이 별도 repo에서 소비)
- 외부 급여/회계 시스템 연동
- GPS/Beacon 기반 위치 출퇴근 검증
- BI 대시보드/리포팅
- 알림 서비스 (Push, SMS, Email)

### 사용자 역할

| 역할 | 코드 | 설명 |
|------|------|------|
| 슈퍼 관리자 | `SUPER_ADMIN` | 전체 매장/사용자/정책 관리. 시스템에서만 생성 가능. |
| 매니저 | `MANAGER` | 소속 매장의 근로자/일정/출퇴근/휴가 관리. |
| 근로자 | `EMPLOYEE` | 본인 출퇴근 체크, 일정 조회, 휴가 신청, 급여 조회. |

### 클라이언트
- Flutter Mobile App (iOS/Android) - 근로자 출퇴근 및 개인 기능
- Flutter Web App - 관리자/매니저 어드민 기능

## 핵심 모델

### Bounded Context 구조

| Bounded Context | 패키지 | Aggregate Root | 설명 |
|----------------|--------|---------------|------|
| User | `model.user` | `User` | 인증/인가 정보 관리 |
| Employee | `model.employee` | `Employee` | 근로자 프로필 및 연차 관리 |
| Store | `model.store` | `Store` | 매장 정보 관리 |
| Attendance | `model.attendance` | `AttendanceRecord` | 출퇴근 기록 관리 |
| Schedule | `model.schedule` | `WorkSchedule` | 근무 일정 관리 |
| Leave | `model.leave` | `LeaveRequest` | 휴가 신청/승인 프로세스 |
| Payroll | `model.payroll` | `Payroll`, `PayrollPolicy` | 급여 산정 및 정책 관리 |
| AuditLog | `model.auditlog` | `AuditLog` | 데이터 변경 이력 추적 |

### User Aggregate

| 필드 | 타입 | 제약 조건 |
|------|------|----------|
| id | `UserId` (UUID) | PK, 자동 생성 |
| email | `Email` (Value Object) | 유니크, 이메일 형식 검증 |
| password | `Password` (Value Object) | BCrypt 인코딩 |
| role | `Role` (Enum) | SUPER_ADMIN, MANAGER, EMPLOYEE |
| isActive | `Boolean` | 기본값 true |
| createdAt | `Instant` | 생성 시점 |
| lastLoginAt | `Instant?` | 마지막 로그인 시점 |

**도메인 규칙:**
- SUPER_ADMIN 역할은 `User.create()`로 생성 불가. 시스템 초기화 시에만 생성.
- 비활성화된 사용자는 로그인 불가.

### Employee Aggregate

| 필드 | 타입 | 제약 조건 |
|------|------|----------|
| id | `EmployeeId` (UUID) | PK, 자동 생성 |
| userId | `UserId` | User 1:1 참조 |
| name | `EmployeeName` (Value Object) | 이름 형식 검증 |
| employeeType | `EmployeeType` (Enum) | REGULAR, IRREGULAR, PART_TIME |
| storeId | `StoreId?` | Store 참조, nullable |
| remainingLeave | `RemainingLeave` (Value Object) | BigDecimal, 0 이상 |
| isActive | `Boolean` | 기본값 true |
| createdAt | `Instant` | 생성 시점 |

**초기 연차 규칙:**

| 근로자 유형 | 초기 연차 (일) |
|------------|--------------|
| REGULAR (정규직) | 15.0 |
| IRREGULAR (계약직) | 11.0 |
| PART_TIME (아르바이트) | 0.0 |

### Store Aggregate

| 필드 | 타입 | 제약 조건 |
|------|------|----------|
| id | `StoreId` (UUID) | PK, 자동 생성 |
| name | `StoreName` (Value Object) | 매장명 검증 |
| location | `StoreLocation` (Value Object) | 주소 |
| createdAt | `Instant` | 생성 시점 |

### AttendanceRecord Aggregate

| 필드 | 타입 | 제약 조건 |
|------|------|----------|
| id | `AttendanceRecordId` (UUID) | PK, 자동 생성 |
| employeeId | `EmployeeId` | Employee 참조 |
| workScheduleId | `WorkScheduleId?` | WorkSchedule 참조, nullable |
| attendanceDate | `LocalDate` | 출근 날짜 |
| attendanceTime | `AttendanceTime` (Value Object) | checkInTime + checkOutTime |
| status | `AttendanceStatus` (Enum) | NORMAL, LATE, EARLY_LEAVE, ABSENT, PENDING |
| note | `String?` | 메모 |
| createdAt | `Instant` | 생성 시점 |

**도메인 규칙:**
- 지각 허용 시간: 10분 (`LATE_TOLERANCE_MINUTES = 10`)
- 퇴근 처리되지 않은 기록은 상태 평가 불가
- 상태 평가는 WorkSchedule의 시작/종료 시간과 실제 출퇴근 시간을 비교하여 자동 결정

### WorkSchedule Aggregate

| 필드 | 타입 | 제약 조건 |
|------|------|----------|
| id | `WorkScheduleId` (UUID) | PK, 자동 생성 |
| employeeId | `EmployeeId` | Employee 참조 |
| storeId | `StoreId` | Store 참조 |
| workDate | `WorkDate` (Value Object) | 근무 날짜 (LocalDate) |
| workTime | `WorkTime` (Value Object) | 시작/종료 시간 (LocalTime) |
| isConfirmed | `Boolean` | 확정 여부, 기본값 false |
| createdAt | `Instant` | 생성 시점 |

**도메인 규칙:**
- 확정된 일정은 시간/날짜 변경 불가
- 주말 근무 여부는 WorkDate에서 판단

### LeaveRequest Aggregate

| 필드 | 타입 | 제약 조건 |
|------|------|----------|
| id | `LeaveRequestId` (UUID) | PK, 자동 생성 |
| employeeId | `EmployeeId` | Employee 참조 |
| leaveType | `LeaveType` (Enum) | ANNUAL, SICK, PERSONAL, MATERNITY, PATERNITY, BEREAVEMENT, UNPAID |
| leavePeriod | `LeavePeriod` (Value Object) | 시작일 ~ 종료일 |
| status | `LeaveStatus` (Enum) | PENDING, APPROVED, REJECTED, CANCELLED |
| reason | `String?` | 신청 사유 |
| approvedBy | `UserId?` | 승인/거부 처리자 |
| approvedAt | `Instant?` | 승인/거부 처리 시점 |
| rejectionReason | `String?` | 거부 사유 (거부 시 필수) |
| createdAt | `Instant` | 생성 시점 |

**도메인 규칙:**
- PENDING 상태에서만 승인/거부 가능
- PENDING 또는 APPROVED 상태에서만 취소 가능
- 거부 시 rejectionReason은 빈 문자열 불가
- 동일 근로자의 다른 휴가와 기간 겹침 체크 (`overlapsWith`)

### Payroll Aggregate

| 필드 | 타입 | 제약 조건 |
|------|------|----------|
| id | `PayrollId` (UUID) | PK, 자동 생성 |
| employeeId | `EmployeeId` | Employee 참조 |
| period | `PayrollPeriod` (Value Object) | YYYY-MM 형식 |
| amount | `PayrollAmount` (Value Object) | baseAmount + overtimeAmount - deductions |
| calculatedAt | `Instant` | 계산 시점 |
| isPaid | `Boolean` | 지급 완료 여부 |
| paidAt | `Instant?` | 지급 시점 |
| createdAt | `Instant` | 생성 시점 |

**도메인 규칙:**
- 이미 지급된 급여는 수정/재계산 불가
- PayrollAmount의 모든 금액 필드는 0 이상
- 총 급여 = baseAmount + overtimeAmount - deductions (소수점 2자리 HALF_UP)

### PayrollPolicy Aggregate

| 필드 | 타입 | 제약 조건 |
|------|------|----------|
| id | `PayrollPolicyId` (UUID) | PK, 자동 생성 |
| policyType | `PolicyType` (Enum) | OVERTIME_WEEKDAY, OVERTIME_WEEKEND, OVERTIME_HOLIDAY, NIGHT_SHIFT, HOLIDAY_WORK, BONUS, ALLOWANCE |
| multiplier | `PolicyMultiplier` (Value Object) | BigDecimal 배율 |
| effectivePeriod | `PolicyEffectivePeriod` (Value Object) | 유효 시작일 ~ 종료일 |
| description | `String?` | 정책 설명 |
| createdAt | `Instant` | 생성 시점 |

**도메인 규칙:**
- 유효하지 않은 정책은 배율 수정 불가
- 특정 날짜의 유효 정책 조회 가능

### AuditLog Aggregate

| 필드 | 타입 | 제약 조건 |
|------|------|----------|
| id | `AuditLogId` (UUID) | PK, 자동 생성 |
| entityType | `EntityType` (Enum) | 대상 엔티티 유형 |
| entityId | `String` | 대상 엔티티 ID |
| actionType | `ActionType` (Enum) | 액션 유형 |
| performedBy | `String` | 수행자 ID |
| performedByName | `String` | 수행자 이름 |
| performedAt | `Instant` | 수행 시점 |
| oldValue | `String?` | 변경 전 값 (JSON) |
| newValue | `String?` | 변경 후 값 (JSON) |
| reason | `String?` | 변경 사유 |
| clientIp | `String?` | 클라이언트 IP |

### DomainContext (공통)

모든 도메인 명령에 전달되는 컨텍스트 객체:

| 필드 | 타입 | 설명 |
|------|------|------|
| userId | `String` | 요청자 ID |
| userName | `String` | 요청자 이름 |
| requestedAt | `Instant` | 요청 시점 |
| clientIp | `String?` | 클라이언트 IP |

## 외부 계약

### 인증 방식
- JWT (JJWT 0.12.x) 기반 Bearer Token 인증
- Access Token + Refresh Token 발급
- `jwt.secretKey`: HS256 서명 키
- `jwt.accessTokenExpiration`: Access Token 유효 시간 (기본 3,600,000ms = 1시간)
- `jwt.refreshTokenExpiration`: Refresh Token 유효 시간 (기본 604,800,000ms = 7일)

### API 기본 규칙
- Base Path: `/api`
- Content-Type: `application/json`
- 인증 헤더: `Authorization: Bearer {accessToken}`
- API 문서: Springdoc OpenAPI (`/swagger-ui.html`)

### API 엔드포인트 목록

| 리소스 | Method | Path | 역할 제한 |
|--------|--------|------|----------|
| 로그인 | POST | `/api/auth/login` | 전체 |
| 토큰 갱신 | POST | `/api/auth/refresh` | 전체 |
| 사용자 등록 | POST | `/api/auth/register` | SUPER_ADMIN |
| 매장 목록 | GET | `/api/stores` | SUPER_ADMIN, MANAGER |
| 매장 등록 | POST | `/api/stores` | SUPER_ADMIN |
| 매장 상세 | GET | `/api/stores/{id}` | SUPER_ADMIN, MANAGER |
| 매장 수정 | PUT | `/api/stores/{id}` | SUPER_ADMIN |
| 매장 삭제 | DELETE | `/api/stores/{id}` | SUPER_ADMIN |
| 근로자 목록 | GET | `/api/employees` | SUPER_ADMIN, MANAGER(소속 매장) |
| 근로자 등록 | POST | `/api/employees` | SUPER_ADMIN, MANAGER(소속 매장) |
| 근로자 상세 | GET | `/api/employees/{id}` | SUPER_ADMIN, MANAGER(소속 매장), EMPLOYEE(본인) |
| 근로자 수정 | PUT | `/api/employees/{id}` | SUPER_ADMIN, MANAGER(소속 매장) |
| 근로자 비활성화 | DELETE | `/api/employees/{id}` | SUPER_ADMIN |
| 일정 목록 | GET | `/api/schedules` | SUPER_ADMIN, MANAGER(소속 매장), EMPLOYEE(본인) |
| 일정 등록 | POST | `/api/schedules` | SUPER_ADMIN, MANAGER(소속 매장) |
| 일정 수정 | PUT | `/api/schedules/{id}` | SUPER_ADMIN, MANAGER(소속 매장) |
| 일정 삭제 | DELETE | `/api/schedules/{id}` | SUPER_ADMIN, MANAGER(소속 매장) |
| 출근 체크 | POST | `/api/attendance/check-in` | SUPER_ADMIN, MANAGER, EMPLOYEE |
| 퇴근 체크 | POST | `/api/attendance/check-out` | SUPER_ADMIN, MANAGER, EMPLOYEE |
| 출퇴근 조정 | PUT | `/api/attendance/{id}/adjust` | SUPER_ADMIN, MANAGER(소속 매장) |
| 휴가 신청 | POST | `/api/leave-requests` | SUPER_ADMIN, MANAGER, EMPLOYEE |
| 휴가 승인 | PUT | `/api/leave-requests/{id}/approve` | SUPER_ADMIN, MANAGER(소속 매장) |
| 휴가 거부 | PUT | `/api/leave-requests/{id}/reject` | SUPER_ADMIN, MANAGER(소속 매장) |
| 휴가 취소 | PUT | `/api/leave-requests/{id}/cancel` | SUPER_ADMIN, MANAGER, EMPLOYEE(본인) |
| 급여 조회 | GET | `/api/payrolls` | SUPER_ADMIN, MANAGER(소속 매장), EMPLOYEE(본인) |
| 급여 산정 | POST | `/api/payrolls/calculate` | SUPER_ADMIN |
| 급여 배치 | POST | `/api/payrolls/batch` | SUPER_ADMIN |
| 급여 정책 목록 | GET | `/api/payroll-policies` | SUPER_ADMIN |
| 급여 정책 등록 | POST | `/api/payroll-policies` | SUPER_ADMIN |
| 급여 정책 수정 | PUT | `/api/payroll-policies/{id}` | SUPER_ADMIN |
| 급여 정책 삭제 | DELETE | `/api/payroll-policies/{id}` | SUPER_ADMIN |
| 헬스 체크 | GET | `/api/health` | 전체 (비인증) |

### HTTP 상태 코드

| 코드 | 용도 |
|------|------|
| 200 | 정상 응답 |
| 201 | 리소스 생성 성공 |
| 400 | 요청 데이터 검증 실패 |
| 401 | 인증 실패 (토큰 없음/만료) |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 409 | 비즈니스 규칙 위반 (중복, 상태 충돌) |
| 500 | 서버 내부 오류 |

## 소유 데이터

### 데이터베이스
- DBMS: MySQL 8.x
- 스키마: `lms_demo`
- 문자셋: UTF-8 (utf8mb4)
- 연결 풀: HikariCP

### 테이블 소유권

| 테이블 | Aggregate | 소유 도메인 |
|--------|-----------|-----------|
| users | User | user |
| employees | Employee | employee |
| stores | Store | store |
| attendance_records | AttendanceRecord | attendance |
| work_schedules | WorkSchedule | schedule |
| leave_requests | LeaveRequest | leave |
| payrolls | Payroll | payroll |
| payroll_details | PayrollDetail | payroll |
| payroll_policies | PayrollPolicy | payroll |
| payroll_batch_histories | PayrollBatchHistory | payroll |
| audit_logs | AuditLog | auditlog |

### ID 생성 전략
- 모든 Aggregate Root의 ID는 UUID v4 (`UUID.randomUUID()`)
- 각 도메인별 inline value class로 래핑 (e.g., `UserId`, `EmployeeId`, `StoreId`)

### 프로파일별 DDL 전략

| 프로파일 | ddl-auto | 용도 |
|---------|----------|------|
| dev | update | 개발 환경 (스키마 자동 갱신) |
| prod | validate | 운영 환경 (스키마 검증만) |
