# Dual-Mode Provider Switching (Worked Example)

## Scenario

User wants two modes with simple trigger phrases:
- **聊天模式**: custom:deepseek + deepseek-v4-flash (日常对话，经济高效)
- **编码模式**: custom:aslnet + gpt-5.5 (代码生成，推理能力强)

## Trigger Phrases

| 用户说 | 动作 |
|--------|------|
| "切编码" / "切编码模式" | 切换到 ASLNet + gpt-5.5，告知需 `/reset` |
| "切聊天" / "切聊天模式" | 切换回 DeepSeek + deepseek-v4-flash，告知需 `/reset` |

## Exact Commands

```bash
# === 编码模式 ===
hermes config set model.provider custom:aslnet
hermes config set model.default gpt-5.5

# === 聊天模式 ===
hermes config set model.provider custom:deepseek
hermes config set model.default deepseek-v4-flash
```

## Important: base_url leakage

After switching provider, always check `hermes config` output. If `model.base_url` still
points to the OLD provider's endpoint, the new session will fail with 404. Fix:

```bash
# Clear base_url for custom providers (they use own base_url from custom_providers list)
hermes config set model.base_url ""
```

The `model.base_url` in the `model:` section is a SESSION-level override that can
persist from a previous provider. Custom providers (`custom:<name>`) use the base_url
from their entry in `custom_providers` list, but if `model.base_url` is set, Hermes
uses that override instead — causing the mismatch.

## After switching

1. Run `hermes config` to verify provider + model + base_url all look correct
2. Tell the user to type `/reset` in the chat to start a new session with the new model
3. Confirm the switch succeeded after the new session starts

## Memory

Save to persistent memory:
> 模式切换: 说「切编码」→ aslnet+gpt-5.5, 说「切聊天」→ custom:deepseek+deepseek-v4-flash。需 hermes config set + /reset 生效。
