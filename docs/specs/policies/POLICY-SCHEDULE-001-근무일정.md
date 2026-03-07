# POLICY-SCHEDULE-001: 근무 일정

## 기본 정보
- type: policy
- category: schedule
- owner: LMS팀
- last_updated: 2026-03-08

## 관련 상위 정책
(없음)

## 정책 규칙

### 일정 생성
- MANAGER 또는 SUPER_ADMIN만 일정 생성 가능
- 근로자는 소속 매장에만 일정 등록 가능 (storeId 일치 검증)
- 하나의 Employee는 하나의 날짜에 하나의 WorkSchedule만 가질 수 있음
- 생성 시 isConfirmed=false로 초기화

### 일정 변경
- MANAGER 또는 SUPER_ADMIN만 변경 가능
- 확정된(isConfirmed=true) 일정은 시간/날짜 변경 불가
- 미확정 일정만 수정/삭제 가능

### 시간 제약
- startTime은 endTime보다 이전이어야 함
- WorkTime 표준 값: 09:00~18:00 (`WorkTime.standard()`)

### 주말 판별
- WorkDate.isWeekend(): 토요일 또는 일요일이면 true

## 적용 대상
- LMS-SCHEDULE-001 (근무 일정 생성)
- LMS-SCHEDULE-002 (근무 일정 변경)
