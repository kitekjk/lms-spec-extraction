# Frontend 네이밍 가이드

## 기본 정보
- type: frontend_naming_guide

## 파일 네이밍

| 대상 | 패턴 | 예시 |
|------|------|------|
| 페이지 컴포넌트 | page.tsx | app/(protected)/dashboard/page.tsx |
| 레이아웃 | layout.tsx | app/(protected)/layout.tsx |
| 컴포넌트 | PascalCase.tsx | AttendanceSummaryCard.tsx |
| 훅 | camelCase.ts (use 접두사) | useAttendance.ts |
| API 클라이언트 | camelCase.ts | attendance.ts |
| 타입 정의 | camelCase.ts | attendance.ts |
| 유틸리티 | camelCase.ts | dateFormat.ts |
| 상수 | camelCase.ts | constants.ts |
| 테스트 | *.test.tsx / *.spec.ts | AttendanceSummaryCard.test.tsx |

## 컴포넌트 네이밍

| 유형 | 패턴 | 예시 |
|------|------|------|
| 페이지 컴포넌트 | {도메인}Page | DashboardPage, AttendancePage |
| 카드 | {내용}Card | AttendanceSummaryCard, ScheduleListCard |
| 폼 | {동작}Form | LoginForm, LeaveRequestForm |
| 테이블 | {데이터}Table | ScheduleTable, PayrollTable |
| 목록 | {데이터}List | LeaveRequestList, EmployeeList |
| 모달/다이얼로그 | {동작}Modal | LeaveRequestModal, ScheduleDetailModal |
| 버튼 | {동작}Button | CheckInButton, ApproveButton |
| 배지 | {상태}Badge | PendingBadge, StatusBadge |
| 빈 상태 | {도메인}EmptyState | AttendanceEmptyState, ScheduleEmptyState |
| 에러 상태 | {도메인}ErrorState | AttendanceErrorState |
| 로딩 | {도메인}Skeleton | DashboardSkeleton |

## 변수/함수 네이밍

| 대상 | 패턴 | 예시 |
|------|------|------|
| React Query 키 | [도메인, ...params] | ['attendance', { date, storeId }] |
| 훅 반환값 | { data, isLoading, error, mutate } | useAttendance() |
| 이벤트 핸들러 | handle{Event} | handleCheckIn, handleApprove |
| 상태 변수 | is{State} / has{State} | isLoading, hasError |
| API 함수 | {동작}{리소스} | fetchAttendanceRecords, createLeaveRequest |

## data-testid 네이밍

| 대상 | 패턴 | 예시 |
|------|------|------|
| 페이지 | {page}-page | dashboard-page, login-page |
| 폼 | {form}-form | login-form, leave-request-form |
| 입력 필드 | {field}-input | email-input, password-input |
| 버튼 | {action}-button | login-button, check-in-button |
| 카드 | {content}-card | attendance-summary-card |
| 테이블 | {data}-table | schedule-table |
| 목록 항목 | {data}-item-{index} | schedule-item-0 |
| 배지 | {status}-badge | leave-pending-badge |
| 빈 상태 | {domain}-empty | attendance-empty |
| 에러 메시지 | {domain}-error | attendance-error |
| 재시도 버튼 | {domain}-retry-button | attendance-retry-button |
| 요약 텍스트 | {metric}-summary | attendance-summary, schedule-count |

## CSS 클래스 네이밍
- Tailwind CSS 유틸리티 클래스를 기본으로 사용
- 커스텀 클래스가 필요한 경우: kebab-case (예: attendance-card, schedule-grid)
- 상태 클래스: is-{state} (예: is-active, is-disabled, is-error)

## 타입 네이밍

| 대상 | 패턴 | 예시 |
|------|------|------|
| API 요청 타입 | {Action}{Resource}Request | LoginRequest, CreateLeaveRequest |
| API 응답 타입 | {Resource}Response | LoginResponse, AttendanceResponse |
| 엔티티 타입 | {Entity} | Employee, WorkSchedule, LeaveRequest |
| Enum 타입 | {Entity}{Field} | EmployeeType, LeaveStatus, AttendanceStatus |
| Props 타입 | {Component}Props | AttendanceSummaryCardProps |

## 상수 네이밍

| 대상 | 패턴 | 예시 |
|------|------|------|
| 역할 코드 | ROLE_{NAME} | ROLE_SUPER_ADMIN, ROLE_MANAGER, ROLE_EMPLOYEE |
| API 경로 | API_{DOMAIN}_{ACTION} | API_AUTH_LOGIN, API_ATTENDANCE_CHECK_IN |
| 상태 코드 | STATUS_{NAME} | STATUS_PENDING, STATUS_APPROVED |
| 에러 메시지 | ERROR_{DOMAIN}_{CASE} | ERROR_AUTH_INVALID, ERROR_NETWORK |
| 빈 상태 메시지 | EMPTY_{DOMAIN} | EMPTY_ATTENDANCE, EMPTY_SCHEDULE |
