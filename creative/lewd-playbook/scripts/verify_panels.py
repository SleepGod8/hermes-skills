#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""面板一致性校验（P1 新增）。

跑法：python scripts/verify_panels.py            # 全量校验，PASS/FAIL + WARN
      python scripts/verify_panels.py --verbose

校验项（FAIL = 必须修；WARN = 需主人确认的规则例外）：
  C1 结构：panel-records.md 含「单一写入者声明 / 快速一览表 / 维护约定 / 面板路由」
  C2 面板齐全：10 位女仆各有 maids/<slug>.md；Eos 绝不建档
  C3 一览表：11 行（10 女仆 + Eos），Eos 各字段为「—」
  C4 数据一致：一览表的 等级 / EXP 与 maids/<slug>.md 一致
  C5 印记规则：所有已开发区域 100% ⇒ 印记必须「完全觉醒」；反之不得写「完全觉醒」
  C6 部位统计：格式 `部位: 高潮/射精`
  C7 备注膨胀：maids/*.md 备注条数 ≤ 6（保留上限）
  C8 归档无损：maids 备注数 + archive 备注数 ≥ 基线（不漏条）
  C9 索引完整：references/ 下每个 .md 都在 SKILL.md 索引表登记
  C10 脚本可编译：scripts/*.py 通过 py_compile
"""
import argparse
import json
import os
import py_compile
import re
import sys
from collections import Counter

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(SKILL, 'references', '面板存档')
MAIDS_DIR, ARCH_DIR = os.path.join(P, 'maids'), os.path.join(P, 'archive')
BASELINE = os.path.join(P, '.panel-baseline.json')
KEEP_MAX = 6
MAIDS = ['hermes', 'iris', 'athena', 'aphrodite', 'dionysus',
         'hebe', 'artemis', 'ares', 'nemesis', 'hypnos']
DISPLAY = {'hermes': 'Hermes', 'iris': 'Iris', 'athena': 'Athena', 'aphrodite': 'Aphrodite',
           'dionysus': 'Dionysus', 'hebe': 'Hebe', 'artemis': 'Artemis', 'ares': 'Ares',
           'nemesis': 'Nemesis', 'hypnos': 'Hypnos'}
FIELDS = {'等级': r'- 等级[:：]', '开发度': r'- 开发度[:：]', '装备': r'- 装备库[:：]',
          '印记': r'- 印记[:：]', '部位统计': r'- 📊 部位统计'}

fails, warns, oks = [], [], []


def fail(c, m):
    fails.append(f'[{c}] {m}')


def warn(c, m):
    warns.append(f'[{c}] {m}')


def ok(c, m):
    oks.append(f'[{c}] {m}')


def parse_table(text):
    rows = {}
    for line in text.split('\n'):
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 4 or cells[0] in ('女仆', '------') or set(cells[0]) <= set('-: '):
            continue
        rows[cells[0]] = cells
    return rows


def exp_of(cell):
    m = re.search(r'(\d+)\s*/\s*(\d+)', cell)
    return (int(m.group(1)), int(m.group(2))) if m else None


def parse_exceptions(check=None):
    """从 rule-exceptions.md 解析已登记待裁决的女仆名。
    check: 只返回该检查项（如 'C5'）适用的例外；None = 全部。"""
    p = os.path.join(P, 'rule-exceptions.md')
    reg = set()
    if not os.path.isfile(p):
        return reg
    for line in open(p, encoding='utf-8'):
        m = re.match(r'^\|\s*\*\*(EX-\d+)\*\*\s*\|\s*([^|]+?)\s*\|', line)
        if not m:
            continue
        affects = line.rstrip().rstrip('|').split('|')[-1].strip()
        if check and check not in affects:
            continue
        for name in re.split(r'[、,，/]', m.group(2).strip()):
            if name.strip():
                reg.add(name.strip())
    return reg


def strip_notes(s):
    """去掉〔...〕与（备注...）等旁注，只留主值。"""
    s = re.sub(r'〔[^〕]*〕', '', s)
    s = re.sub(r'（\s*备注[^）]*）', '', s)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    exceptions = parse_exceptions('C5')   # 仅 C5 类例外豁免印记检查

    main_file = os.path.join(P, 'panel-records.md')
    if not os.path.isfile(main_file):
        print('❌ 缺少 panel-records.md'); return 1
    ptxt = open(main_file, encoding='utf-8').read()

    # C1
    need = ['单一写入者声明', '快速一览表', '维护约定', '面板路由']
    miss = [n for n in need if n not in ptxt]
    (fail if miss else ok)('C1', f'总览章节缺失: {miss}' if miss else '总览结构完整（写入者声明/一览表/路由/维护约定）')

    # C2
    mfiles = {}
    for slug in MAIDS:
        p = os.path.join(MAIDS_DIR, slug + '.md')
        if os.path.isfile(p):
            mfiles[slug] = open(p, encoding='utf-8').read()
        else:
            fail('C2', f'{DISPLAY[slug]} 缺少面板文件 maids/{slug}.md')
    if mfiles:
        ok('C2', f'{len(mfiles)}/10 位女仆面板存在')
    for f in os.listdir(MAIDS_DIR) if os.path.isdir(MAIDS_DIR) else []:
        if 'eos' in f.lower():
            fail('C2', f'Eos 不得建档：maids/{f}')

    # C3
    rows = parse_table(ptxt)
    if 'Eos' not in rows:
        fail('C3', '一览表缺少 Eos 行')
    else:
        eos = rows['Eos']
        body = eos[1:]
        has_num = any(re.search(r'\d', c) for c in body)
        labeled = [c for c in body if c.strip() not in ('—', '-', '–', '')]
        bad = [c for c in labeled if not re.search(r'不参与|纯爱', c)]
        if has_num or bad:
            fail('C3', f'Eos 行不得含数值/等级：{body}')
        else:
            ok('C3', 'Eos 行不参与等级制 ✓')
    for slug in MAIDS:
        if DISPLAY[slug] not in rows:
            fail('C3', f'一览表缺少 {DISPLAY[slug]} 行')
    if len(rows) >= 11:
        ok('C3', f'一览表 {len(rows)} 行')

    # C4/C5/C6/C7
    for slug, body in mfiles.items():
        name = DISPLAY[slug]
        row = rows.get(name)
        txt = body
        for fname, pat in FIELDS.items():
            if not re.search(pat, txt):
                fail('C4', f'{name} 面板缺字段：{fname}')
        m_lv = re.search(r'- 等级[:：]\s*\*{0,2}(Lv\.\d+)', txt)
        m_exp = re.search(r'EXP\s*\*{0,2}(\d+)\s*/\s*(\d+)', txt)
        if row and m_lv and m_exp:
            r_lv = re.search(r'Lv\.\d+', row[1])
            r_exp = exp_of(row[3]) if len(row) > 3 else None
            if r_lv and r_lv.group(0) != m_lv.group(1):
                fail('C4', f'{name} 等级不一致：一览表 {r_lv.group(0)} vs 面板 {m_lv.group(1)}')
            if r_exp and r_exp != (int(m_exp.group(1)), int(m_exp.group(2))):
                fail('C4', f'{name} EXP 不一致：一览表 {r_exp} vs 面板 {(int(m_exp.group(1)), int(m_exp.group(2)))}')
        # C5 印记
        dev = re.search(r'- 开发度[:：](.+)', txt)
        mark = re.search(r'- 印记[:：](.+)', txt)
        if dev and mark:
            dev_v, mark_v = strip_notes(dev.group(1)), strip_notes(mark.group(1))
            pcts = [int(x) for x in re.findall(r'(\d+)%', dev_v)]
            all100 = bool(pcts) and all(p == 100 for p in pcts)
            awakened = '完全觉醒' in mark_v
            if name in exceptions:
                warn('C5', f'{name} 印记/开发度存在已登记例外（见 rule-exceptions.md）→ 待主人裁决，不计 FAIL')
            elif all100 and not awakened:
                warn('C5', f'{name} 全区域 100% 但印记非「完全觉醒」（{mark_v[:40]}…）→ 需主人确认是否视为完全体')
            elif awakened and not all100:
                fail('C5', f'{name} 印记写「完全觉醒」但开发度未满 100%（{dev_v[:40]}…）→ 需登记例外或修正')
        # C6
        st = re.search(r'- 📊 部位统计[^：:]*[:：](.+)', txt)
        if st:
            segs = [s.strip() for s in st.group(1).split('｜') if s.strip()]
            bad = [s for s in segs if not re.match(r'^[\u4e00-\u9fa5]+[:：]\s*\d+\s*/\s*\d+', s)]
            if bad:
                warn('C6', f'{name} 部位统计格式异常：{bad[:2]}')
        # C7
        n_rem = len([l for l in txt.split('\n') if l.startswith('- 备注')])
        if n_rem > KEEP_MAX:
            fail('C7', f'{name} 备注 {n_rem} 条 > 上限 {KEEP_MAX}（跑 panel_maintain.py --apply）')

    # C8 归档无损
    if os.path.isfile(BASELINE):
        base = json.load(open(BASELINE, encoding='utf-8'))
        arch_all = Counter()
        for f in (os.listdir(ARCH_DIR) if os.path.isdir(ARCH_DIR) else []):
            for l in open(os.path.join(ARCH_DIR, f), encoding='utf-8'):
                m = re.match(r'^\*\*\[(.+?)\]\*\*', l)
                if m:
                    arch_all[m.group(1)] += 1
        for slug, body in mfiles.items():
            name = DISPLAY[slug]
            total = len([l for l in body.split('\n') if l.startswith('- 备注')]) + arch_all[name]
            want = base.get(name, 0)
            if total < want:
                fail('C8', f'{name} 备注总量 {total} < 基线 {want}（可能丢条！）')
        if not any(f.startswith('[C8]') for f in fails):
            ok('C8', f'归档无损（基线 {sum(base.values())} 条备注全部可追溯）')
    else:
        warn('C8', f'无基线文件 {BASELINE}，跳过归档无损校验')

    # C9 索引完整
    skill_txt = open(os.path.join(SKILL, 'SKILL.md'), encoding='utf-8').read()
    indexed = {x.rstrip('.,;') for x in re.findall(r'references/[^\s`\)\|]+\.md', skill_txt)}
    real = set()
    for r, d, fs in os.walk(os.path.join(SKILL, 'references')):
        for f in fs:
            if f.endswith('.md'):
                real.add(os.path.relpath(os.path.join(r, f), SKILL).replace('\\', '/'))
    unindexed = sorted(x for x in real - indexed if not x.startswith('references/面板存档/'))
    if unindexed:
        fail('C9', f'{len(unindexed)} 个 reference 未在 SKILL.md 登记：{unindexed}')
    else:
        ok('C9', f'{len(real)} 个 reference 全部已登记')

    # C10 脚本编译
    bad_scripts = []
    for f in os.listdir(os.path.join(SKILL, 'scripts')):
        if f.endswith('.py'):
            sp = os.path.join(SKILL, 'scripts', f)
            try:
                compile(open(sp, encoding='utf-8').read(), sp, 'exec')
            except SyntaxError as e:
                bad_scripts.append(f'{f}: {e}')
    if bad_scripts:
        fail('C10', f'脚本编译失败：{bad_scripts}')
    else:
        ok('C10', 'scripts/*.py 全部可编译')

    print('=' * 62)
    print(f'面板校验 · FAIL={len(fails)} WARN={len(warns)} PASS={len(oks)}')
    print('=' * 62)
    for x in fails:
        print('❌', x)
    for x in warns:
        print('⚠️ ', x)
    if args.verbose:
        for x in oks:
            print('✅', x)
    print('=' * 62)
    print('结论：', 'PASS' if not fails else 'FAIL')
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
