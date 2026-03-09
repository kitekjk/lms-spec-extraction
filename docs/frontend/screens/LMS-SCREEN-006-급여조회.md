# LMS-SCREEN-006: 급여조회

## 기본 정보
- type: screen_spec
- route: /payroll

## 관련 Backend Spec
- LMS-API-PAY-001 (급여 조회/산정 API)
- LMS-PAY-004 (급여 산정 Use Case), LMS-PAY-005 (급여 배치 실행 Use Case), LMS-PAY-006 (급여 조회 Use Case)
- LMS-API-EMP-001 (근로자 정보 조회 API)

## 화면 목적
EMPLOYEE는 본인의 월별 급여 내역을 조회하고, MANAGER는 소속 매장 근로자의 급여 현황을 확인하며, ADMIN은 급여 산정 및 배치 처리를 수행한다.

## 접근 권한
- SUPER_ADMIN: 전체 매장 급여 조회 + 산정 + 배치 처리
- MANAGER: 소속 매장 급여 조회
- EMPLOYEE: 본인 급여 조회만

## 화면 구성 요소

### 급여 기간 선택기
- 표시 데이터: 연도-월 선택기 (예: "2026년 03월"), 이전 월(< 버튼), 다음 월(> 버튼)
- Backend API: GET /api/payrolls?period={YYYY-MM}&storeId={storeId}
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: period (YYYY-MM 형식), storeId (MANAGER의 소속 매장)
  - 응답 매핑: 급여 목록 갱신
- 빈 상태: 기본값 - 이번 달
- 에러 상태: 해당 없음

### 내 급여 상세 카드 (EMPLOYEE 전용)
- 표시 데이터: 기본급(원 단위, 천단위 콤마), 초과근무수당(원), 공제액(원), 총 급여(원, 굵은 글씨), 지급 상태 배지(지급완료: 초록, 미지급: 주황), 산정일(YYYY-MM-DD)
- Backend API: GET /api/payrolls?employeeId={myId}&period={YYYY-MM}
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: employeeId (본인 ID), period (선택한 연월)
  - 응답 매핑: payroll.amount.baseAmount -> 기본급, payroll.amount.overtimeAmount -> 초과근무수당, payroll.amount.deductions -> 공제액, (baseAmount + overtimeAmount - deductions) -> 총 급여, payroll.isPaid -> 지급 상태 배지, payroll.calculatedAt -> 산정일
- 권한: EMPLOYEE만 표시 — MANAGER, SUPER_ADMIN에게는 미표시
- 빈 상태: "해당 월의 급여 내역이 없습니다"
- 에러 상태: "급여 정보를 불러올 수 없습니다. 다시 시도해주세요."

### 매장 급여 목록 (MANAGER/ADMIN 전용)
- 표시 데이터: 테이블 형태 - 직원명, 근로자 유형(REGULAR/IRREGULAR/PART_TIME), 기본급(원), 초과근무수당(원), 공제액(원), 총 급여(원), 지급 상태 배지
- Backend API: GET /api/payrolls?period={YYYY-MM}&storeId={storeId}
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: period (YYYY-MM), storeId (소속 매장 ID)
  - 응답 매핑: payrolls[].employeeName -> 직원명, payrolls[].employeeType -> 근로자 유형, payrolls[].amount.baseAmount -> 기본급, payrolls[].amount.overtimeAmount -> 초과근무수당, payrolls[].amount.deductions -> 공제액, payrolls[].totalAmount -> 총 급여, payrolls[].isPaid -> 지급 상태
- 권한: MANAGER, SUPER_ADMIN만 표시 — EMPLOYEE에게는 미표시
- 빈 상태: "해당 월의 급여 데이터가 없습니다"
- 에러 상태: "급여 목록을 불러올 수 없습니다. 다시 시도해주세요."

### 급여 산정/배치 버튼 영역 (SUPER_ADMIN 전용)
- 표시 데이터: "급여 산정" 버튼 (개별 산정), "배치 처리" 버튼 (전체 일괄 산정), 마지막 산정일시 텍스트
- Backend API: POST /api/payrolls/calculate
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: { period: string, employeeId?: string }
  - 응답 매핑: 산정 성공 시 "급여 산정이 완료되었습니다." 메시지 표시, 목록 갱신
- Backend API: POST /api/payrolls/batch
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: { period: string }
  - 응답 매핑: 배치 성공 시 "급여 배치 처리가 완료되었습니다. ({N}건)" 메시지 표시, 목록 갱신
- 권한: SUPER_ADMIN만 표시 -- MANAGER, EMPLOYEE에게는 미표시
- 빈 상태: 해당 없음
- 에러 상태: "급여 산정에 실패했습니다. 다시 시도해주세요." (산정), "배치 처리에 실패했습니다. 다시 시도해주세요." (배치)

## 사용자 흐름
1. 사용자가 /payroll에 접속하면 이번 달 급여 정보가 표시된다
2. 기간 선택기로 이전/다음 월을 탐색할 수 있다
3. EMPLOYEE: 본인의 급여 상세 카드에서 기본급, 초과근무수당, 공제액, 총 급여를 확인한다
4. MANAGER: 소속 매장 근로자 전체의 급여 목록을 테이블로 확인한다
5. ADMIN: "급여 산정" 버튼 클릭 -> 선택한 월의 급여를 산정한다
6. ADMIN: "배치 처리" 버튼 클릭 -> 전체 근로자 급여를 일괄 산정한다

## 검증 조건
- 기간 선택: 미래 월은 선택 불가 (이번 달까지만)
- 급여 금액: 소수점 2자리까지 표시, 천단위 콤마 포맷
- 이미 지급 완료된 급여는 재산정 불가 표시

## 비기능 요구사항
- 초기 로딩: 2초 이내
- 인터랙션 반응: 100ms 이내
- API 실패 시: 에러 메시지 표시 + 재시도 버튼
- 급여 산정 버튼 클릭 후 로딩 스피너 표시 (배치 처리는 수 초 소요 가능)
