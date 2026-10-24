#!/usr/bin/env python
"""在所有（或指定）Hermes profile 上设置同一个配置键：改前备份、改后读回验证。

为什么需要它：`HERMES_PROFILE=<name> hermes config set ...` **无效**（会静默写到默认
config.yaml），唯一可靠姿势是给每条命令单独设 `HERMES_HOME` 指向该 profile 目录。
本脚本把「逐 profile 设 HERMES_HOME → 备份 → config set → yaml 读回校验」封装好。

用法：
    # 所有 profile 统一把视觉辅助切到 DeepSeek
    python sync_profile_config.py --key auxiliary.vision.provider --value deepseek
    python sync_profile_config.py --key auxiliary.vision.model --value deepseek-v4-flash

    # fallback_chain 这类 JSON 值要加 --force（否则 CLI 报「未识别的键」）
    python sync_profile_config.py --key auxiliary.vision.fallback_chain \
        --value '[{"provider":"custom:ZhipuGLM","model":"glm-4.6v-flash"}]' --force

    # 只改指定档案 / 先看会改什么
    python sync_profile_config.py --key model.default --value deepseek-v4-flash --profiles athena,eos
    python sync_profile_config.py --key auxiliary.vision.model --value x --dry-run

退出码：全部成功 0；任一 profile 失败 1。
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time

ROOT = os.environ.get("HERMES_HOME") or os.path.expanduser(r"~\AppData\Local\hermes")
ROOT = os.path.abspath(ROOT)


def native(p: str) -> str:
    """给 hermes（原生 Windows 程序）的路径必须是正斜杠原生路径。

    MSYS 风格 `/c/Users/...` 会被拼成 `\\c\\Users\\...`，Hermes 读不到配置。
    """
    return os.path.abspath(p).replace("\\", "/")


def profile_dirs(only: list[str] | None) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if not only or "default" in only:
        out.append(("default", ROOT))
    pdir = os.path.join(ROOT, "profiles")
    if os.path.isdir(pdir):
        for name in sorted(os.listdir(pdir)):
            d = os.path.join(pdir, name)
            if not os.path.isfile(os.path.join(d, "config.yaml")):
                continue
            if only and name not in only:
                continue
            out.append((name, d))
    return out


def read_key(cfg_path: str, dotted: str):
    import yaml

    node = yaml.safe_load(open(cfg_path, encoding="utf-8")) or {}
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return "<missing>"
        node = node[part]
    return node


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True, help="点分配置键，如 auxiliary.vision.provider")
    ap.add_argument("--value", required=True, help="值；JSON 用引号包住")
    ap.add_argument("--profiles", default=None, help="逗号分隔的档案名（默认全部）")
    ap.add_argument("--force", action="store_true", help="传 --force 给 config set（自定义键）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    only = [s.strip() for s in args.profiles.split(",") if s.strip()] if args.profiles else None
    targets = profile_dirs(only)
    if not targets:
        print("没有匹配到任何 profile（检查 --profiles 拼写）")
        return 1

    ts = time.strftime("%Y%m%d_%H%M%S")
    failures: list[str] = []

    for name, d in targets:
        cfg = os.path.join(d, "config.yaml")
        before = read_key(cfg, args.key)
        if args.dry_run:
            print(f"[dry] {name:14s} {args.key}: {before!r} -> {args.value!r}")
            continue

        bak = f"{cfg}.bak-sync-{ts}"
        shutil.copy2(cfg, bak)

        cmd = ["hermes", "config", "set", args.key, args.value]
        if args.force:
            cmd.append("--force")
        env = dict(os.environ, HERMES_HOME=native(d))
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=180)
        wrote_to = ""
        for line in (proc.stdout or "").splitlines():
            if "config.yaml" in line:
                wrote_to = line
        after = read_key(cfg, args.key)

        ok = proc.returncode == 0 and str(after) != "<missing>"
        # 防呆：确认真的写进了本 profile，而不是默认 config.yaml
        if ok and os.path.normcase(os.path.abspath(cfg)) not in os.path.normcase(wrote_to.replace("/", os.sep)):
            ok = False
        status = "✅" if ok else "❌"
        print(f"{status} {name:14s} {before!r} -> {after!r}")
        if not ok:
            failures.append(name)
            print(f"   stdout: {(proc.stdout or '').strip()[:300]}")
            print(f"   stderr: {(proc.stderr or '').strip()[:300]}")

    if failures:
        print(f"\n失败: {', '.join(failures)}（备份仍在 config.yaml.bak-sync-{ts}）")
        return 1
    print(f"\n完成 {len(targets)} 个 profile；备份后缀 .bak-sync-{ts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
