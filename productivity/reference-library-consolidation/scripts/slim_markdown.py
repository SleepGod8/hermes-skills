#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""slim_markdown.py — 机械化精简（危险操作，默认拒跑）

只用在一个**已被归档**的文件上（原件必须已存在 `_legacy/` 等同名副本）。
护栏逻辑来自一次真实事故：未归档就精简 → 无法回滚，只能从备份恢复。

用法：
    python scripts/slim_markdown.py <文件> --i-have-archive _legacy/xxx.md
    python scripts/slim_markdown.py <文件> --i-have-archive _legacy/xxx.md --dry-run
    python scripts/slim_markdown.py <文件> --i-have-archive _legacy/xxx.md --max-list 6 --max-para 3

行为：
  · 保留所有标题行、表格行（| 开头）、引用行（> 开头）
  · 每个标题下最多保留 --max-list 条 bullet、--max-para 段正文
  · 追加一行「📦 精简版 / 原文见 …」的回滚指路
  · 同目录生成 `<文件名>.bak`（本次操作前的快照）
退出码：0 成功｜2 护栏拒绝｜3 压缩过度（正文 <原 15%，需人工复核）
"""
import argparse
import os
import re
import shutil
import sys


def chars(t):
    return len(re.sub(r"\s+", "", t))


def slim(t, max_list=3, max_para=2, archive_hint=""):
    out, lst, para = [], 0, 0
    for ln in t.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            out.append(ln)
            lst = para = 0
            continue
        if s.startswith("|") or s.startswith(">"):
            out.append(ln)
            continue
        if not s:
            if out and out[-1] != "":
                out.append("")
            continue
        if s.startswith(("- ", "* ", "• ")):
            if lst < max_list:
                out.append(ln)
                lst += 1
            continue
        if para < max_para:
            out.append(ln)
            para += 1
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
    note = "\n\n> 📦 本节为精简版（规则/表格保留，长叙述已删）；完整原文见 `%s`。" % (
        archive_hint or "_legacy/<原路径>")
    return body + note + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--i-have-archive", required=False, default="",
                    help="已归档的原件路径（护栏：必须存在）")
    ap.add_argument("--max-list", type=int, default=3)
    ap.add_argument("--max-para", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not a.i_have_archive or not os.path.exists(a.i_have_archive):
        print("❌ 护栏拒绝：先归档原件，再用 --i-have-archive <归档路径> 指明。\n"
              "   原因：无归档的精简不可回滚（真实事故：精简后才发现源文件未归档）。", file=sys.stderr)
        return 2

    src = a.file
    t = open(src, encoding="utf-8").read()
    before = chars(t)
    new = slim(t, a.max_list, a.max_para, a.i_have_archive)
    after = chars(new)
    print(f"原 {before} 字 → 精简 {after} 字（{after / max(before, 1) * 100:.0f}%）")
    if after < before * 0.15:
        print("⚠️ 压缩过度：低于原 15%，多半是短 bullet 密度过高被一口气吃掉。\n"
              "   请人工复核后再落盘（本次%s）。" % ("未写入" if a.dry_run else "已写入"))
        code = 3
    else:
        code = 0
    if a.dry_run:
        print("[dry-run] 未写入")
        return code
    shutil.copy2(src, src + ".bak")
    open(src, "w", encoding="utf-8").write(new)
    print("已写入；备份：", src + ".bak")
    return code


if __name__ == "__main__":
    sys.exit(main())
