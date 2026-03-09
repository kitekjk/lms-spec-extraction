# LMS-SCREEN-002: 대시보드

## 기본 정보
- type: screen_spec
- route: /dashboard

## 관련 Backend Spec
- LMS-API-ATT-001 (출퇴근 기록 조회 API)
- LMS-API-SCH-001 (근무 일정 조회 API)
- LMS-API-LEAVE-001 (휴가 요청 조회 API)
- LMS-API-EMP-001 (근로자 목록 조회 API)
- LMS-ATT-004 (출퇴근 기록 조회 Use Case)
- LMS-SCH-004 (근무 일정 조회 Use Case)
- LMS-LEAVE-005 (휴가 조회 Use Case)

## 화면 목적
MANAGER와 ADMIN은 소속 매장의 금일 출퇴근 현황, 근무 일정, 휴가 승인 대기 건을 한눈에 확인하고, EMPLOYEE는 본인의 금일 출퇴근 상태와 다가오는 일정을 확인한다.

## 접근 권한
- SUPER_ADMIN: 전체 매장 데이터 조회
- MANAGER: 소속 매장 데이터 조회
- EMPLOYEE: 본인 데이터만 조회

## 화면 구성 요소

### 금일 출퇴근 현황 카드
- 표시 데이터: 출근 인원수/전체 인원수 (예: "2/3명 출근"), 미출근자 이름 목록
- Backend API: GET /api/attendance?date=2026-03-09&storeId={storeId}
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: date (오늘 날짜, YYYY-MM-DD 형식), storeId (MANAGER의 소속 매장 ID)
  - 응답 매핑: records[].status -> 출근 인원수 집계 (status가 NORMAL, LATE인 건수), records[].employeeName -> 미출근자 이름 목록
- EMPLOYEE 역할: 본인 출퇴근 상태만 표시 (예: "출근 완료 09:00" 또는 "미출근")
- 빈 상태: "오늘 출근 기록이 없습니다"
- 에러 상태: "출퇴근 현황을 불러올 수 없습니다. 다시 시도해주세요."

### 금일 근무 일정 목록
- 표시 데이터: 테이블 형태 - 직원명, 근무 시작 시간(HH:mm), 근무 종료 시간(HH:mm), 확정 여부 배지
- Backend API: GET /api/schedules?startDate=2026-03-09&endDate=2026-03-09&storeId={storeId}
  - 참조 Spec: LMS-API-SCH-001
  - 요청 파라미터: startDate (오늘), endDate (오늘), storeId (MANAGER의 소속 매장 ID)
  - 응답 매핑: schedules[].employeeName -> 직원명, schedules[].workTime.startTime -> 시작 시간, schedules[].workTime.endTime -> 종료 시간, schedules[].isConfirmed -> 확정 배지 (확정/미확정)
- EMPLOYEE 역할: 본인 일정만 표시 (GET /api/schedules?employeeId={myId}&startDate=today&endDate=today)
- 빈 상태: "오늘 등록된 근무 일정이 없습니다"
- 에러 상태: "근무 일정을 불러올 수 없습니다. 다시 시도해주세요."

### 휴가 승인 대기 배지
- 표시 데이터: 승인 대기 건수 숫자 배지 (예: 배지 "2")
- Backend API: GET /api/leave-requests?status=PENDING&storeId={storeId}
  - 참조 Spec: LMS-API-LEAVE-001
  - 요청 파라미터: status=PENDING, storeId (소속 매장 ID)
  - 응답 매핑: leaveRequests.length -> 배지 숫자
- 권한: MANAGER, SUPER_ADMIN만 표시 — EMPLOYEE에게는 미표시
- 빈 상태: 배지 미표시 (0건일 때)
- 에러 상태: 배지 대신 "-" 텍스트 표시

### 내 휴가 현황 카드 (EMPLOYEE 전용)
- 표시 데이터: 잔여 연차 일수 (예: "잔여 연차: 13.5일"), 최근 휴가 신청 상태
- Backend API: GET /api/employees/{myId}
  - 참조 Spec: LMS-API-EMP-001
  - 요청 파라미터: 본인 employeeId
  - 응답 매핑: remainingLeave -> "잔여 연차: {N}일" 텍스트
- 권한: EMPLOYEE만 표시 — MANAGER, SUPER_ADMIN에게는 미표시
- 빈 상태: "휴가 정보를 조회할 수 없습니다"
- 에러 상태: "휴가 현황을 불러올 수 없습니다. 다시 시도해주세요."

## 사용자 흐름
1. 인증된 사용자가 /dashboard에 접속한다
2. 역할에 따라 표시되는 카드가 다르다: MANAGER/ADMIN은 출퇴근 현황 + 일정 목록 + 휴가 대기 배지, EMPLOYEE는 본인 출퇴근 + 본인 일정 + 내 휴가 현황
3. 금일 출퇴근 현황 카드에서 출근/미출근 인원을 확인한다
4. 근무 일정 목록에서 금일 배정된 일정을 확인한다
5. MANAGER는 휴가 승인 대기 배지를 클릭하여 /leave 페이지로 이동할 수 있다
6. 각 카드의 데이터는 페이지 접속 시 병렬로 로딩된다

## 검증 조건
- 역할이 EMPLOYEE일 때 휴가 승인 대기 배지가 미표시되어야 한다
- 역할이 MANAGER/ADMIN일 때 내 휴가 현황 카드가 미표시되어야 한다
- 날짜 필터는 오늘 날짜로 자동 설정된다
- 모든 API 호출이 완료되기 전까지 각 카드에 스켈레톤 로딩을 표시한다

## 비기능 요구사항
- 초기 로딩: 2초 이내
- 인터랙션 반응: 100ms 이내
- API 실패 시: 에러 메시지 표시 + 재시도 버튼
- 각 카드는 독립적으로 로딩/에러 처리 (한 카드 실패 시 다른 카드는 정상 표시)
