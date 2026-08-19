#!/usr/bin/env python
"""Safely sync allowlisted orchestration skills to Hermes sub-profiles.

Examples:
  python sync_orchestration_skills_to_profiles.py --dry-run --diff
  python sync_orchestration_skills_to_profiles.py --profiles athena,eos
  python sync_orchestration_skills_to_profiles.py --skills multi-agent-protocol
  python sync_orchestration_skills_to_profiles.py --verify-only

The script never touches SOUL.md, config.yaml, memories, plugins, or cron.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import shutil
import sys
from pathlib import Path

HERMES_HOME = Path.home() / "AppData" / "Local" / "hermes"
PROFILES_DIR = HERMES_HOME / "profiles"
ROOT_SKILLS = HERMES_HOME / "skills"

SKILLS = [
    Path("orchestration/multi-agent-protocol"),
    Path("orchestration/multi-agent-project-preflight"),
    Path("orchestration/agent-task-book-authoring"),
    Path("orchestration/multi-agent-orchestration-handbook"),
    Path("orchestration/self-improvement-governance"),
    Path("software-development/project-constitution-authoring"),
]

VERIFY_NEEDLES = {
    Path("orchestration/multi-agent-protocol"): [
        "多 Agent 开工技能加载顺序", "文档优先级", "Athena 开工裁决清单",
        "串行框架优先，再并行开发", "Eos 工程宪法验收清单", "模板索引",
        "维护与跨档案同步", "multi-agent-startup-runbook.md",
    ],
    Path("orchestration/multi-agent-project-preflight"): [
        "Step 0: 建立项目工程宪法", "agent-task-book-authoring", "module-ownership.yaml",
    ],
    Path("orchestration/self-improvement-governance"): [
        "自我优化与沉淀治理流程", "自我检查 → 证据化问题清单", "多档案同步", "幂等检查",
    ],
    Path("software-development/project-constitution-authoring"): ["项目工程宪法编写工作流", "版本治理与维护规则"],
    Path("orchestration/multi-agent-orchestration-handbook"): [
        "女仆家族固定编制的软件开发流程以 `multi-agent-protocol` 为准",
    ],
}

REQUIRED_FILES = {
    Path("orchestration/self-improvement-governance"): [
        "templates/self-improvement-batch-checklist.md",
    ],
    Path("orchestration/multi-agent-protocol"): [
        "templates/multi-agent-task-plan-template.md",
        "templates/parallel-readiness-checklist.md",
        "templates/model-switch-record-template.md",
        "templates/startup-artifacts-checklist.md",
        "templates/agents/project-brief.md",
        "templates/agents/task-board.yaml",
        "templates/agents/module-ownership.yaml",
        "templates/agents/decisions.md",
        "templates/agents/validation-log.md",
        "templates/agents/risk-register.md",
        "templates/agents/handoff.md",
        "scripts/sync_orchestration_skills_to_profiles.py",
        "references/multi-agent-startup-runbook.md",
    ],
    Path("software-development/project-constitution-authoring"): [
        "templates/project-constitution-template.md",
        "references/focusflow-project-constitution-example.md",
    ],
}


def csv_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def all_profiles() -> list[Path]:
    return sorted((p for p in PROFILES_DIR.iterdir() if p.is_dir()), key=lambda p: p.name) if PROFILES_DIR.exists() else []


def select_profiles(names: list[str] | None) -> list[Path]:
    profiles = all_profiles()
    if not names:
        return profiles
    lookup = {p.name.lower(): p for p in profiles}
    missing = [name for name in names if name.lower() not in lookup]
    if missing:
        raise ValueError(f"unknown profiles: {', '.join(missing)}")
    return [lookup[name.lower()] for name in names]


def select_skills(names: list[str] | None) -> list[Path]:
    if not names:
        return SKILLS.copy()
    lookup: dict[str, Path] = {}
    for rel in SKILLS:
        lookup[rel.as_posix().lower()] = rel
        lookup[rel.name.lower()] = rel
    selected: list[Path] = []
    missing: list[str] = []
    for name in names:
        rel = lookup.get(name.lower())
        if rel is None:
            missing.append(name)
        elif rel not in selected:
            selected.append(rel)
    if missing:
        raise ValueError(f"skills outside allowlist or unknown: {', '.join(missing)}")
    return selected


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_ignored(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"} or ".bak-" in path.name


def tree_manifest(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        p.relative_to(root).as_posix(): file_hash(p)
        for p in sorted(root.rglob("*")) if p.is_file() and not is_ignored(p.relative_to(root))
    }


def diff_summary(src: Path, dst: Path) -> tuple[int, int, int, list[str]]:
    source, target = tree_manifest(src), tree_manifest(dst)
    added = sorted(source.keys() - target.keys())
    removed = sorted(target.keys() - source.keys())
    changed = sorted(k for k in source.keys() & target.keys() if source[k] != target[k])
    details = [f"+ {x}" for x in added] + [f"~ {x}" for x in changed] + [f"- {x}" for x in removed]
    return len(added), len(changed), len(removed), details


def copy_skill(src: Path, dst: Path, timestamp: str, backup: bool) -> str:
    if not (src / "SKILL.md").exists():
        raise FileNotFoundError(f"missing source skill: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    action = "new"
    if dst.exists():
        if backup:
            backup_path = dst.with_name(f"{dst.name}.bak-{timestamp}")
            shutil.copytree(dst, backup_path)
            action = f"backup={backup_path.name}"
        else:
            action = "replaced-without-backup"
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "*.bak-*"))
    return action


def verify_root(skills_root: Path, skills: list[Path]) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for rel in skills:
        dst = skills_root / rel
        skill_file = dst / "SKILL.md"
        if not skill_file.exists():
            problems.append(f"missing SKILL.md: {rel.as_posix()}")
            continue
        text = skill_file.read_text(encoding="utf-8", errors="strict")
        for needle in VERIFY_NEEDLES.get(rel, []):
            if needle not in text:
                problems.append(f"missing text in {rel.as_posix()}: {needle}")
        for file_rel in REQUIRED_FILES.get(rel, []):
            if not (dst / file_rel).is_file():
                problems.append(f"missing file in {rel.as_posix()}: {file_rel}")
    return not problems, problems


def verify(profile: Path, skills: list[Path]) -> tuple[bool, list[str]]:
    return verify_root(profile / "skills", skills)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--profiles", type=csv_values, help="comma-separated profile names; default: all")
    parser.add_argument("--skills", type=csv_values, help="comma-separated allowlisted names or relative paths; default: all")
    parser.add_argument("--dry-run", action="store_true", help="show planned actions without writing")
    parser.add_argument("--diff", action="store_true", help="show added/changed/removed file summary")
    parser.add_argument("--verify-only", action="store_true", help="do not copy; verify current destinations")
    parser.add_argument("--no-backup", action="store_true", help="replace without .bak copy (explicitly unsafe)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profiles = select_profiles(args.profiles)
        skills = select_skills(args.skills)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 64
    if not profiles:
        print(f"ERROR: no profiles found under {PROFILES_DIR}", file=sys.stderr)
        return 1
    for rel in skills:
        if not (ROOT_SKILLS / rel / "SKILL.md").is_file():
            print(f"ERROR: missing source skill: {ROOT_SKILLS / rel}", file=sys.stderr)
            return 1

    if not args.verify_only:
        print("PLAN" if args.dry_run else "SYNC")
        timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        for profile in profiles:
            for rel in skills:
                src, dst = ROOT_SKILLS / rel, profile / "skills" / rel
                added, changed, removed, details = diff_summary(src, dst)
                same = added == changed == removed == 0
                action = "unchanged" if same else ("would-copy" if args.dry_run else copy_skill(src, dst, timestamp, not args.no_backup))
                print(f"{profile.name}	{rel.as_posix()}	{action}	+{added} ~{changed} -{removed}")
                if args.diff and not same:
                    for item in details:
                        print(f"  {item}")

    if args.dry_run:
        print("\nSOURCE VERIFY")
        ok, problems = verify_root(ROOT_SKILLS, skills)
        print(f"default-source	{'OK' if ok else 'FAIL'}")
        for problem in problems:
            print(f"  - {problem}")
        print("NOTE: dry-run does not modify or verify destination profiles.")
        return 0 if ok else 2

    print("\nVERIFY")
    all_ok = True
    for profile in profiles:
        ok, problems = verify(profile, skills)
        all_ok = all_ok and ok
        print(f"{profile.name}	{'OK' if ok else 'FAIL'}")
        for problem in problems:
            print(f"  - {problem}")
    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
