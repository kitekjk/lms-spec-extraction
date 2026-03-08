# LMS-SCREEN-012: 휴가관리

## 기본 정보
- type: screen_spec
- 화면명: 휴가 관리
- 라우트: `/admin/leaves`
- 대상 사용자: 관리자(MANAGER, SUPER_ADMIN)

## 관련 Backend Spec
- LMS-API-LEAVE-001 (휴가API)
- LMS-API-STORE-001 (매장API)

## 화면 목적
관리자가 휴가 신청을 조회하고, 승인 대기 중인 신청을 승인하거나 반려한다.

## 화면 구성 요소

### 필터 영역
- 표시 데이터: "휴가 신청 관리" 타이틀, 매장 선택 드롭다운, "대기 중만 보기" 스위치(기본 활성)
- Backend API: GET /api/stores
  - 참조 Spec: LMS-API-STORE-001
  - 요청 파라미터: 없음
  - 응답 매핑: stores[] → 매장 드롭다운 항목
- 빈 상태: "매장을 선택하여 휴가 신청을 조회하세요"
- 에러 상태: "매장 목록 로드 실패: {에러 메시지}"

### 휴가 신청 목록
- 표시 데이터: 타이틀 + 총 건수 Chip, 상태별 통계 Chip(대기/승인/반려), 신청 리스트(직원명, 휴가 유형 태그, 상태 Chip, 기간, 총 일수, 사유, 반려 사유), 대기 중 신청 시 승인/반려 버튼, 기타 상태 시 상세 보기 버튼
- Backend API: GET /api/leaves/pending (대기 중만), GET /api/leaves (매장별 전체)
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터(대기 중): 없음
  - 요청 파라미터(매장별): `?storeId={매장ID}`
  - 응답 매핑: requests[] → 리스트, employeeName → 직원명, leaveType.displayName → 유형 태그, status.displayName → 상태 Chip, startDate~endDate → 기간, totalDays → 총 일수, reason → 사유, rejectionReason → 반려 사유
- 빈 상태: "승인 대기 중인 휴가 신청이 없습니다" 또는 "휴가 신청 내역이 없습니다"
- 에러 상태: 에러 아이콘 + "오류: {에러 메시지}"

### 휴가 승인 다이얼로그
- 표시 데이터: "휴가 승인" 확인 다이얼로그 (직원명 포함)
- Backend API: PATCH /api/leaves/{leaveId}/approve
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: Path에 leaveId
  - 응답 매핑: 성공 시 SnackBar "휴가가 승인되었습니다", 목록 갱신
- 빈 상태: "승인할 휴가가 없습니다"
- 에러 상태: SnackBar 에러 메시지

### 휴가 반려 다이얼로그
- 표시 데이터: "휴가 반려" 다이얼로그 (직원명, 반려 사유 입력 필드)
- Backend API: PATCH /api/leaves/{leaveId}/reject
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: `{ "rejectionReason": "string" }`
  - 응답 매핑: 성공 시 SnackBar "휴가가 반려되었습니다", 목록 갱신
- 빈 상태: "반려할 휴가가 없습니다"
- 에러 상태: SnackBar "반려 사유를 입력하세요" (빈 사유 시)

### 휴가 상세 다이얼로그
- 표시 데이터: 상태 Chip, 근로자 정보(이름/매장), 휴가 정보(종류/시작일/종료일/총 일수/신청일), 신청 사유, 승인/반려 정보(처리자/처리일시/반려 사유)
- Backend API: GET /api/leaves
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: `?storeId={매장ID}`
  - 응답 매핑: 선택된 request의 전체 필드 → 다이얼로그 상세 표시
- 빈 상태: "휴가 정보가 없습니다"
- 에러 상태: "상세 정보를 불러올 수 없습니다"

## 사용자 흐름

1. "대기 중만 보기" 스위치가 활성화된 상태에서 승인 대기 중인 신청을 확인한다
2. 승인 아이콘(초록 체크)을 눌러 확인 후 승인한다
3. 반려 아이콘(빨강 취소)을 눌러 반려 사유를 입력하고 반려한다
4. 스위치를 비활성화하고 매장을 선택하여 전체 휴가 내역을 조회한다
5. 각 항목을 탭하면 상세 다이얼로그에서 전체 정보를 확인한다
