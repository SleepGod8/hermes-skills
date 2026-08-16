#!/usr/bin/env python3
"""Zhipu GLM vision probe — direct OpenAI-compatible vision call.

Use when Hermes auxiliary.vision fails with
  "No LLM provider configured for task=vision provider=custom:ZhipuGLM"
but the API itself works (2026-08 validated). Reads the API key from
config.yaml custom_providers entry — never prints it.

Usage:
  python zhipu_vision_probe.py <image_path> ["question text"]
  python zhipu_vision_probe.py shot.png "完整输出那个 .swf 请求的 URL, 不要截断"
"""
import base64, json, os, re, sys, time
import urllib.error, urllib.request

ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4.6v-flash"


def load_zhipu_key(config_path=None):
    cfg = config_path or os.path.expanduser(r"~\AppData\Local\hermes\config.yaml")
    with open(cfg, encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'ZhipuGLM",\s*"base_url":\s*"[^"]+",\s*"api_key":\s*"([^"]+)"', content)
    if not m:
        raise SystemExit("ZhipuGLM key not found in config.yaml custom_providers")
    return m.group(1)


def ask_vision(image_path, question, max_tokens=600, attempts=3):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    key = load_zhipu_key()
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text", "text": question},
        ]}],
        "max_tokens": max_tokens,
    }
    for i in range(1, attempts + 1):
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode())
            out = data["choices"][0]["message"]["content"]
            if out and out.strip():
                return out
            print(f"attempt {i}: empty content, retrying...")
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:300]
            print(f"attempt {i}: HTTP {e.code} {body}")
            if e.code == 429:  # overloaded but model name VALID -> backoff, don't give up
                time.sleep(3)
        except Exception as ex:
            print(f"attempt {i}: {ex}")
        time.sleep(2)
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    img = sys.argv[1]
    q = sys.argv[2] if len(sys.argv) > 2 else "描述这张图片, 用中文回答"
    result = ask_vision(img, q)
    print(result if result else "NO_RESULT")
