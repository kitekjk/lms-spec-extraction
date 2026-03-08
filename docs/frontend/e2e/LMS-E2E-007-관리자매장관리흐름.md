# LMS-E2E-007: 관리자 매장 관리 흐름 E2E 테스트

## 기본 정보
- type: e2e_test_spec
- 화면: StoreListScreen (`/admin/stores`), StoreFormScreen (`/admin/stores/new`, `/admin/stores/:storeId/edit`)
- 관련 위젯: `store_list_screen.dart`, `store_form_screen.dart`
- 대상 사용자: SUPER_ADMIN

## 관련 Backend Spec
- LMS-STORE-001 (매장 등록 Use Case)
- LMS-STORE-002 (매장 수정 Use Case)
- LMS-STORE-003 (매장 삭제 Use Case)
- LMS-STORE-004 (매장 조회 Use Case)
- LMS-API-STORE-001 (매장 API - GET /api/stores, POST /api/stores, PUT /api/stores/:id, DELETE /api/stores/:id)
- POLICY-AUTH-001 (인증/인가 정책 - SUPER_ADMIN 전용)

## 테스트 시나리오

### TC-FE-007-01: 매장 목록 조회 — 데이터 있음 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터 (3개 매장: 강남점/홍대점/신촌점)
  - admin@lms.com (SUPER_ADMIN)으로 관리자 로그인 완료
  - `/admin/stores` 페이지 열림
- When:
  - 페이지 로드 완료 대기
- Then:
  - AdminLayout에 "매장 관리" 타이틀 텍스트 표시
  - "매장 목록" 헤딩 텍스트 표시
  - DataTable에 매장 목록 3건 표시
  - 테이블 컬럼 헤더에 "매장명", "위치", "등록일", "작업" 텍스트 표시
  - "강남점" 행에 "서울시 강남구 테헤란로 123" 위치 텍스트 표시
  - "홍대점" 행에 "서울시 마포구 홍익로 456" 위치 텍스트 표시
  - "신촌점" 행에 "서울시 서대문구 신촌역로 789" 위치 텍스트 표시
  - "매장 추가" 버튼 표시
  - 각 행에 "수정" 아이콘 버튼과 "삭제" 아이콘 버튼 표시

### TC-FE-007-02: 매장 없는 상태 — 빈 데이터 (E2E)
- Given:
  - Backend 데이터: 모든 매장 삭제된 상태 (빈 매장 목록)
  - admin@lms.com 으로 관리자 로그인 완료
  - `/admin/stores` 페이지 열림
- When:
  - 페이지 로드 완료 대기
- Then:
  - "등록된 매장이 없습니다" 메시지 표시
  - store_outlined 아이콘 표시
  - "매장 추가" 버튼 표시

### TC-FE-007-03: 매장 등록 및 삭제 — 입력/행위 테스트 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터
  - admin@lms.com 으로 관리자 로그인 완료
  - `/admin/stores/new` 페이지 열림
- When:
  - "새 매장 등록" 헤딩 확인
  - 매장명 입력란(`labelText: '매장명'`)에 "판교점" 입력
  - 위치 입력란(`labelText: '위치'`)에 "경기도 성남시 분당구 판교역로 235" 입력
  - "등록" 버튼 클릭
- Then:
  - SnackBar에 "매장이 등록되었습니다" 메시지 표시
  - `/admin/stores` 페이지로 이동 표시
  - 매장 목록에 "판교점" 표시

### TC-FE-007-04: SUPER_ADMIN만 매장 관리 접근 — 권한별 화면 차이 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터
  - admin@lms.com (SUPER_ADMIN)으로 관리자 로그인 완료
  - `/admin/stores` 페이지 열림
- When:
  - 매장 목록 확인
- Then:
  - 모든 매장에 대해 "수정" 아이콘 버튼 표시
  - 모든 매장에 대해 "삭제" 아이콘 버튼 (빨간색) 표시
  - "매장 추가" 버튼 표시
  - "삭제" 버튼 클릭 시 "정말 '강남점' 매장을 삭제하시겠습니까?" 확인 다이얼로그 표시
  - 다이얼로그에 "취소", "삭제" 버튼 텍스트 표시

### TC-FE-007-05: 매장 등록 유효성 검증 실패 — 에러 상태 검증 (E2E)
- Given:
  - Backend 데이터: init-data.md 기본 데이터
  - admin@lms.com 으로 관리자 로그인 완료
  - `/admin/stores/new` 페이지 열림
- When:
  - 매장명에 한 글자("점")만 입력
  - 위치 입력란을 비운 채로 "등록" 버튼 클릭
- Then:
  - "매장명은 최소 2자 이상이어야 합니다" 유효성 검증 메시지 표시
  - "위치를 입력하세요" 유효성 검증 메시지 표시

## agent-browser 실행 예시

```python
# TC-FE-007-01: 매장 목록 조회
await page.goto("/admin/login")
await page.fill('input[type="email"]', 'admin@lms.com')
await page.fill('input[type="password"]', 'password123')
await page.click('text=로그인')
await page.goto("/admin/stores")
await expect(page.locator('text=매장 관리')).to_be_visible()
await expect(page.locator('text=강남점')).to_be_visible()
await expect(page.locator('text=홍대점')).to_be_visible()
await expect(page.locator('text=신촌점')).to_be_visible()

# TC-FE-007-03: 매장 등록
await page.click('text=매장 추가')
await expect(page.locator('text=새 매장 등록')).to_be_visible()
await page.fill('input[label="매장명"]', '판교점')
await page.fill('input[label="위치"]', '경기도 성남시 분당구 판교역로 235')
await page.click('text=등록')
await expect(page.locator('text=매장이 등록되었습니다')).to_be_visible()

# TC-FE-007-04: 매장 삭제 확인 다이얼로그
await page.goto("/admin/stores")
delete_button = page.locator('button[tooltip="삭제"]').first
await delete_button.click()
await expect(page.locator('text=매장 삭제')).to_be_visible()
await page.click('text=취소')
```
