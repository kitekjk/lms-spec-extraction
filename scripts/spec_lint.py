#!/usr/bin/env python3
"""
Spec 린터: Markdown Spec 문서의 구조와 완결성을 검증한다.

사용법:
  python spec_lint.py docs/specs/              # 전체 (하위 디렉토리 포함)
  python spec_lint.py docs/specs/attendance/   # 특정 도메인
  python spec_lint.py docs/specs/policies/     # 정책만
  python spec_lint.py docs/specs/LMS-ATT-001.md  # 단일 파일
"""

import sys
import re
import os
from pathlib import Path

REQUIRED_SECTIONS = {
    "service_definition": ["기본 정보", "서비스 목적과 범위", "핵심 모델", "외부 계약", "소유 데이터"],
    "use_case": ["기본 정보", "관련 정책", "관련 Spec", "관련 모델", "개요", "기본 흐름",
                 "검증 조건", "비기능 요구사항", "테스트 시나리오"],
    "api_spec": ["기본 정보", "관련 Spec", "엔드포인트 목록"],
    "policy": ["기본 정보", "정책 규칙", "적용 대상"],
    "architecture_rules": ["레이어 정의와 책임", "의존성 방향"],
    "naming_guide": ["패키지", "클래스", "API 경로"],
    "infra_config": ["데이터베이스", "프로파일별 설정"],
    "init_data": ["기본 사용자"],
}

VAGUE_TERMS = ["적절한", "충분한", "필요한", "적당한", "알맞은",
               "등등", "기타", "필요 시", "상황에 따라", "가능하면", "될 수 있으면"]

TC_ID_PATTERN = re.compile(r"TC-[A-Z]+-\d+-\d+")
TEST_LEVELS = {"Unit", "Integration", "E2E"}


class LintError:
    def __init__(self, file, line, level, message):
        self.file = file
        self.line = line
        self.level = level
        self.message = message

    def __str__(self):
        return f"[{self.level}] {self.file}:{self.line} - {self.message}"


def parse_spec(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    result = {"title": None, "spec_id": None, "type": None,
              "sections": {}, "h3_sections": {}, "lines": lines, "content": content}
    current_h2 = None
    current_content = []

    for line in lines:
        if line.startswith("# ") and result["title"] is None:
            result["title"] = line[2:].strip()
            m = re.match(r"^([A-Z]+(?:-[A-Z]+)*-\d+)", result["title"])
            if m:
                result["spec_id"] = m.group(1)
        elif line.startswith("## "):
            if current_h2:
                result["sections"][current_h2] = "\n".join(current_content)
            current_h2 = line[3:].strip()
            current_content = []
        elif line.startswith("### "):
            h3_title = line[4:].strip()
            result["h3_sections"][h3_title] = current_h2
            current_content.append(line)
        else:
            current_content.append(line)

        if current_h2 == "기본 정보" and line.strip().startswith("- type:"):
            result["type"] = line.split(":", 1)[1].strip()

    if current_h2:
        result["sections"][current_h2] = "\n".join(current_content)
    return result


def lint_spec(filepath):
    errors = []
    fname = str(filepath)

    try:
        spec = parse_spec(filepath)
    except Exception as e:
        errors.append(LintError(fname, 0, "ERROR", f"파일 파싱 실패: {e}"))
        return errors

    # 1. Title
    if not spec["title"]:
        errors.append(LintError(fname, 1, "ERROR", "제목(# )이 없습니다"))

    # 2. type
    if not spec["type"]:
        errors.append(LintError(fname, 0, "WARNING", "## 기본 정보에 type이 없습니다"))

    # 3. 필수 섹션
    if spec["type"] and spec["type"] in REQUIRED_SECTIONS:
        for section in REQUIRED_SECTIONS[spec["type"]]:
            found = any(section in s for s in spec["sections"])
            if not found:
                errors.append(LintError(fname, 0, "ERROR", f"필수 섹션 누락: ## {section}"))

    # 4. 관련 모델 (use_case)
    if spec["type"] == "use_case":
        model_sections = [s for s in spec["sections"] if "모델" in s]
        if not model_sections:
            errors.append(LintError(fname, 0, "ERROR",
                "## 관련 모델 섹션 누락 (주 모델/참조 모델 필요)"))
        else:
            model_content = " ".join(spec["sections"][s] for s in model_sections)
            if "주 모델" not in model_content:
                errors.append(LintError(fname, 0, "WARNING", "## 관련 모델에 '주 모델' 구분이 없습니다"))

    # 5. 참조 링크
    if spec["type"] in ("use_case", "api_spec"):
        for ref in ("관련 정책", "관련 Spec"):
            if ref in spec["sections"]:
                ids = re.findall(r"[A-Z]+(?:-[A-Z]+)*-\d+", spec["sections"][ref])
                if not ids:
                    errors.append(LintError(fname, 0, "WARNING", f"## {ref}에 참조 ID가 없습니다"))

    # 6. 검증 조건 구체성
    if "검증 조건" in spec["sections"]:
        criteria = spec["sections"]["검증 조건"]
        items = [l.strip() for l in criteria.split("\n") if l.strip().startswith("- ")]
        if not items:
            errors.append(LintError(fname, 0, "ERROR", "## 검증 조건에 항목이 없습니다"))
        for cl in items:
            for vague in VAGUE_TERMS:
                if vague in cl:
                    ln = next((i+1 for i, l in enumerate(spec["lines"]) if cl.strip("- ") in l), 0)
                    errors.append(LintError(fname, ln, "WARNING", f"모호한 표현 '{vague}': {cl.strip()}"))

    # 7. 비즈니스/정책 규칙 모호한 표현
    for sec in ("비즈니스 규칙", "정책 규칙"):
        if sec in spec["sections"]:
            for vague in VAGUE_TERMS:
                if vague in spec["sections"][sec]:
                    errors.append(LintError(fname, 0, "WARNING", f"{sec}에 모호한 표현 '{vague}'"))

    # 8. 함수명 경고
    if spec["type"] == "use_case":
        for sec in ("기본 흐름", "대안 흐름"):
            if sec in spec["sections"]:
                if re.search(r"fun\s+\w+|\.invoke\(|\.call\(|\(\)\s*→", spec["sections"][sec]):
                    errors.append(LintError(fname, 0, "WARNING", f"## {sec}에 함수명이 포함된 것 같습니다"))

    # 9. 테스트 시나리오 (use_case)
    if spec["type"] == "use_case" and "테스트 시나리오" in spec["sections"]:
        tc_content = spec["sections"]["테스트 시나리오"]
        tc_ids = TC_ID_PATTERN.findall(tc_content)

        if len(tc_ids) < 3:
            errors.append(LintError(fname, 0, "ERROR",
                f"테스트 시나리오 {len(tc_ids)}개. 최소 3개 필요 (정상/대안/예외)"))

        if len(tc_ids) != len(set(tc_ids)):
            dups = [x for x in tc_ids if tc_ids.count(x) > 1]
            errors.append(LintError(fname, 0, "ERROR", f"TC-ID 중복: {', '.join(set(dups))}"))

        h3s = [k for k, v in spec["h3_sections"].items() if v == "테스트 시나리오"]
        for h3 in h3s:
            if not any(f"({lv})" in h3 for lv in TEST_LEVELS):
                errors.append(LintError(fname, 0, "WARNING",
                    f"테스트 레벨(Unit/Integration/E2E) 없음: {h3[:60]}"))

        lines = tc_content.split("\n")
        has_g = any("Given:" in l or "Given :" in l for l in lines)
        has_w = any("When:" in l or "When :" in l for l in lines)
        has_t = any("Then:" in l or "Then :" in l for l in lines)
        if not (has_g and has_w and has_t):
            missing = [x for x, ok in [("Given", has_g), ("When", has_w), ("Then", has_t)] if not ok]
            errors.append(LintError(fname, 0, "WARNING",
                f"테스트 시나리오에 {'/'.join(missing)} 없음. Given-When-Then 권장"))

    # 10. 비기능 요구사항 (use_case)
    if spec["type"] == "use_case":
        nfr_found = any("비기능" in s for s in spec["sections"])
        if not nfr_found:
            errors.append(LintError(fname, 0, "ERROR",
                "## 비기능 요구사항 섹션 누락. 공통 NFR 참조 또는 특화 NFR 기술 필요"))
        else:
            nfr_content = " ".join(spec["sections"][s] for s in spec["sections"] if "비기능" in s)
            if not nfr_content.strip():
                errors.append(LintError(fname, 0, "WARNING",
                    "## 비기능 요구사항 섹션이 비어 있습니다"))
            # NFR 정책 참조 확인
            if "POLICY-NFR" not in nfr_content and "공통" not in nfr_content:
                errors.append(LintError(fname, 0, "WARNING",
                    "비기능 요구사항에 POLICY-NFR-001 참조가 없습니다"))

    return errors


def lint_directory(dirpath):
    all_errors = []
    spec_files = sorted(Path(dirpath).rglob("*.md"))

    if not spec_files:
        print(f"⚠ {dirpath}에 Spec 파일이 없습니다")
        return all_errors

    all_spec_ids = set()
    all_tc_ids = set()
    for f in spec_files:
        try:
            spec = parse_spec(f)
            if spec["spec_id"]:
                all_spec_ids.add(spec["spec_id"])
            if "테스트 시나리오" in spec["sections"]:
                all_tc_ids.update(TC_ID_PATTERN.findall(spec["sections"]["테스트 시나리오"]))
        except:
            pass

    for f in spec_files:
        errors = lint_spec(f)
        try:
            spec = parse_spec(f)
            for ref in ("관련 정책", "관련 Spec"):
                if ref in spec["sections"]:
                    for rid in re.findall(r"([A-Z]+(?:-[A-Z]+)*-\d+)", spec["sections"][ref]):
                        if rid not in all_spec_ids and not rid.startswith("POLICY-CORP-"):
                            errors.append(LintError(str(f), 0, "WARNING", f"참조 '{rid}' 미존재"))
        except:
            pass
        all_errors.extend(errors)

    # NFR 정책 존재 확인
    nfr_exists = any("POLICY-NFR" in str(f) for f in spec_files)
    if not nfr_exists:
        all_errors.append(LintError("docs/specs/policies/", 0, "ERROR",
            "POLICY-NFR-001 비기능 요구사항 정책 파일이 없습니다"))

    # TC 통계
    if all_tc_ids:
        print(f"\n📊 전체 테스트 케이스: {len(all_tc_ids)}개")
        domain_counts = {}
        for tc in all_tc_ids:
            parts = tc.split("-")
            if len(parts) >= 2:
                domain_counts[parts[1]] = domain_counts.get(parts[1], 0) + 1
        for d, c in sorted(domain_counts.items()):
            print(f"   {d}: {c}개")

    return all_errors


def main():
    if len(sys.argv) < 2:
        print("사용법: python spec_lint.py <파일 또는 디렉토리>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isfile(target):
        errors = lint_spec(target)
    elif os.path.isdir(target):
        errors = lint_directory(target)
    else:
        print(f"❌ 경로를 찾을 수 없습니다: {target}")
        sys.exit(1)

    ec = sum(1 for e in errors if e.level == "ERROR")
    wc = sum(1 for e in errors if e.level == "WARNING")

    if errors:
        print(f"\n{'='*60}")
        print(f"Spec Lint 결과: {ec} errors, {wc} warnings")
        print(f"{'='*60}\n")
        for e in errors:
            print(f"  {'❌' if e.level == 'ERROR' else '⚠'} {e}")
        print()
    else:
        print(f"\n✅ 모든 Spec이 검증을 통과했습니다!\n")

    sys.exit(1 if ec > 0 else 0)


if __name__ == "__main__":
    main()
