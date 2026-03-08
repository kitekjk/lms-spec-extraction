# LMS-PAY-005: 급여배치실행

## 기본 정보
- type: use_case
- domain: payroll

## 관련 Spec
- LMS-API-PAY-001 (급여API)
- LMS-PAY-004 (급여산정)
- LMS-PAY-008 (급여배치이력조회)

## 개요
SUPER_ADMIN이 급여 기간과 매장을 지정하여 대상 직원들의 급여를 일괄 계산하는 배치를 실행한다.

## 관련 모델
- 주 모델: PayrollBatchHistory (Aggregate Root)
- 참조 모델: Payroll, Employee, PayrollBatchHistoryId, BatchStatus, PayrollPeriod, StoreId

## 선행 조건
- 수동 실행: 요청자가 SUPER_ADMIN 권한을 보유해야 한다
- 자동 실행: 시스템 스케줄러에 의해 매월 말일 01:00에 자동 실행
- 대상 직원이 1명 이상 존재해야 한다

## 기본 흐름
1. 관리자가 급여 기간(YYYY-MM)과 매장 ID(선택)를 지정하여 배치 실행을 요청한다
2. 시스템은 대상 직원을 조회한다
   - 매장 ID가 지정된 경우: 해당 매장의 활성 직원만 조회
   - 매장 ID가 없는 경우: 전체 활성 직원 조회
3. 시스템은 배치 이력을 생성한다 (상태: RUNNING, 총 대상 인원 기록)
4. 시스템은 각 직원에 대해 급여 계산을 수행한다
   - 성공 시: 성공 건수 증가
   - 실패 시: 실패 건수 증가, 에러 메시지 기록 (개별 실패가 전체 배치를 중단하지 않음)
5. 시스템은 배치 이력을 완료 처리한다
   - 실패 건수가 0이면: 상태를 COMPLETED로 변경
   - 실패 건수가 1 이상이면: 상태를 PARTIAL_SUCCESS로 변경
6. 시스템은 최종 배치 이력을 저장하고 결과를 반환한다

## 대안 흐름 (자동 배치 스케줄)
- 매월 말일 01:00에 스케줄러가 자동으로 실행한다
- 이전 달(현재월 - 1)의 급여를 전체 매장 대상으로 일괄 산정한다
- 시스템 컨텍스트(payroll-batch-scheduler)로 실행한다

## 예외 흐름
- 대상 직원이 없는 경우: NoEmployeesFoundException 발생
- 배치 실행 중 전체 오류 발생 시: 상태를 FAILED로 변경하고 에러 메시지를 기록한다
- 실행 중 상태가 아닌 배치에 대해 완료/실패 처리 시도 시: 상태 전이 검증 실패

## 검증 조건
- 급여 기간(period)은 YYYY-MM 형식의 유효한 연월이어야 한다
- 매장 ID(storeId)가 제공된 경우 유효한 매장 ID여야 한다
- 배치 상태 전이: RUNNING -> COMPLETED, RUNNING -> PARTIAL_SUCCESS, RUNNING -> FAILED만 허용
- 개별 직원의 급여 계산 실패가 전체 배치를 중단시키지 않아야 한다

## 관련 정책
- POLICY-PAYROLL-001 참조
- POLICY-NFR-001 참조

## 비기능 요구사항
- POLICY-NFR-001 참조
- 배치 처리 중 개별 건 실패 시 전체 트랜잭션이 롤백되지 않아야 한다
- 배치 실행 결과(성공/실패 건수)가 로깅되어야 한다

## 테스트 시나리오

### TC-PAY-005-01: 정상 배치 실행 - 전체 성공 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인하고, 활성 직원 5명이 모두 출퇴근 기록 보유
- When: 2026-03 기간으로 급여 배치 실행 요청
- Then: 배치 이력이 COMPLETED 상태로 완료, 성공 5건, 실패 0건

### TC-PAY-005-02: 부분 성공 배치 실행 (Integration)

- Given: 활성 직원 5명 중 2명은 출퇴근 기록 없음
- When: 급여 배치 실행 요청
- Then: 배치 이력이 PARTIAL_SUCCESS 상태로 완료, 성공 3건, 실패 2건, 실패 에러 메시지 기록

### TC-PAY-005-03: 특정 매장 대상 배치 실행 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인하고, 매장 A에 활성 직원 3명 존재
- When: 매장 A의 2026-03 기간으로 급여 배치 실행 요청
- Then: 매장 A의 직원 3명에 대해서만 급여가 산정됨

### TC-PAY-005-04: 대상 직원이 없는 경우 (Integration)

- Given: 지정한 매장에 활성 직원이 없음
- When: 급여 배치 실행 요청
- Then: NoEmployeesFoundException 발생

### TC-PAY-005-05: 배치 실행 중 전체 오류 발생 시 FAILED 처리 (Integration)

- Given: 배치 실행 중 예상치 못한 시스템 오류 발생
- When: 급여 배치 실행
- Then: 배치 이력 상태가 FAILED로 변경되고 에러 메시지가 기록됨

### TC-PAY-005-06: 배치 상태 전이 검증 - RUNNING에서만 완료 가능 (Unit)

- Given: BatchStatus가 COMPLETED인 배치 이력
- When: 해당 이력에 대해 완료 처리 시도
- Then: 상태 전이 검증 실패 (RUNNING 상태에서만 COMPLETED/PARTIAL_SUCCESS/FAILED로 전이 가능)

### TC-PAY-005-07: 개별 실패가 전체 배치를 중단하지 않음 확인 (Integration)

- Given: 활성 직원 10명 중 첫 번째 직원의 급여 계산에서 오류 발생
- When: 급여 배치 실행
- Then: 나머지 9명의 급여 계산이 정상 수행되고, 실패 1건/성공 9건으로 기록됨

### TC-PAY-005-08: 동시 배치 실행 방지 (Integration)

- Given: 동일 기간에 대한 배치가 이미 RUNNING 상태
- When: 같은 기간에 대해 추가 배치 실행 요청
- Then: 중복 실행이 방지되거나 이미 계산된 급여에 대해 개별 실패로 처리됨

### TC-PAY-005-09: 자동 스케줄 배치 실행 시뮬레이션 (Integration)

- Given: 시스템 스케줄러 컨텍스트(payroll-batch-scheduler)로 실행, 활성 직원 존재
- When: 이전 달 기간으로 전체 매장 대상 배치 자동 실행
- Then: 전체 직원에 대해 급여가 산정되고 배치 이력이 기록됨

### TC-PAY-005-10: 권한 없는 사용자의 배치 실행 거부 (E2E)

- Given: MANAGER 권한 사용자가 로그인한 상태
- When: 급여 배치 실행 API 호출
- Then: 403 Forbidden 응답 반환

### TC-PAY-005-11: 대량 직원 배치 처리 성능 (Integration)

- Given: 활성 직원 1,000명이 모두 출퇴근 기록 보유
- When: 급여 배치 실행 요청
- Then: 배치가 합리적인 시간 내에 완료되고 모든 직원의 급여가 정상 산정됨
