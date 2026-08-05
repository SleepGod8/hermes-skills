---
name: fastapi-chatbot
description: "FastAPI 多轮对话机器人实现：多模型切换、持久化存储、流式输出"
version: 1.1.0
tags: [fastapi, chatbot, streaming, multi-provider]
category: software-development
---

# FastAPI 多轮对话机器人

快速搭建支持多模型切换、持久化存储、流式输出的聊天机器人项目。

## 何时使用

- 需要快速搭建一个聊天机器人 Demo
- 需要演示多轮对话、流式输出、持久化存储
- 需要集成多个 AI 模型（ASLNet、GLM、DeepSeek、Ollama 等）
- 可删除不需要的功能（如RAG流程图）

## 项目结构

```
multi_turn_bot/
├── main.py              # FastAPI 后端（统一 API 入口）
├── .env                 # API Key 配置
├── sessions.json        # 会话数据（自动创建）
├── static/
│   └── index.html       # 聊天界面（原生 HTML/CSS/JS）
└── README.md
```

## 核心功能

1. **多轮对话** - 维护会话历史，支持连续对话
2. **多模型切换** - 通过 `model` 参数选择不同提供商/模型（格式：`provider-model`）
3. **持久化存储** - JSON 文件保存会话，页面刷新不丢失
4. **流式输出** - SSE (Server-Sent Events) 实时推送
5. **健康检查** - `/health` 端点检查服务状态

## 快速启动

```bash
# 启动服务
cd D:/PythonProject/multi_turn_bot
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8090)"

# 访问
# 聊天界面: http://localhost:8090
```

## API 端点

### POST /chat - 普通对话
```json
{
  "message": "你好",
  "session_id": "可选，自动生成",
  "model": "aslnet-gpt-5.5"
}
```

### POST /chat/stream - 流式对话
同上，返回 SSE 格式流式响应。

### GET /providers - 获取可用提供商列表
```json
{
  "aslnet": {"name": "ASLNet", "models": ["gpt-5.5", "gpt-5.6-sol"]},
  "glm": {"name": "GLM", "models": ["glm-4-flash", "glm-4-plus"]},
  "deepseek": {"name": "DeepSeek", "models": ["deepseek-4v-flash", "deepseek-4v-pro"]},
  "ollama": {"name": "Ollama本地", "models": ["qwen2.5:7b", "glm-4.7-flash"]}
}
```

### GET /sessions - 获取所有会话
```json
{"sessions": {...}, "count": 1}
```

### DELETE /session/{id} - 删除会话

## 提供商配置

```python
PROVIDERS = {
    "aslnet": {
        "api_key": os.getenv("ASLNET_API_KEY", ""),
        "base_url": "https://api.aslnet.cloud/v1",
        "models": ["gpt-5.5", "gpt-5.6-sol"]
    },
    "glm": {
        "api_key": os.getenv("GLM_API_KEY", ""),
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": ["glm-4-flash", "glm-4-plus"]
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "models": ["deepseek-4v-flash", "deepseek-4v-pro"]
    },
    "ollama": {
        "api_key": "ollama",
        "base_url": "http://localhost:11434/v1",
        "models": ["qwen2.5:7b", "glm-4.7-flash"]
    }
}
```

模型选择格式：`{provider}-{model}`，如 `aslnet-gpt-5.5`

## 验证测试

```python
import requests

base = 'http://localhost:8090'

# 健康检查
r = requests.get(f'{base}/health')

# 普通对话
r = requests.post(f'{base}/chat', json={'message': '你好', 'model': 'aslnet-gpt-5.5'})

# 流式输出
r = requests.post(f'{base}/chat/stream', json={'message': '你好', 'model': 'aslnet-gpt-5.5'})
for line in r.iter_lines():
    if line.startswith(b'data: '):
        print(line[6:].decode())
```

## 关键实现模式

### 会话持久化
```python
import json
import os

SESSIONS_FILE = "sessions.json"
sessions = {}

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_sessions():
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)
```

### 流式输出
```python
from fastapi.responses import StreamingResponse

async def chat_stream(request: ChatRequest):
    async def generate():
        for token in call_stream_api(...):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"}
    )
```

## 已验证可用的 API（2026-08-04）

### ASLNet API (✅ 可用)
```python
PROVIDERS = {
    "aslnet": {
        "api_key": os.getenv("ASLNET_API_KEY", ""),
        "base_url": "https://api.aslnet.cloud/v1",
        "models": ["gpt-5.5", "gpt-5.6-sol"]
    }
}
```

### GLM API (✅ 可用)
```python
PROVIDERS = {
    "glm": {
        "api_key": os.getenv("GLM_API_KEY", ""),
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": ["glm-4-flash", "glm-4-plus"]
    }
}
```

### DeepSeek API (⚠️ 需验证)
- Hermes 的 `.env` 中的 DeepSeek Key 可能是无效的
- 建议使用已验证的 ASLNet 或 GLM 作为默认模型

## Pitfalls

- **端口冲突**：默认 8090，如被占用可修改
- **API Key 格式**：ASLNet 使用 `sk-` 开头，不要复制错误
- **流式响应头**：必须设置 `X-Accel-Buffering: no` 防止 Nginx 缓冲
- **会话 ID 生成**：使用 `datetime.now().strftime("%Y%m%d%H%M%S")` + 随机字符串避免冲突
- **前端错误处理**：检查 `response.ok`，否则 API 错误时显示 `undefined`
- **DeepSeek API Key**：Hermes 的 `.env` 中的 DeepSeek Key 可能是无效的，需验证
- **默认模型选择**：优先使用已验证可用的 API（ASLNet/GPT-5.5 或 GLM），而非 DeepSeek
- **删除功能**：可以删除 RAG 流程图等不需要的功能，保持项目简洁

## 相关参考

- 完整实现见 `references/fastapi-chatbot-implementation.md`
- 验证脚本见 `scripts/verify_chatbot.py`
