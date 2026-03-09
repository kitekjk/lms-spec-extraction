# LMS-E2E-004: 스케줄관리흐름

## 기본 정보
- type: e2e_test_spec
- tool: agent-browser
- 관련 화면: LMS-SCREEN-004

## 관련 Backend Spec
- LMS-API-SCH-001 (근무 일정 CRUD API)
- LMS-SCH-001 (근무일정 등록 Use Case), LMS-SCH-002 (근무일정 수정 Use Case), LMS-SCH-003 (근무일정 삭제 Use Case), LMS-SCH-004 (근무일정 조회 Use Case)
- LMS-API-EMP-001 (근로자 목록 조회 API)

## 테스트 데이터 준비 방법
- init-data.md 기본 데이터 활용
- 테스트 전용 시딩 API: POST /api/v1/test/seed
- 시딩 시나리오: 강남점 이번 주 근무 일정 5건 (김민수 3건, 이지영 2건), 확정 일정 2건, 미확정 일정 3건

## 테스트 시나리오

### TC-FE-004-01: MANAGER 주간 일정 데이터 있는 상태 조회 (E2E)
- Given:
  - Backend 데이터: 강남점(store-001) 이번 주 근무 일정 5건 (김민수: 월/수/금 09:00~18:00, 이지영: 화/목 10:00~19:00), 확정 2건, 미확정 3건
  - MANAGER(manager.gangnam@lms.com)로 로그인 완료
- When: /schedule 페이지 접속
- Then:
  - 주간 일정 캘린더: 5건 일정 표시
  - 월요일 셀: "김민수 09:00 ~ 18:00" 텍스트 표시
  - 화요일 셀: "이지영 10:00 ~ 19:00" 텍스트 표시
  - 확정 일정: 파란색 배경 배지 2건 표시
  - 미확정 일정: 회색 배경 배지 3건 표시

### TC-FE-004-02: 빈 주간 일정 조회 (E2E)
- Given:
  - Backend 데이터: 강남점(store-001) 다음 주 근무 일정 0건
  - MANAGER(manager.gangnam@lms.com)로 로그인 완료
- When:
  - /schedule 페이지 접속
  - 다음 주(>) 버튼 클릭
- Then:
  - 주간 일정 캘린더: "해당 주에 등록된 근무 일정이 없습니다" 메시지 표시
  - 캘린더 셀 모두 빈 상태 표시

### TC-FE-004-03: MANAGER 일정 등록 (E2E)
- Given:
  - Backend 데이터: 강남점(store-001) 직원 목록 (김민수, 이지영), 다음 주 월요일 일정 없음
  - MANAGER(manager.gangnam@lms.com)로 로그인 완료
- When:
  - /schedule 페이지 접속
  - 다음 주(>) 버튼 클릭
  - 월요일 빈 셀 클릭
  - 직원 드롭다운에서 "김민수" 선택
  - 시작 시간 "09:00" 입력
  - 종료 시간 "18:00" 입력
  - "등록" 버튼 클릭
- Then:
  - "근무 일정이 등록되었습니다." 메시지 표시
  - 월요일 셀에 "김민수 09:00 ~ 18:00" 텍스트 표시

### TC-FE-004-04: EMPLOYEE 권한별 화면 차이 (E2E)
- Given:
  - Backend 데이터: 강남점 이번 주 일정 5건 (김민수 3건, 이지영 2건)
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인
- When: /schedule 페이지 접속
- Then:
  - 주간 일정 캘린더: 본인(김민수) 일정 3건만 표시
  - 이지영 일정: 미표시
  - 일정 등록 모달: 빈 셀 클릭 시 등록 모달 미표시 (EMPLOYEE 권한)
  - 일정 수정/삭제 버튼: 미표시

### TC-FE-004-05: 일정 조회 API 에러 시 동작 (E2E)
- Given:
  - Backend API 응답: 500 (일정 조회 API 오류)
- When: /schedule 페이지 접속
- Then:
  - "근무 일정을 불러올 수 없습니다. 다시 시도해주세요." 에러 메시지 표시
  - 재시도 버튼 표시
  - 주간 네비게이션은 정상 표시 (에러와 무관)
