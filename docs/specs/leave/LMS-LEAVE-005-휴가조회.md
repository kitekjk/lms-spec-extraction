# LMS-LEAVE-005: 휴가조회

## 기본 정보
- type: use_case
- domain: leave

## 관련 Spec
- LMS-API-LEAVE-001 (휴가API)

## 개요
인증된 사용자가 본인의 휴가 신청 내역을 조회하거나, 관리자가 매장별/대기 중인 휴가 신청을 조회한다.

## 관련 모델
- 주 모델: LeaveRequest (Aggregate Root)
- 참조 모델: Employee (employeeId 참조), Store (storeId 참조)

## 선행 조건
- 인증된 사용자여야 한다

## 기본 흐름 (본인 휴가 조회)
1. 근로자가 본인의 휴가 신청 내역 조회를 요청한다
2. 시스템은 현재 로그인한 사용자의 ID로 휴가 신청 내역을 조회한다
3. 시스템은 휴가 신청 목록과 총 건수를 반환한다

## 대안 흐름
- 매장별 조회 (관리자용): MANAGER 또는 SUPER_ADMIN이 storeId를 지정하여 해당 매장의 모든 휴가 신청을 조회한다
- 대기 중인 휴가 조회 (관리자용): MANAGER 또는 SUPER_ADMIN이 승인 대기 중인 모든 휴가 신청을 조회한다

## 예외 흐름
- 인증 정보를 찾을 수 없는 경우: IllegalStateException 발생

## 관련 정책
- POLICY-NFR-001 참조
- POLICY-LEAVE-001-휴가 참조

## 검증 조건
- 인증된 사용자여야 한다
- 매장별 조회 및 대기 중인 휴가 조회는 MANAGER 또는 SUPER_ADMIN 권한이 필요하다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-LEAVE-005-01: 본인 휴가 신청 내역 조회 (Integration)
- Given: 근로자가 3건의 휴가 신청 내역을 보유 (PENDING 1건, APPROVED 1건, REJECTED 1건)
- When: 본인의 휴가 신청 내역 조회를 요청
- Then: 3건의 휴가 신청 목록과 총 건수 3이 반환됨

### TC-LEAVE-005-02: 매장별 휴가 조회 - MANAGER (Integration)
- Given: MANAGER가 인증된 상태이고, storeId="store-A"에 소속된 근로자들의 휴가 신청 5건이 존재
- When: storeId="store-A"로 휴가 신청 조회를 요청
- Then: 해당 매장 소속 근로자들의 5건 휴가 신청 목록이 반환됨

### TC-LEAVE-005-03: 승인 대기 중인 휴가 조회 - MANAGER (Integration)
- Given: MANAGER가 인증된 상태이고, PENDING 상태의 휴가 신청 2건이 존재
- When: 승인 대기 중인 휴가 조회를 요청
- Then: PENDING 상태의 2건만 반환됨

### TC-LEAVE-005-04: 인증 정보 없는 조회 시도 (E2E)
- Given: 인증 토큰 없이 요청
- When: 휴가 신청 내역 조회를 요청
- Then: 401 Unauthorized 응답

### TC-LEAVE-005-05: 휴가 신청 내역이 없는 경우 (Integration)
- Given: 근로자의 휴가 신청 내역이 없음
- When: 본인의 휴가 신청 내역 조회를 요청
- Then: 빈 목록과 총 건수 0이 반환됨

### TC-LEAVE-005-06: SUPER_ADMIN 전체 매장 휴가 조회 (Integration)
- Given: SUPER_ADMIN이 인증된 상태이고, 여러 매장에 걸쳐 총 10건의 휴가 신청이 존재
- When: storeId를 지정하여 특정 매장의 휴가 조회를 요청
- Then: 해당 매장의 휴가 신청만 필터링되어 반환됨
