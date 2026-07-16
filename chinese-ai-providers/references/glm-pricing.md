# ZhipuAI GLM Model Pricing

Source: https://open.bigmodel.cn/pricing (as of 2026-07)

## Free Models 🆓

| Model | Type | Input | Output | Context | Notes |
|-------|------|-------|--------|---------|-------|
| `glm-4.6v-flash` | Vision | Free | Free | 128K | Native function call, near-zero censorship |
| `glm-4.7-flash` | Reasoning | Free | Free | 200K | Output in `reasoning_content` — Hermes incompatible |
| `glm-4-flash` | Text | Free | Free | Standard | Outputs to `content` — works with Hermes |

## Latest Flagship (Paid)

| Model | Input (¥/M tokens) | Output (¥/M tokens) | Context |
|-------|-------------------|---------------------|---------|
| `glm-5.2` | 8 | 28 | 1M |
| `glm-5.1` | 6-8 | 24-28 | Variable |
| `glm-5-turbo` | 5-7 | 22-26 | Variable |
| `glm-5` | 4-6 | 18-22 | Variable |
| `glm-4.7` | 2-4 | 8-16 | Variable |

## Cheap Options

| Model | Input (¥/M tokens) | Output (¥/M tokens) |
|-------|-------------------|---------------------|
| `glm-4.5-air` | 0.8 | 2-6 |
| `glm-4.7-flashx` | 0.5 | 3 |

## Model ID Gotchas

| User-facing name | API model ID (must use lowercase) |
|-----------------|----------------------------------|
| GLM-4.6V-Flash | `glm-4.6v-flash` |
| GLM-4V-Flash | `glm-4v-flash` (older) |

The `/v4/models` endpoint returns IDs in lowercase. Always use lowercase.

## Censorship Comparison

| Model | Adult/NSFW Content |
|-------|-------------------|
| `qwen-vl-max` | Rejects |
| `qwen-vl-plus` | Partial pass |
| `glm-4.6v-flash` | **No filter** — freely describes NSFW |

## API Key Format

API keys from Zhipu open platform: `{id}.{secret}`
Example: `b21361b1145b44c5845e11b5d2b712a5.kvRYd296FLanqGrp`

## Hermes Integration

### As vision model (works)
```bash
hermes config set auxiliary.vision.provider "custom:ZhipuGLM"
hermes config set auxiliary.vision.model "glm-4.6v-flash"
```

### As main chat model (FAILS)
```bash
# ⚠️ DO NOT — causes auth error
hermes config set model.provider "custom:ZhipuGLM"
```
Custom providers work as `auxiliary.vision` but fail with auth errors when set as `model.provider`.

## API Proxy / Middleman Pricing (ChatAnywhere, 2026-07)

| Model | Input (¥/K tokens) | Output (¥/K tokens) |
|------|-------------------|---------------------|
| deepseek-v4-flash | 0.0008 | 0.0016 |
| deepseek-v4-pro | 0.003 | 0.006 |
| deepseek-chat | 0.0012 | 0.0018 |
| deepseek-reasoner | 0.0024 | 0.0096 |
| qwen3.5-plus | 0.00056 (tiered) | 0.00336 |
| kimi-k2.7-code | 0.0052 | 0.0216 |
| glm-5.2 | 0.0064 | 0.0224 |
