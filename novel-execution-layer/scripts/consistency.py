#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consistency.py — 一致性检测与巡检（移植自 dsh-novel-writer src/core/consistency/detect.ts）
  - 账本冲突：同实体字段多次取值（覆盖史），数值单调上升视为升级(info)，回退/无序为 warning
  - 时间线异常：书内时间倒挂/缺失（按章节号排序后比较，乱序记录不误报）
  - 世界书沉淀建议：账本首次出现实体 → 建议条目文本
用法:
  python consistency.py --ledger ledger.json [--timeline timeline.json] [--json]
输入格式（JSON）:
  ledger:   [{"entity":"岚","field":"境界","value":"筑基","chapterNo":1}, ...]
  timeline: [{"chapterNo":1,"bookTime":"第3天","createdAt":"..."}, ...]
"""
import argparse
import json
import re
import sys
from pathlib import Path

NUMERIC_RE = re.compile(r'^-?\d+(\.\d+)?$')


def chinese_to_number(text: str):
    digits = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    if not re.fullmatch(r'[零一二两三四五六七八九十]{1,3}', text):
        return None
    if '十' in text:
        tens_text, _, ones_text = text.partition('十')
        tens = 1 if tens_text == '' else digits.get(tens_text, 0)
        ones = 0 if ones_text == '' else digits.get(ones_text, 0)
        return tens * 10 + ones
    return digits.get(text)


def normalize_book_time(book_time: str):
    text = str(book_time or '').strip()
    m = re.search(r'第\s*([0-9零一二两三四五六七八九十]+)\s*(天|日)', text)
    if m:
        num = int(m.group(1)) if m.group(1).isdigit() else chinese_to_number(m.group(1))
        if num is not None:
            return f'd{num:06d}'
    m = re.search(r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})?', text)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3)) if m.group(3) else 1
        return f'y{year * 10000 + month * 100 + day}'
    m = re.search(r'第\s*(\d+)\s*年', text)
    if m:
        return f'y{int(m.group(1)) * 10000}'
    return None


def detect_ledger_conflicts(entries: list) -> list:
    by_key = {}
    for e in entries:
        key = f"{e.get('entity', '')}\u0000{e.get('field', '')}"
        by_key.setdefault(key, []).append({'chapterNo': e.get('chapterNo', 0), 'value': e.get('value', '')})
    conflicts = []
    for key, history in by_key.items():
        history.sort(key=lambda h: h['chapterNo'])
        distinct = {h['value'] for h in history}
        if len(distinct) <= 1:
            continue
        entity, _, field = key.partition('\u0000')
        numeric = all(NUMERIC_RE.match(h['value']) for h in history)
        severity = 'warning'
        if numeric:
            values = [float(h['value']) for h in history]
            monotonic = all(values[i] >= values[i - 1] for i in range(1, len(values)))
            severity = 'info' if monotonic else 'warning'
        conflicts.append({'kind': 'ledger-overwrite', 'entity': entity, 'field': field,
                          'history': history, 'severity': severity})
    return sorted(conflicts, key=lambda c: c['entity'])


def detect_timeline_anomalies(events: list) -> list:
    issues = []
    sorted_events = sorted(events, key=lambda e: (e.get('chapterNo', 0), e.get('createdAt', '')))
    keys = [normalize_book_time(e.get('bookTime', '')) for e in sorted_events]
    for i, (event, key) in enumerate(zip(sorted_events, keys)):
        ch = event.get('chapterNo', 0)
        if key is None:
            issues.append({
                'kind': 'missing-time', 'chapterNo': ch, 'severity': 'info',
                'message': f"第 {ch} 章书内时间无法解析（{event.get('bookTime', '')}）",
            })
            continue
        # 找前一个可解析的时间
        prev = None
        for j in range(i - 1, -1, -1):
            if keys[j] is not None:
                prev = (sorted_events[j], keys[j])
                break
        if prev and prev[1][0] == key[0] and key < prev[1]:
            issues.append({
                'kind': 'time-regression', 'chapterNo': ch, 'severity': 'warning',
                'message': f"第 {ch} 章书内时间（{event.get('bookTime', '')}）早于第 {prev[0].get('chapterNo', 0)} 章（{prev[0].get('bookTime', '')}），时间倒挂",
            })
    return issues


def suggest_sediment(entries: list) -> list:
    by_entity = {}
    for e in entries:
        by_entity.setdefault(e.get('entity', ''), []).append(e)
    suggestions = []
    for entity, lst in by_entity.items():
        fields = [e for e in lst if e.get('field') != 'stat_data']
        if not fields:
            continue
        lines = [f"{e.get('field', '')}：{e.get('value', '')}" for e in fields[:6]]
        suggestions.append({
            'entity': entity,
            'field': '、'.join(e.get('field', '') for e in fields),
            'value': '、'.join(e.get('value', '') for e in fields),
            'chapterNo': lst[0].get('chapterNo', 0),
            'suggestedEntry': f"【{entity}】\n" + '\n'.join(lines),
        })
    return sorted(suggestions, key=lambda s: s['chapterNo'])


def main():
    ap = argparse.ArgumentParser(description='一致性检测')
    ap.add_argument('--ledger', required=True, help='账本 JSON 文件')
    ap.add_argument('--timeline', default=None, help='时间线 JSON 文件')
    ap.add_argument('--json', action='store_true', help='输出 JSON')
    args = ap.parse_args()

    ledger_path = Path(args.ledger)
    if not ledger_path.exists():
        print(f'文件不存在: {args.ledger}', file=sys.stderr)
        sys.exit(2)
    entries = json.loads(ledger_path.read_text(encoding='utf-8'))

    report = {'conflicts': detect_ledger_conflicts(entries), 'timelineIssues': [], 'sedimentSuggestions': []}
    if args.timeline:
        tl_path = Path(args.timeline)
        if not tl_path.exists():
            print(f'文件不存在: {args.timeline}', file=sys.stderr)
            sys.exit(2)
        events = json.loads(tl_path.read_text(encoding='utf-8'))
        report['timelineIssues'] = detect_timeline_anomalies(events)
    report['sedimentSuggestions'] = suggest_sediment(entries)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    print(f"一致性检测 | 账本 {len(entries)} 条")
    print('-' * 50)
    if report['conflicts']:
        print("⚠️ 账本覆盖冲突:")
        for c in report['conflicts']:
            hist = ' → '.join(f"ch{h['chapterNo']}:{h['value']}" for h in c['history'])
            print(f"  [{c['severity']}] {c['entity']}.{c['field']} = {hist}")
    else:
        print("✅ 账本无覆盖冲突")

    if report['timelineIssues']:
        print("\n⚠️ 时间线异常:")
        for t in report['timelineIssues']:
            print(f"  [{t['severity']}] {t['message']}")
    elif args.timeline:
        print("\n✅ 时间线无倒挂")

    if report['sedimentSuggestions']:
        print("\n📌 世界书沉淀建议:")
        for s in report['sedimentSuggestions']:
            print(f"  ch{s['chapterNo']} 【{s['entity']}】{s['field']}")


if __name__ == '__main__':
    main()
