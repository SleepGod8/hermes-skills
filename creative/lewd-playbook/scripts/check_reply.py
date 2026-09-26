#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""色情回复质检（机械检查）· 2026-09-26 建。

对标 novel-execution-layer 的机械质检三件套：把《输出规范》+《写作技法》+《菜单引擎》
里可机械判定的条款做成脚本，写完一轮正文先自查，再看结果决定改不改。

用法：
    python scripts/check_reply.py --file reply.txt
    python scripts/check_reply.py --text "正文……"
    type reply.txt | python scripts/check_reply.py
    python scripts/check_reply.py --self-test        # 内置样本自测（验收用）

退出码：0 = PASS；1 = 有 FAIL（字数不足 / 缺菜单 / 结算语入侵等硬伤）
"""
import argparse
import re
import sys

MIN_CHARS = 1000            # SKILL.md 输出规范：正文不少于 1000 中文字
MAX_MENU = 4
MIN_MENU = 1
EMOJI = '❤️💦😈😵🥺'

AI_WORDS = ['缓缓地', '慢慢地', '不禁', '忍不住地', '仿佛', '好像', '不知过了多久',
            '空气仿佛凝固', '时间仿佛静止', '一丝', '一抹', '一缕', '完美', '极致',
            '无比', '复杂的情感', '说不清的情绪', '各种各样', '大量的']
HOT_PHRASES = ['被玩到高潮', '玩到高潮', '面无表情', '自动吞吐', '男根贯穿', '求欢模式',
               '主动开发', '开发他人', '共通机制', '详细桥段']
SETTLE_PAT = r'(?:EXP|经验|开发度)\s*[+\-]?\s*\d|\+\s*\d+\s*分|\+\s*20|\+\s*\d+\s*(?:（|$)'
HOST_PAT = r'主人(?:的)?(?:手|身体|腰|呼吸|心跳|大腿|胸口)|主人感到|主人觉得|主人忍不住|主人也'
MOAN = ['呜', '啊', '嗯', '哦', '哈', '咿', '唔']
SETTLE_MARKERS = ('【结算', '—— 结算', '## 结算', '<settle', '面板更新', '档案汇报')


def strip_settlement(t):
    """去掉结算/档案汇报部分（字数统计不含这部分）。"""
    cut = len(t)
    for m in SETTLE_MARKERS:
        i = t.find(m)
        if i != -1:
            cut = min(cut, i)
    return t[:cut]


def cn_len(t):
    return len(re.findall(r'[\u4e00-\u9fff]', t))


def menus_in(t):
    tail = '\n'.join(t.strip().split('\n')[-18:])
    pats = [r'^\s*[①②③④⑤⑥]', r'^\s*[1-4][.、)）]', r'^\s*\[[1-4]\]', r'^\s*\*\*[1-4][.、]']
    n = 0
    for line in tail.split('\n'):
        if any(re.match(p, line) for p in pats):
            n += 1
    return n


def estimate_dial(t):
    """粗略档位估计：按呻吟密度与省略号/破折号密度。"""
    body = strip_settlement(t)
    n = max(cn_len(body), 1)
    moan = sum(body.count(m) for m in MOAN)
    ell = body.count('……') + body.count('——')
    r = (moan / n) * 1000
    e = (ell / n) * 1000
    if r < 3 and e < 6:
        return '① 温柔'
    if r < 8 and e < 14:
        return '② 常规'
    if r < 16:
        return '③ 极限'
    return '④ 黑暗'


def check(text, verbose=False):
    fails, warns, oks = [], [], []
    body = strip_settlement(text)
    n = cn_len(body)

    if n < MIN_CHARS:
        fails.append(f'[C1] 正文字数 {n} < {MIN_CHARS}（结算段已排除）')
    else:
        oks.append(f'[C1] 正文 {n} 字（≥{MIN_CHARS}）')

    ne = sum(text.count(e) for e in EMOJI)
    if ne == 0:
        fails.append('[C2] 全篇零 emoji（规范要求保留 ❤️ 等）')
    elif ne * 60 > n:
        warns.append(f'[C2] emoji 偏密（{ne} 个 / {n} 字），建议只在情动与破功处用')
    else:
        oks.append(f'[C2] emoji {ne} 个')

    nm = menus_in(text)
    if nm == 0:
        fails.append('[C5] 结尾没有菜单（应为 1–4 条后续选项）')
    elif nm > MAX_MENU:
        warns.append(f'[C5] 菜单 {nm} 条 > {MAX_MENU}')
    else:
        oks.append(f'[C5] 菜单 {nm} 条')

    hit = [w for w in AI_WORDS if w in body]
    if hit:
        warns.append(f'[C7] 反 AI 味词命中：{hit}')
    else:
        oks.append('[C7] 无 AI 味禁用词')

    rep = {p: body.count(p) for p in HOT_PHRASES if body.count(p) >= 2}
    if rep:
        warns.append(f'[C8] 高频短语同轮重复：{rep}')
    else:
        oks.append('[C8] 无高频短语重复')

    if re.search(SETTLE_PAT, body):
        fails.append('[C9] 结算语入侵正文（EXP/开发度/+数字 应只在结算段）')
    else:
        oks.append('[C9] 正文无结算语')

    h = re.findall(HOST_PAT, body)
    if h:
        warns.append(f'[C4] 疑似描写了主人（留白规则）：{sorted(set(h))[:3]}')
    else:
        oks.append('[C4] 主人留白 OK')

    lvl = estimate_dial(text)
    oks.append(f'[C10] 档位估计：{lvl}')

    return fails, warns, oks, n, lvl


SAMPLES = {
    'bad_short': '她缓缓地抬起眼，不禁笑了。主人觉得她很可爱。\n\n她高潮了。',
    'bad_no_menu': ('她走近，指尖按在杯沿上。' * 60) + '\n\n这次真的结束了。',
    'good': ('她走近，指尖按在杯沿上，瓷器的凉透过指腹。屋子里只有水汽的声音，'
             '茶香混着一点汗味浮起来。她没有说话，只是把杯子又推近了半寸。\n\n'
             '「……主人。」她开口，声音比平时低，尾音断在半空里。\n\n'
             '她按住自己的手腕，像是要确认脉搏，又像是在忍。地板凉，膝盖压下去时'
             '她轻轻吸了一口气，那口气没吐完就散成了气音。❤️\n\n'
             '到第三轮时她终于咬不住声音，句子碎成单字，最后连单字也散了。\n\n'
             '——\n\n① 桌下那只手，可以不用收回去\n② 换件新的，你还没见过那件\n'
             '③ 换人，让大姐来收拾你\n\n主人点哪道？😈') * 6,
}
SAMPLES['good'] = SAMPLES['good']


def self_test():
    exp = {'bad_short': True, 'bad_no_menu': True, 'good': False}
    allok = True
    for k, sample in SAMPLES.items():
        fails, warns, oks, n, lvl = check(sample)
        hard = any(x.startswith('[C1]') or x.startswith('[C5]') or x.startswith('[C9]') for x in fails)
        verdict = 'FAIL' if hard else 'PASS'
        want = 'FAIL' if exp[k] else 'PASS'
        flag = '✅' if verdict == want else '❌'
        if verdict != want:
            allok = False
        print(f'{flag} 样本 {k:12s} → {verdict}（期望 {want}）| 字数 {n} | {lvl} | FAIL={len(fails)}')
        for x in fails:
            print('      ', x)
    print('\n自测结论：', 'PASS（脚本行为符合预期）' if allok else 'FAIL（脚本判定错误，需修）')
    return 0 if allok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file'), ap.add_argument('--text')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    if a.text is not None:
        text = a.text
    elif a.file:
        text = open(a.file, encoding='utf-8').read()
    else:
        text = sys.stdin.read()
    fails, warns, oks, n, lvl = check(text, a.verbose)

    print('=' * 58)
    print(f'回复质检 · 正文 {n} 字 · 档位估计 {lvl} · FAIL={len(fails)} WARN={len(warns)}')
    print('=' * 58)
    for x in fails:
        print('❌', x)
    for x in warns:
        print('⚠️ ', x)
    for x in oks:
        print('✅', x)
    print('=' * 58)
    print('结论：', 'PASS' if not fails else 'FAIL（硬伤需改）')
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
