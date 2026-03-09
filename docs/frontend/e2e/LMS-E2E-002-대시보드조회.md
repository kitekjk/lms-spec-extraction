# LMS-E2E-002: 대시보드조회

## 기본 정보
- type: e2e_test_spec
- tool: agent-browser
- 관련 화면: LMS-SCREEN-002

## 관련 Backend Spec
- LMS-API-ATT-001 (출퇴근 기록 조회 API)
- LMS-API-SCH-001 (근무 일정 조회 API)
- LMS-API-LEAVE-001 (휴가 요청 조회 API)
- LMS-API-EMP-001 (근로자 정보 조회 API)
- LMS-ATT-004 (출퇴근 기록 조회 Use Case)
- LMS-SCH-004 (근무 일정 조회 Use Case)

## 테스트 데이터 준비 방법
- init-data.md 기본 데이터 활용
- 테스트 전용 시딩 API: POST /api/v1/test/seed
- 시딩 시나리오: 강남점 직원 3명 중 2명 출근, 금일 일정 3건, 휴가 승인대기 1건

## 테스트 시나리오

### TC-FE-002-01: MANAGER 대시보드 데이터 있는 상태 조회 (E2E)
- Given:
  - Backend 데이터: 강남점(store-001) 직원 3명(김민수, 이지영, 박수진), 금일 출근 기록 2건(김민수 09:00 NORMAL, 이지영 09:15 LATE), 금일 근무 일정 3건, 휴가 승인대기 1건(정서연 ANNUAL)
  - MANAGER(manager.gangnam@lms.com)로 로그인 완료
- When: /dashboard 페이지 접속
- Then:
  - 금일 출퇴근 현황 카드: "2/3명 출근" 텍스트 표시
  - 금일 근무 일정 목록: 3건 목록 표시, 각 항목에 직원명과 근무 시간(HH:mm ~ HH:mm) 텍스트 포함
  - 휴가 승인 대기 배지: "1" 숫자 배지 표시

### TC-FE-002-02: MANAGER 대시보드 빈 데이터 조회 (E2E)
- Given:
  - Backend 데이터: 강남점(store-001) 직원 3명 존재, 금일 출근 기록 0건, 금일 근무 일정 0건, 휴가 승인대기 0건
  - MANAGER(manager.gangnam@lms.com)로 로그인 완료
- When: /dashboard 페이지 접속
- Then:
  - 금일 출퇴근 현황 카드: "오늘 출근 기록이 없습니다" 메시지 표시
  - 금일 근무 일정 목록: "오늘 등록된 근무 일정이 없습니다" 메시지 표시
  - 휴가 승인 대기 배지: 미표시 (0건)

### TC-FE-002-03: 대시보드에서 휴가 관리 페이지 이동 (E2E)
- Given:
  - Backend 데이터: 강남점 휴가 승인대기 2건
  - MANAGER(manager.gangnam@lms.com)로 로그인 완료
- When:
  - /dashboard 페이지 접속
  - 휴가 승인 대기 배지 클릭
- Then:
  - /leave 페이지로 이동
  - 승인 대기 목록에 2건 표시

### TC-FE-002-04: EMPLOYEE 대시보드 권한별 화면 차이 (E2E)
- Given:
  - Backend 데이터: 강남점 직원 김민수(emp-001), 금일 출근 기록 1건(09:00 NORMAL), 잔여 연차 13.5일
  - EMPLOYEE(employee1.gangnam@lms.com)로 로그인
- When: /dashboard 페이지 접속
- Then:
  - 금일 출퇴근 현황 카드: "출근 완료 09:00" 텍스트 표시 (본인 상태만)
  - 휴가 승인 대기 배지: 미표시 (EMPLOYEE에게는 미표시)
  - 내 휴가 현황 카드: "잔여 연차: 13.5일" 텍스트 표시

### TC-FE-002-05: 대시보드 API 에러 시 동작 (E2E)
- Given:
  - Backend API 응답: 500 (출퇴근 조회 API 오류)
- When: /dashboard 페이지 접속
- Then:
  - 금일 출퇴근 현황 카드: "출퇴근 현황을 불러올 수 없습니다. 다시 시도해주세요." 에러 메시지 표시
  - 재시도 버튼 표시
  - 다른 카드(일정 목록)는 정상 표시 (독립적 에러 처리)
