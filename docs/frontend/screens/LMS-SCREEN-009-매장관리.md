# LMS-SCREEN-009: 매장관리

## 기본 정보
- type: screen_spec
- 화면명: 매장 관리 (목록 / 등록 / 수정)
- 라우트: `/admin/stores`, `/admin/stores/new`, `/admin/stores/:storeId/edit`
- 대상 사용자: 관리자(SUPER_ADMIN)

## 관련 Backend Spec
- LMS-API-STORE-001 (매장API)

## 화면 목적
관리자가 매장 목록을 조회하고, 새로운 매장을 등록하며, 기존 매장 정보를 수정하거나 삭제한다.

## 화면 구성 요소

### 매장 목록 테이블
- 표시 데이터: DataTable 형태(매장명, 위치, 등록일, 작업 버튼), "매장 추가" 버튼
- Backend API: GET /api/stores
  - 참조 Spec: LMS-API-STORE-001
  - 요청 파라미터: 없음
  - 응답 매핑: stores[] → DataTable rows, name → 매장명, location → 위치, createdAt → 등록일
- 빈 상태: "등록된 매장이 없습니다" (매장 추가 버튼과 함께)
- 에러 상태: 에러 아이콘 + 에러 메시지 + "다시 시도" 버튼

### 매장 삭제 다이얼로그
- 표시 데이터: "매장 삭제" 확인 다이얼로그 (매장명 포함)
- Backend API: DELETE /api/stores/{storeId}
  - 참조 Spec: LMS-API-STORE-001
  - 요청 파라미터: Path에 storeId
  - 응답 매핑: 성공 시 SnackBar "매장이 삭제되었습니다", 목록 갱신
- 빈 상태: "삭제할 매장이 없습니다"
- 에러 상태: SnackBar 에러 메시지

### 매장 등록/수정 폼
- 표시 데이터: 매장명 입력, 위치 입력(2줄 텍스트 필드), 취소/등록(수정) 버튼
- Backend API: POST /api/stores (등록), PUT /api/stores/{storeId} (수정)
  - 참조 Spec: LMS-API-STORE-001
  - 요청 파라미터(등록): `{ "name": "string", "location": "string" }`
  - 요청 파라미터(수정): `{ "name": "string", "location": "string" }`
  - 응답 매핑: 성공 시 SnackBar "매장이 등록/수정되었습니다", `/admin/stores`로 이동
- 빈 상태: "매장 정보를 입력해 주세요"
- 에러 상태: SnackBar "오류: {에러 메시지}"
- 유효성 검증:
  - 매장명: 필수, 최소 2자
  - 위치: 필수

## 사용자 흐름

1. 매장 관리 화면에서 전체 매장 목록을 확인한다
2. "매장 추가" 버튼을 눌러 등록 화면으로 이동한다
3. 매장명과 위치를 입력하고 "등록" 버튼을 누른다
4. 수정 아이콘을 눌러 수정 화면으로 이동한다
5. 삭제 아이콘을 눌러 확인 후 매장을 삭제한다
