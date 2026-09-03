#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""括号配平扫描器：诊断「非严格 JSON」存档/数据文件的结构性损坏。

用法:
    python scan_brackets.py <file1> [file2 ...]

判定:
    - 打印每个文件的首个错配/未闭合位置（若存在）
    - 全部配平 → 结构完好（exit 0）；任一错配 → exit 1

为什么不用 json.loads:
    程序序列化器（Unity/Assembly-CSharp 存档等）常输出游戏能容忍的怪癖
    （如相邻字符串无逗号 "string""value"），strict JSON 解析会误报。
    括号配平扫描忽略字符串内容，只检查 {} [] 配对 → 直击致命结构伤。

要点:
    - 逐字符扫描，字符串内跳过（处理 \" 转义）
    - Windows CRLF 行尾（\r）无影响，但注意 repr 输出会显示 \r\t
"""
import sys


def scan_file(path):
    with open(path, 'r', encoding='utf-8-sig', newline='') as fh:
        text = fh.read()
    lines = text.split('\n')
    stack = []
    for i, line in enumerate(lines):
        in_str = False
        j = 0
        while j < len(line):
            c = line[j]
            if in_str:
                if c == '\\':
                    j += 2
                    continue
                if c == '"':
                    in_str = False
                j += 1
                continue
            if c == '"':
                in_str = True
                j += 1
                continue
            if c in '{[':
                stack.append((c, i + 1))
            elif c in '}]':
                if not stack:
                    return False, f'line {i+1}: unmatched closer {c}'
                o, oi = stack.pop()
                if (o == '{' and c != '}') or (o == '[' and c != ']'):
                    return False, f'line {i+1}: mismatch opened {o}@{oi} closed {c}'
            j += 1
    if stack:
        detail = ', '.join(f'{o}@{ln}' for o, ln in stack[-8:])
        return False, f'unclosed ({len(stack)}): {detail}'
    return True, f'balanced ({len(lines)} lines, 0 unclosed)'


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    ok_all = True
    for path in argv[1:]:
        ok, msg = scan_file(path)
        print(f'{"OK  " if ok else "FAIL"} {path}: {msg}')
        ok_all = ok_all and ok
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
