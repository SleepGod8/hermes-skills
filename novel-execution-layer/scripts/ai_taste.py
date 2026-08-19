#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_taste.py — AI 味扫描器（移植自 dsh-novel-writer src/core/polish/scanner.ts）
纯函数：词库匹配 → 命中明细 + 密度评分（每千字命中数加权，上限 100）。
词库: ai_taste_dict.json（234 词，5 类，随本目录分发）
用法:
  python ai_taste.py <文本文件...> [--json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

CJK_RE = re.compile(r'[\u4e00-\u9fff]')
SENTENCE_END = set('。！？!?\n')
CATEGORY_CN = {
    'connector': '转折连接词/口头禅',
    'action': '万能动作描写',
    'psychology': '心理描写AI腔',
    'adjective': '形容词堆叠/万能句式',
    'tone': '句末感叹/语气词',
}


def load_dict(path: Path) -> list:
    with open(path, encoding='utf-8') as fh:
        words = json.load(fh)
    # 长词优先（避免「微微」先命中「微微一笑」）
    return sorted(words, key=lambda w: (-len(w['word']), w['word']))


def split_sentences(text: str):
    sentences = []
    start = 0
    buf = ''
    for i, ch in enumerate(text):
        buf += ch
        if ch in SENTENCE_END:
            trimmed = buf.strip()
            if trimmed:
                sentences.append((trimmed, start))
            buf = ''
            start = i + 1
    tail = buf.strip()
    if tail:
        sentences.append((tail, start))
    return sentences


def scan_ai_taste(text: str, words: list) -> dict:
    details = []
    by_category = {k: 0 for k in CATEGORY_CN}
    cjk_chars = sum(1 for ch in text if CJK_RE.match(ch))

    for sentence, start in split_sentences(text):
        for w in words:
            word = w['word']
            from_idx = 0
            while True:
                idx = sentence.find(word, from_idx)
                if idx == -1:
                    break
                hit = {
                    'word': word,
                    'category': w['category'],
                    'strategy': w['strategy'],
                    'sentence': sentence[:60],
                    'index': start + idx,
                }
                if w.get('replacement'):
                    hit['replacement'] = w['replacement']
                details.append(hit)
                by_category[w['category']] += 1
                from_idx = idx + len(word)

    per_thousand = (len(details) / cjk_chars) * 1000 if cjk_chars else 0
    score = min(100, round(per_thousand * 10))
    return {
        'score': score,
        'hits': len(details),
        'cjkChars': cjk_chars,
        'byCategory': by_category,
        'details': details,
    }


def main():
    ap = argparse.ArgumentParser(description='AI 味扫描')
    ap.add_argument('files', nargs='+', help='文本文件')
    ap.add_argument('--json', action='store_true', help='输出 JSON')
    ap.add_argument('--dict', default=None, help='词库 JSON 路径（默认同目录 ai_taste_dict.json）')
    args = ap.parse_args()

    dict_path = Path(args.dict) if args.dict else Path(__file__).parent / 'ai_taste_dict.json'
    words = load_dict(dict_path)

    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f'文件不存在: {f}', file=sys.stderr)
            sys.exit(2)
        text = p.read_text(encoding='utf-8')
        report = scan_ai_taste(text, words)

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
            continue

        print(f"AI 味扫描 | {p.name} | 评分 {report['score']}/100 | 命中 {report['hits']} 处 / CJK {report['cjkChars']} 字")
        print('-' * 50)
        for cat, cnt in report['byCategory'].items():
            flag = '⚠️' if cnt > 0 else '·'
            print(f"  {flag} {CATEGORY_CN.get(cat, cat)}: {cnt}")
        if report['details']:
            print('-' * 50)
            for d in report['details'][:20]:
                strat = {'delete': '删', 'replace': '替', 'rewrite': '改'}.get(d['strategy'], '?')
                extra = f" → {d['replacement']}" if d.get('replacement') else ''
                print(f"  [{strat}] 「{d['word']}」({CATEGORY_CN.get(d['category'], d['category'])}){extra}")
                print(f"      …{d['sentence'][:40]}…")
            if len(report['details']) > 20:
                print(f"  … 其余 {len(report['details']) - 20} 处见 --json 输出")


if __name__ == '__main__':
    main()
