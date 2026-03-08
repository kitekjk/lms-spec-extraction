# LMS-SCREEN-005: 휴가

## 기본 정보
- type: screen_spec
- 화면명: 휴가 내역 / 휴가 신청
- 라우트: `/leave`, `/leave/request`
- 대상 사용자: 직원(EMPLOYEE)

## 관련 Backend Spec
- LMS-API-LEAVE-001 (휴가API)

## 화면 목적
직원이 자신의 휴가 신청 내역을 조회하고, 새로운 휴가를 신청하며, 대기 중인 휴가를 취소한다.

## 화면 구성 요소

### 휴가 내역 리스트
- 표시 데이터: 휴가 신청 목록 카드(상태 Chip, 휴가 유형 태그, 기간, 총 일수, 사유, 반려 사유, 승인자), Pull-to-Refresh 지원
- Backend API: GET /api/leave-requests/my-requests
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: 없음
  - 응답 매핑: leaveRequests[] → 카드 목록, status → 상태 Chip(대기:주황/승인:초록/반려:빨강/취소:회색), leaveType.displayName → 유형 태그, startDate~endDate → 기간, totalDays → 총 일수, reason → 사유, rejectionReason → 반려 사유, approverName → 승인자
- 빈 상태: "휴가 신청 내역이 없습니다" (Icons.beach_access 아이콘과 함께)
- 에러 상태: "데이터를 불러올 수 없습니다"

### 휴가 취소 버튼
- 표시 데이터: 대기 중(PENDING) 상태의 신청에만 취소 아이콘(Icons.cancel) 표시, 확인 다이얼로그
- Backend API: DELETE /api/leave-requests/{id}
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: Path에 leaveId
  - 응답 매핑: 성공 시 SnackBar "휴가 신청이 취소되었습니다", 목록 갱신
- 빈 상태: "취소할 휴가가 없습니다"
- 에러 상태: SnackBar "취소 실패: {에러 메시지}"

### 휴가 신청 폼 (request 화면)
- 표시 데이터: 휴가 유형 드롭다운(연차/병가/개인사유 등), 시작일 선택, 종료일 선택, 총 일수 표시(자동 계산), 사유 입력(4줄 텍스트 필드), 신청 버튼
- Backend API: POST /api/leave-requests
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: `{ "leaveType": "string", "startDate": "yyyy-MM-dd", "endDate": "yyyy-MM-dd", "reason": "string" }`
  - 응답 매핑: 성공 시 SnackBar "휴가 신청이 완료되었습니다", 이전 화면으로 pop
- 빈 상태: "휴가 신청 양식을 작성해 주세요"
- 에러 상태: SnackBar "휴가 신청 실패: {에러 메시지}"
- 유효성 검증:
  - 사유: 필수
  - 종료일은 시작일 이전일 수 없음 (자동 조정)

## 사용자 흐름

1. 휴가 내역 화면에서 자신의 모든 휴가 신청을 확인한다
2. FAB "휴가 신청" 버튼을 눌러 휴가 신청 화면으로 이동한다
3. 휴가 유형, 기간, 사유를 입력하고 "휴가 신청" 버튼을 누른다
4. 신청 성공 시 내역 화면으로 돌아가며 새로운 신청이 PENDING 상태로 표시된다
5. 대기 중인 신청의 취소 아이콘을 눌러 취소할 수 있다 (확인 다이얼로그)
6. 반려된 신청은 반려 사유가 빨간 컨테이너에 표시된다
7. 승인된 신청은 승인자 이름이 표시된다
