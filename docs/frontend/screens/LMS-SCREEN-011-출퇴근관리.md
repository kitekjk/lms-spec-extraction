# LMS-SCREEN-011: 출퇴근관리

## 기본 정보
- type: screen_spec
- 화면명: 출퇴근 기록 관리
- 라우트: `/admin/attendance`
- 대상 사용자: 관리자(MANAGER, SUPER_ADMIN)

## 관련 Backend Spec
- LMS-API-ATT-001 (출퇴근API)
- LMS-API-STORE-001 (매장API)

## 화면 목적
관리자가 매장별 직원 출퇴근 기록을 조회하고, 필요 시 출퇴근 시간을 수정(조정)한다.

## 화면 구성 요소

### 필터 영역
- 표시 데이터: "출퇴근 기록 조회" 타이틀, 매장 선택 드롭다운, 시작일/종료일 선택
- Backend API: GET /api/stores
  - 참조 Spec: LMS-API-STORE-001
  - 요청 파라미터: 없음
  - 응답 매핑: stores[] → 매장 드롭다운 항목
- 빈 상태: "매장을 선택하여 출퇴근 기록을 조회하세요"
- 에러 상태: "매장 목록 로드 실패: {에러 메시지}"

### 출퇴근 기록 목록
- 표시 데이터: 총 건수, 상태별 통계 Chip(정상/지각/조퇴/결근 각 건수), 기록 리스트(직원명, 상태 Chip, 날짜, 출근시간, 퇴근시간, 근무시간, 비고), 수정 버튼
- Backend API: GET /api/attendance/records
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: `?storeId={매장ID}&startDate={시작일}&endDate={종료일}`
  - 응답 매핑: records[] → 리스트, employeeName → 직원명, status.displayName → 상태 Chip, attendanceDate → 날짜, checkInTime → 출근시간, checkOutTime → 퇴근시간, actualWorkHours → 근무시간, note → 비고
- 빈 상태: "해당 기간의 출퇴근 기록이 없습니다"
- 에러 상태: 에러 아이콘 + "오류: {에러 메시지}"
- 상태 색상: normal(초록), late(주황), earlyLeave(파랑), absent(빨강), checkedIn(보라)

### 출퇴근 시간 수정 다이얼로그
- 표시 데이터: 근로자 정보(이름/날짜), 원본 출근/퇴근 시간 카드, 수정할 출근/퇴근 시간 선택기(변경 시 편집 아이콘 표시), 수정 사유 입력 필드(필수)
- Backend API: PUT /api/attendance/records/{recordId}
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: `{ "adjustedCheckInTime": "ISO 8601", "adjustedCheckOutTime": "ISO 8601", "reason": "string" }`
  - 응답 매핑: 성공 시 SnackBar "출퇴근 시간이 수정되었습니다", 다이얼로그 닫기
- 빈 상태: "수정할 시간을 선택해 주세요"
- 에러 상태: SnackBar "오류: {에러 메시지}"
- 유효성 검증:
  - 수정 사유: 필수, 최소 5자
  - 퇴근 시간 > 출근 시간
  - 변경사항이 없으면 제출 불가

## 사용자 흐름

1. 매장을 선택하고 기간을 설정하여 출퇴근 기록을 조회한다
2. 상태별 통계 Chip으로 전체 현황을 파악한다
3. 각 기록의 수정 아이콘을 눌러 시간 수정 다이얼로그를 연다
4. 원본 시간을 확인하고 수정할 시간을 선택한다
5. 수정 사유(최소 5자)를 입력하고 "수정" 버튼을 누른다
6. 수정 성공 시 목록이 갱신된다
