# 多档案（profiles）人格编辑 & Profile 路由

会话实战沉淀（2026-07，artemis/athena/hebe 三档案色情设定扩展 + profile 路由调试）。

## 档案布局

```bash
$HERMES_HOME/profiles/<name>/
├── SOUL.md        # 该档案的人格定义（权威）
├── config.yaml    # 该档案的配置，agent.system_prompt 是 SOUL.md 的镜像
├── skills/        # 独立技能
├── memories/      # 独立记忆
└── sessions/      # 独立会话
```

## 双同步规则（与主档案不同）

主档案改人格要三处同步（SOUL.md + config.yaml personalities + memory）；**子档案只需两处**：

1. 写 `profiles/<name>/SOUL.md`（完整版人格）
2. 同步该档案自己的 `config.yaml` 的 `agent.system_prompt` = SOUL.md 全文

```python
import yaml
from pathlib import Path

for name in ['artemis', 'athena', 'hebe']:
    prof = Path(rf"C:\Users\80704\AppData\Local\hermes\profiles\{name}")
    soul = (prof / "SOUL.md").read_text(encoding='utf-8')
    cfg_path = prof / "config.yaml"
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    cfg['agent']['system_prompt'] = soul   # 镜像 SOUL.md
    with open(cfg_path, 'w', encoding='utf-8') as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
```

⚠️ 子档案的 config.yaml **没有** `agent.personalities` 键（那是主档案的 /personality 库）——子档案靠 `agent.system_prompt` 直接注入。验证时读回 config.yaml 确认 system_prompt 与 SOUL.md 一致。

生效条件：修改后新开会话/重启该档案的会话才生效，运行中的会话不热加载。

## gateway.profile_routes 陷阱 ⚠️

Hermes 支持把特定聊天路由到指定档案（`gateway/profile_routing.py`，按 platform+chat_id+thread_id 层级匹配）：

```yaml
gateway:
  profile_routes:
    - name: weixin-artemis
      platform: weixin
      chat_id: "o9cq...@im.wechat"
      profile: artemis
```

匹配优先级（最具体优先）：platform+chat_id+thread_id > platform+chat_id > platform+guild_id > 默认档案。

**关键陷阱**：路由是 chat_id 固定绑定——一个聊天只能路由到一个档案。给**当前正在对话的聊天**配上路由会把当前人格整个切走（用户瞬间"换人"）。配置前先确认 chat_id 对应哪个聊天；想保留当前对话就不要给它配路由。

**同一聊天内切换不同女仆的正确方式**：不是 profile 路由，而是主档案内的 `/personality <name>`（切换 agent.personalities 预设人格）。profile 路由只适合"不同聊天/群对应不同档案"的场景。

## 未成年档案安全边界 ⚠️

给角色档案添加成人设定前，先确认角色年龄设定。若档案明确为未成年（如 eos 设定 16 岁），**一律不加**任何色情设定，明确拒绝并说明原因，保持纯爱向。这是不可协商的红线。
