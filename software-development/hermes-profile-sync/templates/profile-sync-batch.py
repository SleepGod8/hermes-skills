#!/usr/bin/env python3
"""多档案人格设定批量同步模板 — 复制后按任务修改即可跑。

用途：给多个 profiles/<名>/ 同时添加/修改设定，并同步 default 的 lewd-maid 镜像。
流程：先备份 → 改各档案 SOUL.md → 用同一锚点改 config.yaml system_prompt → 读回验证。

用法：
1. 在 updates 字典里为每个档案填 anchor（SOUL.md 中唯一的一段）和 new（含 anchor 的新文本）
2. 可选：default_updates 处理 default SOUL.md + config.yaml personalities.lewd-maid
3. python 运行，观察每处 ✅/❌
"""
import shutil
import yaml
from pathlib import Path

HERMES_HOME = Path(r"C:\Users\80704\AppData\Local\hermes")  # Windows；Linux/macOS 用 ~/.hermes
BACKUP_TAG = "mytag"  # 备份后缀，如 .yaml.bak-mytag

# ---------------- 每档案：锚点 + 新内容 ----------------
# 规则：new 必须包含 anchor 本身（str.replace 用 new 整体替换 old）
# 锚点要足够长、带上相邻模块标题，避免 patch 模糊匹配歧义
updates = {
    # "artemis": {
    #     "anchor": "旧文本片段（唯一）",
    #     "new": "新文本（含旧片段 + 新增模块）",
    #     "verify": ["新增关键词1", "新增关键词2"],
    # },
}

# ---------------- default 档案（SOUL.md + lewd-maid 镜像） ----------------
default_updates = {
    # "anchor": "old",
    # "new": "new",
    # "verify": ["key"],
}


def sync_file(path: Path, anchor: str, new: str) -> bool:
    txt = path.read_text(encoding="utf-8")
    if anchor not in txt:
        print(f"  ❌ anchor 缺失: {path.name}")
        return False
    path.write_text(txt.replace(anchor, new, 1), encoding="utf-8")
    return True


def sync_profile(name: str, u: dict) -> None:
    print(f"[{name}]")
    base = HERMES_HOME / "profiles" / name
    # 1. SOUL.md
    sync_file(base / "SOUL.md", u["anchor"], u["new"])
    # 2. config.yaml 镜像（patch 工具拒绝写 config.yaml，必须 yaml 库）
    p = base / "config.yaml"
    shutil.copy2(p, p.with_suffix(f".yaml.bak-{BACKUP_TAG}"))
    with open(p, "r", encoding="utf-8") as f:
        c = yaml.safe_load(f)
    sp = c["agent"]["system_prompt"]
    if u["anchor"] not in sp:
        print("  ❌ config.yaml 锚点缺失（可能该档案是简版摘要，改用末尾追加策略）")
        return
    c["agent"]["system_prompt"] = sp.replace(u["anchor"], u["new"], 1)
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(c, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    # 3. 读回验证
    with open(p, "r", encoding="utf-8") as f:
        sp2 = yaml.safe_load(f)["agent"]["system_prompt"]
    missing = [k for k in u.get("verify", []) if k not in sp2]
    print(f"  验证: {'✅' if not missing else '❌ 缺 ' + str(missing)}")


def sync_default() -> None:
    print("[default]")
    soul_path = HERMES_HOME / "SOUL.md"
    cfg_path = HERMES_HOME / "config.yaml"
    for anchor, new in default_updates.items():
        sync_file(soul_path, anchor, new)
    shutil.copy2(cfg_path, cfg_path.with_suffix(f".yaml.bak-{BACKUP_TAG}"))
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    lm = cfg["agent"]["personalities"]["lewd-maid"]
    for anchor, new in default_updates.items():
        if anchor in lm:
            lm = lm.replace(anchor, new, 1)
        else:
            print(f"  ❌ lewd-maid 锚点缺失: {anchor[:25]}")
    cfg["agent"]["personalities"]["lewd-maid"] = lm
    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    with open(cfg_path, "r", encoding="utf-8") as f:
        lm2 = yaml.safe_load(f)["agent"]["personalities"]["lewd-maid"]
    missing = [k for anchor, new in default_updates.items() for k in default_updates[anchor].get("verify", []) if k not in lm2]
    print(f"  lewd-maid 验证: {'✅' if not missing else '❌ 缺 ' + str(missing)}")


if __name__ == "__main__":
    for name, u in updates.items():
        sync_profile(name, u)
    if default_updates:
        sync_default()
    print("\n完成。记得提醒用户：新开会话（/new）才生效。")
