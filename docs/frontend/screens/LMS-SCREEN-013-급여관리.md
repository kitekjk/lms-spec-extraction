# LMS-SCREEN-013: 급여관리

## 기본 정보
- type: screen_spec
- 화면명: 급여 관리
- 라우트: `/admin/payroll`
- 대상 사용자: 관리자(MANAGER, SUPER_ADMIN)

## 관련 Backend Spec
- LMS-API-PAY-001 (급여API)

## 화면 목적
관리자가 월별 급여 내역을 조회하고, 급여 일괄 계산을 실행하며, 개별 급여 명세를 확인한다.

## 화면 구성 요소

### 기간 선택 및 배치 실행 영역
- 표시 데이터: "급여 내역 조회" 타이틀, "급여 일괄 계산" 버튼(파란색), 월 선택기(이전/다음/오늘 버튼, yyyy년 MM월 형식)
- Backend API: POST /api/payroll/batch
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: `{ "period": "YYYY-MM" }`
  - 응답 매핑: 성공 시 SnackBar "급여 계산이 완료되었습니다", 목록 갱신
- 빈 상태: "기간을 선택해 주세요"
- 에러 상태: SnackBar 에러 메시지

### 급여 통계 헤더
- 표시 데이터: 총 인원, 확정 인원, 미확정 인원, 총 지급액(₩ 형식) - 각각 아이콘과 색상으로 구분
- Backend API: GET /api/payroll
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: `?period={YYYY-MM}`
  - 응답 매핑: payrolls.length → 총 인원, isConfirmed 필터 → 확정/미확정, sum(netPay) → 총 지급액
- 빈 상태: "해당 기간의 급여 내역이 없습니다"
- 에러 상태: 에러 아이콘 + "오류: {에러 메시지}"

### 급여 목록
- 표시 데이터: 직원별 급여 리스트(직원명, 매장 태그, 확정/미확정 Chip, 근무일수, 근무시간, 기본급, 수당, 실지급액)
- Backend API: GET /api/payroll
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: `?period={YYYY-MM}`
  - 응답 매핑: payrolls[] → 리스트, employeeName → 직원명, storeName → 매장 태그, isConfirmed → 확정/미확정 Chip, workDays → 근무일수, workHours → 근무시간, baseSalary → 기본급, totalAllowance → 수당, netPay → 실지급액
- 빈 상태: "해당 기간의 급여 내역이 없습니다" (급여 일괄 계산 버튼과 함께)
- 에러 상태: 에러 아이콘 + "오류: {에러 메시지}"

### 급여 일괄 계산 다이얼로그
- 표시 데이터: "급여 일괄 계산" 타이틀, 대상 기간 안내 메시지, 주의사항("이미 계산된 급여는 다시 계산되지 않습니다"), 취소/계산 실행 버튼
- Backend API: POST /api/payroll/batch
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: `{ "period": "YYYY-MM" }`
  - 응답 매핑: 성공 시 SnackBar "급여 계산이 완료되었습니다", 목록 갱신
- 빈 상태: "계산 대상이 없습니다"
- 에러 상태: SnackBar 에러 메시지

### 급여 상세 다이얼로그
- 표시 데이터: "급여 명세서" 타이틀 + 확정/미확정 Chip, 근로자 정보(이름/매장/지급 기간), 근무 정보(근무 일수/근무 시간), 급여 내역(기본급/초과근무 수당/야간근무 수당/휴일근무 수당/총 지급액), 공제 내역(세금/4대보험/총 공제액), 실지급액(강조 표시), 계산 정보(계산일시/확정일시)
- Backend API: GET /api/payroll/{payrollId}
  - 참조 Spec: LMS-API-PAY-001
  - 요청 파라미터: Path에 payrollId
  - 응답 매핑: payroll 전체 필드 → 다이얼로그 상세 매핑
- 빈 상태: "급여 정보가 없습니다"
- 에러 상태: "상세 정보를 불러올 수 없습니다"

## 사용자 흐름

1. 월 선택기로 조회할 기간을 선택한다
2. 해당 기간의 급여 목록과 통계를 확인한다
3. 급여 내역이 없으면 "급여 일괄 계산" 버튼으로 배치를 실행한다
4. 각 직원의 급여 항목을 탭하면 상세 명세 다이얼로그가 표시된다
5. 상세 다이얼로그에서 기본급, 각종 수당, 공제 항목, 실지급액을 확인한다
