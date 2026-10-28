#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""focus_check.py — 色情正文「焦点密度」检查器（减法校验）

用法：
    python scripts/focus_check.py --file 本轮正文.txt
    python scripts/focus_check.py --file a.txt --dial 2      # 2=清简档（更严格）
    python scripts/focus_check.py --self-test

检查三件事（对应 references/写作技法/focus-control.md）：
  F1 器具/机制名词密度（每千字命中数）——太高＝在报设备清单，不是在写情色
  F2 单段并列峰值（一段里堆了几件器具/机制）——太高＝段落没有焦距
  F3 报数/数据密度（百分号/毫升/第N轮/小数点）——太高＝说明书腔
退出码：0 全部合格｜1 有 WARN｜2 有 FAIL
"""
import argparse
import re
import sys

# ── 器具 / 机制 / 系统名词库（命中即算「元素」）──────────────────
GEAR = [
    "槽", "义体", "义手", "义腿", "目镜", "机械脊椎", "姿态锁定", "锁定架", "承重钩",
    "步态记忆", "灌注件", "深度传感器", "传感器", "收缩环", "扩张器", "活塞", "炮机",
    "锁精环", "许可锁", "许可卡", "服从卡", "联网卡", "服务器", "芯片", "主槽", "副槽",
    "跳蛋", "项圈", "口球", "贞操带", "装备槽", "词条", "磨合度", "储液腔",
    "三重锁", "理智值", "计时器", "本子", "数据档案", "共感链", "声音烙印",
    "自走腰", "读心波形", "波形", "温阶", "压力图谱", "求欢模式", "遮蔽", "冻结",
    "回溯", "催眠", "印记", "淫纹", "开发度", "EXP", "Lv.",
]
# ── 报数 / 数据痕迹 ────────────────────────────────────────────
NUM = [
    r"\d+(?:\.\d+)?\s*%", r"\d+(?:\.\d+)?\s*(?:ml|毫升)", r"第\s*\d+\s*轮",
    r"\d+\s*/\s*\d+", r"\d+\.\d+", r"百分之[一二三四五六七八九十百零]+",
]
# ── 并列连接（一段里出现太多次＝铺排）────────────────────────
PARALLEL = ["＋", "、", "｜", "同时", "一边", "又……又"]


def paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]


def analyze(text, dial=3):
    body = re.sub(r"\s+", "", text)
    n = max(len(body), 1)
    k = n / 1000.0  # 千字单位

    hits = sum(body.count(w) for w in GEAR)
    density = hits / k

    num_hits = sum(len(re.findall(p, text)) for p in NUM)
    num_density = num_hits / k

    paras = paragraphs(text)
    peak, peak_txt = 0, ""
    for p in paras:
        c = sum(p.count(w) for w in GEAR)
        if c > peak:
            peak, peak_txt = c, p[:40]

    par_hits = sum(len(re.findall(p, text)) for p in PARALLEL)
    par_density = par_hits / k

    # 阈值随档位变化：1=极简 2=清简 3=常规 4=重载
    th = {
        1: dict(d=18, p=3, nu=3, par=6),
        2: dict(d=25, p=4, nu=4, par=8),
        3: dict(d=40, p=6, nu=6, par=12),
        4: dict(d=60, p=9, nu=9, par=18),
    }[dial]

    res = []
    res.append(("F1 器具/机制密度",
                density,
                th["d"],
                f"命中 {hits} 次 / {n} 字 = {density:.1f} 每千字（阈值 {th['d']}）"))
    res.append(("F2 单段并列峰值",
                peak,
                th["p"],
                f"最挤的一段堆了 {peak} 件：{peak_txt}…（阈值 {th['p']}）"))
    res.append(("F3 报数/数据密度",
                num_density,
                th["nu"],
                f"命中 {num_hits} 次 = {num_density:.1f} 每千字（阈值 {th['nu']}）"))
    res.append(("F4 并列连词密度",
                par_density,
                th["par"],
                f"命中 {par_hits} 次 = {par_density:.1f} 每千字（阈值 {th['par']}）"))
    return n, res


def report(path, dial):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    n, res = analyze(text, dial)
    print("=" * 58)
    print(f"焦点密度检查 · {path}")
    print(f"档位 {'Ⅰ极简 Ⅱ清简 Ⅲ常规 Ⅳ重载'.split()[dial-1]} ｜ 正文 {n} 字")
    print("=" * 58)
    worst = 0
    for name, val, lim, desc in res:
        if val > lim * 1.6:
            tag, code = "❌ FAIL", 2
        elif val > lim:
            tag, code = "⚠️  WARN", 1
        else:
            tag, code = "✅ PASS", 0
        worst = max(worst, code)
        print(f"{tag} [{name}] {desc}")
    if worst:
        print("\n减法建议（详见 references/写作技法/focus-control.md）：")
        print("  • 每场只留 1 件主器具 + 1 个主机制，其余改名或删掉")
        print("  • 机制名 → 换成体感（不写「收缩环 Lv.2」，写「里面收紧了一下」）")
        print("  • 报数每千字 ≤3 次；其余改成身体反应")
        print("  • 一段一个焦点，段中并列细节 ≤2")
    else:
        print("\n结论：焦点干净 ✅")
    return worst


SELF_TEST_TEXT = """改造间。托盘上只摆着一件东西。
「Lv.3。」她念完铭牌，把裙子挽到腰上，躺下。
手掌落在她小腹上。波形开始的那一瞬，她整个人静了。
里面收紧，松开，收紧——跟着那只手的搏动走。她的呼吸被改成同一个拍子。
「……三点四秒一拍。」她低声说，「人家，从里面数到了。」
"""


def self_test():
    n, res = analyze(SELF_TEST_TEXT, 2)
    print("self-test text:", n, "字")
    for name, val, lim, desc in res:
        print(("PASS" if val <= lim else "WARN"), name, desc)
    print("✅ self-test ran")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--dial", type=int, default=3, choices=[1, 2, 3, 4])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        sys.exit(0)
    if not a.file:
        ap.print_help()
        sys.exit(0)
    sys.exit(report(a.file, a.dial))
