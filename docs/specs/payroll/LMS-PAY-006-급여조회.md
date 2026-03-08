# LMS-PAY-006: 급여조회

## 기본 정보
- type: use_case
- domain: payroll

## 관련 Spec
- LMS-API-PAY-001 (급여API)
- LMS-PAY-004 (급여산정)

## 개요
인증된 사용자가 급여 상세, 본인 급여 내역, 기간별 급여 내역을 조회한다.

## 관련 모델
- 주 모델: Payroll (Aggregate Root)
- 참조 모델: PayrollDetail, PayrollAmount, PayrollPeriod, PayrollId, PayrollDetailId, WorkType, EmployeeId

## 선행 조건
- 인증된 사용자여야 한다

## 기본 흐름

### 흐름 1: 급여 상세 조회 (단건)
1. 사용자가 급여 ID를 지정하여 급여 상세 조회를 요청한다
2. 시스템은 해당 급여를 조회한다
3. 시스템은 해당 급여의 상세 내역(PayrollDetail) 목록을 조회한다
4. 시스템은 급여 정보와 상세 내역을 함께 반환한다
   - 급여 정보: ID, 근로자 ID, 기간, 기본급, 초과근무수당, 총 급여, 지급 여부, 지급일, 계산일, 생성일
   - 상세 내역: ID, 급여 ID, 근무일, 근무유형, 근무시간, 시급, 가산율, 금액
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN

### 흐름 2: 본인 급여 내역 조회
1. 사용자가 본인 급여 내역 조회를 요청한다
2. 시스템은 로그인한 사용자의 ID를 기준으로 전체 급여 내역을 조회한다
3. 시스템은 급여 목록을 반환한다
- 권한: EMPLOYEE, MANAGER, SUPER_ADMIN

### 흐름 3: 기간별 급여 내역 조회
1. 관리자가 급여 기간(YYYY-MM)을 지정하여 조회를 요청한다
2. 시스템은 해당 기간의 전체 급여 내역을 조회한다
3. 시스템은 급여 목록을 반환한다
- 권한: MANAGER, SUPER_ADMIN

## 대안 흐름
- 본인 급여 내역이 없는 경우: 빈 목록을 반환한다
- 해당 기간의 급여 내역이 없는 경우: 빈 목록을 반환한다

## 예외 흐름
- 급여 상세 조회 시 해당 급여를 찾을 수 없는 경우: PayrollNotFoundException (PAYROLL001) 발생

## 검증 조건
- 급여 ID는 비어 있지 않은 유효한 문자열이어야 한다
- 기간별 조회 시 period는 유효한 YearMonth 형식이어야 한다
- 총 급여 계산: 기본급 + 초과근무수당 - 공제액 (소수점 둘째 자리 반올림)
- 기본급, 초과근무수당, 공제액은 각각 0 이상이어야 한다

## 관련 정책
- POLICY-PAYROLL-001 참조 (급여 계산, 총 급여 산출, 공제액 규칙)
- POLICY-NFR-001 참조

## 비기능 요구사항
- POLICY-NFR-001 참조
- 조회 API는 읽기 전용 트랜잭션으로 처리한다

## 테스트 시나리오

### TC-PAY-006-01: 급여 상세 조회 - 정상 (Integration)

- Given: 급여가 계산된 상태이고, 해당 급여에 PayrollDetail 5건 존재
- When: 해당 급여 ID로 상세 조회 요청
- Then: 급여 정보(ID, 근로자 ID, 기간, 기본급, 초과근무수당, 총 급여, 지급 여부)와 상세 내역 5건이 반환됨

### TC-PAY-006-02: 존재하지 않는 급여 상세 조회 (Integration)

- Given: 인증된 사용자가 로그인한 상태
- When: 존재하지 않는 급여 ID로 상세 조회 요청
- Then: PayrollNotFoundException (PAYROLL001) 발생 - "급여를 찾을 수 없습니다: {payrollId}"

### TC-PAY-006-03: 본인 급여 내역 조회 - 정상 (Integration)

- Given: EMPLOYEE 권한 사용자가 로그인하고, 본인의 급여 기록 3건 존재
- When: 본인 급여 내역 조회 요청
- Then: 본인의 급여 목록 3건이 반환됨

### TC-PAY-006-04: 본인 급여 내역이 없는 경우 (Integration)

- Given: EMPLOYEE 권한 사용자가 로그인하고, 급여 기록이 없는 상태
- When: 본인 급여 내역 조회 요청
- Then: 빈 목록이 반환됨

### TC-PAY-006-05: 기간별 급여 내역 조회 - 정상 (Integration)

- Given: MANAGER 권한 사용자가 로그인하고, 2026-03 기간에 급여 기록 10건 존재
- When: 기간 2026-03으로 급여 내역 조회 요청
- Then: 해당 기간의 급여 목록 10건이 반환됨

### TC-PAY-006-06: 기간별 조회 결과 없음 (Integration)

- Given: SUPER_ADMIN 권한 사용자가 로그인한 상태
- When: 급여 기록이 없는 기간으로 조회 요청
- Then: 빈 목록이 반환됨

### TC-PAY-006-07: EMPLOYEE 권한으로 기간별 조회 거부 (E2E)

- Given: EMPLOYEE 권한 사용자가 로그인한 상태
- When: 기간별 급여 내역 조회 API 호출
- Then: 403 Forbidden 응답 반환

### TC-PAY-006-08: 총 급여 계산 검증 (Unit)

- Given: 기본급 1,000,000원, 초과근무수당 250,000원, 공제액 50,000원
- When: 총 급여 계산
- Then: 총 급여 = 1,000,000 + 250,000 - 50,000 = 1,200,000.00 (소수점 둘째 자리 반올림)

### TC-PAY-006-09: 지급 완료된 급여 상세 조회 (E2E)

- Given: 지급 완료(isPaid=true, paidAt 기록)된 급여가 존재
- When: 해당 급여 ID로 상세 조회 API 호출
- Then: 200 OK 응답과 함께 지급 여부 true, 지급일이 포함된 급여 정보 반환
