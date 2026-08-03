---
name: multi-provider-llm-gateway
description: "Python 多供应商 LLM 统一调用层：单函数接入多云模型+本地 Ollama，云失败自动降级本地兜底。"
version: 1.0.0
tags: [llm, gateway, multi-provider, ollama, fallback, python]
metadata:
  hermes:
    tags: [llm, gateway, multi-provider, ollama, fallback, python]
    category: software-development
---

# 多供应商 LLM 统一调用层 (Multi-Provider LLM Gateway)

把多个大模型供应商（OpenAI 兼容云厂商 + 本地 Ollama）封装到单一入口，云模型失败时自动降级到本地兜底。参考实现：`D:\PythonProject\unified-llm-gateway\`（llm_gateway.py + example.py + .env + README.md）。

## 何时使用

- 用户要求"把所有模型 API 封装成一个函数/模块"
- 需要同时支持多个云供应商（ASLNet/DeepSeek/GLM/OpenRouter 等）和本地 Ollama
- 需要"云模型没钱/失败时用本地兜底"的降级能力

## 核心设计

### 1. 供应商注册表（dict 驱动）

```python
PROVIDERS = {
    "aslnet":   {"name": "ASLNet", "base_url": os.getenv("ASLNET_BASE_URL", "https://api.aslnet.cloud/v1"),
                 "api_key_env": "ASLNET_API_KEY", "models": ["gpt-5.6-sol", "gpt-5.5"]},
    "ollama":   {"name": "Ollama", "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                 "api_key_env": None, "models": ["qwen2.5:7b", "glm-4.7-flash"]},  # 本地无 key
}
# 模型 → 供应商 反向索引
MODEL_TO_PROVIDER = {m: p for p, cfg in PROVIDERS.items() for m in cfg["models"]}
```

关键点：
- **全部走 OpenAI 兼容协议** `/v1/chat/completions`（Ollama 也兼容），减少适配成本
- `api_key_env: None` 表示无需 key（本地）
- API Key 一律从环境变量读，**零硬编码**

### 2. 统一响应结构（dataclass）

```python
@dataclass
class LLMResponse:
    content: str; provider: str; model: str
    usage: dict; latency_ms: float
    fallback_used: bool   # 是否降级
    error: Optional[str]  # 降级时保留原始错误
```

### 3. 单入口 chat()

```python
def chat(messages, model=None, provider=None, fallback=True,
         fallback_model=None, temperature=0.7, max_tokens=1024, timeout=60):
    # 1. 字符串 → [{"role":"user","content":...}]
    # 2. model 或 provider 至少一个；model 自动推断 provider（或显式指定）
    # 3. 调用主供应商；失败且可降级 → 调 ollama，fallback_used=True
```

### 4. 错误分类 + 降级链

```python
def classify_error(exc, status_code=None) -> str:
    if status_code == 402: return "quota"        # 余额不足 → 可降级
    if status_code == 429: return "rate_limit"   # 限流 → 可降级
    if status_code == 401: return "auth"         # 鉴权失败 → 可降级
    if status_code == 404: return "not_found"    # 模型不存在 → 可降级
    if isinstance(exc, requests.exceptions.RequestException): return "network"
    return "other"

recoverable = category in ("quota", "rate_limit", "auth", "network", "not_found")
```

降级目标默认 `qwen2.5:7b`（Ollama），可用 `OLLAMA_FALLBACK_MODEL` 环境变量覆盖。

## 关键坑（实测踩过）

1. **⚠️ 404 必须归为可降级**：最初 `classify_error` 把 404 归为 `other`（不可恢复），导致"模型不存在"时**降级不触发**。本地兜底的场景下，云上模型不存在/余额不足/限流/鉴权/断网**全都应该降级**。
2. **⚠️ 测试降级要显式指定 provider**：`MODEL_TO_PROVIDER` 索引会把未知模型名拦在参数校验（"找不到模型对应的供应商"），永远走不到供应商调用。测降级用 `chat(..., provider="aslnet", model="gpt-9.9-nonexistent")` 显式指定 provider 绕过索引。
3. **🔐 Hermes secret redaction 会打码 API key**：在 Hermes 的 terminal 里 `grep`/`echo` .env 中的 key 会输出 `sk-3d6...10bb`（被脱敏）。复制 key 到新项目要用 **Python 脚本直接读写文件**（不经 stdout），或者让用户手动粘贴。
4. **降级后要保留原始错误**：`resp.error = f"原始调用失败[{provider}/{model}]: {e}"`，方便排查。

## 辅助功能

- `list_models(provider=None)`：列出可用模型
- `health_check()`：顺序 ping 各供应商 `/models` 端点，返回 {provider, ok, http/error}
- `python example.py --health / --models`：命令行自检

## 验证方式

真实调用三连测（必须真跑，不能 mock）：
1. 云调用：`chat("say OK", model="gpt-5.6-sol")` → content 非空
2. 本地调用：`chat("say OK", model="qwen2.5:7b")` → provider == "ollama"
3. 降级：`chat("hi", provider="aslnet", model="gpt-9.9-nonexistent", fallback=True)` → fallback_used=True 且 provider == "ollama"
4. 分类单测：402/429/401/404 → 对应类别

## 扩展方向（用户常提）

- 运行时按需切换供应商
- 模型能力标签（fast/strong/vision）自动路由
- 多级降级链（ASLNet → DeepSeek → Ollama）
- token/成本统计
