# DashScope Vision Setup for Hermes (China-Accessible)

## Problem

Setting `auxiliary.vision.provider = dashscope` directly **does not work**. Hermes's vision resolution chain only includes: main provider → OpenRouter → Nous Portal → Anthropic → custom endpoint. DashScope is not in the chain, so it falls back to OpenRouter with the model name, resulting in a 404 error.

## Working Solution: Custom Provider

### Step 1: Add DashScope as a custom provider in `config.yaml`

```yaml
custom_providers:
  - name: DashScope
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key: ${DASHSCOPE_API_KEY}
```

The `DASHSCOPE_API_KEY` must be set in `.env`.

### Step 2: Configure vision to use the custom provider

```bash
hermes config set auxiliary.vision.provider "custom:DashScope"
hermes config set auxiliary.vision.model "qwen-vl-plus"
```

### Model Selection

| Model | Content Moderation | Recommendation |
|-------|-------------------|----------------|
| `qwen-vl-max` | Strict — rejects NSFW/adult content | ❌ Avoid for anime/art |
| `qwen-vl-plus` | Lenient — describes all images | ✅ Recommended |
| `qwen2.5-vl-72b-instruct` | Unknown | Untested |

### Why Not Google Gemini?

Google AI Studio (`aistudio.google.com`) is blocked in China. Getting an API key requires VPN. Even with a key, `generativelanguage.googleapis.com` is also blocked, requiring a proxy for API calls.

## Verification

After configuration, test with:
```bash
# In a Hermes session, send an image — vision_analyze should work
```

Or check with `hermes config show` — should show:
```
◆ Auxiliary Models (overrides)
  Vision        provider=custom:DashScope, model=qwen-vl-plus
```

## Notes

- DashScope OpenAI-compatible endpoint: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- This uses Alibaba's free tier (有免费额度)
- No VPN needed — direct access from China
- The custom provider approach works because Hermes's vision resolution chain includes custom endpoints at step 5
