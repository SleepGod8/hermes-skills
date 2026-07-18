# ZhipuGLM (智谱AI) Provider Reference

## Configuration

Base URL: `https://open.bigmodel.cn/api/paas/v4/`

Added to Hermes via `hermes config set custom_providers`:
```json
{"name":"ZhipuGLM","base_url":"https://open.bigmodel.cn/api/paas/v4/","api_key":"<key>"}
```

## Model Summary

| Model | Type | Price | Notes |
|-------|------|-------|-------|
| **glm-4.6v-flash** | Vision | 🆓 FREE | Zero censorship, 128K context, native Function Call, thinking mode toggleable |
| **glm-4-flash** | Text | 🆓 FREE | Normal content output, works as chat model |
| **glm-4.7-flash** | Text (Reasoning) | 🆓 FREE | Answer in `reasoning_content`, `content` is empty — NOT compatible with Hermes |
| glm-4.7 | Text | Paid | Good mid-range |
| glm-5.2 | Text | Paid (¥8/28 per M) | Latest flagship, 1M context |
| glm-5-turbo | Text | Paid | Fast variant |

## Critical Quirk: glm-4.7-flash

This is a **reasoning model**. Its `content` field is always empty; the actual response is in `reasoning_content`. Hermes reads `content` only, so using glm-4.7-flash as main model results in silent empty responses. **Use glm-4-flash instead** for free chat.

## Vision Model: glm-4.6v-flash

- **Zero censorship** — freely describes NSFW/adult content in detail
- Native Function Call support — vision-to-action pipeline
- 128K context window
- Thinking mode can be toggled (reasoning_content available)
- Configured as `auxiliary.vision.provider: custom:ZhipuGLM`, `auxiliary.vision.model: glm-4.6v-flash`

## Important: Main Model Limitation

`custom:ZhipuGLM` **cannot be used as the main chat model** (`model.provider`). Hermes returns "Provider authentication failed" when used this way. It only works as `auxiliary.vision` provider or as a fallback for specific tools.
