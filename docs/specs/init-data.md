# 초기 데이터 정의

## 기본 정보
- type: init_data
- 적용 프로파일: local, dev
- 초기화 방식: DemoDataInitializer (`@Component`, ApplicationRunner)
- 재시작 시 초기화됨 (`ddl-auto: create-drop`)

## 기본 매장

| 매장명 | 위치 |
|--------|------|
| 강남점 | 서울시 강남구 테헤란로 123 |
| 홍대점 | 서울시 마포구 홍대입구 456 |
| 신촌점 | 서울시 서대문구 신촌로 789 |

## 기본 사용자

| 역할 | 이메일 | 비밀번호 | 소속 매장 | 설명 |
|------|--------|----------|-----------|------|
| SUPER_ADMIN | admin@lms.com | password123 | 전체 | 시스템 관리자 |
| MANAGER | manager.gangnam@lms.com | password123 | 강남점 | 강남점 매니저 |
| MANAGER | manager.hongdae@lms.com | password123 | 홍대점 | 홍대점 매니저 |
| EMPLOYEE | employee1.gangnam@lms.com | password123 | 강남점 | 강남점 직원 1 |
| EMPLOYEE | employee2.gangnam@lms.com | password123 | 강남점 | 강남점 직원 2 |
| EMPLOYEE | employee1.hongdae@lms.com | password123 | 홍대점 | 홍대점 직원 1 |

## 기본 근로자

| 이름 | 유형 | 소속 매장 | 잔여 연차 |
|------|------|-----------|-----------|
| 김민수 | REGULAR | 강남점 | 15.0일 |
| 이영희 | REGULAR | 강남점 | 15.0일 |
| 박지훈 | IRREGULAR | 홍대점 | 11.0일 |

## 급여 정책

| 정책 유형 | 가산율 | 설명 |
|-----------|--------|------|
| OVERTIME_WEEKDAY | 1.5배 | 평일 초과근무 |
| NIGHT_SHIFT | 1.5배 | 야간 근무 (22:00~06:00) |
| OVERTIME_WEEKEND | 1.5배 | 주말 근무 |
| HOLIDAY_WORK | 2.0배 | 공휴일 근무 |

## 규칙
- local/dev 프로파일에서만 자동 생성
- 서버 재시작 시 초기화 (create-drop)
- 비밀번호는 BCrypt로 암호화하여 저장
- SUPER_ADMIN은 `User.reconstruct()`로 생성 (create()에서 제한됨)
- 매장-근로자 연결은 Employee의 storeId로 설정
