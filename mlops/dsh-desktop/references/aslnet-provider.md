# ASLNet 端点实测与接入（2026-08）

用户常用的 OpenAI 兼容中转服务。实测通过。

## 端点与模型

- Base URL: `https://api.aslnet.cloud/v1`（OpenAI 兼容，`/chat/completions`）
- 已实测模型：`gpt-5.5`（两把 key 均 200 OK）
- 模型池（用户 Hermes 配置）：
  - `ASLNET_PLUS_KEY`（aslnet-plus）= gpt-plus 0.1x 池，含 gpt-5.4/5.5/5.6/5.6-sol/5.6-terra，≈0.98元/M，**最便宜**
  - `ASLNET_API_KEY`（aslnet）= gpt-纯 pro 0.18x 池
- key 存放在 `C:\Users\80704\AppData\Local\hermes\.env`（ASLNET_PLUS_KEY / ASLNET_API_KEY）

## 验证代码

```python
import re, json, urllib.request
with open(r"C:\Users\80704\AppData\Local\hermes\.env", encoding="utf-8") as f:
    content = f.read()
key = re.search(r"^ASLNET_PLUS_KEY=(.+)$", content, re.M).group(1).strip()

body = json.dumps({"model": "gpt-5.5",
                   "messages": [{"role": "user", "content": "hi"}],
                   "max_tokens": 8}).encode()
req = urllib.request.Request("https://api.aslnet.cloud/v1/chat/completions", data=body,
    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=25) as resp:
    print(json.loads(resp.read().decode())["model"])  # gpt-5.5
```

## 接入 DSH Desktop

推荐设置页（不动系统环境变量）：设置 → ClawBot/IM 桥接 → 第三方模型端点（OpenAI 兼容）
- baseURL: `https://api.aslnet.cloud/v1`
- API Key: ASLNET_PLUS_KEY 那把（gpt-plus 池最便宜）
- 模型名: `gpt-5.5`

## 接入 Hermes（已有）

Hermes config.yaml 的 custom provider：
```yaml
providers:
  aslnet-plus:
    base_url: https://api.aslnet.cloud/v1
    model: gpt-5.5
    key_env: ASLNET_PLUS_KEY
  aslnet:
    key_env: ASLNET_API_KEY
```
