# LMS-SCREEN-005: 휴가관리

## 기본 정보
- type: screen_spec
- route: /leave

## 관련 Backend Spec
- LMS-API-LEAVE-001 (휴가 신청/승인/거부/취소 API)
- LMS-LEAVE-001 (휴가 신청 Use Case), LMS-LEAVE-002 (휴가 승인 Use Case), LMS-LEAVE-003 (휴가 반려 Use Case), LMS-LEAVE-004 (휴가 취소 Use Case), LMS-LEAVE-005 (휴가 조회 Use Case)
- LMS-API-EMP-001 (근로자 정보 조회 API)

## 화면 목적
EMPLOYEE는 휴가를 신청하고 본인의 휴가 내역을 조회하며, MANAGER/ADMIN은 소속 매장 근로자의 휴가 요청을 승인하거나 거부한다.

## 접근 권한
- SUPER_ADMIN: 전체 매장 휴가 요청 관리
- MANAGER: 소속 매장 휴가 요청 승인/거부
- EMPLOYEE: 본인 휴가 신청, 조회, 취소

## 화면 구성 요소

### 잔여 연차 표시 (EMPLOYEE 전용)
- 표시 데이터: 잔여 연차 일수 (예: "잔여 연차: 13.5일"), 프로그레스 바 (사용 비율)
- Backend API: GET /api/employees/{myId}
  - 참조 Spec: LMS-API-EMP-001
  - 요청 파라미터: 본인 employeeId
  - 응답 매핑: remainingLeave -> "잔여 연차: {N}일" 텍스트, (초기 연차 - remainingLeave) / 초기 연차 -> 프로그레스 바 비율
- 권한: EMPLOYEE만 표시 — MANAGER, SUPER_ADMIN에게는 미표시
- 빈 상태: "연차 정보를 확인할 수 없습니다"
- 에러 상태: "연차 정보를 불러올 수 없습니다. 다시 시도해주세요."

### 휴가 신청 폼 (EMPLOYEE 전용)
- 표시 데이터: 휴가 유형 드롭다운(ANNUAL, SICK, PERSONAL, MATERNITY, PATERNITY, BEREAVEMENT, UNPAID), 시작일(DatePicker), 종료일(DatePicker), 신청 사유 텍스트 영역
- Backend API: POST /api/leave-requests
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: { employeeId: string, leaveType: string, startDate: string, endDate: string, reason: string }
  - 응답 매핑: 신청 성공 시 "휴가 신청이 완료되었습니다." 메시지 표시, 내 휴가 목록 갱신
- 권한: EMPLOYEE만 사용 가능 — MANAGER, SUPER_ADMIN에게는 미표시
- 빈 상태: 해당 없음 (폼 초기 상태)
- 에러 상태: 기간 중복 시 "해당 기간에 이미 휴가가 존재합니다.", 잔여 연차 부족 시 "잔여 연차가 부족합니다.", 기타 "휴가 신청에 실패했습니다. 다시 시도해주세요."

### 내 휴가 내역 목록 (EMPLOYEE 전용)
- 표시 데이터: 테이블 형태 - 휴가 유형, 시작일(YYYY-MM-DD), 종료일(YYYY-MM-DD), 상태 배지(PENDING: 주황, APPROVED: 초록, REJECTED: 빨강, CANCELLED: 회색), 취소 버튼 (PENDING/APPROVED 상태만)
- Backend API: GET /api/leave-requests?employeeId={myId}
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: employeeId (본인 ID)
  - 응답 매핑: leaveRequests[].leaveType -> 휴가 유형, leaveRequests[].leavePeriod.startDate -> 시작일, leaveRequests[].leavePeriod.endDate -> 종료일, leaveRequests[].status -> 상태 배지
- Backend API: PUT /api/leave-requests/{id}/cancel
  - 참조 Spec: LMS-API-LEAVE-001
  - 응답 매핑: 취소 성공 시 "휴가가 취소되었습니다." 메시지, 목록 갱신
- 권한: EMPLOYEE만 표시 — MANAGER, SUPER_ADMIN에게는 미표시
- 빈 상태: "신청한 휴가가 없습니다"
- 에러 상태: "휴가 내역을 불러올 수 없습니다. 다시 시도해주세요."

### 승인 대기 목록 (MANAGER/ADMIN 전용)
- 표시 데이터: 테이블 형태 - 신청자명, 휴가 유형, 시작일(YYYY-MM-DD), 종료일(YYYY-MM-DD), 신청 사유, 승인 버튼, 거부 버튼
- Backend API: GET /api/leave-requests?status=PENDING&storeId={storeId}
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: status=PENDING, storeId (소속 매장 ID)
  - 응답 매핑: leaveRequests[].employeeName -> 신청자명, leaveRequests[].leaveType -> 휴가 유형, leaveRequests[].leavePeriod -> 기간, leaveRequests[].reason -> 신청 사유
- Backend API: PUT /api/leave-requests/{id}/approve
  - 참조 Spec: LMS-API-LEAVE-001
  - 응답 매핑: 승인 성공 시 "휴가가 승인되었습니다." 메시지, 목록에서 해당 건 제거
- Backend API: PUT /api/leave-requests/{id}/reject
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: { rejectionReason: string }
  - 응답 매핑: 거부 성공 시 "휴가가 거부되었습니다." 메시지, 목록에서 해당 건 제거
- 권한: MANAGER, SUPER_ADMIN만 표시 — EMPLOYEE에게는 미표시
- 빈 상태: "승인 대기 중인 휴가 요청이 없습니다"
- 에러 상태: "휴가 요청 목록을 불러올 수 없습니다. 다시 시도해주세요."

### 거부 사유 입력 모달 (MANAGER/ADMIN 전용)
- 표시 데이터: 거부 사유 텍스트 입력 필드, 확인 버튼, 취소 버튼
- Backend API: PUT /api/leave-requests/{id}/reject
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: { rejectionReason: string }
  - 응답 매핑: 거부 완료 시 모달 닫힘, 목록 갱신
- 권한: MANAGER, SUPER_ADMIN만 사용 가능
- 빈 상태: 해당 없음
- 에러 상태: "거부 처리에 실패했습니다. 다시 시도해주세요."

## 사용자 흐름
1. EMPLOYEE: /leave 접속 시 잔여 연차 + 휴가 신청 폼 + 내 휴가 내역 목록 표시
2. EMPLOYEE: 휴가 유형 선택 -> 시작일/종료일 선택 -> 사유 입력 -> "신청" 클릭
3. EMPLOYEE: 내 휴가 내역에서 PENDING/APPROVED 상태의 휴가에 "취소" 클릭 -> 확인 후 취소 처리
4. MANAGER: /leave 접속 시 승인 대기 목록 표시
5. MANAGER: "승인" 클릭 -> 즉시 승인 처리
6. MANAGER: "거부" 클릭 -> 거부 사유 입력 모달 -> 사유 입력 후 "확인" -> 거부 처리

## 검증 조건
- 휴가 시작일은 오늘 이후여야 한다
- 종료일은 시작일 이후여야 한다
- 신청 사유는 선택 입력 (빈 값 허용)
- 거부 사유는 필수 입력 (빈 값 불가)
- ANNUAL 유형 신청 시 잔여 연차가 신청 일수보다 많아야 한다

## 비기능 요구사항
- 초기 로딩: 2초 이내
- 인터랙션 반응: 100ms 이내
- API 실패 시: 에러 메시지 표시 + 재시도 버튼
- 승인/거부 버튼 클릭 후 중복 요청 방지
