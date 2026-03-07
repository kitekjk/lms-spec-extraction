# POLICY-LEAVE-001: 휴가

## 기본 정보
- type: policy
- category: leave
- owner: LMS팀
- last_updated: 2026-03-08

## 관련 상위 정책
(없음)

## 정책 규칙

### 연차 정책 (근로자 유형별)
- REGULAR (정규직): 15일/년
- IRREGULAR (비정규직): 11일/년
- PART_TIME (파트타임): 0일 (무급 휴가만 가능)

### 휴가 유형
- ANNUAL (연차), SICK (병가), PERSONAL (개인 사유), MATERNITY (출산 휴가), PATERNITY (육아 휴가), BEREAVEMENT (경조사), UNPAID (무급 휴가)
- 모든 유형에 대해 승인이 필요함 (requiresApproval=true)

### 휴가 신청 규칙
- 과거 날짜 휴가 신청 불가 (startDate >= 오늘)
- 시작일이 종료일 이후일 수 없음
- 휴가 일수 = endDate - startDate + 1 (양 끝 포함)
- 잔여 연차가 신청 일수 이상이어야 함 (PART_TIME 제외)
- PART_TIME 근로자는 잔여 연차 검증을 건너뜀 (항상 신청 가능)
- 승인된(APPROVED) 기존 휴가와 기간 중복 불가

### 상태 전이
- PENDING → APPROVED: 승인 (연차 차감)
- PENDING → REJECTED: 거절 (거절 사유 필수, 비어있을 수 없음)
- PENDING → CANCELLED: 취소 (연차 변동 없음)
- APPROVED → CANCELLED: 취소 (연차 복원)

### 연차 관리
- 승인 시: employee.deductLeave(days) 즉시 차감
- 승인 후 취소 시: employee.restoreLeave(days) 복원
- 거절/미승인 취소 시: 잔여 연차 변동 없음

## 적용 대상
- LMS-LEAVE-001 (휴가 신청)
- LMS-LEAVE-002 (휴가 승인)
