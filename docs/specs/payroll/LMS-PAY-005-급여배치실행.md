# LMS-PAY-005 급여배치실행

## 기본 정보
- type: use_case
- id: LMS-PAY-005
- domain: payroll
- last-updated: 2026-03-09

## 관련 정책
- POLICY-PAYROLL-001: 급여 산정 방식 (§1), 급여 계산 시 제외 조건 (§6)
- POLICY-NFR-001: 데이터 무결성 (§2), 성능 요구사항 (§5)

## 관련 Spec
- LMS-PAY-004-급여산정 (개별 산정 로직 참조)
- LMS-PAY-008-급여배치이력조회 (배치 결과 조회)
- LMS-API-PAY-001-급여API (POST /api/payroll/batch)

## 관련 모델
- **주 모델**: `PayrollBatchHistory` (Entity)
- 참조 모델: `Payroll` (Aggregate Root), `PayrollDetail` (Entity), `BatchStatus` (Enum), `PayrollPeriod` (Value Object), `StoreId` (매장 필터링)

## 개요
SUPER_ADMIN이 특정 기간(YYYY-MM)의 급여를 매장 단위 또는 전체 매장에 대해 일괄 산정한다. 시스템은 대상 근로자를 조회하여 개별 급여를 산정하고, PayrollBatchHistory에 배치 실행 결과(성공/실패 건수)를 기록한다. 배치 상태는 RUNNING → COMPLETED/PARTIAL_SUCCESS/FAILED로 전이한다.

## 기본 흐름
1. SUPER_ADMIN이 급여 기간(period, YearMonth)과 매장 ID(storeId, 선택)를 입력한다.
2. 시스템이 PayrollBatchHistory를 RUNNING 상태로 생성한다.
3. storeId가 지정된 경우 해당 매장 소속 활성 근로자 목록을, 미지정인 경우 전체 활성 근로자 목록을 조회한다.
4. 시스템이 totalCount에 대상 근로자 수를 기록한다.
5. 시스템이 각 근로자에 대해 급여 산정(LMS-PAY-004 로직)을 실행한다:
   - 산정 성공 시 successCount를 1 증가시킨다.
   - 산정 실패 시(이미 산정됨, 출퇴근 기록 없음 등) failureCount를 1 증가시키고 해당 근로자를 건너뛴다.
6. 모든 근로자 처리 완료 후, 시스템이 배치 상태를 결정한다:
   - failureCount == 0 → COMPLETED
   - failureCount > 0 && successCount > 0 → PARTIAL_SUCCESS
   - successCount == 0 → FAILED
7. 시스템이 PayrollBatchHistory를 완료 상태로 업데이트하고 completedAt을 기록한다.
8. 시스템이 배치 결과를 반환한다 (HTTP 200).

## 대안 흐름
- **AF-1**: 대상 근로자가 0명인 경우 → COMPLETED 상태(totalCount=0, successCount=0, failureCount=0)로 완료한다.
- **AF-2**: 배치 실행 중 시스템 오류 발생 → FAILED 상태로 변경하고 errorMessage에 오류 내용을 기록한다.
- **AF-3**: MANAGER 또는 EMPLOYEE가 배치를 시도하는 경우 → HTTP 403을 반환한다.
- **AF-4**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.

## 검증 조건
- period는 NOT NULL이어야 한다. 위반 시 HTTP 400
- storeId가 지정된 경우 해당 매장이 DB에 존재해야 한다. 위반 시 HTTP 404
- 배치 상태는 RUNNING → COMPLETED(failureCount == 0) / PARTIAL_SUCCESS(failureCount > 0 && successCount > 0) / FAILED(successCount == 0) 순서로 전이한다
- 매장당 100명 근로자 기준 배치 처리는 10초 이내에 완료되어야 한다
- 배치 요청자의 역할은 SUPER_ADMIN이어야 한다. 위반 시 HTTP 403

## 비기능 요구사항
- **POLICY-NFR-001 §2.1**: 각 근로자의 급여 산정은 개별 트랜잭션으로 처리하여, 하나의 실패가 다른 근로자의 산정에 영향을 주지 않는다.
- **POLICY-NFR-001 §5.2**: 매장당 100명 근로자 기준 10초 이내에 배치 처리를 완료한다.
- **POLICY-NFR-001 §5.4**: Hibernate 배치 사이즈 20으로 INSERT/UPDATE를 배치 처리한다.
- **POLICY-NFR-001 §3**: 배치 실행 시 AuditLog에 기록한다 (EntityType: PAYROLL_BATCH, ActionType: EXECUTE).

## 테스트 시나리오

### TC-PAY-005-01: 매장 단위 급여 배치 실행 성공
- **레벨**: Integration
- **Given**: 매장 A에 활성 근로자 3명이 소속되어 있고, 각각 2026-03 기간에 유효한 출퇴근 기록이 존재한다. 해당 기간의 급여는 아직 산정되지 않았다.
- **When**: SUPER_ADMIN이 period=2026-03, storeId=매장A_ID로 배치를 실행한다.
- **Then**: PayrollBatchHistory가 생성되고, status=COMPLETED, totalCount=3, successCount=3, failureCount=0이다. HTTP 200이 반환된다.

### TC-PAY-005-02: 일부 실패가 포함된 배치 실행
- **레벨**: Integration
- **Given**: 매장 A에 활성 근로자 3명이 소속되어 있고, 1명은 해당 기간에 이미 급여가 산정되어 있다.
- **When**: SUPER_ADMIN이 period=2026-03, storeId=매장A_ID로 배치를 실행한다.
- **Then**: PayrollBatchHistory가 생성되고, status=PARTIAL_SUCCESS, totalCount=3, successCount=2, failureCount=1이다.

### TC-PAY-005-03: 전체 매장 급여 배치 실행
- **레벨**: Integration
- **Given**: 전체 시스템에 활성 근로자 10명이 존재한다.
- **When**: SUPER_ADMIN이 period=2026-03, storeId=null로 배치를 실행한다.
- **Then**: 10명에 대해 급여 산정이 실행되고, PayrollBatchHistory에 결과가 기록된다.

### TC-PAY-005-04: 성능 요구사항 - 100명 기준 10초 이내
- **레벨**: E2E
- **Given**: 매장 A에 100명의 활성 근로자가 소속되어 있고, 각각 해당 기간에 20일의 출퇴근 기록이 존재한다.
- **When**: SUPER_ADMIN이 배치를 실행한다.
- **Then**: 배치가 10초 이내에 완료되고, completedAt - startedAt < 10초이다.
