# LMS-SCREEN-006: 급여조회

## 기본 정보
- type: screen_spec
- 화면명: 급여 내역 / 급여 상세
- 라우트: `/payroll`, `/payroll/:id`
- 대상 사용자: 직원(EMPLOYEE)

## 관련 Backend Spec
- LMS-API-PAY-001 (급여API)

## 화면 목적
직원이 자신의 월별 급여 내역을 조회하고, 상세 급여 명세(기본급, 수당, 공제, 실수령액)를 확인한다.

## 화면 구성 요소

### 급여 내역 리스트
- 표시 데이터: 급여 목록 카드(기간, 확정/미확정 상태, 실수령액, 근무일수, 근무시간), Pull-to-Refresh 지원
- Backend API: GET /api/payroll/my-payroll
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: 없음
  - 응답 매핑: payrolls[] → 카드 목록, periodString → 기간, isConfirmed → 확정/미확정 Chip, netPay → 실수령액(₩ 형식), workDays → 근무일수, workHours → 근무시간
- 빈 상태: "급여 내역이 없습니다" (Icons.attach_money 아이콘과 함께)
- 에러 상태: "데이터를 불러올 수 없습니다"

### 급여 상세 화면
- 표시 데이터: 기간/매장/상태 헤더 카드, 실수령액 카드(큰 금액 표시), 근무 정보(근무일수/근무시간), 지급 항목(기본급/연장근무수당/야간근무수당/휴일근무수당/총 지급액), 공제 항목(소득세/4대보험/총 공제액)
- Backend API: GET /api/payroll/{id}
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: Path에 payrollId
  - 응답 매핑: payroll → 전체 상세 매핑, baseSalary → 기본급, overtimePay → 연장근무수당, nightWorkPay → 야간근무수당, holidayWorkPay → 휴일근무수당, totalPay → 총 지급액, taxAmount → 소득세, insuranceAmount → 4대보험, totalDeduction → 총 공제액, netPay → 실수령액
- 빈 상태: "급여 정보를 불러올 수 없습니다"
- 에러 상태: "데이터를 불러올 수 없습니다"

## 사용자 흐름

1. 급여 내역 화면에서 월별 급여 목록을 확인한다
2. 각 급여 카드를 탭하면 급여 상세 화면(`/payroll/{id}`)으로 이동한다
3. 상세 화면에서 기본급, 각종 수당, 공제 항목, 실수령액을 확인한다
4. 새로고침 버튼으로 최신 급여 정보를 다시 불러올 수 있다
