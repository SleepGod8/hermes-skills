#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""library_audit.py — 参考库体检（先取证，别凭感觉）

用法：
    python scripts/library_audit.py "<库根目录>"
    python scripts/library_audit.py . --skip _legacy,_frozen,node_modules

输出四块：
  1. 目录字数占比（找结构倒挂）
  2. 最胖文件（字数 / 小节数）
  3. 跨文件逐字重复行（模板行 vs 真冗余，人工判读）
  4. 内部引用断链（`xxx.md` 形式的相对/根路径引用）
退出码：0 正常｜1 有断链
"""
import argparse
import collections
import os
import re
import sys


def chars(t):
    return len(re.sub(r"\s+", "", t))


def walk(root, skip):
    for dp, dn, fn in os.walk(root):
        if any(s and s in dp for s in skip):
            continue
        dn[:] = [d for d in dn if not any(s and s == d for s in skip)]
        for f in fn:
            if f.endswith((".md", ".txt")):
                yield os.path.join(dp, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--skip", default="_legacy,_frozen,archive,node_modules,.git")
    ap.add_argument("--min-dup-len", type=int, default=18)
    ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()

    skip = [s for s in a.skip.split(",") if s]
    root = os.path.abspath(a.root)
    dirs = collections.Counter()
    files = []
    for p in walk(root, skip):
        t = open(p, encoding="utf-8", errors="ignore").read()
        rel = os.path.relpath(p, root)
        top = rel.split(os.sep)[0] if os.sep in rel else "(root)"
        dirs[top] += chars(t)
        files.append((rel, chars(t), len(re.findall(r"(?m)^#{2,3} ", t))))

    total = sum(dirs.values()) or 1
    print("== 1. 目录字数占比 ==")
    for d, c in dirs.most_common():
        print(f"  {d:26}{c:9}  {c / total * 100:5.1f}%")
    print(f"  {'合计':26}{total:9}  {len(files)} 文件")

    print("\n== 2. 最胖文件（字数 / 小节数）==")
    for rel, c, h in sorted(files, key=lambda x: -x[1])[: a.top]:
        print(f"  {c:9} {h:4} 节   {rel}")

    seen = collections.defaultdict(set)
    for rel, _, _ in files:
        t = open(os.path.join(root, rel), encoding="utf-8", errors="ignore").read()
        for ln in t.splitlines():
            s = ln.strip()
            if len(s) >= a.min_dup_len and not s.startswith(("|", ">", "#", "```")):
                seen[s].add(rel)
    dups = [(s, v) for s, v in seen.items() if len(v) >= 2]
    print(f"\n== 3. 跨文件重复行：{len(dups)} 条（模板行可留，重复段落要合并）==")
    for s, v in sorted(dups, key=lambda x: -len(x[1]))[: a.top]:
        print(f"  ×{len(v)} {s[:42]}…  ← {', '.join(sorted(v))[:60]}")

    broken = set()
    for rel, _, _ in files:
        p = os.path.join(root, rel)
        t = open(p, encoding="utf-8", errors="ignore").read()
        for m in re.findall(r"`([\w./\-`]+?\.md)`", t):
            if "<" in m or " " in m:
                continue  # 占位符跳过
            cands = [os.path.join(root, m), os.path.join(os.path.dirname(p), m)]
            if not any(os.path.exists(x) for x in cands):
                broken.add(m)
    print(f"\n== 4. 内部引用断链：{len(broken)} ==")
    for b in sorted(broken)[: a.top]:
        print("  ✗", b)

    print("\n结论口径：占比 >25% 的非核心目录＝膨胀点；0 使用的章节＝冷藏候选；"
          "同组相似度需另算（2-gram Jaccard）。")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
