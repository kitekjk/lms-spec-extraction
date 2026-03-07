# LMS-API-EMPLOYEE-001: 근로자 API

## 기본 정보
- type: api_spec
- domain: employee
- service: LMS
- base_path: /api/employees

## 관련 Spec
- [LMS-EMPLOYEE-001-근로자등록](LMS-EMPLOYEE-001-근로자등록.md)
- [LMS-EMPLOYEE-002-근로자수정](LMS-EMPLOYEE-002-근로자수정.md)

## 인증/인가
- JWT Bearer Token 필수
- 등록/수정/비활성화: MANAGER 또는 SUPER_ADMIN
- 조회: 역할에 따라 범위 제한

## 엔드포인트 목록

### POST /api/employees
- 설명: 근로자 등록
- 권한: MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "userId": "user-uuid",
    "name": "김민수",
    "employeeType": "REGULAR",
    "storeId": "store-uuid"
  }
  ```
  - userId: 필수
  - name: 필수, 1~100자
  - employeeType: 필수, REGULAR/IRREGULAR/PART_TIME
  - storeId: 선택 (null 가능)
- 응답 (201):
  ```json
  {
    "id": "employee-uuid",
    "userId": "user-uuid",
    "name": "김민수",
    "employeeType": "REGULAR",
    "storeId": "store-uuid",
    "remainingLeave": 15.0,
    "isActive": true,
    "createdAt": "2026-03-08T00:00:00Z"
  }
  ```
- 응답 (400): DuplicateEmployeeUserException - 동일 User 중복

### GET /api/employees
- 설명: 근로자 목록 조회
- 권한: MANAGER, SUPER_ADMIN
- 쿼리 파라미터: storeId (선택, 매장별 필터링)
- 응답 (200):
  ```json
  {
    "employees": [...],
    "totalCount": 10
  }
  ```

### GET /api/employees/{employeeId}
- 설명: 근로자 상세 조회
- 권한: EMPLOYEE (본인만), MANAGER, SUPER_ADMIN
- 응답 (200): EmployeeResponse
- 응답 (404): EmployeeNotFoundException

### PUT /api/employees/{employeeId}
- 설명: 근로자 정보 수정
- 권한: MANAGER, SUPER_ADMIN
- 요청:
  ```json
  {
    "name": "김민수",
    "employeeType": "IRREGULAR",
    "storeId": "new-store-uuid"
  }
  ```
- 응답 (200): EmployeeResponse
- 응답 (404): EmployeeNotFoundException

### DELETE /api/employees/{employeeId}
- 설명: 근로자 비활성화 (soft delete)
- 권한: MANAGER, SUPER_ADMIN
- 응답 (204): No Content
- 응답 (404): EmployeeNotFoundException

## 공통 규칙
- 에러 응답: `{ "code": "EMP001", "message": "..." }`
- 하위호환: POLICY-NFR-001 하위호환 규칙 적용
