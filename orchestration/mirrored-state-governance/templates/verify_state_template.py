#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""状态档案校验骨架（编号检查项 + 例外登记 + 提取口径）。

用法：python scripts/verify_state.py [--verbose]
约定：FAIL 决定返回码；WARN 必须能被解释（通常是已登记的规则例外）。

设计要点（踩过的坑都在注释里）：
  * 判定值取「行首主值」或「剔除溯源括号」，否则自己写的说明会把判定带偏（坑 #7）
  * 解析表格时**限定 section**，否则后置的路由表会覆盖一览表 → 比对静默空转（坑 #6）
  * 例外登记表存在时对应检查项降级 WARN，不 FAIL（数据真伪交主人裁决）
  * 脚本编译检查用 compile(source,...)，Windows 上不要用 os.devnull（坑 #10）
"""
import argparse, json, os, re, sys
from collections import Counter

# ============================== CONFIG ==============================
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(SKILL, 'references', 'state')      # 状态目录
OVERVIEW = 'panel-records.md'                            # 总览文件名
ENTITY_DIR = 'entities'                                  # 实体目录名
ARCHIVE_DIR = 'archive'
BASELINE = os.path.join(STATE, '.baseline.json')
EXCEPTIONS = os.path.join(STATE, 'rule-exceptions.md')
ENTITIES = ['alpha', 'beta']                             # 实体 slug
DISPLAY = {'alpha': 'Alpha', 'beta': 'Beta'}             # slug → 显示名
EXCLUDED = ['gamma']                                     # 不建档的实体（如年龄红线）
KEEP_MAX = 6                                             # 备注条数上限
OVERVIEW_SECTIONS = ['单一写入者声明', '快速一览表', '维护约定', '路由']
ENTITY_FIELDS = {'状态': r'- 状态[:：]', '数值': r'- 数值[:：]', '备注统计': r'- 📊 备注统计'}
# ====================================================================

fails, warns, oks = [], [], []
def fail(c, m): fails.append(f'[{c}] {m}')
def warn(c, m): warns.append(f'[{c}] {m}')
def ok(c, m): oks.append(f'[{c}] {m}')

TRACE_KW = ('备注', '裁决', '素材', '来源', '来自', '说明', '原素', '溯源', '依据')

def strip_notes(s):
    s = re.sub(r'〔[^〕]*〕', '', s)
    return re.sub(r'（\s*备注[^）]*）', '', s)

def drop_trace(s):
    """去掉含溯源关键词的括号段（保留普通说明性括号）。"""
    def repl(m):
        return '' if any(k in m.group(1) for k in TRACE_KW) else m.group(0)
    s = re.sub(r'〔[^〕]*〕', '', s)
    s = re.sub(r'（([^）]*)）', repl, s)
    return re.sub(r'\(([^)]*)\)', repl, s)

def main_value(s):
    return re.split(r'[（(]', strip_notes(s))[0]

def parse_section_table(text, section_re):
    """只在目标 section 内解析表格（坑 #6）。"""
    m = re.search(section_re + r'[^\n]*\n(.*?)(?=\n##\s|\Z)', text, re.S)
    seg = m.group(1) if m else ''
    rows = {}
    for line in seg.split('\n'):
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 3 or cells[0] in ('实体', '------') or set(cells[0]) <= set('-: '):
            continue
        rows[cells[0]] = cells
    return rows

def parse_exceptions(check=None):
    """从 rule-exceptions.md 读「待裁决/已登记例外」，按检查项过滤（最后一列含检查号）。"""
    reg = set()
    if not os.path.isfile(EXCEPTIONS):
        return reg
    for line in open(EXCEPTIONS, encoding='utf-8'):
        m = re.match(r'^\|\s*\*\*(EX-\d+)\*\*\s*\|\s*([^|]+?)\s*\|', line)
        if not m:
            continue
        affects = line.rstrip().rstrip('|').split('|')[-1].strip()
        if check and check not in affects:
            continue
        reg.add(m.group(2).strip())
    return reg

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    exc = parse_exceptions('C5')

    op = os.path.join(STATE, OVERVIEW)
    if not os.path.isfile(op):
        print('❌ 缺少总览文件'); return 1
    ptxt = open(op, encoding='utf-8').read()

    miss = [s for s in OVERVIEW_SECTIONS if s not in ptxt]
    (fail if miss else ok)('C1', f'总览缺章节 {miss}' if miss else '总览结构完整')

    bodies = {}
    for slug in ENTITIES:
        p = os.path.join(STATE, ENTITY_DIR, slug + '.md')
        if os.path.isfile(p):
            bodies[slug] = open(p, encoding='utf-8').read()
        else:
            fail('C2', f'{DISPLAY.get(slug, slug)} 缺少实体文件 {ENTITY_DIR}/{slug}.md')
    if bodies:
        ok('C2', f'{len(bodies)}/{len(ENTITIES)} 实体文件存在')

    rows = parse_section_table(ptxt, r'##\s*快速一览表')
    for slug, body in bodies.items():
        name = DISPLAY.get(slug, slug)
        for fname, pat in ENTITY_FIELDS.items():
            if not re.search(pat, body):
                fail('C4', f'{name} 缺字段 {fname}')
        n_rem = sum(1 for l in body.split('\n') if l.startswith('- 备注'))
        if n_rem > KEEP_MAX:
            fail('C7', f'{name} 备注 {n_rem} 条 > 上限 {KEEP_MAX}')
        dev = re.search(r'- 状态[:：](.+)', body)
        mark = re.search(r'- 印记[:：](.+)', body)
        if dev and mark:
            if name in exc:
                warn('C5', f'{name} 存在已登记例外（见 rule-exceptions.md）→ 不计 FAIL')
            else:
                pcts = [int(x) for x in re.findall(r'(\d+)%', drop_trace(dev.group(1)))]
                all100 = bool(pcts) and all(p == 100 for p in pcts)
                awakened = '完全觉醒' in strip_notes(mark.group(1))
                if awakened and not all100:
                    fail('C5', f'{name} 状态「完全觉醒」但数据未满 100% → 登记例外或修正')

    if os.path.isfile(BASELINE):
        base = json.load(open(BASELINE, encoding='utf-8'))
        arch = Counter()
        ad = os.path.join(STATE, ARCHIVE_DIR)
        for f in (os.listdir(ad) if os.path.isdir(ad) else []):
            for l in open(os.path.join(ad, f), encoding='utf-8'):
                m = re.match(r'^\*\*\[(.+?)\]\*\*', l)
                if m:
                    arch[m.group(1)] += 1
        for slug, body in bodies.items():
            name = DISPLAY.get(slug, slug)
            total = sum(1 for l in body.split('\n') if l.startswith('- 备注')) + arch[name]
            if total < base.get(name, 0):
                fail('C8', f'{name} 条目总量 {total} < 基线 {base.get(name, 0)}（可能丢条）')
        if not any(x.startswith('[C8]') for x in fails):
            ok('C8', f'归档无损（基线 {sum(base.values())} 条可追溯）')

    real = set()
    for r, _, fs in os.walk(os.path.join(SKILL, 'references')):
        for f in fs:
            if f.endswith('.md'):
                real.add(os.path.relpath(os.path.join(r, f), SKILL).replace('\\', '/'))
    indexed = {x.rstrip('.,;') for x in re.findall(r'references/[^\s`\)\|]+\.md', open(os.path.join(SKILL, 'SKILL.md'), encoding='utf-8').read())}
    un = sorted(real - indexed)
    (fail if un else ok)('C9', f'{len(un)} 个文件未登记：{un[:4]}' if un else f'{len(real)} 个文件全部已登记')

    bad = []
    sd = os.path.join(SKILL, 'scripts')
    for f in (os.listdir(sd) if os.path.isdir(sd) else []):
        if f.endswith('.py'):
            p = os.path.join(sd, f)
            try:
                compile(open(p, encoding='utf-8').read(), p, 'exec')   # 坑 #10
            except SyntaxError as e:
                bad.append(f'{f}: {e}')
    (fail if bad else ok)('C10', f'脚本编译失败：{bad}' if bad else 'scripts/*.py 可编译')

    print('=' * 60)
    print(f'校验 · FAIL={len(fails)} WARN={len(warns)} PASS={len(oks)}')
    print('=' * 60)
    for x in fails: print('❌', x)
    for x in warns: print('⚠️ ', x)
    if a.verbose:
        for x in oks: print('✅', x)
    print('结论：', 'PASS' if not fails else 'FAIL')
    return 0 if not fails else 1

if __name__ == '__main__':
    sys.exit(main())
