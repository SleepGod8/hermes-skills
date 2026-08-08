#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""腾讯文档 textPool 提取后的原始文本清洗器。

用法: python clean_tencent_doc.py <input_raw.txt> <output_clean.md>
8 次实测（元素法典/解构原典系列），处理 \u0013HYPERLINK 链接块、控制字符、\b 图片占位符、多余空行。
"""
import re
import sys


def clean(text: str) -> str:
    text = text.lstrip('\ufeff')
    # 腾讯文档内链块（HYPERLINK ... 卡片的字符区）
    text = re.sub(r'\u0013HYPERLINK.*?\u0015', '', text, flags=re.DOTALL)
    # 卡片字段残留（tdfu/tdfn/tdlf...）
    text = re.sub(r'\\tdfu \S+ \\tdfn[^\\]*\\tdlf[^\\]*\\tdle \d+ \\tdlt card', '', text)
    # 控制字符（含 \u0005 段落分隔、\u0013/14/15 链接边界）
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\u0005\u0013\u0014\u0015]', '', text)
    # 图片占位符
    text = text.replace('\b', '')
    # 行尾空格 + 多余空行压缩
    text = re.sub(r'[ \t]+\r\n', '\r\n', text)
    text = re.sub(r'\r\n{3,}', '\r\n\r\n', text)
    return text


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        raw = f.read()
    out = clean(raw)
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'OK {len(out)} chars, {out.count(chr(10))} lines -> {sys.argv[2]}')
