# LMS-PAY-008: 급여배치이력조회

## 기본 정보
- type: use_case
- domain: payroll

## 관련 Spec
- LMS-API-PAY-001 (급여API)
- LMS-PAY-005 (급여배치실행)

## 개요
관리자가 급여 계산 배치의 실행 이력을 기간별로 조회한다.

## 관련 모델
- 주 모델: PayrollBatchHistory
- 참조 모델: PayrollBatchHistoryId, BatchStatus, PayrollPeriod, StoreId

## 선행 조건
- 요청자가 MANAGER 또는 SUPER_ADMIN 권한을 보유해야 한다
- 인증된 사용자여야 한다

## 기본 흐름
1. 관리자가 배치 이력 조회를 요청한다 (시작일시(선택), 종료일시(선택))
2. 시스템은 조건에 맞는 배치 이력을 조회한다
   - 시작일시/종료일시가 제공된 경우: 해당 기간 내의 이력만 조회
   - 파라미터가 없는 경우: 전체 이력 조회
3. 시스템은 배치 이력 목록을 반환한다
   - 각 이력: ID, 급여 기간, 매장 ID, 배치 상태, 총 대상 수, 성공 수, 실패 수, 시작 시각, 완료 시각, 에러 메시지, 생성일

## 대안 흐름
- 조회 결과가 없는 경우: 빈 목록을 반환한다
- 시작일시만 제공된 경우: 시작일시 이후의 이력을 조회한다
- 종료일시만 제공된 경우: 종료일시 이전의 이력을 조회한다

## 예외 흐름
- 없음 (조회 실패 시 빈 목록 반환)

## 검증 조건
- 시작일시(startDate)와 종료일시(endDate)는 ISO 8601 형식의 Instant 값이어야 한다
- 배치 상태(status)는 RUNNING, COMPLETED, PARTIAL_SUCCESS, FAILED 중 하나여야 한다

## 관련 정책
- POLICY-NFR-001 참조

## 비기능 요구사항
- POLICY-NFR-001 참조
- 조회 API는 읽기 전용 트랜잭션으로 처리한다

## 테스트 시나리오

### TC-PAY-008-01: 전체 배치 이력 조회 - 정상 (Integration)

- Given: MANAGER 권한 사용자가 로그인하고, 배치 이력 5건 존재
- When: 파라미터 없이 배치 이력 조회 요청
- Then: 전체 배치 이력 5건이 반환되고, 각 이력에 ID, 급여 기간, 배치 상태, 성공/실패 수, 시작/완료 시각 포함

### TC-PAY-008-02: 기간 필터 조회 - 시작일시/종료일시 지정 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인하고, 2026-01~2026-03 기간에 배치 이력 3건 존재
- When: 시작일시 2026-01-01T00:00:00Z, 종료일시 2026-03-31T23:59:59Z로 조회 요청
- Then: 해당 기간 내 배치 이력 3건만 반환됨

### TC-PAY-008-03: 시작일시만 지정 조회 (Integration)

- Given: 2026-02-01 이후의 배치 이력이 2건 존재
- When: 시작일시 2026-02-01T00:00:00Z만 지정하여 조회 요청
- Then: 시작일시 이후의 배치 이력 2건이 반환됨

### TC-PAY-008-04: 조회 결과 없음 (Integration)

- Given: 지정한 기간에 배치 이력이 없음
- When: 배치 이력 조회 요청
- Then: 빈 목록이 반환됨

### TC-PAY-008-05: 다양한 배치 상태 이력 포함 검증 (E2E)

- Given: COMPLETED, PARTIAL_SUCCESS, FAILED 상태의 배치 이력이 각 1건씩 존재
- When: 전체 배치 이력 조회 API 호출
- Then: 200 OK 응답과 함께 3건 반환, 각 이력의 status 필드가 올바른 값

### TC-PAY-008-06: EMPLOYEE 권한 사용자의 배치 이력 조회 거부 (E2E)

- Given: EMPLOYEE 권한 사용자가 로그인한 상태
- When: 배치 이력 조회 API 호출
- Then: 403 Forbidden 응답 반환

### TC-PAY-008-07: 에러 메시지 포함 이력 조회 (E2E)

- Given: FAILED 상태의 배치 이력이 에러 메시지와 함께 존재
- When: 배치 이력 조회 API 호출
- Then: 해당 이력의 errorMessage 필드에 에러 내용이 포함되어 반환됨
