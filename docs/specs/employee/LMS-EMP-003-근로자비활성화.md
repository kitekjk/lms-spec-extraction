# LMS-EMP-003: 근로자비활성화

## 기본 정보
- type: use_case
- domain: employee

## 관련 Spec
- LMS-API-EMP-001 (근로자API)
- LMS-EMP-001 (근로자등록)

## 개요
관리자가 근로자를 비활성화(isActive=false)하여 해당 근로자의 로그인 및 활동을 차단한다.

## 관련 모델
- 주 모델: Employee (Aggregate Root)

## 선행 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 비활성화 대상 근로자가 존재해야 한다
- 근로자가 현재 활성화(isActive=true) 상태여야 한다

## 기본 흐름
1. 관리자가 근로자 ID를 지정하여 비활성화를 요청한다
2. 시스템은 근로자를 조회한다
3. 시스템은 근로자의 활성화 상태를 확인한다
4. 시스템은 근로자를 비활성화(isActive=false)한다
5. 시스템은 수정된 근로자를 저장하고 결과를 반환한다

## 대안 흐름
- 없음

## 예외 흐름
- 근로자를 찾을 수 없는 경우: EmployeeNotFoundException (EMP001) 발생
- 이미 비활성화된 근로자인 경우: IllegalArgumentException ("이미 비활성화된 근로자입니다.") 발생

## 관련 정책
- POLICY-NFR-001 참조

## 검증 조건
- 요청자가 SUPER_ADMIN 또는 MANAGER 권한을 보유해야 한다
- 비활성화 대상 근로자가 존재해야 한다
- 근로자가 현재 활성화(isActive=true) 상태여야 한다

## 비기능 요구사항
- POLICY-NFR-001 참조

## 테스트 시나리오

### TC-EMP-003-01: 정상 근로자 비활성화 (Unit)
- Given: isActive=true 상태의 근로자가 존재
- When: 해당 근로자의 비활성화를 요청
- Then: 근로자의 isActive가 false로 변경됨

### TC-EMP-003-02: 존재하지 않는 근로자 비활성화 시도 (Unit)
- Given: 존재하지 않는 employeeId
- When: 해당 근로자의 비활성화를 요청
- Then: EmployeeNotFoundException (EMP001) 발생

### TC-EMP-003-03: 이미 비활성화된 근로자 재비활성화 시도 (Unit)
- Given: isActive=false 상태의 근로자가 존재
- When: 해당 근로자의 비활성화를 요청
- Then: IllegalArgumentException 발생 - "이미 비활성화된 근로자입니다."

### TC-EMP-003-04: 비활성화된 근로자의 로그인 차단 확인 (Integration)
- Given: 근로자가 비활성화(isActive=false)된 상태
- When: 해당 사용자의 이메일/비밀번호로 로그인을 시도
- Then: InactiveUserException (AUTH002) 발생 - 로그인이 차단됨

### TC-EMP-003-05: EMPLOYEE 권한으로 비활성화 시도 (E2E)
- Given: EMPLOYEE 역할의 사용자가 인증된 상태
- When: 근로자 비활성화를 요청
- Then: 403 Forbidden 응답
