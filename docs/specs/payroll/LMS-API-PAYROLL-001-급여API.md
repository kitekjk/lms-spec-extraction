# LMS-API-PAYROLL-001: 급여 API

## 기본 정보
- type: api_spec
- domain: payroll
- service: LMS
- base_path: /api/payroll, /api/payroll-policies

## 관련 Spec
- [LMS-PAYROLL-001-급여산정](LMS-PAYROLL-001-급여산정.md)
- [LMS-PAYROLL-002-급여정책관리](LMS-PAYROLL-002-급여정책관리.md)

## 인증/인가
- JWT Bearer Token 필수
- 급여 산정/배치: MANAGER 또는 SUPER_ADMIN
- 급여 조회: 역할별 범위 제한
- 정책 생성/수정/삭제: SUPER_ADMIN만

## 엔드포인트 목록

### 급여 엔드포인트

#### POST /api/payroll/calculate
- 설명: 개별 급여 산정
- 권한: MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "employeeId": "employee-uuid",
    "period": "2026-02",
    "hourlyRate": 10000
  }
  ```
- 응답 (201): PayrollResult
- 응답 (400): PayrollAlreadyCalculatedException, NoAttendanceRecordsFoundException
- 응답 (404): EmployeeNotFoundException

#### GET /api/payroll/{id}
- 설명: 급여 상세 조회 (상세 내역 포함)
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 응답 (200): PayrollWithDetailsResult
- 응답 (404): PayrollNotFoundException

#### GET /api/payroll/my-payroll
- 설명: 본인 급여 조회
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 응답 (200): List\<PayrollResult\>

#### GET /api/payroll
- 설명: 기간별 급여 조회
- 권한: MANAGER, SUPER_ADMIN
- 쿼리 파라미터: period (필수, YYYY-MM)
- 응답 (200): List\<PayrollResult\>

#### POST /api/payroll/batch
- 설명: 배치 급여 산정
- 권한: SUPER_ADMIN
- 요청:
  ```json
  {
    "period": "2026-02",
    "storeId": "store-uuid"
  }
  ```
  - storeId: 선택 (null이면 전체 매장)
- 응답 (200): PayrollBatchHistoryResult

#### GET /api/payroll/batch-history
- 설명: 배치 실행 이력 조회
- 권한: MANAGER, SUPER_ADMIN
- 쿼리 파라미터:
  - startDate (선택)
  - endDate (선택)
- 응답 (200): List\<PayrollBatchHistoryResult\>

### 급여 정책 엔드포인트

#### POST /api/payroll-policies
- 설명: 급여 정책 생성
- 권한: SUPER_ADMIN
- 요청:
  ```json
  {
    "policyType": "OVERTIME_WEEKDAY",
    "multiplier": 1.5,
    "effectiveFrom": "2026-01-01",
    "effectiveTo": null,
    "description": "평일 초과근무 1.5배"
  }
  ```
  - policyType: 필수
  - multiplier: 필수, 0~10
  - effectiveFrom: 필수
  - effectiveTo: 선택 (null이면 무기한)
  - description: 선택
- 응답 (201): PayrollPolicyResult
- 응답 (400): PayrollPolicyPeriodOverlapException

#### GET /api/payroll-policies/active
- 설명: 현재 유효한 정책 조회
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN
- 응답 (200): List\<PayrollPolicyResult\>

#### GET /api/payroll-policies
- 설명: 유형별 정책 조회
- 권한: MANAGER, SUPER_ADMIN
- 쿼리 파라미터: policyType (선택)
- 응답 (200): List\<PayrollPolicyResult\>

#### PUT /api/payroll-policies/{id}
- 설명: 정책 수정
- 권한: SUPER_ADMIN
- 요청:
  ```json
  {
    "multiplier": 2.0,
    "effectiveTo": "2026-12-31",
    "description": "수정된 설명"
  }
  ```
  - 모든 필드 선택
- 응답 (200): PayrollPolicyResult
- 응답 (400): InactivePolicyCannotBeModifiedException
- 응답 (404): PayrollPolicyNotFoundException

#### DELETE /api/payroll-policies/{id}
- 설명: 정책 삭제
- 권한: SUPER_ADMIN
- 응답 (204): No Content
- 응답 (404): PayrollPolicyNotFoundException

## 공통 규칙
- 에러 응답: `{ "code": "PAYROLL001", "message": "..." }`
- 하위호환: POLICY-NFR-001 하위호환 규칙 적용
