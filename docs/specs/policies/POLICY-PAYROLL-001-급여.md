# POLICY-PAYROLL-001: 급여

## 기본 정보
- type: policy
- category: payroll
- owner: LMS팀
- last_updated: 2026-03-08

## 관련 상위 정책
(없음)

## 정책 규칙

### 급여 계산 공식
- amount = hours × hourlyRate × multiplier
- 소수점 2자리, HALF_UP 반올림
- baseAmount = WEEKDAY 근무의 합계
- overtimeAmount = 비WEEKDAY (NIGHT, WEEKEND, HOLIDAY) 근무의 합계
- totalAmount = baseAmount + overtimeAmount - deductions

### 근무유형 판정 (우선순위)
1. HOLIDAY: 공휴일 (1월 1일, 12월 25일)
2. WEEKEND: 토요일 또는 일요일
3. NIGHT: 22:00 ~ 06:00 사이에 출근 또는 퇴근
4. WEEKDAY: 위에 해당하지 않는 경우

### 가산율
- WEEKDAY: 정책 적용 없음 (1.0배)
- NIGHT: OVERTIME_WEEKDAY 정책 적용 (기본 1.5배)
- WEEKEND: OVERTIME_WEEKEND 정책 적용 (기본 2.0배)
- HOLIDAY: OVERTIME_HOLIDAY 정책 적용 (기본 2.5배)
- 정책이 없는 경우 기본값: 1.0배

### 금액 제약
- baseAmount >= 0
- overtimeAmount >= 0
- deductions >= 0
- multiplier: 0 이상 10 이하

### 급여 산정 규칙
- 동일 기간에 중복 급여 산정 불가
- 해당 기간에 출퇴근 기록이 있어야 함
- 완료된 출퇴근 기록만 사용 (checkOutTime 존재)
- 승인된 휴가 날짜는 계산에서 제외
- 지급 완료(isPaid=true)된 급여는 수정 불가
- 기간 형식: YYYY-MM (정규식 검증)

### 배치 급여 산정
- 특정 매장 또는 전체 활성 근로자 대상
- 개별 실패 시에도 나머지 계속 처리 (graceful degradation)
- BatchStatus: 모든 성공 → COMPLETED, 부분 실패 → PARTIAL_SUCCESS, 전체 실패 → FAILED
- hourlyRate: 하드코딩 10,000원 (FIXME: 근로자별 시급 테이블 필요)
- 스케줄: 매월 마지막 날 01:00 (cron: `0 0 1 L * ?`)

### 급여 정책 관리
- 동일 PolicyType에 유효 기간이 겹치는 정책 생성 불가
- 현재 유효한 정책만 수정 가능
- effectiveTo가 null이면 무기한 유효
- 정책 종료(terminate): endDate >= effectiveFrom 검증

## 적용 대상
- LMS-PAYROLL-001 (급여 산정)
- LMS-PAYROLL-002 (급여 정책 관리)
