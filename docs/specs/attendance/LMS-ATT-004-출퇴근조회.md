# LMS-ATT-004: 출퇴근조회

## 기본 정보
- type: use_case
- domain: attendance

## 관련 Spec
- LMS-API-ATT-001 (출퇴근API)

## 개요
인증된 사용자가 본인의 출퇴근 기록을 조회하거나, 관리자가 매장별 출퇴근 기록을 조회한다.

## 관련 모델
- 주 모델: AttendanceRecord (Aggregate Root)
- 참조 모델: Employee (employeeId 참조), Store (storeId 참조)

## 선행 조건
- 인증된 사용자여야 한다

## 기본 흐름 (본인 기록 조회)
1. 근로자가 본인의 출퇴근 기록 조회를 요청한다 (날짜 범위 선택적 지정)
2. 시스템은 현재 로그인한 사용자의 ID로 출퇴근 기록을 조회한다
3. 시스템은 기록 목록과 총 건수를 반환한다

## 대안 흐름
- 날짜 범위 지정 (startDate, endDate): 지정된 기간의 기록만 조회한다
- 매장별 조회 (관리자용): MANAGER 또는 SUPER_ADMIN이 storeId를 지정하여 해당 매장의 모든 출퇴근 기록을 조회한다

## 예외 흐름
- 인증 정보를 찾을 수 없는 경우: IllegalStateException 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-ATTENDANCE-001-출퇴근 참조

## 검증 조건
- 인증된 사용자여야 한다
- 매장별 조회는 MANAGER 또는 SUPER_ADMIN 권한이 필요하다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-ATT-004-01: 본인 출퇴근 기록 전체 조회 (Integration)
- Given: 근로자가 5건의 출퇴근 기록을 보유하고 있음
- When: 본인의 출퇴근 기록 조회를 요청
- Then: 5건의 기록 목록과 총 건수 5가 반환됨

### TC-ATT-004-02: 날짜 범위 지정 조회 (Integration)
- Given: 근로자가 3월 1일~3월 9일 사이에 7건의 출퇴근 기록이 있음
- When: startDate=2026-03-05, endDate=2026-03-09로 조회를 요청
- Then: 해당 기간에 해당하는 기록만 반환됨

### TC-ATT-004-03: 매장별 출퇴근 조회 - MANAGER (Integration)
- Given: MANAGER가 인증된 상태이고, storeId="store-A"에 소속된 근로자 3명의 출퇴근 기록이 존재
- When: storeId="store-A"로 출퇴근 기록 조회를 요청
- Then: 해당 매장 소속 근로자들의 전체 출퇴근 기록이 반환됨

### TC-ATT-004-04: 인증 정보 없는 조회 시도 (E2E)
- Given: 인증 토큰 없이 요청
- When: 출퇴근 기록 조회를 요청
- Then: 401 Unauthorized 응답

### TC-ATT-004-05: 출퇴근 기록이 없는 경우 (Integration)
- Given: 근로자의 출퇴근 기록이 없음
- When: 본인의 출퇴근 기록 조회를 요청
- Then: 빈 목록과 총 건수 0이 반환됨

### TC-ATT-004-06: 타 매장 기록 접근 시도 - MANAGER (E2E)
- Given: MANAGER가 storeId="store-A"에 소속
- When: storeId="store-B"의 출퇴근 기록 조회를 요청
- Then: 권한 오류 또는 빈 결과가 반환됨
