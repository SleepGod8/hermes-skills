#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把飞书抓取的 block 数据清洗为标准 Markdown。
用法：脚本和 milvus_blocks.json 放在同一目录，运行 `python clean_feishu_blocks.py <json> <输出.md> [标题]`
输入 JSON 格式：[{"cls": "heading2-|heading3-|text-|bullet-|code-|image-", "text": "..."}]
"""
import json
import re
import sys


def clean_text(s):
    # 去零宽空格/不可见字符，压缩空白
    s = s.replace('\u200b', '').replace('\u200e', '').replace('\ufeff', '')
    s = s.replace('\u00a0', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()


def extract_code(text):
    """从 '代码块XXX复制<真实代码>' 格式中提取代码，返回 (语言, 代码)"""
    t = clean_text(text)
    m = re.search(r'代码块\s*(.*?)复制\s*(.*)$', t, re.S)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    t = re.sub(r'^代码块', '', t)
    t = re.sub(r'复制$', '', t)
    return '', t.strip()


def convert(blocks, title=''):
    lines = []
    for b in blocks:
        cls = b['cls']
        text = b['text']
        if 'isEmpty' in cls:
            continue
        if cls.startswith('image'):
            continue  # 图片占位跳过（源文档中为图片）
        if cls.startswith('heading2'):
            lines.append('\n## ' + clean_text(text) + '\n')
        elif cls.startswith('heading3'):
            lines.append('\n### ' + clean_text(text) + '\n')
        elif cls.startswith('bullet'):
            t = clean_text(text).lstrip('•·-')
            lines.append('- ' + t)
        elif cls.startswith('code'):
            lang, code = extract_code(text)
            if not code:
                continue
            lang_map = {'python': 'python', 'java': 'bash', 'go': 'bash',
                        'markdown': 'yaml', 'xml': 'xml', '': ''}
            out_lang = lang_map.get(lang.lower(), lang.lower())
            lines.append(f'\n```{out_lang}\n{code}\n```\n')
        else:
            t = clean_text(text)
            if t:
                lines.append(t)
    md = '\n'.join(lines)
    md = re.sub(r'\n{3,}', '\n\n', md)
    md = re.sub(r'```\n\n+```', '```\n```', md)
    if title:
        md = f'# {title}\n\n' + md
    return md


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'blocks.json'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'output.md'
    title = sys.argv[3] if len(sys.argv) > 3 else ''
    with open(src, encoding='utf-8') as f:
        blocks = json.load(f)
    md = convert(blocks, title)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f'生成完成: {len(md)} 字符, {md.count(chr(10))} 行 -> {dst}')
