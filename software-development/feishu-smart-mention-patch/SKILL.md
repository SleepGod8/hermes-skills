---
name: feishu-smart-mention-patch
description: "飞书 adapter require_mention smart 模式补丁 —— 无@时女仆自主接话，有@时只响应被@的。含完整代码 diff、配置、验证与升级重打步骤。Use when 飞书群聊 @ 一个全员回复 / 想实现自主接话+定向@响应共存 / 升级 Hermes 后需要重打飞书补丁。"
version: 1.0.0
tags: [feishu, adapter, patch, require_mention, smart, multi-agent, group-chat]
---

# 飞书 adapter require_mention smart 模式补丁

> 版本：v1.0 | 2026-08-09 | 本地 patch（非官方功能）
> 文件：`$HERMES_HOME/hermes-agent/plugins/platforms/feishu/adapter.py`

## 触发条件

- 飞书群聊中 @ 一个 agent，其他 agent 也跟着回复（require_mention: false 的副作用）
- 想要「无 @ 时自主接话 + 有 @ 时只响应被 @ 的」混合模式
- 升级 Hermes 后 adapter 被覆盖，需要重打本补丁

## 背景

Hermes 飞书 adapter 的 `_admit` 准入逻辑原本只有**二元开关**：

```python
require_mention = is_group and self._require_mention_for(chat_id)
...
if require_mention and not self._mentions_self(message):
    return "group_policy_rejected"   # 没@自己 → 拒绝
```

- `require_mention: true` → 必须 @ 自己才响应（但没 @ 时全员沉默）
- `require_mention: false` → 全员都响应（@ 谁谁都回，造成抢答）

**需求**：无 @ 放行（自主接话），有 @ 只回被 @ 的 → 需要第三态 `"smart"`。

## 补丁内容（4 处修改 + 1 处新增）

### 1. 导入 Union

```python
# 原
from typing import Any, Dict, List, Literal, Optional, Sequence
# 改
from typing import Any, Dict, List, Literal, Optional, Sequence, Union
```

### 2. 新增 `_normalize_require_mention()`（放在 `_to_boolean` 定义之后）

```python
def _normalize_require_mention(value: Any) -> Union[bool, str]:
    """Normalize require_mention config to True / False / "smart".

    - True / "true" / 1  -> True
    - False / "false" / 0 -> False
    - "smart" / "smart_mode" -> "smart" (reply only to @mentions; if no one
      is mentioned, allow autonomous group chat)
    """
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "1", "yes"}:
            return True
        if v in {"false", "0", "no"}:
            return False
        if v in {"smart", "smart_mode"}:
            return "smart"
        return True
    return bool(value)
```

### 3. 类型定义支持 str

```python
# FeishuGroupRule
require_mention: Optional[bool] = None  # None = inherit global
# 改
require_mention: Optional[Union[bool, str]] = None  # None = inherit global; "smart" = reply only to @, else autonomous

# FeishuAdapterSettings
require_mention: bool = True
# 改
require_mention: Union[bool, str] = True  # True | False | "smart"
```

### 4. 配置解析改用 `_normalize_require_mention`

```python
# 4a: per-chat group_rules 解析
per_chat_require_mention: Optional[bool] = None
if "require_mention" in rule_cfg:
    per_chat_require_mention = _to_boolean(rule_cfg.get("require_mention"))
# 改
per_chat_require_mention: Optional[Union[bool, str]] = None
if "require_mention" in rule_cfg:
    per_chat_require_mention = _normalize_require_mention(rule_cfg.get("require_mention"))

# 4b: 全局 require_mention 解析
require_mention=_to_boolean(
    extra.get("require_mention", os.getenv("FEISHU_REQUIRE_MENTION", "true"))
),
# 改
require_mention=_normalize_require_mention(
    extra.get("require_mention", os.getenv("FEISHU_REQUIRE_MENTION", "true"))
),
```

### 5. `_admit` 核心准入逻辑（smart 分支）

```python
# _require_mention_for 返回类型
def _require_mention_for(self, chat_id: str) -> bool:
# 改
def _require_mention_for(self, chat_id: str) -> Union[bool, str]:

# _admit 中：
if require_mention and not self._mentions_self(message):
    return "group_policy_rejected"
# 改
if require_mention == "smart":
    # Smart mode: if anyone is @mentioned, only respond when *we* are
    # mentioned. If no one is mentioned, allow autonomous group chat.
    raw_content = getattr(message, "content", "") or ""
    mentions = getattr(message, "mentions", None) or []
    has_any_mention = bool(mentions) or "@_all" in raw_content
    if has_any_mention and not self._mentions_self(message):
        return "group_policy_rejected"
elif require_mention and not self._mentions_self(message):
    return "group_policy_rejected"
```

## 配置方法

所有接飞书的档案（default + 各女仆 profile）的 `config.yaml`：

```yaml
platforms:
  feishu:
    enabled: true
    extra:
      require_mention: smart   # true | false | smart
```

或 `.env`：`FEISHU_REQUIRE_MENTION=smart`（注意：env 会经 `_normalize_require_mention` 解析，同样支持 smart）

## 生效行为

| 场景 | 行为 |
|------|------|
| 群里发消息不 @ 任何人 | 女仆们自主接话（群聊协议 P0-P4） |
| @ 某女仆 | 只有被 @ 的响应 |
| @ 全体（@_all） | 全员响应 |
| 女仆互 @ 接力 | 被 @ 的才回 |
| is_bot 消息 | smart 下 `not "smart"` 为 False，不会提前拒 bot；走 smart 判断 |

## 验证步骤

```bash
# 1. 语法检查
python -c "import py_compile; py_compile.compile(r'$HERMES_HOME/hermes-agent/plugins/platforms/feishu/adapter.py', doraise=True)"

# 2. 配置所有档案
# config.yaml platforms.feishu.extra.require_mention: smart

# 3. 重启所有飞书 gateway（kill 后 Desktop 自动重启）
# 确认日志出现 ✓ feishu connected

# 4. 飞书群实测
#   不 @ 发消息 → 有女仆自主接话
#   @ 单个 → 只有那个回
```

## 升级重打补丁

Hermes 升级会覆盖 `plugins/platforms/feishu/adapter.py`。升级后：
1. `grep "smart" "$HERMES_HOME/hermes-agent/plugins/platforms/feishu/adapter.py"` 检查补丁是否还在
2. 若丢失，按上面 5 步重新打补丁
3. 配置通常不受影响（config.yaml 不被覆盖），但验证 require_mention: smart 仍被解析

## 相关

- 群聊自主沟通协议：`group-chat-autonomous-chat` skill
- 多档案抢 token / 飞书接入：`hermes-gateway-watchdog` skill（含 FEISHU_GROUP_POLICY=open 等）
- adapter 官方路径：`plugins/platforms/feishu/adapter.py`（升级会被覆盖，注意备份）
