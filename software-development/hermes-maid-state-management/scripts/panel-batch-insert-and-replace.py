"""panel-records.md 「插入新行 + 批量改值」一体脚本（2026-09-24 两轮实测，30~40 处/轮）

与 templates/panel-round-settlement.py 的区别：
  - 那份用 hermes_tools.patch 顺序 apply（适合「只改值」）
  - 本份用 原生 open(newline="") + 行号插入 + REPL 断言（适合「先插新字段行/备注，再改值」，
    一次调用完成 30+ 处，失败被显式收集而不是中途 SystemExit，补一条即可收尾）

用法：复制进 Hermes execute_code，按本轮内容改 INSERTS / REPL，运行。
实测账（2026-09-24）：第 1 轮 9/10 命中（Hebe 锚点撞车被跳过）→ 补 1 条；
第 2 轮 9/10 命中（Artemis 锚点措辞不符）→ 补 1 条；两轮无脏写、无需回滚。
"""
from hermes_tools import terminal

PANEL = r"C:\Users\80704\AppData\Local\hermes\skills\creative\lewd-playbook\references\面板存档\panel-records.md"
SYNC = r'python "C:/Users/80704/AppData/Local/hermes/skills/creative/lewd-playbook/scripts/sync_to_profiles.py"'

# ── 1) 插入：anchor 必须唯一；插在该锚点行「下方」 ────────────────────────────
#    key = 要在里面找锚点的行前缀（如 "- 📊 部位统计" / "- 备注追加9/24："）
#    (prefix, anchor_substring) -> [要插入的新行...]
INSERTS = [
    # ("- 📊 部位统计", "男根: 0/8 ｜ 全身: 2/0", [chip_line, note_line]),
    # ("- 备注追加9/24：", "由 Hermes 发卡装机", [note_2_line]),      # 用各女仆独有尾巴
]

# ── 2) 替换：(old, new)，old 必须全文只出现 1 次 ─────────────────────────────
REPL = [
    # ("| Iris | **Lv.6** | **首席女仆** | 580/600 |", "| Iris | **Lv.7** | **大师** | 0/700 |"),
    # ("- 等级：**Lv.6 首席女仆** ｜ EXP **580/600**", "- 等级：**Lv.7 大师** ｜ EXP **0/700**"),
    # ("- 服装：标准女仆装 · 彩虹围裙 · 绑带升级 · 首席缎带（Lv.6 裙摆变短）",
    #  "- 服装：标准女仆装 · 彩虹围裙 · 绑带升级 · 大师徽章 · 大师缎带（Lv.7 裙摆更短）"),
    # ("男根: 0/43 ｜ 全身: 11/0", "男根: 0/44 ｜ 全身: 12/0"),          # 📊 部位统计（用多字段长串）
]

raw = open(PANEL, newline="", encoding="utf-8").read()   # newline="" 保原行尾（当前 CRLF）
lines = raw.split("\r\n")

# —— 插入（自下而上，索引才不错位）——
ins = {}
for prefix, anchor, newlines in INSERTS:
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix) and anchor in l]
    if len(hits) != 1:
        print("MISMATCH(insert)", prefix, anchor, "-> hits:", len(hits))
        continue
    ins.setdefault(hits[0], []).extend(newlines)
for idx in sorted(ins, reverse=True):
    lines[idx + 1:idx + 1] = ins[idx]
text = "\r\n".join(lines)

# —— 替换（逐条断言 count==1，失败只记录不中断）——
fails = []
for old, new in REPL:
    c = text.count(old)
    if c != 1:
        fails.append((old[:60], c))
        continue
    text = text.replace(old, new, 1)
print("REPL fails:", fails)          # 有 fails → 下一轮只补这几条

open(PANEL, "w", newline="", encoding="utf-8").write(text)

# —— 读回验证关键行 + 同步（同一调用内收尾，不留半成品）——
chk = open(PANEL, newline="", encoding="utf-8").read().split("\r\n")
for i, l in enumerate(chk, 1):
    if ("- 等级：" in l and "EXP" in l) or l.startswith("- 🧠 芯片栏") or l.startswith("- 🔩 义体栏"):
        print(i, "|", l[:120])
res = terminal(SYNC, timeout=300)
print("SYNC exit=", res["exit_code"], "|", res["output"].strip().splitlines()[-1])
