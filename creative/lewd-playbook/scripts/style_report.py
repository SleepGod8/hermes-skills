#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文笔量化报告 · style_report（2026-09-26 建）。

把「这轮是不是写平了」变成数字。与 check_reply.py 分工：
  * check_reply.py  = 及格线（字数/emoji/菜单/留白/AI 味/结算语）→ PASS/FAIL
  * style_report.py = 文笔画像（句长/段长/五感/对话比/重复/意象）→ 数字与对比

用法：
    python scripts/style_report.py --file reply.txt
    python scripts/style_report.py --text "正文……"
    python scripts/style_report.py --file a.txt --compare b.txt     # 两篇对比
    python scripts/style_report.py --self-test                      # 指标方向自测
    python scripts/style_report.py --file reply.txt --save          # 追加一行到文风监控档

指标异常会给出「怎么改」的提示，不判定 PASS/FAIL（好坏由主人定）。
"""
import argparse
import json
import os
import re
import statistics
import sys
import time
from collections import Counter

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE_LOG = os.path.join(SKILL, 'references', '文风监控', 'style-log.md')

SENSE = {
    '触觉': ['碰', '按', '扣', '抓', '捏', '擦', '咬', '贴', '磨', '勒', '压', '掐', '指的', '掌', '湿', '滑', '紧', '绷', '抖', '颤'],
    '听觉': ['声', '响', '喘', '哼', '叫', '呼吸', '耳鸣', '吱', '砰', '静', '听', 'echo', '水声', '机器声'],
    '体感': ['热', '凉', '冷', '烫', '酸', '麻', '软', '绷紧', '失重', '发白', '发烫', '晕', '空', '震', '抽'],
    '嗅觉': ['味', '香', '腥', '臭', '甜', '咸', '茶香', '汗', '酒', '金属', '消毒', '奶', '烟', '霉'],
    '视觉': ['看', '眼', '光', '影', '亮', '红', '白', '暗', '颜色', '浮', '映'],
}
MOTIF = {
    '汗': ['汗'], '水': ['水', '湿', '潮'], '茶': ['茶'], '金属': ['金属', '铁', '钢', '机器'],
    '光': ['光', '灯', '亮'], '影': ['影', '影子'], '纸笔': ['纸', '笔', '本子', '记录'],
    '温度': ['热', '凉', '冷', '烫'], '布': ['布', '裙', '被', '枕', '床单'], '气味': ['味', '香', '臭'],
}
SIMILE = ['像', '似', '如', '宛如', '仿佛']
ADV = ['缓缓', '轻轻', '慢慢', '悄悄', '狠狠', '猛地', '微微', '渐渐', '静静地', '深深地']


def strip_settlement(t):
    cut = len(t)
    for marker in ('【结算', '—— 结算', '## 结算', '<settle', '面板更新', '档案汇报'):
        i = t.find(marker)
        if i != -1:
            cut = min(cut, i)
    return t[:cut]


def cn(s):
    return len(re.findall(r'[\u4e00-\u9fa5]', s))


def sentences(t):
    return [s for s in re.split(r'[。！？…]+|——|\n+', t) if cn(s) > 0]


def paras(t):
    return [p for p in re.split(r'\n\s*\n', t) if cn(p) > 0]


def metrics(text):
    body = strip_settlement(text)
    n = cn(body) or 1
    ps = paras(body)
    ss = sentences(body)
    slens = [cn(s) for s in ss]
    plens = [cn(p) for p in ps]
    senses = {k: sum(body.count(w) for w in ws) for k, ws in SENSE.items()}
    dialog = sum(cn(x) for x in re.findall(r'「[^」]*」', body))
    grams = Counter()
    for seg in re.findall(r'[\u4e00-\u9fa5]+', body):
        for i in range(len(seg) - 1):
            for L in (2, 3):
                if i + L <= len(seg):
                    grams[seg[i:i + L]] += 1
    top_rep = [(g, c) for g, c in grams.most_common(25) if c >= 3]
    motifs = {k: sum(body.count(w) for w in ws) for k, ws in MOTIF.items()}
    emoji_pat = r'[❤💦😈😵🥺♡]️?'
    emoji = re.findall(emoji_pat, text)
    emoji_end = sum(1 for m in re.finditer(emoji_pat, text)
                    if re.fullmatch(r'[」）)\]\s]*', text[m.end(): text.find('\n', m.end()) if text.find('\n', m.end()) != -1 else len(text)]))
    return {
        'chars': cn(body), 'paras': len(ps),
        'para_mean': round(statistics.mean(plens), 1) if plens else 0,
        'para_max': max(plens) if plens else 0,
        'para_over300': sum(1 for p in plens if p > 300),
        'sent': len(ss), 'sent_mean': round(statistics.mean(slens), 1) if slens else 0,
        'sent_max': max(slens) if slens else 0,
        'short_ratio': round(100 * sum(1 for x in slens if x <= 8) / len(slens), 1) if slens else 0,
        'senses': senses, 'sense_kinds': sum(1 for v in senses.values() if v > 0),
        'dialog_ratio': round(100 * dialog / n, 1),
        'quotes': len(re.findall(r'「[^」]*」', body)),
        'simile': sum(body.count(w) for w in SIMILE),
        'adv': sum(body.count(w) for w in ADV),
        'emoji': len(emoji), 'emoji_end': emoji_end,
        'top_rep': top_rep[:6], 'motifs': {k: v for k, v in motifs.items() if v},
    }


def hints(m):
    h = []
    if m['short_ratio'] < 18:
        h.append(f"短句比例 {m['short_ratio']}% 偏低 → 释放段/破功处把句子砍短（craft §2）")
    if m['sent_mean'] > 26:
        h.append(f"平均句长 {m['sent_mean']} 字偏长 → 长句拆两句，动作分开写")
    if m['sense_kinds'] < 3:
        h.append(f"五感只覆盖 {m['sense_kinds']} 类 → 至少补两类（craft §1）")
    per100 = 100 * m['quotes'] / max(m['chars'], 1)
    if per100 < 0.6:
        h.append(f"台词密度 {per100:.1f} 句/100字 偏低 → 每 150–250 字给一句台词（craft §5）")
    if m['para_over300']:
        h.append(f"有 {m['para_over300']} 段超过 300 字 → 拆段（typography §2）")
    if m['adv'] >= 6:
        h.append(f"副词/状语 {m['adv']} 处偏多 → 删「缓缓/轻轻」类填充（craft §8）")
    if m['simile'] >= 6:
        h.append(f"比喻标记 {m['simile']} 处偏多 → 留最狠的一处，其余改直写")
    if m['emoji'] and m['emoji_end'] / max(m['emoji'], 1) < 0.6:
        h.append("emoji 多在句中 → 建议放句末（typography §4）")
    dups = [f"{g}×{c}" for g, c in m['top_rep'] if c >= 4]
    if dups:
        h.append(f"同轮高频重复：{'、'.join(dups[:4])} → 换词或换意象（craft §9）")
    if len(m['motifs']) and max(m['motifs'].values()) >= 8:
        k = max(m['motifs'], key=m['motifs'].get)
        h.append(f"意象「{k}」出现 {m['motifs'][k]} 次 → 单一意象过载（motif-ledger）")
    return h


def show(m, title):
    print(f'\n── {title} ──')
    print(f"  正文 {m['chars']} 字 ｜ 段落 {m['paras']}（均 {m['para_mean']} / 最长 {m['para_max']}）"
          f" ｜ 句子 {m['sent']}（均 {m['sent_mean']} / 最长 {m['sent_max']} / 短句 {m['short_ratio']}%）")
    print(f"  对话比 {m['dialog_ratio']}%（台词 {m['quotes']} 句） ｜ 比喻标记 {m['simile']} ｜ 副词状语 {m['adv']}")
    print(f"  emoji {m['emoji']}（句末 {m['emoji_end']}） ｜ 五感覆盖 {m['sense_kinds']}/5 {m['senses']}")
    if m['motifs']:
        print(f"  意象分布 {m['motifs']}")
    if m['top_rep']:
        print(f"  同轮高频 {[f'{g}×{c}' for g, c in m['top_rep']]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file'), ap.add_argument('--text'), ap.add_argument('--compare')
    ap.add_argument('--save', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()

    if a.self_test:
        calm = ('她坐在靠窗的那把旧椅子上，看着窗外一点一点暗下去的天色，手里那杯茶已经凉透了。'
                '\n\n'
                '她没有说话，只是把杯子放回托盘，听着院子里很远的狗叫声，慢慢数了一遍自己的呼吸。'
                '\n\n'
                '「今天就这样吧。」她轻声说完，又替自己拢了拢肩上的披肩，坐在那里等天彻底黑下来。') * 2
        hot = ('「呜——！」她的话被撞断。\n\n腰塌下去。抓住床单。指甲发白。汗顺着后颈流。呼吸碎了。\n\n'
               '「不行了。」她喘。抓。颤。❤️\n\n① 继续\n② 停下\n③ 换人\n') * 3
        mc, mh = metrics(calm), metrics(hot)
        ok1 = mh['short_ratio'] > mc['short_ratio']
        ok2 = mh['dialog_ratio'] > 0 and mc['dialog_ratio'] > 0
        print(f"{'✅' if ok1 else '❌'} 激烈样本短句比例({mh['short_ratio']}%) 应 > 平静样本({mc['short_ratio']}%)")
        print(f"{'✅' if ok2 else '❌'} 对话比均可计算：平静 {mc['dialog_ratio']}% / 激烈 {mh['dialog_ratio']}%")
        print(f"{'✅' if mh['chars'] != mc['chars'] else '❌'} 字数区分正常：{mc['chars']} vs {mh['chars']}")
        print('自测结论：', 'PASS' if ok1 and ok2 else 'FAIL')
        return 0 if ok1 and ok2 else 1

    if a.text is not None:
        text = a.text
    elif a.file:
        text = open(a.file, encoding='utf-8').read()
    else:
        text = sys.stdin.read()

    m = metrics(text)
    show(m, a.file or '输入文本')
    if a.compare:
        m2 = metrics(open(a.compare, encoding='utf-8').read())
        show(m2, a.compare)
        print('\n对比（左＝A，右＝B）:')
        for k in ['chars', 'sent_mean', 'short_ratio', 'dialog_ratio', 'sense_kinds', 'simile', 'adv', 'emoji']:
            print(f"  {k:14s} {m[k]:>8}  |  {m2[k]:>8}")
    hs = hints(m)
    print('\n建议：' if hs else '\n建议：无明显短板 ✅')
    for x in hs:
        print('  •', x)

    if a.save:
        os.makedirs(os.path.dirname(STYLE_LOG), exist_ok=True)
        if not os.path.isfile(STYLE_LOG):
            open(STYLE_LOG, 'w', encoding='utf-8').write(
                '# 文风监控 · style-log（🆕 2026-09-26）\n\n'
                '> 每轮互动后追加一行；用于发现「写平了／写同了」的趋势。由 `scripts/style_report.py --save` 写入。\n\n'
                '| 时间 | 来源 | 正文汉字 | 句均长 | 短句% | 对话比% | 五感类数 | 比喻 | 副词 | emoji | 高频重复数 |\n'
                '|------|------|---------|-------|-------|--------|---------|------|------|-------|-----------|\n')
        with open(STYLE_LOG, 'a', encoding='utf-8') as f:
            f.write(f"| {time.strftime('%m/%d %H:%M')} | {os.path.basename(a.file) if a.file else 'inline'} | "
                    f"{m['chars']} | {m['sent_mean']} | {m['short_ratio']} | {m['dialog_ratio']} | "
                    f"{m['sense_kinds']} | {m['simile']} | {m['adv']} | {m['emoji']} | {len(m['top_rep'])} |\n")
        print(f'\n已追加到 {STYLE_LOG}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
