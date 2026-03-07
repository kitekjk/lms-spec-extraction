# POLICY-ATTENDANCE-001: 출퇴근

## 기본 정보
- type: policy
- category: attendance
- owner: LMS팀
- last_updated: 2026-03-08

## 관련 상위 정책
(없음)

## 정책 규칙

### 출근
- 동일 날짜에 중복 출근 불가 (AlreadyCheckedInException)
- 출근 시 상태: PENDING (퇴근 대기)
- workScheduleId는 선택값 (일정 없이도 출근 가능)

### 퇴근
- 출근 기록이 없으면 퇴근 불가 (NotCheckedInException)
- 이미 퇴근한 기록에 재퇴근 불가 (AlreadyCheckedOutException)
- 퇴근 시간은 출근 시간 이후여야 함
- 퇴근 완료 시 상태: NORMAL

### 상태 판정
- 지각(LATE): 예정 출근 시간 + 10분 이후 출근
- 조퇴(EARLY_LEAVE): 예정 퇴근 시간 이전 퇴근
- 정상(NORMAL): 지각, 조퇴에 해당하지 않는 경우
- 결근(ABSENT): 관리자가 수동 설정
- 지각 허용 시간(LATE_TOLERANCE_MINUTES): 10분

### 출퇴근 수정
- MANAGER 또는 SUPER_ADMIN만 수정 가능
- 수정 사유(reason)는 필수
- 수정 시 AuditLog 자동 생성 (EntityListener)
- 변경 전/후 값은 AuditLog의 oldValue/newValue에 JSON으로 저장
- adjustedCheckOutTime은 선택값 (출근시간만 수정 가능)
- adjustedCheckInTime이 adjustedCheckOutTime 이후일 수 없음

## 적용 대상
- LMS-ATTENDANCE-001 (출퇴근 기록)
- LMS-ATTENDANCE-002 (출퇴근 수정)
