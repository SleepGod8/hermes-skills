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

## 相关

- provider 细节（auxiliary vision 等）：hermes-custom-providers（user-owned）
- 本地模型下载/GGUF 模板坑：ollama-hf-gguf-import（user-owned）
- 酒馆 RP：sillytavern-character-cards
