#!/usr/bin/env python3
"""
Spec 린터: Backend + Frontend Spec 문서 검증.

사용법:
  python spec_lint.py docs/specs/
  python spec_lint.py docs/specs/screens/
  python spec_lint.py docs/specs/e2e/
"""

import sys, re, os
from pathlib import Path

REQUIRED_SECTIONS = {
    "service_definition": ["기본 정보", "서비스 목적과 범위", "핵심 모델", "외부 계약", "소유 데이터"],
    "use_case": ["기본 정보", "관련 정책", "관련 Spec", "관련 모델", "개요", "기본 흐름",
                 "검증 조건", "비기능 요구사항", "테스트 시나리오"],
    "api_spec": ["기본 정보", "관련 Spec", "엔드포인트 목록"],
    "policy": ["기본 정보", "정책 규칙", "적용 대상"],
    "architecture_rules": ["레이어 정의와 책임", "의존성 방향"],
    "naming_guide": ["패키지", "클래스", "API 경로"],
    "infra_config": ["데이터베이스"],
    "init_data": ["기본 사용자"],
    "frontend_definition": ["기본 정보", "Backend API 연동", "화면 목록"],
    "frontend_architecture": ["디렉토리 규칙", "API 연동 규칙"],
    "screen_spec": ["기본 정보", "관련 Backend Spec", "화면 목적", "화면 구성 요소", "사용자 흐름"],
    "e2e_test_spec": ["기본 정보", "관련 Backend Spec", "테스트 시나리오"],
}

VAGUE_TERMS = ["적절한", "충분한", "필요한", "적당한", "알맞은",
               "등등", "기타", "필요 시", "상황에 따라", "가능하면"]

TC_ID_PATTERN = re.compile(r"TC-[A-Z]+-\d+-\d+")
TC_FE_PATTERN = re.compile(r"TC-FE-\d+-\d+")
API_PATTERN = re.compile(r"(GET|POST|PUT|PATCH|DELETE)\s+/api/")
TEST_LEVELS = {"Unit", "Integration", "E2E"}


class LintError:
    def __init__(self, file, line, level, message):
        self.file, self.line, self.level, self.message = file, line, level, message
    def __str__(self):
        return f"[{self.level}] {self.file}:{self.line} - {self.message}"


def parse_spec(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")
    result = {"title": None, "spec_id": None, "type": None,
              "sections": {}, "h3_sections": {}, "lines": lines, "content": content}
    current_h2, current_content = None, []
    for line in lines:
        if line.startswith("# ") and result["title"] is None:
            result["title"] = line[2:].strip()
            m = re.match(r"^((?:[A-Z]+-)+\d+)", result["title"])
            if m: result["spec_id"] = m.group(1)
        elif line.startswith("## "):
            if current_h2: result["sections"][current_h2] = "\n".join(current_content)
            current_h2 = line[3:].strip(); current_content = []
        elif line.startswith("### "):
            result["h3_sections"][line[4:].strip()] = current_h2
            current_content.append(line)
        else:
            current_content.append(line)
        if current_h2 == "기본 정보" and line.strip().startswith("- type:"):
            result["type"] = line.split(":", 1)[1].strip()
    if current_h2: result["sections"][current_h2] = "\n".join(current_content)
    return result


def lint_spec(filepath):
    errors = []
    fname = str(filepath)
    try: spec = parse_spec(filepath)
    except Exception as e:
        errors.append(LintError(fname, 0, "ERROR", f"파싱 실패: {e}")); return errors

    if not spec["title"]: errors.append(LintError(fname, 1, "ERROR", "제목 없음"))
    if not spec["type"]: errors.append(LintError(fname, 0, "WARNING", "type 없음"))

    # 필수 섹션
    if spec["type"] and spec["type"] in REQUIRED_SECTIONS:
        for sec in REQUIRED_SECTIONS[spec["type"]]:
            if not any(sec in s for s in spec["sections"]):
                errors.append(LintError(fname, 0, "ERROR", f"필수 섹션 누락: ## {sec}"))

    # ── use_case ──
    if spec["type"] == "use_case":
        if not any("모델" in s for s in spec["sections"]):
            errors.append(LintError(fname, 0, "ERROR", "## 관련 모델 누락"))
        else:
            mc = " ".join(spec["sections"][s] for s in spec["sections"] if "모델" in s)
            if "주 모델" not in mc:
                errors.append(LintError(fname, 0, "WARNING", "'주 모델' 구분 없음"))

        if not any("비기능" in s for s in spec["sections"]):
            errors.append(LintError(fname, 0, "ERROR", "## 비기능 요구사항 누락"))
        else:
            nc = " ".join(spec["sections"][s] for s in spec["sections"] if "비기능" in s)
            if "POLICY-NFR" not in nc and "공통" not in nc:
                errors.append(LintError(fname, 0, "WARNING", "NFR에 POLICY-NFR-001 참조 없음"))

        if "테스트 시나리오" in spec["sections"]:
            tc = spec["sections"]["테스트 시나리오"]
            ids = TC_ID_PATTERN.findall(tc)
            if len(ids) < 3:
                errors.append(LintError(fname, 0, "ERROR", f"테스트 시나리오 {len(ids)}개, 최소 3개 필요"))
            if len(ids) != len(set(ids)):
                errors.append(LintError(fname, 0, "ERROR", "TC-ID 중복"))
            for h3 in [k for k,v in spec["h3_sections"].items() if v == "테스트 시나리오"]:
                if not any(f"({lv})" in h3 for lv in TEST_LEVELS):
                    errors.append(LintError(fname, 0, "WARNING", f"레벨 없음: {h3[:50]}"))

        for sec in ("기본 흐름", "대안 흐름"):
            if sec in spec["sections"] and re.search(r"fun\s+\w+", spec["sections"][sec]):
                errors.append(LintError(fname, 0, "WARNING", f"## {sec}에 함수명 포함"))

    # ── screen_spec: 구성 요소별 Backend API 매핑 검증 ──
    if spec["type"] == "screen_spec":
        # Backend Spec 참조
        if "관련 Backend Spec" in spec["sections"]:
            ids = re.findall(r"LMS-(?:[A-Z]+-)+\d+", spec["sections"]["관련 Backend Spec"])
            if not ids:
                errors.append(LintError(fname, 0, "ERROR", "화면 Spec에 Backend Spec 참조 없음"))

        # 화면 구성 요소 검증
        if "화면 구성 요소" in spec["sections"]:
            comp_content = spec["sections"]["화면 구성 요소"]
            # h3 수집 (구성 요소 제목들)
            components = [k for k, v in spec["h3_sections"].items() if v == "화면 구성 요소"]

            if not components:
                errors.append(LintError(fname, 0, "WARNING", "## 화면 구성 요소에 ### 항목이 없습니다"))
            else:
                for comp in components:
                    # 해당 컴포넌트 내용 찾기 (h3 이후 ~ 다음 h3 전까지)
                    # 간단히 전체 content에서 검사
                    pass

                # Backend API 매핑 확인
                has_api = bool(API_PATTERN.search(comp_content)) or "Backend API" in comp_content
                if not has_api:
                    errors.append(LintError(fname, 0, "ERROR",
                        "화면 구성 요소에 Backend API 매핑이 없습니다. 각 요소에 'Backend API: GET/POST ...' 필요"))

                # 빈 상태 정의 확인
                if "빈 상태" not in comp_content:
                    errors.append(LintError(fname, 0, "WARNING",
                        "화면 구성 요소에 '빈 상태' 정의가 없습니다. 데이터 0건 시 UI를 정의하세요"))

                # 참조 Spec 확인
                api_refs = re.findall(r"LMS-API-[A-Z]+-\d+", comp_content)
                if not api_refs:
                    errors.append(LintError(fname, 0, "WARNING",
                        "화면 구성 요소에 API Spec 참조(LMS-API-xxx)가 없습니다"))

    # ── e2e_test_spec: 데이터 시딩 + 조회 검증 ──
    if spec["type"] == "e2e_test_spec":
        if "관련 Backend Spec" not in spec["sections"]:
            errors.append(LintError(fname, 0, "ERROR", "E2E Spec에 ## 관련 Backend Spec 없음"))
        else:
            ids = re.findall(r"LMS-(?:[A-Z]+-)+\d+", spec["sections"]["관련 Backend Spec"])
            if not ids:
                errors.append(LintError(fname, 0, "ERROR", "## 관련 Backend Spec에 참조 ID 없음"))

        if "테스트 시나리오" in spec["sections"]:
            tc = spec["sections"]["테스트 시나리오"]
            ids = TC_FE_PATTERN.findall(tc)
            if len(ids) < 2:
                errors.append(LintError(fname, 0, "ERROR", f"E2E 시나리오 {len(ids)}개, 최소 2개 필요"))
            if len(ids) != len(set(ids)):
                errors.append(LintError(fname, 0, "ERROR", "TC-FE ID 중복"))

            lines = tc.split("\n")
            has_given = any("Given:" in l or "Given :" in l for l in lines)
            has_when = any("When:" in l or "When :" in l for l in lines)
            has_then = any("Then:" in l or "Then :" in l for l in lines)
            if not (has_given and has_when and has_then):
                missing = [x for x, ok in [("Given",has_given),("When",has_when),("Then",has_then)] if not ok]
                errors.append(LintError(fname, 0, "WARNING", f"Given-When-Then 불완전: {'/'.join(missing)} 없음"))

            # 데이터 시딩 확인 (Given에 Backend 데이터 언급)
            given_sections = []
            in_given = False
            for line in lines:
                if "Given:" in line or "Given :" in line:
                    in_given = True
                elif ("When:" in line or "When :" in line or
                      "Then:" in line or "Then :" in line or
                      line.startswith("### ")):
                    in_given = False
                if in_given:
                    given_sections.append(line)
            given_text = " ".join(given_sections)
            has_data_prep = any(kw in given_text for kw in
                ["Backend 데이터", "데이터 준비", "seed", "init-data", "로그인"])
            if not has_data_prep:
                errors.append(LintError(fname, 0, "WARNING",
                    "E2E Given에 데이터 준비(Backend 데이터/시딩) 내용이 없습니다"))

            # 조회 검증 확인 (Then에 표시/텍스트 확인)
            then_sections = []
            in_then = False
            for line in lines:
                if "Then:" in line or "Then :" in line:
                    in_then = True
                elif ("Given:" in line or "Given :" in line or
                      "When:" in line or "When :" in line or
                      line.startswith("### ")):
                    in_then = False
                if in_then:
                    then_sections.append(line)
            then_text = " ".join(then_sections)
            has_view_check = any(kw in then_text for kw in
                ["표시", "텍스트", "목록", "건", "메시지", "배지", "미표시", "이동"])
            if not has_view_check:
                errors.append(LintError(fname, 0, "WARNING",
                    "E2E Then에 화면 조회 검증(표시/텍스트 확인) 내용이 없습니다"))

    # ── 공통: 참조 링크, 모호한 표현 ──
    if spec["type"] in ("use_case", "api_spec"):
        for ref in ("관련 정책", "관련 Spec"):
            if ref in spec["sections"] and not re.findall(r"(?:[A-Z]+-)+\d+", spec["sections"][ref]):
                errors.append(LintError(fname, 0, "WARNING", f"## {ref}에 참조 ID 없음"))

    if "검증 조건" in spec["sections"]:
        items = [l.strip() for l in spec["sections"]["검증 조건"].split("\n") if l.strip().startswith("- ")]
        if not items: errors.append(LintError(fname, 0, "ERROR", "검증 조건 항목 없음"))
        for cl in items:
            for v in VAGUE_TERMS:
                if v in cl: errors.append(LintError(fname, 0, "WARNING", f"모호: '{v}' in {cl.strip()}"))

    for sec in ("비즈니스 규칙", "정책 규칙"):
        if sec in spec["sections"]:
            for v in VAGUE_TERMS:
                if v in spec["sections"][sec]:
                    errors.append(LintError(fname, 0, "WARNING", f"{sec}에 모호한 표현 '{v}'"))

    return errors


def lint_directory(dirpath):
    all_errors = []
    files = sorted(Path(dirpath).rglob("*.md"))
    if not files: print(f"⚠ {dirpath}에 Spec 없음"); return all_errors

    all_ids, all_tc = set(), set()
    for f in files:
        try:
            sp = parse_spec(f)
            if sp["spec_id"]: all_ids.add(sp["spec_id"])
            for sec in sp["sections"]:
                all_tc.update(TC_ID_PATTERN.findall(sp["sections"][sec]))
                all_tc.update(TC_FE_PATTERN.findall(sp["sections"][sec]))
        except: pass

    for f in files:
        errs = lint_spec(f)
        try:
            sp = parse_spec(f)
            for ref in ("관련 정책", "관련 Spec", "관련 Backend Spec"):
                if ref in sp["sections"]:
                    for rid in re.findall(r"((?:[A-Z]+-)+\d+)", sp["sections"][ref]):
                        if rid not in all_ids and not rid.startswith("POLICY-CORP-"):
                            errs.append(LintError(str(f), 0, "WARNING", f"참조 '{rid}' 미존재"))
        except: pass
        all_errors.extend(errs)

    if not any("frontend" in str(dirpath).lower() for _ in [1]):
        if not any("POLICY-NFR" in str(f) for f in files):
            all_errors.append(LintError("policies/", 0, "ERROR", "POLICY-NFR-001 없음"))

    if all_tc:
        be = [t for t in all_tc if not t.startswith("TC-FE")]
        fe = [t for t in all_tc if t.startswith("TC-FE")]
        print(f"\n📊 테스트 케이스: Backend {len(be)}개, Frontend E2E {len(fe)}개, 총 {len(all_tc)}개")

    return all_errors


def main():
    if len(sys.argv) < 2: print("사용법: python spec_lint.py <파일|디렉토리>"); sys.exit(1)
    target = sys.argv[1]
    if os.path.isfile(target): errors = lint_spec(target)
    elif os.path.isdir(target): errors = lint_directory(target)
    else: print(f"❌ 없음: {target}"); sys.exit(1)

    ec = sum(1 for e in errors if e.level == "ERROR")
    wc = sum(1 for e in errors if e.level == "WARNING")
    if errors:
        print(f"\n{'='*60}\nSpec Lint: {ec} errors, {wc} warnings\n{'='*60}\n")
        for e in errors: print(f"  {'❌' if e.level=='ERROR' else '⚠'} {e}")
        print()
    else: print(f"\n✅ 모든 Spec 통과!\n")
    sys.exit(1 if ec > 0 else 0)

if __name__ == "__main__": main()
