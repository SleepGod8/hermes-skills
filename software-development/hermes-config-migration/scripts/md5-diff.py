#!/usr/bin/env python3
"""Compare MD5 of skill files between a package dir and a profile skill dir.

Usage:
  python md5-diff.py <pkg_skill_dir> <local_skill_dir>

Example (compare package athena folder vs local profile skill):
  python md5-diff.py multi-agent-export/athena profiles/athena/skills/orchestration/multi-agent-protocol

Prints per file:
  OK      — same relative path, identical hash (已同步，不动)
  DIFF    — same path, different content (需人工裁定，勿覆盖)
  MISSING — in pkg only (纯新增，可导入)
  EXTRA   — local only

Exit code: 0 when no DIFF/MISSING, 1 otherwise.
Why Python, not sed: sed with Windows backslash paths fails with
"Invalid back reference" — Python handles native paths cleanly.
"""
import hashlib
import os
import sys


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(base):
    out = {}
    if not os.path.isdir(base):
        return out
    for root, _dirs, files in os.walk(base):
        for f in files:
            p = os.path.join(root, f)
            out[os.path.relpath(p, base)] = p
    return out


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    pkg, local = sys.argv[1], sys.argv[2]
    pkg_files, local_files = walk(pkg), walk(local)
    ok = diff = missing = extra = 0
    for rel in sorted(set(pkg_files) | set(local_files)):
        if rel in pkg_files and rel in local_files:
            if md5(pkg_files[rel]) == md5(local_files[rel]):
                print(f"OK      {rel}")
                ok += 1
            else:
                print(f"DIFF    {rel}")
                diff += 1
        elif rel in pkg_files:
            print(f"MISSING {rel}")
            missing += 1
        else:
            print(f"EXTRA   {rel}")
            extra += 1
    print(f"\nok={ok} diff={diff} missing={missing} extra={extra}")
    sys.exit(1 if (diff or missing) else 0)


if __name__ == "__main__":
    main()
