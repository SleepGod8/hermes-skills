---
name: local-llm-python
description: Python scripting for local LLM inference via Ollama — model selection, SDK usage, prompt roles, and output post-processing
---

# local-llm-python

## When to load
- User wants to call a local LLM from Python
- User asks about Ollama Python integration
- User needs to process/clean model output (disclaimers, annotations)

## Three ways to call Ollama from Python

### 1. `requests` to native API (`/api/generate`)
```python
import requests
url = "http://localhost:11434/api/generate"
payload = {"model": "qwen2.5:7b", "prompt": "...", "stream": False}
resp = requests.post(url, json=payload).json()
print(resp["response"])
```

### 2. `ollama` Python SDK (simplest)
```python
from ollama import chat, ChatResponse
res = chat(model="qwen2.5:7b", messages=[{"role": "user", "content": "..."}])
print(res.message.content)
```

### 3. `ollama.client.Client` (configurable)
```python
from ollama.client import Client
client = Client(host="http://localhost:11434")
res = client.chat(model="qwen2.5:7b", messages=[...])
```

## Message roles
```python
messages = [
    {"role": "system",   "content": "你是一个角色扮演助手"},
    {"role": "user",     "content": "用户的问题"},
    {"role": "assistant","content": "模型回复"},
]
```
- **System**: persona, style, constraints (best for suppressing disclaimers)
- **User**: the current query
- **Assistant**: previous turns (multi-turn context)

## Model selection for CPU-only hardware
| Hardware | Recommended | Size | Speed |
|----------|-------------|------|-------|
| Laptop CPU 2GHz, 32GB RAM | qwen2.5:7b | 4.7GB | ⚡⚡⚡ |
| Laptop CPU, 16GB RAM | qwen2.5:3b / llama3.2:3b | ~2GB | ⚡⚡⚡⚡ |
| Desktop CPU, 64GB RAM | qwen2.5:14b / gemma2:9b | 5-9GB | ⚡⚡ |
| With GPU (6GB+ VRAM) | mistral:7b / qwen2.5:7b | 4.7GB | ⚡⚡⚡⚡⚡ |

Sweet spot for CPU 32GB: **7B params (Q4, ~5GB)**.

## Handling Chinese model disclaimers
Chinese models (qwen, glm, deepseek) append notes like `【注：虚构】`. Two-layer defence:

### Layer 1: Prompt engineering
```python
{"role": "system", "content": "直接输出正文，不要包含任何「注」、「提示」、「虚构声明」等附加文字。"}
{"role": "user", "content": "…要求：不要加任何'注'、'提示'等附加文字。"}
```

### Layer 2: Regex post-processing
```python
import re
content = res.message.content
content = re.sub(r'[【\[]\s*[注备注提示此处]+\s*[：:].*?[】\]]', '', content)
content = re.sub(r'\[.*?\]', '', content)
content = re.sub(r'\n?\s*(注|备注|提示)[：:].*', '', content)
content = re.sub(r'[（(]?纯属虚构[）)]?.*', '', content)
content = content.strip()
```

## Common pitfalls
- **Model name mismatch**: `ollama list` to verify exact names
- **First-load latency**: large models (19GB+) take minutes to load; 4-5GB models load in seconds
- **Ollama not in PATH on Windows**: use full path `/c/Users/Windows/AppData/Local/Programs/Ollama/ollama.exe`
- **Secure credentials**: never hardcode passwords; use `os.getenv('VAR')`

## References
See `references/hardware-model-guide.md` for detailed hardware-to-model mapping.
