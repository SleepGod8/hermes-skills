#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""面板备注归档维护（P0/P1 新增 · 防止面板无限膨胀）。

规则：`references/面板存档/maids/<名字>.md` 只保留**最新 --keep 条**备注；
更早的移到 `references/面板存档/archive/<年-月>.md`（**全文无损**，不压缩不改写）。

用法：
    python panel_maintain.py --check        # 只检查（默认），报告谁会溢出
    python panel_maintain.py --apply        # 执行归档（幂等，重复跑不会重复搬运）
    python panel_maintain.py --apply --keep 8
"""
import argparse
import os
import re
import sys
from collections import Counter

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(SKILL, 'references', '面板存档')
MAIDS_DIR = os.path.join(P, 'maids')
ARCH_DIR = os.path.join(P, 'archive')
MAIDS = ['hermes', 'iris', 'athena', 'aphrodite', 'dionysus',
         'hebe', 'artemis', 'ares', 'nemesis', 'hypnos']
DISPLAY = {'hermes': 'Hermes', 'iris': 'Iris', 'athena': 'Athena', 'aphrodite': 'Aphrodite',
           'dionysus': 'Dionysus', 'hebe': 'Hebe', 'artemis': 'Artemis', 'ares': 'Ares',
           'nemesis': 'Nemesis', 'hypnos': 'Hypnos'}


def date_key(line):
    m = re.search(r'(\d{1,2})/(\d{1,2})(?:-(\d+))?', line)
    if not m:
        return (0, 0, 0)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0))


def month_of(line):
    m = re.search(r'(\d{1,2})/(\d{1,2})', line)
    return f'2026-{int(m.group(1)):02d}' if m else 'undated'


def split(path):
    """返回 (head_lines, remark_lines, tail_lines)"""
    lines = open(path, encoding='utf-8').read().split('\n')
    try:
        i = next(k for k, l in enumerate(lines) if l.startswith('## 最近备注'))
    except StopIteration:
        return lines, [], []
    try:
        j = next(k for k, l in enumerate(lines) if l.startswith('## 历史归档'))
    except StopIteration:
        j = len(lines)
    return lines[:i + 1], [l for l in lines[i + 1:j] if l.startswith('- 备注')], lines[j:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--keep', type=int, default=6)
    args = ap.parse_args()
    if not os.path.isdir(MAIDS_DIR):
        print(f'❌ 未找到 {MAIDS_DIR}')
        return 1
    os.makedirs(ARCH_DIR, exist_ok=True)

    overflow_total = moved_total = 0
    for slug in MAIDS:
        p = os.path.join(MAIDS_DIR, slug + '.md')
        if not os.path.isfile(p):
            print(f'⚠️  {slug}: 面板缺失（跳过）')
            continue
        head, remarks, tail = split(p)
        remarks = sorted(remarks, key=date_key, reverse=True)
        keep, old = remarks[:args.keep], remarks[args.keep:]
        if not old:
            print(f'✅ {slug}: {len(remarks)} 条 ≤ {args.keep}，无需归档')
            continue
        overflow_total += 1
        by_month = {}
        for r in old:
            by_month.setdefault(month_of(r), []).append(r)
        print(f'📦 {slug}: 溢出 {len(old)} 条 → ' +
              ', '.join(f'{m}({len(v)})' for m, v in sorted(by_month.items())))
        if not args.apply:
            continue
        name = DISPLAY[slug]
        for month, items in sorted(by_month.items()):
            ap_ = os.path.join(ARCH_DIR, month + '.md')
            existing = open(ap_, encoding='utf-8').read() if os.path.isfile(ap_) else \
                f'# 面板备注归档 · {month}\n\n> 从 `maids/*.md` 溢出的历史备注**全文**（无损搬运，未压缩、未改写）。\n\n'
            have = set(re.sub(r'^\*\*\[[^\]]+\]\*\*\s*', '', l)
                       for l in existing.split('\n') if l.startswith('**['))
            add = [f'**[{name}]** {r[2:]}' for r in items
                   if re.sub(r'^-\s*', '', r) not in have]
            if add:
                existing = existing.rstrip('\n') + '\n' + '\n'.join(add) + '\n'
                open(ap_, 'w', encoding='utf-8').write(existing)
                moved_total += len(add)
        # 重写 maids 文件：保留 head + keep + tail(历史归档链接)
        months = sorted({month_of(r) for r in old})
        lnk = [f'- `../archive/{m}.md`' for m in months]
        new_tail = ['## 历史归档', '', '更早备注全文（未压缩）见：'] + lnk + ['']
        open(p, 'w', encoding='utf-8').write(
            '\n'.join(head) + '\n' + '\n'.join(keep) + '\n\n' + '\n'.join(new_tail))

    if not args.apply:
        print(f'\n[check] {overflow_total} 个面板需要归档（加 --apply 执行；当前保留 {args.keep} 条）')
    else:
        print(f'\n[apply] 归档完成：{overflow_total} 个面板，搬运 {moved_total} 条（幂等：重复跑为 0）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
