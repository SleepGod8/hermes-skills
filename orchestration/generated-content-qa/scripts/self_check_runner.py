#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自检编排骨架 · generated-content-qa

把「生成类产物交付前的机械质检」编排成一条命令：
  1) 先跑各工具的自证（--self-test），证明工具本身有效（工具无效则后续结论一律不可信）
  2) 再跑各检查脚本
  3) 汇总 PASS/FAIL，任一 FAIL 就退出码 1
  4) 把本轮指标追加到趋势档（可选）

用法：
    python self_check_runner.py --artifact <产物文件路径> [--log <趋势档路径>]

复制到目标项目后，只需改下面的 TOOLS 表（命令里用 {artifact} 占位）。
依赖：仅标准库；各检查脚本自行负责退出码（0=PASS）。
"""
import argparse
import datetime as dt
import os
import subprocess
import sys

# ============================ CONFIG ============================
# 每项：名字 → (自证命令 or None, 检查命令模板)
# 命令用 {artifact} 占位；cwd 默认为本脚本所在项目根（见 ROOT_HINT）
TOOLS = [
    ("check_reply",    "python scripts/check_reply.py --self-test",   "python scripts/check_reply.py --file {artifact}"),
    ("style_report",   "python scripts/style_report.py --self-test",  "python scripts/style_report.py --file {artifact}"),
]
ROOT_HINT = os.environ.get("SELF_CHECK_ROOT", os.getcwd())   # 项目根目录
TIMEOUT = 180
# ================================================================


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT_HINT, shell=True, capture_output=True, text=True, timeout=TIMEOUT)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", required=True, help="本轮产物文件")
    ap.add_argument("--log", default=None, help="趋势档：追加一行时间与结论")
    ap.add_argument("--skip-self-test", action="store_true", help="跳过工具自证（仅在自证刚刚通过时使用）")
    a = ap.parse_args()

    if not os.path.isfile(a.artifact):
        print(f"❌ 产物不存在: {a.artifact}")
        return 2

    # ---- 1) 工具自证：不通过就别看产物结论 ----
    if not a.skip_self_test:
        print("=" * 60)
        print("① 工具自证（证明检查器本身有效）")
        bad_tools = []
        for name, selftest, _ in TOOLS:
            if not selftest:
                print(f"  · {name}: 无自证命令（跳过）")
                continue
            rc, out = run(selftest)
            ok = (rc == 0)
            print(f"  {'✅' if ok else '❌'} {name}: self-test rc={rc}")
            if not ok:
                bad_tools.append(name)
                print("     " + out.strip().splitlines()[-1] if out.strip() else "")
        if bad_tools:
            print(f"\n⚠️  工具自证未通过：{bad_tools}")
            print("   → 先修工具或样本，再谈产物是否达标（口径不可信时结论无意义）")

    # ---- 2) 产物检查 ----
    print("=" * 60)
    print(f"② 产物检查：{a.artifact}")
    fails = []
    for name, _, cmd_t in TOOLS:
        cmd = cmd_t.format(artifact=a.artifact)
        try:
            rc, out = run(cmd)
        except subprocess.TimeoutExpired:
            rc, out = 124, f"timeout after {TIMEOUT}s"
        verdict = "PASS" if rc == 0 else "FAIL"
        print(f"\n--- {name} → {verdict} (rc={rc}) ---")
        tail = [l for l in out.strip().splitlines() if l.strip()][-12:]
        print("\n".join("   " + l for l in tail))
        if rc != 0:
            fails.append(name)

    # ---- 3) 汇总 ----
    print("=" * 60)
    print("结论：", "PASS（可交付）" if not fails else f"FAIL → {fails}（先判断是产物错还是工具口径错）")

    # ---- 4) 趋势档 ----
    if a.log:
        os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
        new = not os.path.isfile(a.log)
        with open(a.log, "a", encoding="utf-8") as f:
            if new:
                f.write("| 时间 | 产物 | 结论 |\n|------|------|------|\n")
            f.write(f"| {dt.datetime.now():%Y-%m-%d %H:%M} | {os.path.basename(a.artifact)} | "
                    f"{'PASS' if not fails else 'FAIL:' + ','.join(fails)} |\n")
        print(f"已追加趋势档：{a.log}")

    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
