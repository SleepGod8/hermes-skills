#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""body_ratio.py — 肉戏配比检查器（设定 vs 身体）

用法：
    python scripts/body_ratio.py --file 本轮正文.txt
    python scripts/body_ratio.py --self-test

回答一个问题：这一场到底是「在写色情」，还是「在讲设定」。

输出四项：
  R1 身体段占比   —— 以身体/动作/感官为主的段落 ÷ 总段落（目标 ≥50%）
  R2 机制段占比   —— 以机制/系统/数据/验收为主的段落 ÷ 总段落（目标 ≤25%）
  R3 最长无身体断档—— 连续多少字没有任何身体描写（目标 ≤250 字）
  R4 台词占比     —— 引号内字数 ÷ 正文（参考值，不计入好坏）
退出码：0 合格｜1 WARN｜2 FAIL
"""
import argparse
import re
import sys

BODY = [
    "皮肤", "指尖", "手指", "指节", "掌心", "舌", "唇", "齿", "喉咙", "喉间", "颈",
    "耳", "后颈", "肩", "背脊", "脊背", "腰", "小腹", "腹", "膝盖", "腿", "大腿",
    "胸口", "胸", "乳", "臀", "后庭", "里面", "内壁", "深处", "内腔", "湿", "水",
    "热", "烫", "凉", "冷", "汗", "抖", "颤", "抽搐", "绷", "软", "喘", "呼吸",
    "呻吟", "气音", "声音", "眼", "泪", "红", "潮", "抽送", "抽插", "插", "顶",
    "撞", "吞", "含", "舔", "咬", "蹭", "摩", "收紧", "松开", "绞", "贴", "按",
    "抓", "握", "抬", "塌", "伏", "跪", "骑", "夹", "射", "精", "高潮", "快感",
    "酥", "麻", "酸", "胀", "满", "空",
]

MECH = [
    "槽", "义体", "义手", "义腿", "目镜", "机械脊椎", "姿态锁定", "锁定架", "承重钩",
    "步态记忆", "灌注件", "深度传感器", "传感器", "收缩环", "扩张器", "活塞", "炮机",
    "锁精环", "许可锁", "许可卡", "服从卡", "联网卡", "服务器", "芯片", "主槽", "副槽",
    "跳蛋", "项圈", "口球", "贞操带", "装备槽", "词条", "磨合度", "储液腔",
    "三重锁", "理智值", "计时器", "本子", "数据档案", "共感链", "声音烙印",
    "自走腰", "读心波形", "波形", "温阶", "压力图谱", "求欢模式",
    "数据", "参数", "模型", "演算", "验收", "自检", "校准", "流程", "权限", "许可",
    "报数", "记录", "建档", "档位", "面板", "装备", "系统", "模块", "负载", "接口",
    "装机", "升级", "重启", "导出", "毫米", "毫秒", "百分比", "容量",
]


# ── 具体性行为 / 器官 / 体液词（衡量「到底有没有在写色情」）───────────
EXPLICIT = [
    "插入", "抽送", "抽插", "进出", "顶", "撞", "贯穿", "贯穿", "吞吐", "含着", "含住",
    "舔", "吮", "吸", "舐", "骑乘", "骑", "跨", "磨蹭", "摩擦", "套弄", "撸", "拨弄",
    "揉", "捏", "掐", "咬", "射", "内射", "喷射", "高潮", "痉挛", "抽搐", "浪", "呻吟",
    "小穴", "穴", "内壁", "子宫", "男根", "性器", "冠头", "精", "淫水", "潮吹",
    "乳尖", "乳头", "胸乳", "后庭", "菊", "唇舌", "舌吻", "咽", "深喉", "口交",
    "后入", "下半身", "湿透", "水声", "啪", "摩挲", "探入", "塞进", "撑开",
]


# ── 动作动词（衡量「有没有在动」）─────────────────────────────
ACTION = [
    "抓","按住","按","推开","推","拉","扯","撕","抬","压","顶","撞","抽","送进","送出",
    "退","进","翻","转","跪","趴","伏","骑","抱","搂","吻","咬","舔","含","吞","吐",
    "握","揉","捏","掐","拨","勾","缠","磨","蹭","抖","颤","弓","塌","仰","垂","拍",
    "晃","摆","扭","夹","松开","收紧","探进","塞","撑","抵","俯","起","落","坐","挺",
]


# ── 娇喘音节（从台词里剥离，单独计量 R8）─────────────────────
MOAN = ["嗯","啊","呜","唔","哦","哈","呼","齁","唉","呀","噫","嘶","咿","嗷","哼","嘤","呃"]

NUMRE = [r"\d+(?:\.\d+)?\s*%", r"\d+(?:\.\d+)?\s*(?:ml|毫升)", r"\d+\.\d+", r"第\s*\d+\s*轮", r"Lv\.?\d"]


def paras(text):
    return [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]


def dialogue_len(text):
    return sum(len(m) for m in re.findall(r"「[^」]*」", text))


def body_density(s):
    return sum(s.count(w) for w in BODY)


def mech_density(s):
    return sum(s.count(w) for w in MECH) + sum(len(re.findall(p, s)) for p in NUMRE)


def analyze(text):
    body_chars = len(re.sub(r"\s+", "", text))
    ps = paras(text)
    body_p = mech_p = neut_p = 0
    for p in ps:
        # 台词先剥离，避免 Athena 的数据台词拉高机制判定
        core = re.sub(r"「[^」]*」", "", p)
        # 机制词先剔除，再数身体词（防止「腰槽」「小腹感」这类子串误算成身体）
        masked = core
        for w in MECH:
            masked = masked.replace(w, "")
        for pat in NUMRE:
            masked = re.sub(pat, "", masked)
        b, m = body_density(masked), mech_density(core)
        if b > m:
            body_p += 1
        elif m > b:
            mech_p += 1
        else:
            neut_p += 1
    total = max(len(ps), 1)

    # 最长无身体断档（按段落累计字数）
    gap = longest = 0
    for p in ps:
        core = re.sub(r"「[^」]*」", "", p)
        for w in MECH:
            core = core.replace(w, "")
        if body_density(core) == 0:
            gap += len(re.sub(r"\s+", "", p))
            longest = max(longest, gap)
        else:
            gap = 0

    dlg_text_all = "".join(re.findall(r"「([^」]*)」", text))
    dlg_chars = len(dlg_text_all)
    moan_hits = sum(dlg_text_all.count(w) for w in MOAN)
    semantic_dlg = max(dlg_chars - moan_hits, 0)
    dlg_ratio_full = semantic_dlg / max(body_chars, 1)
    moan_density = moan_hits / (body_chars / 1000.0)
    act_hits = sum(text.count(w) for w in ACTION)
    act_density = act_hits / (body_chars / 1000.0)

    body_only = re.sub(r"「[^」]*」", "", text)
    exp_hits = sum(body_only.count(w) for w in EXPLICIT)
    mech_hits = mech_density(body_only)
    exp_density = exp_hits / (body_chars / 1000.0)
    ratio_mech_exp = mech_hits / exp_hits if exp_hits else 99.0

    return dict(
        moan_density=moan_density,
        moan_hits=moan_hits,
        dlg_ratio_full=dlg_ratio_full,
        act_density=act_density,
        exp_density=exp_density,
        exp_hits=exp_hits,
        mech_hits=mech_hits,
        mech_per_exp=ratio_mech_exp,
        chars=body_chars,
        paras=total,
        body_p=body_p,
        mech_p=mech_p,
        neut_p=neut_p,
        body_ratio=body_p / total,
        mech_ratio=mech_p / total,
        gap=longest,
        dlg_ratio=dialogue_len(text) / max(body_chars, 1),
    )


def report(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    r = analyze(text)
    print("=" * 58)
    print(f"肉戏配比检查 · {path}")
    print(f"正文 {r['chars']} 字 ｜ 段落 {r['paras']} ｜ 台词占比 {r['dlg_ratio']*100:.1f}%")
    print("=" * 58)
    print(f"  段落分类：身体 {r['body_p']} ／ 机制 {r['mech_p']} ／ 中性 {r['neut_p']}")
    code = 0
    tag = "✅ PASS" if r["body_ratio"] >= 0.50 else ("⚠️  WARN" if r["body_ratio"] >= 0.35 else "❌ FAIL")
    if tag != "✅ PASS":
        code = 1 if tag.startswith("⚠️") else 2
    print(f"{tag} [R1 身体段占比] {r['body_ratio']*100:.0f}%（目标 ≥50%）")
    tag2 = "✅ PASS" if r["mech_ratio"] <= 0.25 else ("⚠️  WARN" if r["mech_ratio"] <= 0.40 else "❌ FAIL")
    if tag2 != "✅ PASS":
        code = max(code, 1 if tag2.startswith("⚠️") else 2)
    print(f"{tag2} [R2 机制段占比] {r['mech_ratio']*100:.0f}%（目标 ≤25%）")
    tag3 = "✅ PASS" if r["gap"] <= 250 else ("⚠️  WARN" if r["gap"] <= 400 else "❌ FAIL")
    if tag3 != "✅ PASS":
        code = max(code, 1 if tag3.startswith("⚠️") else 2)
    print(f"{tag3} [R3 最长无身体断档] {r['gap']} 字（目标 ≤250）")
    tag4 = "✅ PASS" if r["exp_density"] >= 8 else ("⚠️  WARN" if r["exp_density"] >= 4 else "❌ FAIL")
    if tag4 != "✅ PASS":
        code = max(code, 1 if tag4.startswith("⚠️") else 2)
    print(f"{tag4} [R4 露骨度（性行为/器官/体液词）] {r['exp_density']:.1f} 每千字（目标 ≥8，命中 {r['exp_hits']} 次）")
    tag5 = "✅ PASS" if r["mech_per_exp"] <= 1.5 else ("⚠️  WARN" if r["mech_per_exp"] <= 2.5 else "❌ FAIL")
    if tag5 != "✅ PASS":
        code = max(code, 1 if tag5.startswith("⚠️") else 2)
    print(f"{tag5} [R5 机制代偿比] 机制词 {r['mech_hits']} : 性行为词 {r['exp_hits']} = {r['mech_per_exp']:.2f}（目标 ≤1.5，越高＝越像说明书）")
    dr = r["dlg_ratio_full"]
    if 0.15 <= dr <= 0.28:
        tag6 = "✅ PASS"
    elif 0.10 <= dr < 0.15 or 0.28 < dr <= 0.35:
        tag6 = "⚠️  WARN"
    else:
        tag6 = "❌ FAIL"
    if tag6 != "✅ PASS":
        code = max(code, 1 if tag6.startswith("⚠️") else 2)
    hint = "太低＝旁白替她说" if dr < 0.15 else ("太高＝变成聊天" if dr > 0.28 else "甜区 18–25%")
    print(f"{tag6} [R6 台词占比（只算有语义的话）] {dr*100:.1f}%（甜区 15–28%；{hint}）")
    md = r["moan_density"]
    if 10 <= md <= 25:
        tag8 = "✅ PASS"
    elif 6 <= md < 10 or 25 < md <= 35:
        tag8 = "⚠️  WARN"
    else:
        tag8 = "❌ FAIL"
    if tag8 != "✅ PASS":
        code = max(code, 1 if tag8.startswith("⚠️") else 0)
    print(f"{tag8} [R8 娇喘密度] {md:.1f} 个音节/千字（档② 目标 10–25，命中 {r['moan_hits']} 次）")
    tag7 = "✅ PASS" if r["act_density"] >= 25 else ("⚠️  WARN" if r["act_density"] >= 15 else "❌ FAIL")
    if tag7 != "✅ PASS":
        code = max(code, 1 if tag7.startswith("⚠️") else 2)
    print(f"{tag7} [R7 动作密度] {r['act_density']:.1f} 个/千字（目标 ≥25，动作不能靠形容词撑）")
    if code:
        print("\n修法（详见 references/写作技法/focus-control.md §肉戏配比 / §对话与动作配比）：")
        print("  • 机制只做「入场券」：开场 2–3 句交代完，之后回落到身体")
        print("  • 删清单：不列「十二件一起运转」，只写与焦点相关的那一件")
        print("  • 每段先给触感，再给解释；能换体感就不写设定名")
    else:
        print("\n结论：肉戏为主，设定为辅 ✅")
    return code


SELF = """手掌落在她小腹上。波形开始的那一瞬，她整个人静了。
里面收紧，松开，收紧——跟着那只手的搏动走。她的呼吸被改成同一个拍子。
「……三点四秒一拍。」她低声说，「人家，从里面数到了。」
"""


def self_test():
    r = analyze(SELF)
    print("self-test:", r["chars"], "字 ｜ 身体段", r["body_p"], "机制段", r["mech_p"], "｜ 断档", r["gap"])
    assert r["body_ratio"] >= 0.5, r
    print("✅ self-test ran")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        sys.exit(0)
    if not a.file:
        ap.print_help()
        sys.exit(0)
    sys.exit(report(a.file))
