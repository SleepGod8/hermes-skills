# ZhipuAI GLM Model Pricing

Source: https://open.bigmodel.cn/pricing (as of 2026-07)

## Free Models

| Model | Type | Input | Output | Context |
|-------|------|-------|--------|---------|
| `glm-4.7-flash` | Text | Free | Free | 200K |
| `glm-4.6v-flash` | Vision | Free | Free | 128K |
| `glm-4-flash` | Text | Free | Free | Standard |

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

## API Key Format

API keys from Zhipu open platform are in format: `{id}.{secret}`
Example: `b21361b1145b44c5845e11b5d2b712a5.kvRYd296FLanqGrp`

## Notes
- Flash models are Zhipu's "便宜/免费" line
- `glm-4.7-flash` is a reasoning model — answer goes in `reasoning_content` not `content`
- `glm-4-flash` outputs normally to `content` — works with Hermes
- All models support OpenAI-compatible `/v4/chat/completions` endpoint
