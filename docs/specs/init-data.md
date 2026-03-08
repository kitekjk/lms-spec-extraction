# LMS Backend - 초기 데이터

## 기본 정보
- type: init_data
- 로드 조건: `local` 프로파일에서 서버 시작 시 자동 로드 (`spring.sql.init.mode: always`)
- 데이터 소스: `interfaces/src/main/resources/data.sql`, `DemoDataInitializer.kt`

## 초기 매장

| store_id | 매장명 | 위치 |
|----------|--------|------|
| store-001 | 강남점 | 서울시 강남구 테헤란로 123 |
| store-002 | 홍대점 | 서울시 마포구 홍익로 456 |
| store-003 | 신촌점 | 서울시 서대문구 신촌역로 789 |

## 기본 사용자

비밀번호는 모두 `password123` (BCrypt 해시: `$2a$10$EfRjwpUmoHURFezK9f2Z2eLe1rCpDUBy5BGVrhjWqC4BYOhDf4FFS`)

| user_id | 이메일 | 역할 | 활성 |
|---------|--------|------|------|
| user-admin | admin@lms.com | SUPER_ADMIN | true |
| user-manager-001 | manager.gangnam@lms.com | MANAGER | true |
| user-emp-001 | employee1.gangnam@lms.com | EMPLOYEE | true |
| user-emp-002 | employee2.gangnam@lms.com | EMPLOYEE | true |
| user-manager-002 | manager.hongdae@lms.com | MANAGER | true |
| user-emp-003 | employee1.hongdae@lms.com | EMPLOYEE | true |

## 초기 근로자

| employee_id | user_id | 이름 | 직급 | 소속 매장 | 잔여 연차 |
|-------------|---------|------|------|----------|----------|
| emp-manager-001 | user-manager-001 | 박수진 | REGULAR (정규직) | store-001 (강남점) | 15.0 |
| emp-001 | user-emp-001 | 김민수 | REGULAR (정규직) | store-001 (강남점) | 13.5 |
| emp-002 | user-emp-002 | 이지영 | REGULAR (정규직) | store-001 (강남점) | 14.0 |
| emp-manager-002 | user-manager-002 | 최동현 | REGULAR (정규직) | store-002 (홍대점) | 15.0 |
| emp-003 | user-emp-003 | 정서연 | REGULAR (정규직) | store-002 (홍대점) | 15.0 |

## 초기 급여 정책

| policy_id | 유형 | 가산율 | 시작일 | 종료일 | 설명 |
|-----------|------|--------|--------|--------|------|
| policy-001 | OVERTIME | 1.5 | 2024-01-01 | 없음 (무기한) | 초과근무 가산율 |
| policy-002 | NIGHT_SHIFT | 1.5 | 2024-01-01 | 없음 (무기한) | 야간근무 가산율 |
| policy-003 | WEEKEND | 1.5 | 2024-01-01 | 없음 (무기한) | 주말근무 가산율 |
| policy-004 | HOLIDAY | 2.0 | 2024-01-01 | 없음 (무기한) | 공휴일근무 가산율 |

## 시연용 근무 일정 (DemoDataInitializer)

- 실행 조건: `local` 프로파일에서만 실행 (`@Profile("local")`)
- 실행 시점: 서버 시작 시 (`ApplicationRunner`)
- 대상 매장: 강남점 (`store-001`)
- 대상 근로자:
  - `emp-manager-001` (박수진, 매니저)
  - `emp-001` (김민수)
  - `emp-002` (이지영)
- 일정 기간: 오늘 기준 1주 전 ~ 2주 후 (총 3주)
- 근무 요일: 월~금 (주말 제외)
- 근무 시간: 09:00 ~ 18:00
- 확정 상태: `true` (모두 확정)
- 중복 방지: 이미 해당 날짜에 일정이 존재하면 건너뜀

## 테스트 계정 요약

| 역할 | 이메일 | 비밀번호 | 소속 매장 |
|------|--------|----------|-----------|
| 관리자 (SUPER_ADMIN) | admin@lms.com | password123 | 전체 |
| 매니저 (MANAGER) | manager.gangnam@lms.com | password123 | 강남점 |
| 매니저 (MANAGER) | manager.hongdae@lms.com | password123 | 홍대점 |
| 직원 (EMPLOYEE) | employee1.gangnam@lms.com | password123 | 강남점 |
| 직원 (EMPLOYEE) | employee2.gangnam@lms.com | password123 | 강남점 |
| 직원 (EMPLOYEE) | employee1.hongdae@lms.com | password123 | 홍대점 |
