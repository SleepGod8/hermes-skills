#!/usr/bin/env python3
"""Verify a Hermes custom provider/model by probing its chat/completions endpoint.

Reads the API key from Hermes .env so secrets are NEVER pasted into chat.
Re-run this instead of hand-typing curl each time.

Usage:
    python verify_provider.py <base_url> <env_key_name> <model_name> [max_tokens]

Examples:
    python verify_provider.py https://api.deepseek.com DEEPSEEK_API_KEY deepseek-v4-pro
    python verify_provider.py https://open.bigmodel.cn/api/paas/v4 GLM_API_KEY GLM-4.1V-Thinking-Flash 400

Interpretation:
    HTTP 200           -> provider + key + model name all good
    HTTP 404 / 4xx json "model not found" -> model NAME is wrong
    HTTP 429           -> name is VALID but endpoint overloaded, retry later
    finish_reason:stop -> full clean response (raise max_tokens if you see "length")
"""
import os
import sys

import httpx

# Primary: Hermes .env on Windows. Falls back to running env vars.
ENV_PATH = os.path.expanduser(r"C:\Users\Windows\AppData\Local\hermes\.env")


def load_env(path: str) -> dict:
    d = {}
    try:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return d


def main() -> None:
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(2)

    base, keyname, model = sys.argv[1], sys.argv[2], sys.argv[3]
    max_tokens = int(sys.argv[4]) if len(sys.argv) > 4 else 400

    env = load_env(ENV_PATH)
    key = env.get(keyname) or os.environ.get(keyname)
    if not key:
        print(f"[!] 未找到 {keyname}（既不在 .env 也不在环境变量）")
        sys.exit(1)

    url = base.rstrip("/") + "/chat/completions"
    print(f"=== 探测: {model} @ {base} ===")
    try:
        r = httpx.post(
            url,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": max_tokens},
            timeout=40,
        )
        print("HTTP 状态码:", r.status_code)
        if r.status_code == 200:
            fr = r.json().get("choices", [{}])[0].get("finish_reason")
            print("finish_reason:", fr, "(stop=正常结束; length=被 max_tokens 截断)")
        print(r.text[:600])
    except Exception as e:
        print("[!] 请求异常:", type(e).__name__, e)


if __name__ == "__main__":
    main()
