# DashScope (阿里云百炼) in Hermes

## OpenAI-Compatible Endpoint

```
https://dashscope.aliyuncs.com/compatible-mode/v1
```

## Configuration

```yaml
custom_providers:
  - name: DashScope
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key: ${DASHSCOPE_API_KEY}
```

```bash
hermes config set auxiliary.vision.provider "custom:DashScope"
hermes config set auxiliary.vision.model "qwen-vl-max"
```

## Available Vision Models

| Model | Notes |
|-------|-------|
| `qwen-vl-max` | Best quality, but enforces content restrictions |
| `qwen-vl-plus` | Balanced |
| `qwen2.5-vl-72b-instruct` | Newer architecture |

## Known Issues

- **Content filtering**: DashScope models refuse to describe adult/NSFW content, returning a compliance refusal message.
- **API key**: Set `DASHSCOPE_API_KEY` in `~/.hermes/.env`. Get it from [阿里云百炼控制台](https://bailian.console.aliyun.com/).
- **Free tier**: DashScope has free monthly quotas. Check your balance at the console.

## Test Verification

After configuring, test with any image:
```
vision_analyze with any local image
```

A successful response (even a content-filter refusal) confirms the endpoint is connected. A "model not found" or 404 error means the config isn't taking effect.
