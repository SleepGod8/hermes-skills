"""
统一大模型调用模块 (Unified LLM Gateway) — 可复用模板
========================================
- 单函数入口 `chat()`，对接多个供应商（OpenAI 兼容云厂商 + 本地 Ollama）
- 统一响应结构：{content, usage, latency, provider, model}
- 自动降级兜底：云模型失败（余额不足/限流/鉴权/模型不存在/网络）→ 切到本地 Ollama

用法：
    from llm_gateway import chat
    resp = chat("你好", model="gpt-5.6-sol")                        # 云模型
    resp = chat("你好", model="qwen2.5:7b")                         # 本地模型
    resp = chat("你好", model="gpt-5.6-sol", fallback=True)         # 云失败自动降级

配套 .env（API Key 一律放这里，禁止硬编码）：
    ASLNET_API_KEY=...
    DEEPSEEK_API_KEY=...
    GLM_API_KEY=...
    OPENROUTER_API_KEY=...
    AGNES_API_KEY=...
    OLLAMA_BASE_URL=http://localhost:11434/v1
    OLLAMA_FALLBACK_MODEL=qwen2.5:7b
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests

# ============================================================
# 供应商配置（OpenAI 兼容协议为主）
# ============================================================
PROVIDERS: Dict[str, dict] = {
    "aslnet": {
        "name": "ASLNet 中转站",
        "base_url": os.getenv("ASLNET_BASE_URL", "https://api.aslnet.cloud/v1"),
        "api_key_env": "ASLNET_API_KEY",
        "models": ["gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.5", "gpt-5.4"],
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        "api_key_env": "DEEPSEEK_API_KEY",
        "models": ["deepseek-chat", "deepseek-v4-pro"],
    },
    "glm": {
        "name": "智谱 GLM",
        "base_url": os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
        "api_key_env": "GLM_API_KEY",
        "models": ["glm-4-flash", "glm-4v-flash", "glm-5.2"],
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        "api_key_env": "OPENROUTER_API_KEY",
        "models": ["kimi/kimi-k3", "z-ai/glm-5.2", "deepseek/deepseek-v4-pro"],
    },
    "agnes": {
        "name": "Agnes AI",
        "base_url": os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
        "api_key_env": "AGNES_API_KEY",
        "models": ["agnes-2.0-flash"],
    },
    "ollama": {
        "name": "Ollama 本地",
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "api_key_env": None,  # 本地无需 Key
        "models": ["qwen2.5:7b", "glm-4.7-flash"],
    },
}

MODEL_TO_PROVIDER: Dict[str, str] = {}
for _prov_name, _prov in PROVIDERS.items():
    for _m in _prov["models"]:
        MODEL_TO_PROVIDER[_m] = _prov_name

MODELS: List[str] = list(MODEL_TO_PROVIDER.keys())


# ============================================================
# 统一响应结构
# ============================================================
@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    usage: Dict = field(default_factory=dict)
    latency_ms: float = 0.0
    fallback_used: bool = False
    error: Optional[str] = None


# ============================================================
# 错误分类（可降级 vs 不可降级）
# ============================================================
class LLMError(Exception):
    def __init__(self, message: str, category: str = "unknown"):
        super().__init__(message)
        self.category = category


def classify_error(exc: Exception, status_code: Optional[int] = None) -> str:
    if status_code == 402:
        return "quota"          # 余额不足 → 可降级
    if status_code == 429:
        return "rate_limit"     # 限流 → 可降级
    if status_code == 401:
        return "auth"           # 鉴权失败 → 可降级
    if status_code == 404:
        return "not_found"      # 模型不存在 → 可降级（本地兜底）
    if isinstance(exc, requests.exceptions.RequestException):
        return "network"        # 网络错误 → 可降级
    return "other"


RECOVERABLE = ("quota", "rate_limit", "auth", "network", "not_found")


# ============================================================
# 底层调用
# ============================================================
def _call_provider(provider: str, model: str, messages: List[dict],
                   temperature: float = 0.7, max_tokens: int = 1024,
                   timeout: int = 60) -> dict:
    prov = PROVIDERS.get(provider)
    if not prov:
        raise LLMError(f"未知供应商: {provider}", "other")

    api_key = os.getenv(prov["api_key_env"]) if prov["api_key_env"] else None
    url = f"{prov['base_url'].rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model, "messages": messages,
        "temperature": temperature, "max_tokens": max_tokens, "stream": False,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        if resp.status_code >= 400:
            raise LLMError(f"[{provider}] HTTP {resp.status_code}: {resp.text[:200]}",
                           classify_error(None, resp.status_code))
        return resp.json()
    except requests.exceptions.RequestException as e:
        raise LLMError(f"[{provider}] 网络错误: {e}", "network") from e


def _parse_response(data: dict, provider: str, model: str,
                    fallback_used: bool = False) -> LLMResponse:
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        content = str(data)
    return LLMResponse(
        content=content, provider=provider, model=model,
        usage=data.get("usage", {}), fallback_used=fallback_used,
    )


# ============================================================
# 统一入口
# ============================================================
def chat(messages: List[dict] | str,
         model: Optional[str] = None,
         provider: Optional[str] = None,
         fallback: bool = True,
         fallback_model: Optional[str] = None,
         temperature: float = 0.7,
         max_tokens: int = 1024,
         timeout: int = 60) -> LLMResponse:
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    if model is None:
        if provider is None:
            raise LLMError("必须指定 model 或 provider 至少一个", "other")
        prov_cfg = PROVIDERS.get(provider)
        if not prov_cfg:
            raise LLMError(f"未知供应商: {provider}", "other")
        model = prov_cfg["models"][0]
    else:
        if provider is None:
            provider = MODEL_TO_PROVIDER.get(model)
        if provider is None:
            raise LLMError(f"找不到模型 {model} 对应的供应商", "other")

    start = time.time()
    try:
        data = _call_provider(provider, model, messages, temperature, max_tokens, timeout)
        resp = _parse_response(data, provider, model)
        resp.latency_ms = (time.time() - start) * 1000
        return resp
    except LLMError as e:
        if fallback and e.category in RECOVERABLE:
            fb_model = fallback_model or os.getenv("OLLAMA_FALLBACK_MODEL", "qwen2.5:7b")
            try:
                data = _call_provider("ollama", fb_model, messages, temperature, max_tokens, timeout)
                resp = _parse_response(data, "ollama", fb_model, fallback_used=True)
                resp.latency_ms = (time.time() - start) * 1000
                resp.error = f"原始调用失败[{provider}/{model}]: {e}"
                return resp
            except LLMError as fb_e:
                raise LLMError(
                    f"主调用({provider}/{model})与降级(ollama/{fb_model})均失败: {e} | {fb_e}", "other"
                ) from fb_e
        raise LLMError(str(e), e.category) from e


# ============================================================
# 辅助
# ============================================================
def list_models(provider: Optional[str] = None) -> List[str]:
    if provider:
        return PROVIDERS.get(provider, {}).get("models", [])
    return MODELS


def health_check() -> List[dict]:
    results = []
    for name, prov in PROVIDERS.items():
        try:
            url = f"{prov['base_url'].rstrip('/')}/models"
            api_key = os.getenv(prov["api_key_env"]) if prov["api_key_env"] else None
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            resp = requests.get(url, headers=headers, timeout=5)
            results.append({"provider": name, "ok": resp.status_code < 400, "http": resp.status_code})
        except Exception as e:
            results.append({"provider": name, "ok": False, "error": str(e)})
    return results


if __name__ == "__main__":
    import sys
    if "--health" in sys.argv:
        for r in health_check():
            mark = "✅" if r["ok"] else "❌"
            print(f"  {mark} {r['provider']}: {r.get('http', r.get('error', ''))}")
        sys.exit(0)
    if "--models" in sys.argv:
        for m in MODELS:
            print(f"  - {m} ({MODEL_TO_PROVIDER[m]})")
        sys.exit(0)
