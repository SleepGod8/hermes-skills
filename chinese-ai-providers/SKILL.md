---
name: chinese-ai-providers
description: "Chinese AI API providers (Zhipu/GLM, DashScope, DeepSeek) — pricing, censorship, function calling, and Hermes integration patterns."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [AI-Provider, Zhipu, GLM, DashScope, DeepSeek, Vision]
---

# Chinese AI API Providers

Reference for evaluating and integrating Chinese AI API providers. Covers ZhipuAI (GLM), DashScope (Qwen), and DeepSeek.

## Provider Overview

| Provider | Base URL | Strengths |
|----------|----------|-----------|
| ZhipuAI | `https://open.bigmodel.cn/api/paas/v4/` | Free vision, function calling, 1M context |
| DashScope | `https://dashscope.aliyuncs.com/compatible-mode/v1` | Stable vision |
| DeepSeek | `https://api.deepseek.com` | Strong coding, main chat |

## Adding to Hermes

```bash
hermes config set custom_providers '[{"name":"ZhipuGLM","base_url":"https://open.bigmodel.cn/api/paas/v4/","api_key":"YOUR_KEY"}]'
```

### Vision model configuration

```bash
hermes config set auxiliary.vision.provider "custom:ZhipuGLM"
hermes config set auxiliary.vision.model "glm-4.6v-flash"
```

### ⚠️ Pitfall: Custom providers as main chat model

Custom providers work as `auxiliary.vision` but may fail with auth errors when set as `model.provider`. Keep DeepSeek as primary chat.

## Zhipu GLM Free Models

| Model | Type | Price | Notes |
|-------|------|-------|-------|
| `glm-4.6v-flash` | Vision | Free | 128K context, function calling, near-zero censorship |
| `glm-4-flash` | Text | Free | Outputs to `content` |
| `glm-4.7-flash` | Reasoning | Free | Output in `reasoning_content` — Hermes incompatible |

### GLM-4.6V-Flash Key Features
- 128K context tokens
- Native function calling (tools API)
- Optional thinking mode
- Near-zero censorship on adult/NSFW content

### Censorship Comparison
| Model | Adult Content |
|-------|--------------|
| `qwen-vl-max` | Rejects |
| `qwen-vl-plus` | Partial |
| `glm-4.6v-flash` | No filter |

## Function Calling

GLM-4.6V-Flash supports OpenAI-compatible tools API with `tool_choice: "auto"`. Works with both text and vision inputs.

## OpenCode China Install

```bash
npm i -g opencode-ai@latest --registry=https://registry.npmmirror.com
```

Desktop installs to: `%LOCALAPPDATA%\Programs\@opencode-aidesktop\`

Model format: `--model ProviderID/model-name`

See also: `references/glm-pricing.md`
