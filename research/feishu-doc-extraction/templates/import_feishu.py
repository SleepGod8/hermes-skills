#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书导入模板（Plan B：无 convert 权限版，2026-08 实测 40 篇）
流程：raw [cls,text] → docx blocks → create → 根块 → children 分批写入
用法：python import_feishu.py raw/01AI应用开发项目总览.json [更多文件...]
环境：.env 需有 FEISHU_APP_ID / FEISHU_APP_SECRET
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

ENV_PATH = r'C:/Users/<user>/AppData/Local/hermes/.env'   # ← 改成实际用户
API = 'https://open.feishu.cn'


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
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode('utf-8'))
    if d.get('code') != 0:
        raise RuntimeError(f'token 失败: {d}')
    return d['tenant_access_token']


def api_call(token, method, path, body=None, timeout=120):
    url = API + path
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode('utf-8'))
        except Exception:
            return {'code': e.code, 'msg': str(e)}


def inline_elements(text):
    """**bold** / `code` → 多个 text_run"""
    elements = []
    for p in re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', text):
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
    """去「代码块XXX复制」UI 噪音"""
    m = re.search(r'代码块\s*(.*?)复制\s*(.*)$', text, re.S)
    if m:
        return m.group(2).strip()
    return re.sub(r'^代码块|复制$', '', text).strip()


def raw_to_docx_blocks(blocks):
    """raw [cls,text] → docx Block。heading2→4, heading3→5, heading4→6, bullet→12, code→14, text→2"""
    out = []
    for b in blocks:
        if isinstance(b, dict):
            cls, text = b.get('cls', 't'), b.get('text', '')
        else:
            cls, text = b[0], b[1]
        cls = cls.replace('-', '')
        if cls.startswith('image'):
            continue
        if cls.startswith('heading'):
            level = cls.replace('heading', '')
            btype = {1: 3, 2: 4, 3: 5, 4: 6}.get(int(level) if level.isdigit() else 2, 4)
            field = {3: 'heading1', 4: 'heading2', 5: 'heading3', 6: 'heading4'}[btype]
            out.append({'block_type': btype, field: {'elements': inline_elements(text)}})
        elif cls.startswith('bullet'):
            t = text.lstrip('•·-').strip()
            if t:
                out.append({'block_type': 12, 'bullet': {'elements': inline_elements(t)}})
        elif cls.startswith('code'):
            code = extract_code_text(text)
            if code:
                lang = 2 if 'python' in text.lower() else 1
                out.append({'block_type': 14, 'code': {'elements': [{'text_run': {'content': code}}], 'style': {'language': lang}}})
        else:
            t = text.strip()
            if t:
                out.append({'block_type': 2, 'text': {'elements': inline_elements(t)}})
    return out


def import_one(token, raw_path):
    with open(raw_path, encoding='utf-8') as f:
        raw = json.load(f)
    title = os.path.basename(raw_path)[:-5]
    if not raw:
        return title, None, '空文档'
    blocks = raw_to_docx_blocks(raw)
    if not blocks:
        return title, None, '无内容块'

    d = api_call(token, 'POST', '/open-apis/docx/v1/documents', {'title': title})
    if d.get('code') != 0:
        raise RuntimeError(f'create 失败: {d}')
    document_id = d['data']['document']['document_id']

    d = api_call(token, 'GET', f'/open-apis/docx/v1/documents/{document_id}/blocks?page_size=500')
    items = d['data']['items']
    root = next((b['block_id'] for b in items if b.get('block_type') == 1), items[0]['block_id'])

    total = 0
    for i in range(0, len(blocks), 40):
        r = api_call(token, 'POST',
                     f'/open-apis/docx/v1/documents/{document_id}/blocks/{root}/children',
                     {'children': blocks[i:i + 40]})
        if r.get('code') != 0:
            raise RuntimeError(f'children 失败: {r}')
        total += len(blocks[i:i + 40])
        time.sleep(0.2)
    return title, document_id, f'ok({total}块)'


def main():
    env = load_env()
    token = get_token(env['FEISHU_APP_ID'], env['FEISHU_APP_SECRET'])
    print('token ok', flush=True)
    ok = fail = 0
    for t in sys.argv[1:]:
        try:
            title, doc_id, status = import_one(token, t)
            print(f'{title} | {status} | {doc_id}', flush=True)
            ok += 1 if doc_id else 0
            fail += 0 if doc_id else 1
        except Exception as e:
            print(f'{os.path.basename(t)} | 失败: {e}', flush=True)
            fail += 1
    print(f'完成: 成功 {ok}, 失败 {fail}', flush=True)


if __name__ == '__main__':
    main()
