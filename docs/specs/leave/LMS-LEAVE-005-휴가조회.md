# LMS-LEAVE-005 휴가조회

## 기본 정보
- type: use_case
- id: LMS-LEAVE-005
- domain: leave
- last-updated: 2026-03-09

## 관련 정책
- POLICY-LEAVE-001: 휴가 상태 정의 (§3)
- POLICY-NFR-001: 멀티 매장 지원 (§4), 성능 요구사항 (§5)

## 관련 Spec
- LMS-API-LEAVE-001-휴가API (GET /api/leaves, GET /api/leaves/my-leaves, GET /api/leaves/pending)

## 관련 모델
- **주 모델**: `LeaveRequest` (Aggregate Root)
- 참조 모델: `LeaveStatus` (Enum), `LeaveType` (Enum), `StoreId` (매장 필터링)

## 개요
사용자가 역할에 따라 휴가 신청 내역을 조회한다. EMPLOYEE는 본인의 휴가 내역만, MANAGER는 소속 매장 근로자의 휴가 내역을, SUPER_ADMIN은 전체 매장의 휴가 내역을 조회할 수 있다. 추가로 PENDING 상태의 휴가 신청만 별도 조회할 수 있다.

## 기본 흐름

### 흐름 A: 본인 휴가 조회 (GET /api/leaves/my-leaves)
1. 인증된 사용자가 본인의 휴가 신청 내역 조회를 요청한다.
2. 시스템이 JWT에서 사용자 ID를 추출한다.
3. 시스템이 해당 사용자의 employeeId로 LeaveRequest 목록을 조회한다.
4. 시스템이 휴가 신청 목록과 총 건수(totalCount)를 반환한다 (HTTP 200).

### 흐름 B: 매장별 휴가 조회 (GET /api/leaves?storeId={storeId})
1. MANAGER 또는 SUPER_ADMIN이 매장 ID(storeId)를 지정하여 휴가 내역 조회를 요청한다.
2. MANAGER인 경우, 시스템이 요청자의 소속 매장과 조회 대상 매장이 동일한지 검증한다. 다르면 HTTP 403을 반환한다.
3. 시스템이 해당 매장 소속 근로자들의 LeaveRequest 목록을 조회한다.
4. 시스템이 휴가 신청 목록과 총 건수(totalCount)를 반환한다 (HTTP 200).

### 흐름 C: 승인 대기 휴가 조회 (GET /api/leaves/pending)
1. MANAGER 또는 SUPER_ADMIN이 승인 대기 중인 휴가 신청 목록 조회를 요청한다.
2. 시스템이 PENDING 상태의 LeaveRequest 목록을 조회한다.
3. 시스템이 휴가 신청 목록과 총 건수(totalCount)를 반환한다 (HTTP 200).

## 대안 흐름
- **AF-1**: 조회 결과가 0건인 경우 → 빈 배열([])과 totalCount: 0을 반환한다. HTTP 200이 반환된다.
- **AF-2**: 인증 토큰이 없거나 만료된 경우 → HTTP 401을 반환한다.
- **AF-3**: EMPLOYEE가 매장별 조회 또는 승인 대기 조회를 시도하는 경우 → HTTP 403을 반환한다.

## 검증 조건
- EMPLOYEE는 본인(employeeId 일치)의 휴가 내역만 조회할 수 있다. 타인 조회 시 HTTP 403
- MANAGER는 본인 소속 매장의 근로자 휴가 내역만 조회할 수 있다. 타 매장 storeId 지정 시 HTTP 403
- SUPER_ADMIN은 전체 매장의 휴가 내역을 조회할 수 있다
- 매장별 조회(GET /api/leaves) 시 storeId 쿼리 파라미터가 존재해야 한다. 위반 시 HTTP 400
- 매장별 조회 및 승인 대기 조회는 MANAGER 또는 SUPER_ADMIN만 가능하다. 위반 시 HTTP 403

## 비기능 요구사항
- **POLICY-NFR-001 §4**: MANAGER는 소속 매장 데이터만 접근 가능하다. storeId 필터링을 쿼리 레벨에서 강제한다.
- **POLICY-NFR-001 §5.1**: API 응답 시간 500ms 이내.

## 테스트 시나리오

### TC-LEAVE-005-01: EMPLOYEE 본인 휴가 내역 조회 성공
- **레벨**: Integration
- **Given**: 근로자 A가 3건의 휴가 신청(PENDING 1건, APPROVED 1건, CANCELLED 1건)을 보유하고 있다.
- **When**: 근로자 A가 본인 휴가 내역을 조회한다 (GET /api/leaves/my-leaves).
- **Then**: 3건의 휴가 신청이 반환되고, totalCount는 3이다. HTTP 200이 반환된다.

### TC-LEAVE-005-02: MANAGER 매장별 휴가 조회 성공
- **레벨**: Integration
- **Given**: 매장 A에 소속된 MANAGER가 존재하고, 매장 A에 5건의 휴가 신청이 존재한다.
- **When**: MANAGER가 storeId를 매장 A로 지정하여 조회한다 (GET /api/leaves?storeId={매장A_ID}).
- **Then**: 5건의 휴가 신청이 반환되고, totalCount는 5이다. HTTP 200이 반환된다.

### TC-LEAVE-005-03: MANAGER 타 매장 조회 시 권한 오류
- **레벨**: Integration
- **Given**: 매장 A에 소속된 MANAGER가 존재한다.
- **When**: MANAGER가 storeId를 매장 B로 지정하여 조회한다.
- **Then**: HTTP 403이 반환된다.

### TC-LEAVE-005-04: 승인 대기 휴가 조회 성공
- **레벨**: Integration
- **Given**: 시스템에 PENDING 상태의 휴가 신청이 2건 존재한다.
- **When**: SUPER_ADMIN이 승인 대기 휴가 목록을 조회한다 (GET /api/leaves/pending).
- **Then**: 2건의 PENDING 상태 휴가 신청이 반환되고, totalCount는 2이다. HTTP 200이 반환된다.
