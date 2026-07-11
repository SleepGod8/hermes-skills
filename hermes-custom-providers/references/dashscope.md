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
hermes config set auxiliary.vision.model "qwen-vl-plus"
```

## Available Vision Models

| Model | Notes |
|-------|-------|
| `qwen-vl-plus` | **Recommended.** Good quality, NO content filtering on anime/illustration — describes NSFW content normally. |
| `qwen-vl-max` | Best quality, but enforces strict content restrictions — refuses adult/NSFW content. |
| `qwen2.5-vl-72b-instruct` | Newer architecture, content policy untested. |

## Known Issues

- **Model-dependent content filtering**: `qwen-vl-max` refuses to describe adult/NSFW content, returning a compliance refusal. **Use `qwen-vl-plus` instead** — it has no such restrictions on anime/illustration content and describes everything normally. If you hit a refusal, switch models.
- **API key**: Set `DASHSCOPE_API_KEY` in `~/.hermes/.env`. Get it from [阿里云百炼控制台](https://bailian.console.aliyun.com/).
- **Free tier**: DashScope has free monthly quotas. Check your balance at the console.
- **Config overwrite pitfall**: `hermes config set custom_providers "[...]"` overwrites ALL existing entries AND serializes as a broken JSON string. Never use it to add entries — always edit config.yaml directly or use the Python repair script below.

## Repair Script (fix broken custom_providers)

If `hermes config set` corrupted `custom_providers` into a JSON string, run this:

```python
import yaml
config_path = r'C:\Users\<user>\AppData\Local\hermes\config.yaml'
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
# Fix or add custom_providers as a proper YAML list
config['custom_providers'] = [
    {'name': 'ExistingProvider', 'base_url': '...', 'api_key': '${ENV_VAR}'},
    {'name': 'NewProvider', 'base_url': '...', 'api_key': '${ENV_VAR}'},
]
with open(config_path, 'w', encoding='utf-8') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

## Test Verification

After configuring, test with any image via `vision_analyze`:
- A successful description (including NSFW anime art — `qwen-vl-plus` handles this) confirms everything works.
- A "model not found" or 404 error: check that `custom_providers` has the DashScope entry and `auxiliary.vision.provider` is set to `custom:DashScope` (NOT just `dashscope`).
- A content refusal ("不符合中国法规"): you're using `qwen-vl-max` — switch to `qwen-vl-plus`.
