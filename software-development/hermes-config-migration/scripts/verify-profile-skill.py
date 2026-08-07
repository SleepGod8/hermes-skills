#!/usr/bin/env python
"""Verify multi-profile skill structure normalization.

Scans the same-named skill across all Hermes profiles and reports:
  - per-profile file inventory (SKILL.md + references/)
  - shared references MD5 consistency across profiles
  - leftover old-name references (case variants, old role-file prefixes, source-machine paths)

Usage:
    python verify-profile-skill.py <skill_name> [--profiles artemis,athena,eos,hebe,iris,nemesis] [--root C:\\Users\\<user>\\AppData\\Local\\hermes]

Exit code 0 = all profiles present, shared files MD5-consistent, no stale references.
"""
import argparse
import hashlib
import os
import re
import sys

DEFAULT_PROFILES = ["artemis", "athena", "eos", "hebe", "iris", "nemesis"]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_skill_dir(profile_skills_root, skill_name):
    """Find skills/<category>/<skill_name> under a profile's skills dir."""
    target = os.path.join(profile_skills_root, skill_name)
    if os.path.isdir(target):
        return target
    for entry in os.listdir(profile_skills_root):
        cand = os.path.join(profile_skills_root, entry, skill_name)
        if os.path.isdir(cand):
            return cand
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_name")
    ap.add_argument("--profiles", default=",".join(DEFAULT_PROFILES))
    ap.add_argument("--root", default=os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes"))
    args = ap.parse_args()

    profiles = [p for p in args.profiles.split(",") if p]
    base = os.path.join(args.root, "profiles")
    ok = True

    # stale-name patterns that normalization should have removed
    stale_patterns = [
        re.compile(r"MULTI-AGENT-PROTOCOL\.md", re.IGNORECASE),  # case variant of protocol file
        re.compile(r"SOUL-0\d-", re.IGNORECASE),                  # old SOUL-0N- prefix
        re.compile(r"agent1-project-lead"),                       # old athena role file name
        re.compile(r"agent-5-feature-developer/SKILL"),           # standalone role skill
        re.compile(r"multi-agent-collab-protocol"),               # old hebe dir name
        re.compile(r"autonomous-ai-agents[\\\\/]multi-agent-protocol"),  # old iris path
    ]

    inventories = {}
    for prof in profiles:
        skills_root = os.path.join(base, prof, "skills")
        skill_dir = find_skill_dir(skills_root, args.skill_name)
        if not skill_dir:
            print(f"[{prof}] MISSING skill dir: {skills_root}")
            ok = False
            continue
        files = {}
        for root, _dirs, fnames in os.walk(skill_dir):
            for fn in fnames:
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, skill_dir)
                files[rel] = fp
        inventories[prof] = (skill_dir, files)
        print(f"[{prof}] {os.path.relpath(skill_dir, base)} ({len(files)} files)")
        for rel in sorted(files):
            print(f"    {rel}")

    # shared references MD5 consistency
    if inventories:
        all_refs = set()
        for _d, files in inventories.values():
            all_refs.update(r for r in files if r.startswith("references" + os.sep))
        print("\n--- shared references MD5 consistency ---")
        for ref in sorted(all_refs):
            hashes = {}
            for prof, (_d, files) in inventories.items():
                if ref in files:
                    hashes.setdefault(md5(files[ref]), []).append(prof)
            if len(hashes) == 1:
                print(f"OK   {ref}  {list(hashes)[0][:8]}")
            else:
                print(f"DIFF {ref}  {hashes}")
                ok = False

    # stale reference scan
    print("\n--- stale reference scan ---")
    stale_found = False
    for prof, (_d, files) in inventories.items():
        for rel, fp in files.items():
            try:
                content = open(fp, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for pat in stale_patterns:
                if pat.search(content):
                    print(f"STALE {prof}/{rel}: matches {pat.pattern}")
                    stale_found = True
    if not stale_found:
        print("none")

    print("\nRESULT:", "PASS" if ok and not stale_found else "FAIL")
    sys.exit(0 if ok and not stale_found else 1)


if __name__ == "__main__":
    main()
