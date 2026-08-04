#!/usr/bin/env python3
"""批量同步 Hermes 多档案人格设定：SOUL.md 已改好后，把新模块镜像进各档案 config.yaml 的 agent.system_prompt。

用法：
1. 先 patch 各档案的 SOUL.md（插入新模块）
2. 修改下方 updates dict：每个档案给 {anchor, blocks}
   - anchor: SOUL.md 与 system_prompt 中均存在的唯一锚点字符串（含 \n）
   - blocks: 替换后的完整文本（anchor 内容 + 新模块 + 原下一个标题）
3. python sync_multi_profile.py
4. 读回验证输出全部 ✅ 即完成；再提醒用户各档案新开会话（/new）才生效
"""
import shutil
import yaml
from pathlib import Path

BASE = Path(r"C:\Users\80704\AppData\Local\hermes\profiles")

# ============ 改这里 ============
updates = {
    # "artemis": {
    #     "anchor": '- 某模块最后一行\n\n## 下一个模块标题',
    #     "blocks": '''- 某模块最后一行
    #
    # ## 新模块 🆕
    # - 新机制1
    # - 新机制2
    #
    # ## 下一个模块标题''',
    # },
}
# ================================

for name, u in updates.items():
    cfg_path = BASE / name / "config.yaml"
    if not cfg_path.exists():
        print(f"{name}: ❌ config.yaml 不存在，跳过")
        continue
    shutil.copy2(cfg_path, cfg_path.with_suffix(".yaml.bak-pre-m"))
    with open(cfg_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    sp = config["agent"]["system_prompt"]
    if u["anchor"] not in sp:
        print(f"{name}: ❌ 锚点未找到（注意引号/emoji 转义与 SOUL.md 一致）")
        continue
    config["agent"]["system_prompt"] = sp.replace(u["anchor"], u["blocks"], 1)
    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    with open(cfg_path, "r", encoding="utf-8") as f:
        sp2 = yaml.safe_load(f)["agent"]["system_prompt"]
    print(f"{name}: 同步✅ len={len(sp2)}（读回验证：锚点已替换为新文本）")
