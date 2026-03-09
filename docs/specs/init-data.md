# 초기 데이터

## 기본 정보
- type: init_data
- last-updated: 2026-03-09
- 적용 프로파일: local (sql.init.mode: always)
- 데이터 소스: interfaces/src/main/resources/data.sql

## 기본 사용자

### 사용자 계정 (users 테이블)

| user_id | email | password | role | is_active | 소속 매장 |
|---------|-------|----------|------|-----------|-----------|
| user-admin | admin@lms.com | password123 | SUPER_ADMIN | true | 전체 |
| user-manager-001 | manager.gangnam@lms.com | password123 | MANAGER | true | 강남점 |
| user-manager-002 | manager.hongdae@lms.com | password123 | MANAGER | true | 홍대점 |
| user-emp-001 | employee1.gangnam@lms.com | password123 | EMPLOYEE | true | 강남점 |
| user-emp-002 | employee2.gangnam@lms.com | password123 | EMPLOYEE | true | 강남점 |
| user-emp-003 | employee1.hongdae@lms.com | password123 | EMPLOYEE | true | 홍대점 |

- 비밀번호 해시: BCrypt (`$2a$10$EfRjwpUmoHURFezK9f2Z2eLe1rCpDUBy5BGVrhjWqC4BYOhDf4FFS`)
- 모든 계정의 평문 비밀번호: `password123`

### 근로자 정보 (employees 테이블)

| employee_id | user_id | name | employee_type | store_id | remaining_leave |
|-------------|---------|------|---------------|----------|-----------------|
| emp-manager-001 | user-manager-001 | 박수진 | REGULAR | store-001 | 15.0 |
| emp-001 | user-emp-001 | 김민수 | REGULAR | store-001 | 13.5 |
| emp-002 | user-emp-002 | 이지영 | REGULAR | store-001 | 14.0 |
| emp-manager-002 | user-manager-002 | 최동현 | REGULAR | store-002 | 15.0 |
| emp-003 | user-emp-003 | 정서연 | REGULAR | store-002 | 15.0 |

## 기본 매장

### 매장 정보 (stores 테이블)

| store_id | name | location |
|----------|------|----------|
| store-001 | 강남점 | 서울시 강남구 테헤란로 123 |
| store-002 | 홍대점 | 서울시 마포구 홍익로 456 |
| store-003 | 신촌점 | 서울시 서대문구 신촌역로 789 |

## 기본 급여 정책

### 급여 정책 (payroll_policies 테이블)

| payroll_policy_id | policy_type | multiplier | effective_from | effective_to | description |
|-------------------|-------------|------------|----------------|--------------|-------------|
| policy-001 | OVERTIME | 1.5 | 2024-01-01 | NULL (무기한) | 초과근무 가산율 |
| policy-002 | NIGHT_SHIFT | 1.5 | 2024-01-01 | NULL (무기한) | 야간근무 가산율 |
| policy-003 | WEEKEND | 1.5 | 2024-01-01 | NULL (무기한) | 주말근무 가산율 |
| policy-004 | HOLIDAY | 2.0 | 2024-01-01 | NULL (무기한) | 공휴일근무 가산율 |

## 데이터 로드 규칙

1. local 프로파일에서만 data.sql이 실행됨 (`spring.sql.init.mode: always`)
2. dev/prod 프로파일에서는 data.sql이 실행되지 않음 (`spring.sql.init.mode: never`)
3. local 프로파일은 `ddl-auto: create-drop`이므로 서버 재시작 시 모든 데이터가 초기화됨
4. data.sql은 JPA 엔티티 초기화 이후에 실행됨 (`defer-datasource-initialization: true`)
5. 모든 레코드의 `created_at`, `updated_at`은 `NOW()`로 삽입 시점의 타임스탬프 사용

## 매장-사용자 매핑 관계

```
강남점 (store-001)
├── 매니저: 박수진 (manager.gangnam@lms.com)
├── 직원: 김민수 (employee1.gangnam@lms.com)
└── 직원: 이지영 (employee2.gangnam@lms.com)

홍대점 (store-002)
├── 매니저: 최동현 (manager.hongdae@lms.com)
└── 직원: 정서연 (employee1.hongdae@lms.com)

신촌점 (store-003)
└── (매니저/직원 미배정)
```
