# LMS-SCREEN-008: 직원관리

## 기본 정보
- type: screen_spec
- 화면명: 근로자 관리 (목록 / 등록 / 수정)
- 라우트: `/admin/employees`, `/admin/employees/new`, `/admin/employees/:employeeId/edit`
- 대상 사용자: 관리자(MANAGER, SUPER_ADMIN)

## 관련 Backend Spec
- LMS-API-EMP-001 (근로자API)
- LMS-API-STORE-001 (매장API)

## 화면 목적
관리자가 근로자 목록을 조회하고, 새로운 근로자를 등록하며, 기존 근로자 정보를 수정하거나 비활성화한다.

## 화면 구성 요소

### 근로자 목록 테이블
- 표시 데이터: DataTable 형태(이름, 사용자 ID, 근로자 유형, 잔여 연차, 상태 Chip, 등록일, 작업 버튼), 매장 필터 드롭다운, "근로자 추가" 버튼
- Backend API: GET /api/employees
  - 참조 Spec: LMS-API-EMP-001
  - 요청 파라미터: `?storeId={선택된 매장 ID}` (전체 매장 시 파라미터 없음)
  - 응답 매핑: employees[] → DataTable rows, name → 이름, userId → 사용자 ID, employeeType.displayName → 근로자 유형, remainingLeave → 잔여 연차, isActive → 활성/비활성 Chip, createdAt → 등록일
- 빈 상태: "등록된 근로자가 없습니다" (근로자 추가 버튼과 함께)
- 에러 상태: 에러 아이콘 + 에러 메시지 + "다시 시도" 버튼

### 근로자 비활성화 다이얼로그
- 표시 데이터: "근로자 비활성화" 확인 다이얼로그 (근로자명 포함)
- Backend API: PATCH /api/employees/{employeeId}/deactivate
  - 참조 Spec: LMS-API-EMP-001
  - 요청 파라미터: Path에 employeeId
  - 응답 매핑: 성공 시 SnackBar "근로자가 비활성화되었습니다", 목록 갱신
- 빈 상태: "비활성화할 근로자가 없습니다"
- 에러 상태: SnackBar 에러 메시지

### 근로자 등록/수정 폼
- 표시 데이터: 사용자 ID 입력(수정 시 비활성), 이름 입력, 근로자 유형 드롭다운(정규직/비정규직/파트타임), 매장 선택 드롭다운, 취소/등록(수정) 버튼
- Backend API: POST /api/employees (등록), PUT /api/employees/{employeeId} (수정)
  - 참조 Spec: LMS-API-EMP-001
  - 요청 파라미터(등록): `{ "userId": "string", "name": "string", "employeeType": "string", "storeId": "string" }`
  - 요청 파라미터(수정): `{ "name": "string", "employeeType": "string", "storeId": "string" }`
  - 응답 매핑: 성공 시 SnackBar "근로자가 등록/수정되었습니다", `/admin/employees`로 이동
- 빈 상태: "근로자 정보를 입력해 주세요"
- 에러 상태: SnackBar "오류: {에러 메시지}"
- 유효성 검증:
  - 사용자 ID: 필수
  - 이름: 필수, 최소 2자
  - 근로자 유형: 필수
  - 매장: 필수

## 사용자 흐름

1. 근로자 관리 화면에서 전체 또는 매장별 근로자 목록을 확인한다
2. "근로자 추가" 버튼을 눌러 등록 화면으로 이동한다
3. 필수 정보를 입력하고 "등록" 버튼을 누른다
4. 수정 아이콘을 눌러 수정 화면으로 이동한다
5. 비활성화 아이콘을 눌러 확인 후 근로자를 비활성화한다
