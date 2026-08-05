---
name: multi-turn-chatbot
description: "Build FastAPI chatbots with sessions, streaming, multi-model"
version: 1.2.0
author: agent
license: MIT
tags: [fastapi, chatbot, streaming, multi-model, ai]
---

# Multi-Turn Chatbot Pattern

Build conversational AI interfaces with FastAPI supporting multiple models, streaming output, session persistence.

## When to Use

- Building chatbot interfaces for AI applications
- Implementing multi-model selection (DeepSeek, ASLNet, GLM, Ollama, etc.)
- Need streaming output (SSE) for real-time responses
- Demo mode development without real API keys

## Core Patterns

### 1. Session Management (Memory + JSON)

```python
sessions = {}
SESSIONS_FILE = "sessions.json"

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_sessions():
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)
```

### 2. Multi-Provider Config (Recommended Pattern)

```python
PROVIDERS = {
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "models": ["deepseek-4v-flash", "deepseek-4v-pro"],
        "name": "DeepSeek"
    },
    "glm": {
        "api_key": os.getenv("GLM_API_KEY", ""),
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": ["glm-4-flash", "glm-4-plus"],
        "name": "GLM"
    },
    "aslnet": {
        "api_key": os.getenv("ASLNET_API_KEY", ""),
        "base_url": "https://api.aslnet.cloud/v1",
        "models": ["gpt-5.5", "gpt-5.6-sol"],
        "name": "ASLNet"
    },
    "ollama": {
        "api_key": "ollama",
        "base_url": "http://localhost:11434/v1",
        "models": ["qwen2.5:7b", "glm-4.7-flash"],
        "name": "Ollama本地"
    }
}
DEFAULT_PROVIDER = "aslnet"  # Use ASLNet as default since it's verified working
```

### 3. Model Naming Convention

Use `provider-model` format for unambiguous routing:
- `aslnet-gpt-5.5`
- `glm-glm-4-flash`
- `deepseek-deepseek-4v-flash`
- `ollama-qwen2.5:7b`

Parse: `provider, model = request.model.split("-", 1)`

### 4. SSE Streaming

```python
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        for token in stream:
            yield f"data: {token}\n\n"
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"}  # Critical for SSE!
    )
```

### 5. Demo Mode Fallback

```python
def call_ai(provider: str, model: str, message: str, history: list) -> str:
    config = PROVIDERS.get(provider, {})
    api_key = config.get("api_key", "")
    
    if not api_key or api_key == "your_key_here":
        return f"[Demo] {provider} 回复：{message}"
    # Real API call...
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Frontend HTML |
| GET | /health | Health check |
| POST | /chat | Normal conversation |
| POST | /chat/stream | Streaming conversation |
| GET | /providers | List providers/models |
| GET | /sessions | List sessions |
| DELETE | /session/{id} | Delete session |

## Key Classes

```python
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = "aslnet-gpt-5.5"  # Default to working provider

class ChatResponse(BaseModel):
    session_id: str
    message: str
    model: str
    provider: str
    timestamp: str
```

## Common Pitfalls

1. **Port conflicts**: Use `netstat -ano | findstr :port`
2. **Windows curl**: Use Python requests instead
3. **SSE buffering**: Always include `X-Accel-Buffering: no` header
4. **Provider naming**: Provider names must NOT contain `-` (used as separator)
5. **Session IDs**: Use timestamp to avoid collisions
6. **API key loading**: Use `python-dotenv` with `.env` file, never hardcode
7. **Empty API key**: Check before calling - expect 401 if not configured
8. **Stream errors**: Catch exceptions and yield error messages as SSE data
9. **Frontend error handling**: Check `response.ok` before parsing JSON to avoid `undefined` display when API returns errors
10. **DeepSeek model names (CORRECT)**: Use `deepseek-chat`, `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-coder`. NOT `deepseek-4v-flash`/`deepseek-4v-pro` (these are 400 errors).
11. **Default model selection**: Prefer ASLNet (gpt-5.5) as default since DeepSeek API keys in Hermes may be invalid/expired
12. **GLM API**: Use GLM-4V-Flash as backup — verified working
13. **.env loading path**: Always use absolute path: `load_dotenv("D:/PythonProject/multi_turn_bot/.env")` — never bare `load_dotenv()` which loads from cwd and misses project keys
14. **API key discovery**: Hermes stores keys in two locations — `~/.hermes/.env` (minimal, GLM only) and `C:/Users/Windows/AppData/Local/hermes/.env` (full keys for all providers). Always check both.

## Getting API Keys

```bash
# Check available keys (redacted output)
python -c "import os; [print(k, v[:20]+'...') for k,v in os.environ.items() if 'KEY' in k and v]"
```

## Verification Checklist

- [ ] Health check `/health` returns 200 with providers list
- [ ] Normal chat `/chat` returns session_id and message
- [ ] Multi-turn history maintained
- [ ] Streaming `/chat/stream` returns SSE chunks
- [ ] Sessions persist to JSON
- [ ] Model switching works
- [ ] `/providers` lists all configured providers
- [ ] Frontend handles API errors gracefully (no `undefined` display)

## Linked References

- `references/multi-provider-config.md` - Provider registry patterns and model naming
- `references/windows-testing-pitfalls.md` - Windows-specific testing gotchas
- `references/api-key-discovery.md` - Hermes API key locations and provider model names
