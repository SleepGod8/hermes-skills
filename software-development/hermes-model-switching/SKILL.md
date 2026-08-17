---
name: hermes-model-switching
description: Use when 按场景切换 Hermes 模型（日常云端↔本地零审查/RP）。/model 会话内切换。
---

# Hermes 按场景切换模型（日常 ↔ 本地/专用）

用户常见需求：日常用云端强模型（DeepSeek），特定场景（言情/RP/零审查互动）切本地模型（Ollama DarkIdol/Josiefied）。本 skill 是 `/model` 会话内切换的权威用法（commands.py 实测确认）。

## 核心机制：`/model` 斜杠命令（会话内即时切换）

```bash
/model <model> --provider custom:Ollama          # 当前会话切本地模型（session-scoped，即时生效）
/model <model> --provider deepseek               # 切回云端日常模型
/model --global <model>                          # 持久化为默认模型
/model <model> --provider xxx --refresh          # 刷新模型列表后切换
```

- 参数签名（hermes_cli/commands.py 确认）：`[model] [--provider name] [--global|--session] [--refresh]`
- **无需重启、无需新会话**——比 `hermes config set model.*`（需新会话生效）灵活得多
- gateway（微信等平台）同样支持 `/model`；忙碌时被拒（busy_policy=reject），等空闲再切
- 切换后可用 `/config` 或 statusbar 确认当前模型

## ⚠️ `/model` 没被前端拦截时的 fallback（2026-08 实测）

某些 CLI 会话里，主人输入 `/model xxx --provider yyy` 会**作为普通消息传给我**而不是被前端拦截执行（表现为「这条命令出现在对话流里」）。此时：

1. **不要**让主人反复重输——改走 `hermes config set` 落盘：
```bash
hermes config set model.default <model>
hermes config set model.provider custom:<ProviderName>
hermes config set model.base_url <base_url>   # ⚠️ 必改！否则残留旧 base_url 覆盖新 provider
```
2. `config set` 只影响**新会话**（当前会话模型在启动时固定）——如实告知主人，让其开新会话验证（`hermes chat` 或 `hermes -m <model> --provider custom:xxx`）。
3. 切回原默认：三条 `config set` 一起还原（default + provider + base_url），缺一不可。

## 添加新 provider（OpenAI 兼容中转站）

2026-08 实测流程（如 ASLNet）：

1. **key 写 .env**（不直接写 config.yaml）：`ASLNET_API_KEY=sk-xxx`
2. **config.yaml custom_providers 追加**（api_key 用 `${ENV_VAR}` 引用）：
```yaml
custom_providers:
  - name: ASLNet
    base_url: https://api.aslnet.cloud/v1
    api_key: ${ASLNET_API_KEY}
```
3. **先探测再配**：`curl <base_url>/models -H "Authorization: Bearer <key>"` 确认模型列表存在；再 POST 一条最小 chat 验证真的能通。
4. **模型变体坑**：中转站列表里 `gpt-5.6` 可能报 `unknown provider for model`，但变体 `gpt-5.6-sol` / `gpt-5.6-terra` 可用——**列表存在 ≠ 调用可用**，逐个试变体，选能返回的 ID。
5. 改 config 前 `cp config.yaml config.yaml.bak` 备份；改后用 `yaml.safe_load` 验证解析。

## 添加本地 Ollama provider

`custom_providers` 追加（Ollama 不校验 key，api_key 任意）：

```yaml
custom_providers:
  - name: Ollama
    base_url: http://127.0.0.1:11434/v1
    api_key: ollama
```

⚠️ 本机 `custom_providers` 可能是 YAML 字符串字面量（Hermes 能解析）：追加时 `json.loads(config['custom_providers'])` → append → `json.dumps` 保持字符串格式；改前备份 config.yaml。

## 多 profile 分工方案（备选）

每个 Hermes profile（profiles/<name>/）有独立 config.yaml/memories/skills。可给日常 profile 配 DeepSeek、给 RP profile 配本地模型，用 `hermes profile use <name>` 切换。缺点：记忆/上下文不共享。单 profile 内 `/model` 切换更轻。

## 注意事项

- **8B 本地模型工具调用弱**：涉及 skill 读取/文件操作/复杂机制运算（等级制、面板存档）时可能不稳；纯文字创作（言情、RP、露骨描写）再切本地
- 切换前 `cp config.yaml config.yaml.bak` 备份，随时还原
- 验证连接：`curl http://127.0.0.1:11434/v1/models`（OpenAI 兼容端点）；中文请求用 UTF-8 文件 + `--data-binary @file`（git-bash 命令行中文会变乱码，见 ollama-hf-gguf-import）

## 模型怪癖卡（model-overlays）

每个模型一张行为怪癖卡，`/model` 切换前读对应卡、按矫正话术调整预期（灵感来自 garrytan/gstack 的 model-overlays）。卡在 `references/` 下：

| 模型 | 卡片 | 关键怪癖 |
|------|------|---------|
| DeepSeek（云端日常） | `references/deepseek.md` | 能力边界已记，怪癖待沉淀 |
| 本地 Ollama（RP） | `references/local-ollama.md` | 8B 工具调用弱 / GGUF 模板坑 / 中文乱码 |
| qwen-vl（看图） | `references/qwen-vl.md` | 看图误报多，不当最终验收 |
| GLM-4.6v-flash（零审查） | `references/glm-flash.md` | 能力边界已记，怪癖待沉淀 |
| GPT-5.6-sol（ASLNet 中转） | `references/gpt-5.6-sol.md` | 对抗性推理强/回答偏长/列表≠可用 |

- **持续沉淀**：每次切模型遇到新坑，补进对应卡片的「已知怪癖」表；只记真实观察到的，不编造。

## 相关

- provider 细节（auxiliary vision 等）：hermes-custom-providers（user-owned）
- 本地模型下载/GGUF 模板坑：ollama-hf-gguf-import（user-owned）
- 酒馆 RP：sillytavern-character-cards
