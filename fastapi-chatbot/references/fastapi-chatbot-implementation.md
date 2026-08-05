# FastAPI 多轮对话机器人 - 完整实现

## 项目路径
`D:\PythonProject\multi_turn_bot\`

## 核心代码模式

### 1. 统一 API 调用层
```python
PROVIDERS = {
    "aslnet": {
        "api_key": os.getenv("ASLNET_API_KEY", ""),
        "base_url": "https://api.aslnet.cloud/v1",
        "models": ["gpt-5.5", "gpt-5.6-sol"]
    },
    "ollama": {
        "api_key": "ollama",
        "base_url": "http://localhost:11434/v1",
        "models": ["qwen2.5:7b", "glm-4.7-flash"]
    }
}

def get_client(provider: str):
    from openai import OpenAI
    config = PROVIDERS[provider]
    return OpenAI(api_key=config["api_key"], base_url=config["base_url"])
```

### 2. 模型选择格式
使用 `provider-model` 格式，如 `aslnet-gpt-5.5`，后端自动解析：
```python
if "-" in model:
    provider, model_name = model.split("-", 1)
else:
    provider = DEFAULT_PROVIDER
```

### 3. 会话持久化
```python
import json
import os

SESSIONS_FILE = "sessions.json"
sessions = load_sessions()

def save_sessions():
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)
```

### 4. 流式输出
```python
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        for token in call_stream_api(provider, model, message, history):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"}
    )
```

## 验证结果（2026-08-04）

```
✅ 1. 健康检查
✅ 2. 提供商列表
✅ 3. GPT-5.5 真实 API 调用
✅ 4. GPT-5.6-Sol 真实 API 调用
✅ 5. 多轮对话
✅ 6. 持久化存储
✅ 7. 流式输出
✅ 8. RAG 流程图页面
✅ 9. Python 语法检查
✅ 10. 项目结构
```

## ASLNet API 实测
- 可用模型：`gpt-5.5`, `gpt-5.6-sol`
- 不可用：`luna`, `terra`（返回 404）
- API Key 来自环境变量 `ASLNET_API_KEY`

## Ollama 注意事项
- 可能返回 502（服务未运行或模型未加载）
- 使用完整模型名：`qwen2.5:7b`
- 检查：`curl http://localhost:11434/api/tags`

## 访问地址
- 聊天界面：http://localhost:8090
- RAG 流程图：http://localhost:8090/rag-flow
- API 文档：http://localhost:8090/docs
