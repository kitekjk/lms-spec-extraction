# LMS-SCREEN-007: 대시보드

## 기본 정보
- type: screen_spec
- 화면명: 관리자 대시보드
- 라우트: `/admin/dashboard`
- 대상 사용자: 관리자(MANAGER, SUPER_ADMIN)

## 관련 Backend Spec
- LMS-API-USER-001 (인증API)
- LMS-API-ATT-001 (출퇴근API)
- LMS-API-STORE-001 (매장API)
- LMS-API-EMP-001 (근로자API)

## 화면 목적
관리자가 시스템의 주요 지표(총 매장, 총 직원, 금일 출근, 휴가 중)를 한눈에 파악하고, 금일 출근 현황과 최근 활동을 모니터링한다.

## 화면 구성 요소

### 환영 메시지 카드
- 표시 데이터: 관리자 아이콘, "환영합니다!" 타이틀, 이메일 및 역할(슈퍼 관리자/매니저), 담당 매장명
- Backend API: GET /api/auth/me
  - 참조 Spec: LMS-API-USER-001
  - 요청 파라미터: 없음
  - 응답 매핑: email → 이메일, role → 역할 표시, storeName → 담당 매장
- 빈 상태: "사용자 정보가 없습니다"
- 에러 상태: 카드가 표시되지 않음

### 주요 지표 카드 그리드
- 표시 데이터: 4개 통계 카드 (총 매장/파란, 총 직원/초록, 금일 출근/주황, 휴가 중/보라)
- Backend API: GET /api/stores
  - 참조 Spec: LMS-API-STORE-001
  - 요청 파라미터: 없음
  - 응답 매핑: totalCount → 총 매장 수
- 빈 상태: "데이터가 없습니다"
- 에러 상태: "통계를 불러올 수 없습니다"
- 비고: 현재 mock 데이터 사용 (TODO: 실제 API 연동 필요)

### 금일 출근 현황 위젯
- 표시 데이터: "금일 출근 현황" 타이틀, 정상 출근(초록)/지각(주황)/조퇴(파랑)/결근(빨강) 항목별 인원 수, 총계
- Backend API: GET /api/attendance/records
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: `?storeId={매장ID}&startDate={오늘}&endDate={오늘}`
  - 응답 매핑: records를 status별로 그룹핑하여 인원 수 계산 (NORMAL → 정상 출근, LATE → 지각, EARLY_LEAVE → 조퇴, ABSENT → 결근)
- 빈 상태: "출근 기록이 없습니다"
- 에러 상태: "출근 현황을 불러올 수 없습니다"

### 최근 활동 위젯
- 표시 데이터: "최근 활동" 타이틀, 활동 목록(아이콘/색상별 유형 구분, 직원명, 활동 내용, 시간)
- Backend API: GET /api/attendance/records
  - 참조 Spec: LMS-API-ATT-001
  - 요청 파라미터: `?storeId={매장ID}&startDate={오늘}&endDate={오늘}`
  - 응답 매핑: 최근 출퇴근/휴가/일정 변경 활동을 시간순으로 표시, type별 아이콘(attendance:초록/leave_request:주황/schedule:파랑)
- 빈 상태: "최근 활동이 없습니다"
- 에러 상태: "활동 내역을 불러올 수 없습니다"

## 사용자 흐름

1. 관리자 로그인 후 대시보드가 표시된다
2. 환영 메시지에서 본인 정보와 담당 매장을 확인한다
3. 주요 지표 카드에서 전체 현황을 파악한다
4. 금일 출근 현황 위젯에서 직원들의 출근 상태를 확인한다
5. 최근 활동 위젯에서 실시간 활동을 모니터링한다
6. AdminLayout 사이드바를 통해 다른 관리 화면으로 이동한다
