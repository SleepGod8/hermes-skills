#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
golden3.py — 黄金三章规则层诊断（移植自 dsh-novel-writer src/core/diagnose/rules.ts）
纯函数、离线可跑，模型层失败时兜底，保证评分必出。
用法:
  python golden3.py <章文件...> [--min 2000] [--max 5000] [--count 3]
  章文件: 每个文件一章，文件名或首行可含章节号；也支持 --json 输出 JSON 报告。
"""
import argparse
import json
import re
import sys
from pathlib import Path

HOOK_WORDS = ['突然', '竟然', '怎么可能', '难道', '究竟', '只见', '却见', '猛然', '赫然', '不妙', '危险', '完了']
CONFLICT_WORDS = ['杀', '怒', '敌', '危险', '逃', '追', '仇', '挑战', '打', '死', '血', '战', '恨']
STRONG_PUNCT = re.compile(r'[！？!?]')
CJK_RE = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
OPEN_QUOTES = set('“「『')
CLOSE_QUOTES = set('”」』')
SENTENCE_END_RE = re.compile(r'[。！？!?；;]')

DIMENSIONS = ['开场钩子', '主角亮相', '冲突引入', '爽点密度', '章末悬念', '设定灌输']


def count_chapter(text: str, chapter_no: int) -> dict:
    """字数统计（移植 wordcount.ts countChapter）。"""
    total = len(text)
    cjk = sum(1 for ch in text if CJK_RE.match(ch))
    paragraphs = sum(1 for line in text.splitlines() if line.strip())
    in_quote = False
    quote_chars = 0
    for ch in text:
        if ch == '"':
            in_quote = not in_quote
            continue
        if ch in OPEN_QUOTES:
            in_quote = True
            continue
        if ch in CLOSE_QUOTES:
            in_quote = False
            continue
        if in_quote:
            quote_chars += 1
    dialogue_ratio = min(1.0, quote_chars / total) if total else 0.0
    sentences = [s.strip() for s in SENTENCE_END_RE.split(text) if s.strip()]
    avg_sentence = (sum(len(s) for s in sentences) / len(sentences)) if sentences else 0.0
    return {
        'chapterNo': chapter_no,
        'totalChars': total,
        'cjkChars': cjk,
        'paragraphs': paragraphs,
        'dialogueRatio': round(dialogue_ratio, 3),
        'avgSentenceLen': round(avg_sentence, 1),
    }


def dialogue_ratio_of(text: str) -> float:
    in_quote = False
    dialogue_chars = 0
    for ch in text:
        if ch == '"':
            in_quote = not in_quote
            continue
        if ch in OPEN_QUOTES:
            in_quote = True
            continue
        if ch in CLOSE_QUOTES:
            in_quote = False
            continue
        if in_quote:
            dialogue_chars += 1
    return min(1.0, dialogue_chars / len(text)) if text else 0.0


def tail(text: str, length: int) -> str:
    return text.rstrip()[-length:]


def is_dialogue(text: str) -> bool:
    return bool(re.search(r'["“「『]', text))


def has_chapter_hook(text: str) -> bool:
    t = tail(text, 80)
    return (is_dialogue(t)
            or any(w in t for w in HOOK_WORDS)
            or any(w in t for w in CONFLICT_WORDS)
            or bool(STRONG_PUNCT.search(t)))


def diagnose_chapter(chapter: dict, word_min: int, word_max: int) -> tuple:
    issues = []
    hits = {d: 100 for d in DIMENSIONS}
    text = chapter['text']
    stats = count_chapter(text, chapter['no'])

    # 1. 字数达标
    if stats['totalChars'] < word_min:
        issues.append({
            'severity': 'warning', 'rule': 'rule-wordcount', 'chapter': chapter['no'],
            'evidence': f"本章 {stats['totalChars']} 字（目标 {word_min}-{word_max}）",
            'advice': f"本章字数不足，需扩写至 {word_min} 字以上（补冲突/细节/对话，勿注水）",
        })
        hits['爽点密度'] -= 15
    elif stats['totalChars'] > word_max:
        issues.append({
            'severity': 'warning', 'rule': 'rule-wordcount', 'chapter': chapter['no'],
            'evidence': f"本章 {stats['totalChars']} 字，超过上限 {word_max}",
            'advice': '本章超长，检查是否有拖沓段落，建议拆分或压缩',
        })

    # 2. 对话占比
    ratio = dialogue_ratio_of(text)
    if ratio < 0.05 and stats['totalChars'] > 200:
        issues.append({
            'severity': 'warning', 'rule': 'rule-dialogue', 'chapter': chapter['no'],
            'evidence': f"对话占比约 {round(ratio * 100)}%（建议 ≥5%）",
            'advice': '本章对话过少，节奏易沉闷；至少安排一次有目的的对话推进情节',
        })
        hits['爽点密度'] -= 10
    elif ratio > 0.7:
        issues.append({
            'severity': 'warning', 'rule': 'rule-dialogue', 'chapter': chapter['no'],
            'evidence': f"对话占比约 {round(ratio * 100)}%（建议 ≤70%）",
            'advice': '对话占比过高，注意动作与描写穿插',
        })

    # 3. 章末钩子
    if not has_chapter_hook(text) and len(text.strip()) > 100:
        issues.append({
            'severity': 'error', 'rule': 'rule-hook', 'chapter': chapter['no'],
            'evidence': f"章末：{tail(text, 40)}",
            'advice': '章末必须有具体钩子：悬念（威胁逼近/真相一角/人物反常）或冲突升级，禁止平淡收尾',
        })
        hits['章末悬念'] -= 40

    # 4. 开场钩子（仅第一章）
    if chapter['no'] == 1:
        opening = text[:150]
        has_opening = (bool(STRONG_PUNCT.search(opening))
                       or any(w in opening for w in CONFLICT_WORDS)
                       or is_dialogue(opening))
        if not has_opening and opening.strip() and len(opening.strip()) > 30:
            issues.append({
                'severity': 'error', 'rule': 'rule-opening', 'chapter': chapter['no'],
                'evidence': f"开头：{opening[:60]}",
                'advice': '黄金三章要求 3 行内进入事件：用动作/冲突/反常开局，先写事件再补背景',
            })
            hits['开场钩子'] -= 40

    # 5. 设定灌输（连续无对话长段）
    silent_run = 0
    silent_run_start = 0
    for line_index, line in enumerate(text.split('\n')):
        trimmed = line.strip()
        if not trimmed:
            continue
        if is_dialogue(trimmed):
            silent_run = 0
            continue
        if len(trimmed) > 120:
            silent_run += 1
            if silent_run == 1:
                silent_run_start = line_index
        else:
            silent_run = 0
        if silent_run >= 3:
            issues.append({
                'severity': 'warning', 'rule': 'rule-infodump', 'chapter': chapter['no'],
                'evidence': f"连续 {silent_run} 段无对话的长段落（起始行 {silent_run_start + 1}）",
                'advice': "设定应通过事件/对话呈现（show, don't tell），把说明拆散并绑定角色动作",
            })
            hits['设定灌输'] -= 25
            break

    # 6. 冲突词密度
    conflict_count = sum(text.count(w) for w in CONFLICT_WORDS)
    if conflict_count < 2 and stats['totalChars'] > 500:
        issues.append({
            'severity': 'warning', 'rule': 'rule-conflict', 'chapter': chapter['no'],
            'evidence': f"本章冲突信号词仅 {conflict_count} 处",
            'advice': '每章至少一个冲突事件（利益/立场/力量对抗），纯日常推进会让读者流失',
        })
        hits['冲突引入'] -= 15

    return issues, hits


def diagnose_first_chapters(chapters: list, word_min: int, word_max: int, count: int = 3) -> dict:
    targets = chapters[:count]
    all_issues = []
    dim_sum = {d: 0 for d in DIMENSIONS}
    dim_cnt = {d: 0 for d in DIMENSIONS}
    for ch in targets:
        issues, hits = diagnose_chapter(ch, word_min, word_max)
        all_issues.extend(issues)
        for d in DIMENSIONS:
            dim_sum[d] += hits[d]
            dim_cnt[d] += 1
    dims = {}
    total = 0
    for d in DIMENSIONS:
        v = max(0, round(dim_sum[d] / dim_cnt[d])) if dim_cnt[d] else 0
        dims[d] = v
        total += v
    score = max(0, min(100, round(total / len(DIMENSIONS))))
    return {
        'chapters': [c['no'] for c in targets],
        'score': score,
        'dimensions': dims,
        'issues': all_issues,
    }


def main():
    ap = argparse.ArgumentParser(description='黄金三章诊断')
    ap.add_argument('files', nargs='+', help='章节文件（每文件一章）')
    ap.add_argument('--min', type=int, default=2000, help='每章目标字数下限')
    ap.add_argument('--max', type=int, default=5000, help='每章目标字数上限')
    ap.add_argument('--count', type=int, default=3, help='诊断前 N 章')
    ap.add_argument('--json', action='store_true', help='输出 JSON')
    args = ap.parse_args()

    chapters = []
    for i, f in enumerate(args.files, start=1):
        p = Path(f)
        if not p.exists():
            print(f'文件不存在: {f}', file=sys.stderr)
            sys.exit(2)
        text = p.read_text(encoding='utf-8')
        # 尝试从文件名识别章节号（第N章 / chN / 数字）
        m = re.search(r'[第]?(\d+)[章回]?', p.stem)
        no = int(m.group(1)) if m else i
        chapters.append({'no': no, 'title': p.stem, 'text': text})

    report = diagnose_first_chapters(chapters, args.min, args.max, args.count)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    print(f"黄金三章诊断 | 章节 {report['chapters']} | 总分 {report['score']}/100")
    print('-' * 50)
    for d, v in report['dimensions'].items():
        flag = '⚠️' if v < 70 else ('✔️' if v >= 85 else '·')
        print(f"  {flag} {d}: {v}")
    print('-' * 50)
    if not report['issues']:
        print('✅ 无规则问题')
        return
    for it in report['issues']:
        print(f"[{it['severity'].upper()}] ({it['rule']}) 第{it['chapter']}章")
        print(f"  证据: {it['evidence']}")
        print(f"  建议: {it['advice']}")


if __name__ == '__main__':
    main()
