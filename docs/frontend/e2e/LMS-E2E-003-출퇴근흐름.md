# LMS-E2E-003: 출퇴근흐름

## 기본 정보
- type: e2e_test_spec
- tool: agent-browser
- 관련 화면: LMS-SCREEN-003

## 관련 Backend Spec
- LMS-API-ATT-001 (출퇴근 기록 조회/처리 API)
- LMS-ATT-001 (출근 Use Case), LMS-ATT-002 (퇴근 Use Case), LMS-ATT-003 (출퇴근 조정 Use Case)
- LMS-API-SCH-001 (근무 일정 조회 API)

## 테스트 데이터 준비 방법
- init-data.md 기본 데이터 활용
- 테스트 전용 시딩 API: POST /api/v1/test/seed
- 시딩 시나리오: 강남점 직원 김민수에게 금일 근무 일정(09:00~18:00) 배정, 출퇴근 기록 없음

## 테스트 시나리오

### TC-FE-003-01: EMPLOYEE 출근 처리 후 기록 조회 (E2E)
- Given:
  - Backend 데이터: 김민수(emp-001) 금일 근무 일정 09:00~18:00, 출퇴근 기록 0건
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인 완료
- When:
  - /attendance 페이지 접속
  - "출근" 버튼 클릭
- Then:
  - "출근 완료: {HH:mm}" 텍스트 표시 (현재 시각)
  - 출근 버튼이 "퇴근" 버튼으로 변경 표시
  - 출퇴근 기록 목록에 금일 기록 1건 표시 (출근 시간 있음, 퇴근 시간 "-", 상태 PENDING)

### TC-FE-003-02: EMPLOYEE 빈 출퇴근 기록 조회 (E2E)
- Given:
  - Backend 데이터: 김민수(emp-001) 이번 주 출퇴근 기록 0건
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인 완료
- When: /attendance 페이지 접속
- Then:
  - 출퇴근 버튼 영역: "출근" 버튼 활성화 상태 표시
  - 출퇴근 기록 목록: "해당 기간의 출퇴근 기록이 없습니다" 메시지 표시

### TC-FE-003-03: MANAGER 출퇴근 기록 조정 (E2E)
- Given:
  - Backend 데이터: 강남점(store-001) 김민수 금일 출근 기록 1건 (출근 09:15, 퇴근 18:00, 상태 LATE)
  - MANAGER(manager.gangnam@lms.com)로 로그인 완료
- When:
  - /attendance 페이지 접속
  - 김민수의 출퇴근 기록 행 클릭
  - 출근 시간을 "09:00"으로 수정
  - 조정 사유에 "교통 사고로 인한 지연, 사전 연락 확인" 입력
  - "저장" 버튼 클릭
- Then:
  - "출퇴근 기록이 조정되었습니다." 메시지 표시
  - 목록에서 김민수 기록의 출근 시간이 "09:00" 텍스트로 갱신
  - 상태 배지가 "정상"으로 변경 표시

### TC-FE-003-04: EMPLOYEE 권한별 화면 차이 (E2E)
- Given:
  - Backend 데이터: 강남점 직원 3명 출퇴근 기록 각 1건
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인
- When: /attendance 페이지 접속
- Then:
  - 출퇴근 버튼 영역: 표시 (본인 출퇴근 처리용)
  - 출퇴근 기록 목록: 본인(김민수) 기록만 1건 표시
  - 출퇴근 조정 모달: 기록 행 클릭 시 조정 모달 미표시 (EMPLOYEE 권한)
  - 다른 직원 기록: 미표시

### TC-FE-003-05: 출퇴근 처리 API 에러 시 동작 (E2E)
- Given:
  - Backend API 응답: 500 (출근 처리 API 오류)
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인 완료
- When:
  - /attendance 페이지 접속
  - "출근" 버튼 클릭
- Then:
  - "출퇴근 처리에 실패했습니다. 다시 시도해주세요." 에러 메시지 표시
  - 재시도 버튼 표시
  - "출근" 버튼이 다시 활성화 상태로 복귀 표시
