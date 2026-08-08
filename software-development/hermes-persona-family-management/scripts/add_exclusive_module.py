#!/usr/bin/env python
"""Add or replace an exclusive (专属) module in a maid profile's SOUL.md + config.yaml.

Usage:
    python add_exclusive_module.py <profile> <module.md> [backup_tag]

  <profile>    name under ~/AppData/Local/hermes/profiles/ (e.g. dionysus)
  <module.md>  plain-text file with the new module. First line MUST be the
               module heading (e.g. "## 酒印开关（Dionysus 专属）🆕").
               Line endings may be LF or CRLF; the script normalizes.
  [backup_tag] suffix for backups, default 'excl' (-> SOUL.md.bak-<tag>,
               config.yaml.bak-<tag>)

Behavior (validated 2026-08 on dionysus/ares/hypnos):
  - Backs up both files before writing.
  - If the module heading already exists in the text, the ENTIRE old module
    span (heading .. next "## " anchor) is REPLACED (in-place upgrade).
    Otherwise it is INSERTED before the standard anchor "## 共通色情机制 🆕".
  - SOUL.md is written CRLF double-spaced ('\\r\\n\\r\\n' between lines);
    config.yaml agent.system_prompt is written LF ('\\n'), via yaml lib with
    allow_unicode=True, default_flow_style=False, sort_keys=False.
  - Prints ✅/❌ verification for both files.

Requires: PyYAML (available in Hermes env).
"""
import os
import shutil
import sys

try:
    import yaml
except ImportError:
    print("PyYAML not available: pip install pyyaml")
    sys.exit(2)

BASE = os.path.join(os.path.expanduser("~"), "AppData", "Local", "hermes", "profiles")
ANCHOR = "## 共通色情机制 🆕"


def normalize_lines(md_path):
    """Read module file -> list of content lines (LF-normalized, trailing empties stripped)."""
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    lines = [l.rstrip("\n").rstrip("\r") for l in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    assert lines, "module file is empty"
    return lines


def build_variants(lines):
    heading = lines[0]
    mod_crlf = "\r\n\r\n".join(lines) + "\r\n\r\n"  # double-spaced CRLF (matches family SOUL.md)
    mod_lf = "\n".join(lines) + "\n\n"              # normal LF (config.yaml side)
    return heading, mod_crlf, mod_lf


def insert_or_replace(text, heading, mod, label):
    """Insert module before anchor, or replace existing module span (heading..anchor)."""
    if heading in text:
        i = text.index(heading)
        j = text.index(ANCHOR, i)
        return text[:i] + mod + text[j:], "replaced"
    assert text.count(ANCHOR) == 1, f"{label}: anchor count={text.count(ANCHOR)} (expect 1)"
    return text.replace(ANCHOR, mod + ANCHOR, 1), "inserted"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    name, md_path = sys.argv[1], sys.argv[2]
    tag = sys.argv[3] if len(sys.argv) > 3 else "excl"

    soul_p = os.path.join(BASE, name, "SOUL.md")
    cfg_p = os.path.join(BASE, name, "config.yaml")
    for p in (soul_p, cfg_p):
        if not os.path.exists(p):
            print(f"missing: {p}")
            sys.exit(1)
        shutil.copy2(p, p + f".bak-{tag}")

    heading, mod_crlf, mod_lf = build_variants(normalize_lines(md_path))

    with open(soul_p, encoding="utf-8", newline="") as f:
        soul = f.read()
    with open(cfg_p, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if "agent" not in cfg or "system_prompt" not in cfg["agent"]:
        print("ERROR: config has no agent.system_prompt (check profile shape)")
        sys.exit(1)
    sp = cfg["agent"]["system_prompt"]

    soul, act_s = insert_or_replace(soul, heading, mod_crlf, "SOUL")
    sp, act_c = insert_or_replace(sp, heading, mod_lf, "cfg")

    with open(soul_p, "w", encoding="utf-8", newline="") as f:
        f.write(soul)
    cfg["agent"]["system_prompt"] = sp
    with open(cfg_p, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # verify
    with open(soul_p, encoding="utf-8", newline="") as f:
        s2 = f.read()
    with open(cfg_p, encoding="utf-8") as f:
        sp2 = yaml.safe_load(f)["agent"]["system_prompt"]
    print(f"action: SOUL={act_s} cfg={act_c}")
    for label, txt in (("SOUL", s2), ("cfg", sp2)):
        ok = heading in txt
        print(("✅" if ok else "❌"), label, heading)
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
