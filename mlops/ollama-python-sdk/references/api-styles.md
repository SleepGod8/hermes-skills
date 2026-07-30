# Ollama 三种 API 风格对比

## 1. Python SDK（推荐）

**安装：** `pip install ollama`

```python
from ollama import chat

res = chat(
    model="glm-4.7-flash",
    messages=[{"role": "user", "content": "你好"}]
)
print(res.message.content)
```

**优点：** 最简洁，自动处理 JSON 序列化/反序列化
**缺点：** 需要额外安装 `ollama` 包

---

## 2. 直接 HTTP 调用（`/api/generate`）

**不需要额外安装库**（用标准库 `requests` 或 `urllib`）

```python
import requests
import json

url = "http://localhost:11434/api/generate"
payload = {
    "model": "glm-4.7-flash",
    "prompt": "你好",
    "stream": False
}

resp = requests.post(url, json=payload)
result = resp.json()
print(result["response"])
```

**优点：** 零依赖，`requests` 已是常用库
**缺点：** 手动处理 JSON，stream 需要自己解析

---

## 3. OpenAI 兼容 API（`/v1/chat/completions`）

**安装：** `pip install openai`

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Ollama 不验证 api_key，但需要传一个
)

resp = client.chat.completions.create(
    model="glm-4.7-flash",
    messages=[{"role": "user", "content": "你好"}]
)
print(resp.choices[0].message.content)
```

**优点：** 与 OpenAI SDK 完全兼容，方便切换 provider
**缺点：** 需要装 `openai` 包，且 Ollama 的 OpenAI 兼容层功能有限

---

## 对比总结

| 特性 | Python SDK | HTTP 原生 | OpenAI 兼容 |
|------|-----------|----------|------------|
| 安装包 | `ollama` | 无（用 `requests`） | `openai` |
| 代码行数 | 最少 | 中等 | 中等 |
| 自动 JSON 处理 | ✅ | ❌ | ✅ |
| 流式支持 | 简单 | 需手动解析 | 简单 |
| 跨 provider 切换 | ❌（仅 Ollama） | ❌ | ✅ |
| 类型提示 | `ChatResponse` | 无 | `ChatCompletion` |
