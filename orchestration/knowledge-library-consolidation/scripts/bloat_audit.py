#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bloat_audit.py — 知识库体量审计（四张表）

用法：
    python scripts/bloat_audit.py --root <库目录>
    python scripts/bloat_audit.py --root <库目录> --corpus <备注目录>[,<目录2>] --keywords 玩法A,玩法B
    python scripts/bloat_audit.py --self-test

输出：
    T1 清单：每文件字数 + 按目录小计占比
    T2 跨文件逐字重复行（>=18 字，出现在 >=2 文件）
    T3 同目录两两 2-gram Jaccard 相似度（降序）
    T4 使用台账：关键词在 corpus 中的提及次数
退出码：0 无超阈项｜1 有超阈项（T1 目录占比>25% / T3 相似度>18% / T4 零使用且字数>5000）
"""
import argparse
import collections
import itertools
import os
import re
import sys
import tempfile

SKIP_DIRS = {"_legacy", "_frozen", ".git", "__pycache__", "node_modules"}
LEGACY_DIRS = {"_legacy", "_frozen"}


def md_files(root, skip_legacy=True):
    out = []
    for dp, dn, fn in os.walk(root):
        parts = set(dp.split(os.sep))
        if skip_legacy and (parts & SKIP_DIRS):
            continue
        for f in fn:
            if f.endswith(".md"):
                out.append(os.path.join(dp, f))
    return sorted(out)


def chars_of(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    return len(re.sub(r"\s+", "", t)), t


def inventory(root):
    rows = []
    for p in md_files(root):
        c, t = chars_of(p)
        rows.append((os.path.relpath(p, root), c,
                     len(re.findall(r"^## ", t, re.M)),
                     len(re.findall(r"^### ", t, re.M))))
    rows.sort(key=lambda r: -r[1])
    legacy = []
    for p in md_files(root, skip_legacy=False):
        if set(p.split(os.sep)) & SKIP_DIRS:
            c, _ = chars_of(p)
            legacy.append((os.path.relpath(p, root), c))
    return rows, legacy


def subtotals(rows):
    sub = collections.Counter()
    for rel, c, _, _ in rows:
        key = rel.split(os.sep)[0]
        if rel.count(os.sep) >= 1:
            key = rel.split(os.sep)[0]
        sub[key] += c
    return sub


def dup_lines(root, min_line=18):
    seen = collections.defaultdict(set)
    for p in md_files(root):
        rel = os.path.relpath(p, root)
        for ln in open(p, encoding="utf-8", errors="ignore").read().splitlines():
            s = ln.strip()
            if len(s) < min_line:
                continue
            if s.startswith(("#", "|", ">", "`", "-", "*")):
                continue
            seen[s].add(rel)
    return sorted(((s, fs) for s, fs in seen.items() if len(fs) >= 2),
                  key=lambda x: -len(x[1]))


def _tok(t):
    t = re.sub(r"[\s>#*\-|`（）()\[\]：:，,。.、；;「」\"'~～!?！？]", "", t)
    return {t[i:i + 2] for i in range(len(t) - 1)}


def similarities(root):
    by_dir = collections.defaultdict(list)
    for p in md_files(root):
        rel = os.path.relpath(p, root)
        d = os.path.dirname(rel) or "."
        by_dir[d].append((rel, p))
    pairs = []
    for d, items in by_dir.items():
        if len(items) < 2:
            continue
        toks = {rel: _tok(open(p, encoding="utf-8", errors="ignore").read()) for rel, p in items}
        for (a, _), (b, _) in itertools.combinations(items, 2):
            A, B = toks[a], toks[b]
            j = len(A & B) / max(len(A | B), 1)
            pairs.append((j, a, b))
    return sorted(pairs, reverse=True)


def usage(corpus_dirs, keywords):
    corpus = ""
    for d in corpus_dirs:
        if os.path.isfile(d):
            corpus += open(d, encoding="utf-8", errors="ignore").read()
        else:
            for dp, dn, fn in os.walk(d):
                if set(dp.split(os.sep)) & SKIP_DIRS:
                    continue
                for f in fn:
                    if f.endswith((".md", ".txt")):
                        corpus += open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
    return sorted(((corpus.count(k), k) for k in keywords), reverse=True)


def report(root, corpus_dirs, keywords, top=10):
    rows, legacy = inventory(root)
    total = sum(r[1] for r in rows)
    flag = False
    print("=" * 64)
    print(f"T1 清单 · {len(rows)} 文件 / {total} 字" + (f" ｜ _legacy {len(legacy)} 文件 / {sum(c for _, c in legacy)} 字" if legacy else ""))
    print("=" * 64)
    print(f"{'文件':52}{'字数':>8}{'##':>4}{'###':>5}")
    for rel, c, h2, h3 in rows[:25]:
        print(f"{rel[:52]:52}{c:8}{h2:4}{h3:5}")
    if len(rows) > 25:
        print(f"... 其余 {len(rows)-25} 个文件合计 {total-sum(r[1] for r in rows[:25])} 字")

    print("\n【按顶层目录占比】")
    sub = subtotals(rows)
    for k, v in sub.most_common():
        pct = v / max(total, 1) * 100
        mark = "  ⚠️ >25%" if pct > 25 else ""
        if pct > 25:
            flag = True
        print(f"  {k:30}{v:8} 字  {pct:5.1f}%{mark}")

    dups = dup_lines(root)
    print(f"\nT2 跨文件逐字重复行：{len(dups)} 条")
    for s, fs in dups[:top]:
        print(f"  ×{len(fs)} {s[:44]}…  ← {', '.join(sorted(fs))[:80]}")

    sims = similarities(root)
    print(f"\nT3 同目录相似度（Top {top}）")
    for j, a, b in sims[:top]:
        mark = "  ⚠️ >18%" if j > 0.18 else ""
        if j > 0.18:
            flag = True
        print(f"  {j*100:5.1f}%  {os.path.basename(a)} ↔ {os.path.basename(b)}{mark}")

    if keywords:
        print("\nT4 使用台账")
        sized = {os.path.basename(r[0]): r[1] for r in rows}
        for n, k in usage(corpus_dirs, keywords):
            print(f"  {k:14}{n:5} 次")
            if n == 0:
                flag = True

    print("\n" + ("结论：存在超阈项，建议进入草案阶段 ⚠️" if flag else "结论：未发现超阈项 ✅"))
    return 1 if flag else 0


SELF_A = """# 甲册

冻结会让高潮变成一张空白的许可条，解除的瞬间全部爆发，这一点所有控制系都一样。
通用规则：解除优先级 安全词 > 摸额头 > 口令。
"""
SELF_B = """# 乙册

冻结会让高潮变成一张空白的许可条，解除的瞬间全部爆发，这一点所有控制系都一样。
遮蔽会让快感存起来，解除时一次回流，所以两册的分级表几乎一样。
"""
SELF_C = """# 丙册

这是完全无关的一册，只讲别的东西，与上面两册没有共同的句子。
"""


def self_test():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "grp"))
        os.makedirs(os.path.join(d, "other"))
        open(os.path.join(d, "grp", "a.md"), "w", encoding="utf-8").write(SELF_A)
        open(os.path.join(d, "grp", "b.md"), "w", encoding="utf-8").write(SELF_B)
        open(os.path.join(d, "other", "c.md"), "w", encoding="utf-8").write(SELF_C)
        rows, legacy = inventory(d)
        assert len(rows) == 3, rows
        dups = dup_lines(d)
        assert dups, "应检出跨文件重复行"
        sims = similarities(d)
        assert sims and sims[0][0] > 0.18, sims
        u = usage([d], ["冻结", "遮蔽", "不存在的词"])
        d_ = dict((k, n) for n, k in u)
        assert d_["冻结"] >= 2 and d_["不存在的词"] == 0, d_
        print("inventory:", len(rows), "| dup lines:", len(dups), "| top sim:",
              round(sims[0][0], 3), "| usage:", d_)
        print("✅ self-test ran")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--corpus", default="")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if not a.root:
        ap.print_help()
        sys.exit(0)
    cd = [x for x in a.corpus.split(",") if x.strip()]
    kw = [x for x in a.keywords.split(",") if x.strip()]
    sys.exit(report(a.root, cd, kw, a.top))
