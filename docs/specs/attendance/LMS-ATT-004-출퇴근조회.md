# LMS-ATT-004 출퇴근조회

## 기본 정보
- type: use_case
- domain: attendance
- id: LMS-ATT-004

## 관련 정책
- POLICY-AUTH-001 (인증/인가)
- POLICY-NFR-001 (비기능 요구사항)
- POLICY-ATTENDANCE-001 (출퇴근)

## 관련 Spec
- LMS-API-ATT-001

## 관련 모델
- 주 모델: AttendanceRecord
- 참조 모델: Employee, Store

## 개요
역할에 따라 출퇴근 기록을 조회한다. EMPLOYEE는 본인의 출퇴근 기록만 조회할 수 있고, MANAGER는 소속 매장 근로자의 기록을 조회할 수 있으며, SUPER_ADMIN은 전체 매장의 기록을 조회할 수 있다. 날짜 범위(startDate, endDate) 필터링을 지원한다.

## 기본 흐름

### 흐름 A: 본인 출퇴근 기록 조회 (GET /api/attendance/my-records)
1. 근로자가 JWT 인증 토큰과 함께 본인 출퇴근 기록 조회 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증하여 인증된 사용자인지 확인한다.
3. 시스템이 인증된 userId로부터 employeeId를 조회한다.
4. startDate와 endDate 쿼리 파라미터가 제공되면 해당 날짜 범위 내의 기록을 조회한다.
5. startDate와 endDate가 미제공이면 전체 기록을 조회한다.
6. 조회 결과를 AttendanceRecordListResponse 형태로 200 OK 응답과 함께 반환한다.

### 흐름 B: 매장별 출퇴근 기록 조회 (GET /api/attendance/records)
1. 관리자(MANAGER 또는 SUPER_ADMIN)가 JWT 인증 토큰과 함께 매장별 출퇴근 기록 조회 요청을 전송한다.
2. 시스템이 JWT 토큰을 검증하고 역할(MANAGER 또는 SUPER_ADMIN)을 확인한다.
3. 필수 쿼리 파라미터 storeId를 확인한다.
4. MANAGER인 경우, storeId가 자신의 소속 매장인지 확인한다.
5. startDate와 endDate 쿼리 파라미터가 제공되면 해당 날짜 범위 내의 기록을 조회한다.
6. 해당 매장 소속 근로자들의 출퇴근 기록을 조회한다.
7. 조회 결과를 AttendanceRecordListResponse 형태로 200 OK 응답과 함께 반환한다.

## 대안 흐름
- **AF-1: 인증 실패** - JWT 토큰이 없거나 만료된 경우 HTTP 401 Unauthorized를 반환한다.
- **AF-2: EMPLOYEE의 매장별 조회 시도** - EMPLOYEE 역할의 사용자가 GET /api/attendance/records를 호출하면 HTTP 403 Forbidden을 반환한다.
- **AF-3: MANAGER의 타 매장 조회 시도** - MANAGER가 소속 매장이 아닌 storeId로 조회하면 HTTP 403 Forbidden을 반환한다.
- **AF-4: 조회 결과 없음** - 해당 조건에 맞는 출퇴근 기록이 없으면 빈 목록(records: [], totalCount: 0)을 200 OK로 반환한다.
- **AF-5: storeId 미제공 (매장별 조회)** - GET /api/attendance/records에서 storeId가 없으면 HTTP 400 Bad Request를 반환한다.

## 검증 조건
- EMPLOYEE는 GET /api/attendance/my-records만 호출 가능하며, 반환되는 기록의 employeeId가 모두 본인의 것이어야 한다.
- MANAGER는 소속 매장의 storeId로만 GET /api/attendance/records를 호출할 수 있다.
- SUPER_ADMIN은 모든 storeId로 GET /api/attendance/records를 호출할 수 있다.
- startDate와 endDate가 둘 다 제공되면, startDate <= endDate여야 한다.
- 응답의 totalCount는 records 배열의 길이와 일치해야 한다.
- 각 AttendanceRecordResponse는 id, employeeId, attendanceDate, checkInTime, status, createdAt 필드를 포함해야 한다.

## 비기능 요구사항
- POLICY-NFR-001 참조
- API 응답 시간: 500ms 이내
- 매장 기반 데이터 격리: MANAGER는 소속 매장 데이터만 접근 가능 (POLICY-NFR-001 멀티 매장 지원)

## 테스트 시나리오

### TC-ATT-004-01: 본인 출퇴근 기록 전체 조회 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자의 출퇴근 기록이 5건 존재한다.
- **When**: startDate, endDate 없이 본인 기록 조회를 요청한다.
- **Then**: 5건의 AttendanceRecordResult가 반환되고, 모든 기록의 employeeId가 "emp-001"이다.

### TC-ATT-004-02: 날짜 범위 필터링 조회 (Unit)
- **Given**: employeeId가 "emp-001"인 근로자의 2026-03-01 ~ 2026-03-07 기간에 출퇴근 기록이 3건 존재한다.
- **When**: startDate를 2026-03-01, endDate를 2026-03-07로 설정하여 본인 기록 조회를 요청한다.
- **Then**: 3건의 AttendanceRecordResult가 반환되고, 모든 기록의 attendanceDate가 2026-03-01 ~ 2026-03-07 범위 내이다.

### TC-ATT-004-03: 매장별 조회 - MANAGER 정상 조회 (Integration)
- **Given**: storeId가 "store-001"인 매장에 소속된 MANAGER가 인증되어 있고, 해당 매장 근로자의 출퇴근 기록이 10건 존재한다.
- **When**: GET /api/attendance/records?storeId=store-001 요청을 전송한다.
- **Then**: HTTP 200 OK 응답과 함께 10건의 records가 반환되고, totalCount가 10이다.

### TC-ATT-004-04: EMPLOYEE의 매장별 조회 차단 (Integration)
- **Given**: EMPLOYEE 역할로 인증된 사용자가 존재한다.
- **When**: GET /api/attendance/records?storeId=store-001 요청을 전송한다.
- **Then**: HTTP 403 Forbidden 응답이 반환된다.

### TC-ATT-004-05: 조회 결과 없음 시 빈 목록 반환 (E2E)
- **Given**: EMPLOYEE 역할로 인증된 사용자가 존재하고, 2026-01-01 ~ 2026-01-31 기간에 출퇴근 기록이 없다.
- **When**: GET /api/attendance/my-records?startDate=2026-01-01&endDate=2026-01-31 요청을 전송한다.
- **Then**: HTTP 200 OK 응답과 함께 records: [], totalCount: 0이 반환된다.
