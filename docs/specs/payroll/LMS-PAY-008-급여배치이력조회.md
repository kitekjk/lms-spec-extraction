# LMS-PAY-008 급여배치이력조회

## 기본 정보
- type: use_case
- id: LMS-PAY-008
- domain: payroll
- last-updated: 2026-03-09

## 관련 정책
- POLICY-NFR-001: 멀티 매장 지원 (§4), 성능 요구사항 (§5)

## 관련 Spec
- LMS-PAY-005-급여배치실행 (선행)
- LMS-API-PAY-001-급여API (GET /api/payroll/batch-history)

## 관련 모델
- **주 모델**: `PayrollBatchHistory` (Entity)
- 참조 모델: `BatchStatus` (Enum: RUNNING, COMPLETED, PARTIAL_SUCCESS, FAILED), `PayrollPeriod` (Value Object)

## 개요
MANAGER 또는 SUPER_ADMIN이 급여 배치 실행 이력을 조회한다. 시작일/종료일 범위로 필터링할 수 있다. 각 이력에는 배치 상태, 대상 근로자 수, 성공/실패 건수, 실행 시간이 포함된다.

## 기본 흐름
1. MANAGER 또는 SUPER_ADMIN이 조회 시작일(startDate, Instant, 선택)과 종료일(endDate, Instant, 선택)을 지정하여 배치 이력 조회를 요청한다.
2. 시스템이 조건에 맞는 PayrollBatchHistory 목록을 조회한다:
   - startDate와 endDate가 모두 지정된 경우: 해당 기간 내 배치 이력을 조회한다.
   - 둘 다 미지정인 경우: 전체 배치 이력을 조회한다.
3. 시스템이 배치 이력 목록을 반환한다 (HTTP 200).

## 대안 흐름
- **AF-1**: 조회 결과가 0건인 경우 → 빈 배열([])을 반환한다. HTTP 200이 반환된다.
- **AF-2**: EMPLOYEE가 배치 이력 조회를 시도하는 경우 → HTTP 403을 반환한다.
- **AF-3**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.

## 검증 조건
- 배치 이력 조회는 MANAGER 또는 SUPER_ADMIN만 가능하다. 위반 시 HTTP 403
- startDate와 endDate가 모두 지정된 경우 startDate <= endDate여야 한다. 위반 시 HTTP 400
- startDate와 endDate는 유효한 Instant 형식(ISO-8601)이어야 한다. 위반 시 HTTP 400

## 비기능 요구사항
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-PAY-008-01: 전체 배치 이력 조회 성공
- **레벨**: Integration
- **Given**: 배치 이력이 5건 존재한다 (COMPLETED 3건, PARTIAL_SUCCESS 1건, FAILED 1건).
- **When**: SUPER_ADMIN이 파라미터 없이 배치 이력을 조회한다 (GET /api/payroll/batch-history).
- **Then**: 5건의 배치 이력이 반환된다. 각 항목에 id, period, storeId, status, totalCount, successCount, failureCount, startedAt, completedAt, errorMessage가 포함된다. HTTP 200이 반환된다.

### TC-PAY-008-02: 기간 범위 필터링 조회 성공
- **레벨**: Integration
- **Given**: 2026-03-01T00:00:00Z ~ 2026-03-31T23:59:59Z 기간에 배치 이력이 2건 존재한다.
- **When**: MANAGER가 startDate=2026-03-01T00:00:00Z, endDate=2026-03-31T23:59:59Z로 조회한다.
- **Then**: 2건의 배치 이력이 반환된다. HTTP 200이 반환된다.

### TC-PAY-008-03: EMPLOYEE의 배치 이력 조회 시도 시 권한 오류
- **레벨**: Unit
- **Given**: EMPLOYEE가 인증되어 있다.
- **When**: EMPLOYEE가 배치 이력 조회를 시도한다.
- **Then**: HTTP 403이 반환된다.
