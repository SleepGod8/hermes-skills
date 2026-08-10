#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书导入脚本（方案 B：手动构造 docx blocks，无需 convert/wiki 写权限）
用法：
  python import_feishu.py                       # 默认导入 raw/07Milvus快速入门.json（单篇测试）
  python import_feishu.py raw/xxx.json          # 导入指定 raw json
  python import_feishu.py raw/*.json            # 批量导入
前置：C:/Users/80704/AppData/Local/hermes/.env 里有 FEISHU_APP_ID / FEISHU_APP_SECRET
输入：feishu_import/raw/<标题>.json，格式为 [["cls","text"],...] 或 [{"cls":...,"text":...}]
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = r'C:/Users/80704/AppData/Local/hermes/.env'
RAW_DIR = os.path.join(BASE, 'raw')
API = 'https://open.feishu.cn'

# docx block_type: 1=page 2=text 3=heading1 4=heading2 5=heading3 6=heading4
# 12=bullet 14=code 15=quote 25=divider


def load_env():
    env = {}
    with open(ENV_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def get_token(app_id, app_secret):
    req = urllib.request.Request(
        API + '/open-apis/auth/v3/tenant_access_token/internal',
        data=json.dumps({'app_id': app_id, 'app_secret': app_secret}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode('utf-8'))
    if d.get('code') != 0:
        raise RuntimeError(f'获取 token 失败: {d}')
    return d['tenant_access_token']


def api_call(token, method, path, body=None, timeout=120):
    url = API + path
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode('utf-8'))
        except Exception:
            return {'code': e.code, 'msg': str(e)}


def inline_elements(text):
    """构造 text 元素，支持 **bold** 和 `code`"""
    elements = []
    parts = re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', text)
    for p in parts:
        if not p:
            continue
        if p.startswith('**') and p.endswith('**'):
            elements.append({'text_run': {'content': p[2:-2], 'text_element_style': {'bold': True}}})
        elif p.startswith('`') and p.endswith('`'):
            elements.append({'text_run': {'content': p[1:-1], 'text_element_style': {'inline_code': True}}})
        else:
            elements.append({'text_run': {'content': p}})
    return elements


def extract_code_text(text):
    """从 代码块XXX复制 格式提取真实代码"""
    m = re.search(r'代码块\s*(.*?)复制\s*(.*)$', text, re.S)
    if m:
        return m.group(2).strip()
    t = re.sub(r'^代码块', '', text)
    t = re.sub(r'复制$', '', t)
    return t.strip()


def raw_to_docx_blocks(blocks):
    """raw [cls, text] → docx Block 列表"""
    out = []
    for b in blocks:
        if isinstance(b, dict):
            cls, text = b.get('cls', 't'), b.get('text', '')
        else:
            cls, text = b[0], b[1]
        cls = cls.replace('-', '')  # 'heading2-' → 'heading2'
        if cls.startswith('image'):
            continue
        if cls.startswith('heading'):
            level = cls.replace('heading', '')
            btype = {1: 3, 2: 4, 3: 5, 4: 6}.get(level, 4)
            field = {3: 'heading1', 4: 'heading2', 5: 'heading3', 6: 'heading4'}[btype]
            out.append({'block_type': btype, field: {'elements': inline_elements(text)}})
        elif cls.startswith('bullet'):
            t = text.lstrip('•·-').strip()
            if t:
                out.append({'block_type': 12, 'bullet': {'elements': inline_elements(t)}})
        elif cls.startswith('code'):
            code = extract_code_text(text)
            if code:
                lang = 'python' if 'python' in text.lower() or 'py' in text[:30].lower() else 'plain'
                out.append({'block_type': 14, 'code': {
                    'elements': [{'text_run': {'content': code}}],
                    'style': {'language': 2 if lang == 'python' else 1},
                }})
        else:
            t = text.strip()
            if t:
                out.append({'block_type': 2, 'text': {'elements': inline_elements(t)}})
    return out


def create_document(token, title):
    d = api_call(token, 'POST', '/open-apis/docx/v1/documents', {'title': title})
    if d.get('code') != 0:
        raise RuntimeError(f'create 失败: {d}')
    return d['data']['document']['document_id']


def get_root_block(token, document_id):
    d = api_call(token, 'GET', f'/open-apis/docx/v1/documents/{document_id}/blocks?page_size=500')
    if d.get('code') != 0:
        raise RuntimeError(f'list blocks 失败: {d}')
    items = d['data']['items']
    for b in items:
        if b.get('block_type') == 1:
            return b['block_id']
    return items[0]['block_id'] if items else None


def add_children(token, document_id, parent_block_id, blocks):
    d = api_call(token, 'POST',
                 f'/open-apis/docx/v1/documents/{document_id}/blocks/{parent_block_id}/children',
                 {'children': blocks})
    if d.get('code') != 0:
        raise RuntimeError(f'children create 失败: {d}')
    return d['data']


def import_one(token, raw_path):
    """导入单篇 raw json，返回 (标题, document_id, 状态)"""
    with open(raw_path, encoding='utf-8') as f:
        raw = json.load(f)
    title = os.path.basename(raw_path)[:-5]
    if not raw:
        return title, None, '空文档'
    blocks = raw_to_docx_blocks(raw)
    if not blocks:
        return title, None, '无可用内容块'
    document_id = create_document(token, title)
    root_id = get_root_block(token, document_id)
    if not root_id:
        return title, document_id, '根块获取失败'
    total = 0
    for i in range(0, len(blocks), 40):
        chunk = blocks[i:i + 40]
        add_children(token, document_id, root_id, chunk)
        total += len(chunk)
        time.sleep(0.2)
    return title, document_id, f'ok({total}块)'


def main():
    env = load_env()
    token = get_token(env['FEISHU_APP_ID'], env['FEISHU_APP_SECRET'])
    print('token 获取成功')
    targets = sys.argv[1:]
    if not targets:
        targets = [os.path.join(RAW_DIR, '07Milvus快速入门.json')]
    ok, fail = 0, 0
    for t in targets:
        if not os.path.exists(t):
            print(f'文件不存在: {t}')
            fail += 1
            continue
        try:
            title, doc_id, status = import_one(token, t)
            print(f'{title} | {status} | document_id={doc_id}')
            if doc_id:
                ok += 1
            else:
                fail += 1
        except Exception as e:
            print(f'{os.path.basename(t)} | 失败: {e}')
            fail += 1
    print(f'\n完成: 成功 {ok}, 失败 {fail}')


if __name__ == '__main__':
    main()
