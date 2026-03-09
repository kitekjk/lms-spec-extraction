# POLICY-PAYROLL-001 급여

## 기본 정보
- type: policy
- id: POLICY-PAYROLL-001
- last-updated: 2026-03-09

## 정책 규칙

### 1. 급여 산정 방식
1. 급여는 시간 단위(hourlyRate)로 산정한다.
2. 일별 근무 시간 = 퇴근 시각 - 출근 시각 (시간 단위, 소수점 2자리, HALF_UP 반올림).
3. 일별 급여 = 근무 시간 x 시급 x 가산율 (소수점 2자리, HALF_UP 반올림).
4. 총 급여 = 기본급(baseAmount) + 가산금액(overtimeAmount) (소수점 2자리, HALF_UP 반올림).

### 2. 근무 유형별 가산율 (WorkType)
1. 시스템은 4가지 근무 유형을 정의한다:
   - WEEKDAY: 평일 기본 근무 (가산율 1.0)
   - NIGHT: 야간 근무 (22:00 ~ 06:00)
   - WEEKEND: 주말 근무 (토요일, 일요일)
   - HOLIDAY: 공휴일 근무

### 3. 가산율 정책 (초기 데이터 기준)
| 정책 ID | 유형 | 가산율 | 시행일 | 종료일 |
|---------|------|--------|--------|--------|
| policy-001 | OVERTIME (초과근무) | 1.5배 | 2024-01-01 | 무기한 |
| policy-002 | NIGHT_SHIFT (야간근무) | 1.5배 | 2024-01-01 | 무기한 |
| policy-003 | WEEKEND (주말근무) | 1.5배 | 2024-01-01 | 무기한 |
| policy-004 | HOLIDAY (공휴일근무) | 2.0배 | 2024-01-01 | 무기한 |

### 4. 급여 정책 유형 (PolicyType)
1. OVERTIME_WEEKDAY: 평일 초과근무
2. OVERTIME_WEEKEND: 주말 초과근무
3. OVERTIME_HOLIDAY: 공휴일 초과근무
4. NIGHT_SHIFT: 야간 근무
5. HOLIDAY_WORK: 휴일 근무
6. BONUS: 보너스
7. ALLOWANCE: 수당

### 5. 근무 유형 판정 우선순위
1. 근무 유형은 다음 우선순위로 판정한다: 공휴일 > 주말 > 야간 > 평일.
2. 공휴일 판정: 1월 1일(신정), 12월 25일(크리스마스). (향후 공휴일 테이블 또는 외부 API로 확장 예정)
3. 주말 판정: 토요일(SATURDAY) 또는 일요일(SUNDAY).
4. 야간 근무 판정: 출근 시각이 22:00 이후이거나 06:00 이전, 또는 퇴근 시각이 22:00 이후이거나 06:00 이전.
5. 위 조건에 해당하지 않으면 평일(WEEKDAY) 근무로 판정한다.

### 6. 급여 계산 시 제외 조건
1. 퇴근 기록이 없는(PENDING 상태) 출퇴근 기록은 급여 계산에서 제외한다.
2. 승인된 휴가(APPROVED) 기간의 출퇴근 기록은 급여 계산에서 제외한다.

### 7. 급여 정책 관리
1. SUPER_ADMIN만 급여 정책(가산율)을 등록/수정할 수 있다.
2. 급여 정책은 시행일(effective_from)과 종료일(effective_to)을 가진다.
3. effective_to가 NULL이면 무기한 유효하다.
4. 급여 계산 시 해당 근무 날짜에 유효한 정책을 적용한다.
5. 유효한 정책이 없으면 가산율 1.0(기본)을 적용한다.

### 8. 급여 조회 권한
1. EMPLOYEE는 본인의 급여 내역만 조회할 수 있다.
2. MANAGER는 소속 매장 근로자의 급여 산정 결과를 조회할 수 있다.
3. SUPER_ADMIN은 전체 매장의 급여 산정 결과를 조회할 수 있다.

### 9. 급여 산정 구성 요소
| 항목 | 설명 |
|------|------|
| payrollId | 급여 고유 식별자 |
| employeeId | 근로자 식별자 |
| period | 급여 산정 기간 (시작일 ~ 종료일) |
| baseAmount | 기본급 (평일 근무 합계) |
| overtimeAmount | 가산 금액 (야간/주말/공휴일 합계) |
| totalAmount | 총 급여 (baseAmount + overtimeAmount) |

### 10. 급여 상세 (PayrollDetail)
| 항목 | 설명 |
|------|------|
| workDate | 근무 날짜 |
| workType | 근무 유형 (WEEKDAY/NIGHT/WEEKEND/HOLIDAY) |
| hours | 근무 시간 (소수점 2자리) |
| hourlyRate | 시급 |
| multiplier | 적용된 가산율 |
| amount | 일별 급여 금액 |

## 적용 대상
- 급여(Payroll) 도메인: 급여 산정, 정책 관리, 결과 조회
- 출퇴근(Attendance) 도메인: 근무 시간 데이터 제공
- 휴가(Leave) 도메인: 승인된 휴가 기간 급여 제외
- 근로자(Employee) 도메인: 시급 정보 제공
