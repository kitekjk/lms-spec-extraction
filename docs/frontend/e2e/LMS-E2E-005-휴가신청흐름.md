# LMS-E2E-005: 휴가신청흐름

## 기본 정보
- type: e2e_test_spec
- tool: agent-browser
- 관련 화면: LMS-SCREEN-005

## 관련 Backend Spec
- LMS-API-LEAVE-001 (휴가 신청/승인/거부/취소 API)
- LMS-LEAVE-001 (휴가 신청 Use Case), LMS-LEAVE-002 (휴가 승인 Use Case), LMS-LEAVE-003 (휴가 반려 Use Case), LMS-LEAVE-004 (휴가 취소 Use Case)
- LMS-API-EMP-001 (근로자 정보 조회 API)

## 테스트 데이터 준비 방법
- init-data.md 기본 데이터 활용
- 테스트 전용 시딩 API: POST /api/v1/test/seed
- 시딩 시나리오: 강남점 김민수 잔여 연차 13.5일, 기존 휴가 신청 2건 (APPROVED 1건, PENDING 1건), 강남점 승인대기 휴가 2건

## 테스트 시나리오

### TC-FE-005-01: EMPLOYEE 휴가 내역 데이터 있는 상태 조회 (E2E)
- Given:
  - Backend 데이터: 김민수(emp-001) 잔여 연차 13.5일, 휴가 신청 2건 (ANNUAL 2026-04-01~04-02 APPROVED, SICK 2026-04-10~04-10 PENDING)
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인 완료
- When: /leave 페이지 접속
- Then:
  - 잔여 연차 표시: "잔여 연차: 13.5일" 텍스트 표시
  - 내 휴가 내역 목록: 2건 표시
  - 1번째 항목: "ANNUAL", "2026-04-01", "2026-04-02", 승인 완료 배지 표시
  - 2번째 항목: "SICK", "2026-04-10", "2026-04-10", 승인 대기 배지 표시, "취소" 버튼 표시

### TC-FE-005-02: EMPLOYEE 휴가 내역 빈 데이터 조회 (E2E)
- Given:
  - Backend 데이터: 이지영(emp-002) 잔여 연차 14.0일, 휴가 신청 0건
  - EMPLOYEE(employee2.gangnam@lms.com)로 로그인 완료
- When: /leave 페이지 접속
- Then:
  - 잔여 연차 표시: "잔여 연차: 14.0일" 텍스트 표시
  - 내 휴가 내역 목록: "신청한 휴가가 없습니다" 메시지 표시

### TC-FE-005-03: EMPLOYEE 휴가 신청 (E2E)
- Given:
  - Backend 데이터: 김민수(emp-001) 잔여 연차 13.5일, 2026-05-01~05-02 기간에 기존 휴가 없음
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인 완료
- When:
  - /leave 페이지 접속
  - 휴가 유형 드롭다운에서 "ANNUAL" 선택
  - 시작일에 "2026-05-01" 선택
  - 종료일에 "2026-05-02" 선택
  - 신청 사유에 "가족 행사 참석" 입력
  - "신청" 버튼 클릭
- Then:
  - "휴가 신청이 완료되었습니다." 메시지 표시
  - 내 휴가 내역 목록에 신규 건 표시: "ANNUAL", "2026-05-01", "2026-05-02", 승인 대기 배지 표시

### TC-FE-005-04: EMPLOYEE 권한별 화면 차이 - 승인 대기 목록 미표시 (E2E)
- Given:
  - Backend 데이터: 강남점 승인대기 휴가 2건 존재
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인
- When: /leave 페이지 접속
- Then:
  - 잔여 연차 표시: 표시 (EMPLOYEE 전용)
  - 휴가 신청 폼: 표시 (EMPLOYEE 전용)
  - 승인 대기 목록: 미표시 (MANAGER 전용이므로 EMPLOYEE에게 미표시)
  - 승인/거부 버튼: 미표시

### TC-FE-005-05: 휴가 신청 API 에러 시 동작 (E2E)
- Given:
  - Backend API 응답: 500 (휴가 신청 API 오류)
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인 완료
- When:
  - /leave 페이지 접속
  - 휴가 유형 "ANNUAL" 선택
  - 시작일 "2026-06-01", 종료일 "2026-06-01" 선택
  - "신청" 버튼 클릭
- Then:
  - "휴가 신청에 실패했습니다. 다시 시도해주세요." 에러 메시지 표시
  - 재시도 버튼 표시
  - 입력한 폼 데이터 유지 (초기화되지 않음)
