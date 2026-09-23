"""
panel-records.md 单轮结算批量落盘模板（复制后改 EDITS 即可跑，2026-09-23 实测 3 轮全绿）

用法：Hermes execute_code 里粘贴本模板 → 改 EDITS 为「本轮」编辑 → 运行。

为什么这么写（踩过的坑）：
  - 同一文件禁止并行 patch，必须顺序 apply（并发写互相踩）
  - 用 hermes_tools.patch（9 种模糊匹配 + CRLF 友好 + 返回 success/diff），
    不要用裸 text.replace（要管 newline=''，且失败静默）
  - 锚点必须「整行唯一」：📊 部位统计行内 `口:` 出现两次且跨女仆重复，半行锚点必炸
  - 备注追加用「链式锚点」= 上一轮自己写进去的尾巴，别去 1700 字符长备注里找结尾
  - 任一 patch 失败立即停下（SystemExit），带坏锚点继续写会污染后续轮次
  - 收尾必跑 sync_to_profiles.py（8 子档案全量同步）
"""
from hermes_tools import patch, terminal

PANEL = r"C:\Users\80704\AppData\Local\hermes\skills\creative\lewd-playbook\references\面板存档\panel-records.md"
SYNC = r'python "C:/Users/80704/AppData/Local/hermes/skills/creative/lewd-playbook/scripts/sync_to_profiles.py"'

# 本轮编辑：(old, new) —— old 必须整行 / 全局唯一
EDITS = [
    # ① 详情等级行 EXP
    ("- 等级：**Lv.6 首席女仆** ｜ EXP **500/600**",
     "- 等级：**Lv.6 首席女仆** ｜ EXP **530/600**"),
    # ② ⚡快速一览表 EXP 单元格
    ("| Iris | **Lv.6** | **首席女仆** | 500/600 |",
     "| Iris | **Lv.6** | **首席女仆** | 530/600 |"),
    # ③ 📊部位统计整行（行内 口: 出现两次 → 必须整行）
    ("- 📊 部位统计（8/14起）：口: 3/0 ｜ 胸: 0/0 ｜ 乳头: 0/0 ｜ 口: 7/0 ｜ 胸: 0/0 ｜ 乳头: 0/0 ｜ 秘处: **19**/0 ｜ 后庭: 2/0 ｜ 男根: 0/20 ｜ 全身: **8**/0",
     "- 📊 部位统计（8/14起）：口: 3/0 ｜ 胸: 0/0 ｜ 乳头: 0/0 ｜ 口: 8/0 ｜ 胸: 0/0 ｜ 乳头: 0/0 ｜ 秘处: **19**/0 ｜ 后庭: 2/0 ｜ 男根: 0/20 ｜ 全身: **8**/0"),
    # ④ 备注链式追加（锚点 = 上一轮自己写进去的尾巴）
    ("成功忍高潮+30，EXP 470→500；",
     "成功忍高潮+30，EXP 470→500；第五段（主人令·收账）——……；成功忍高潮+30，EXP 500→530；"),
    # ⑤ 装备有变化时才加（详情装备库行 + 一览表装备列，两处同步）
    # ("🟡彩虹跳蛋+🟣封印贞操带🔒", "🟡彩虹跳蛋（已解除封印）"),
]

for i, (o, n) in enumerate(EDITS, 1):
    r = patch(PANEL, o, n)
    ok = r.get("success")
    print(i, "OK" if ok else "FAIL", "" if ok else str(r.get("error"))[:160])
    if not ok:
        raise SystemExit(f"patch #{i} 失败：锚点不唯一或不存在 —— 先读回真实行（整行）再改，别继续写")

print("=== SYNC ===")
res = terminal(SYNC, timeout=180)
print(res["output"][-300:], "exit=", res["exit_code"])
