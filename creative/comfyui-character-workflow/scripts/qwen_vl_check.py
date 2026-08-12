#!/usr/bin/env python3
"""批量视觉验证画像（qwen-vl-plus，DashScope 国内直连）。

用途：ComfyUI 出图后逐张验证质量（手部/发型/表情/服装/整体），
取代人工一张张看，本机女仆画像流水线实战验证 15+ 次。

用法：
    python qwen_vl_check.py <图片路径或目录> [--prompt 自定义检查提示词]

依赖：
    - DASHSCOPE_API_KEY 环境变量（存于 C:/Users/<user>/AppData/Local/hermes/.env）
    - 无第三方库（urllib + base64 + json）

返回：每张图打印「通过/不通过 + 关键描述」，exit 0。
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.request

DEFAULT_PROMPT = (
    "检查这张动漫图：1)手部：手指数量正常吗？有无畸形/多指/断指/扭曲？"
    "2)发色/发型是否符合描述？3)表情是否符合？4)服装是否符合？"
    "5)总体通过/不通过？简短回答。"
)

# DashScope key 自动探测：环境变量 -> hermes .env
def get_api_key():
    key = os.environ.get("DASHSCOPE_API_KEY")
    if key:
        return key
    env_path = os.path.expanduser(r"~/AppData/Local/hermes/.env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("DASHSCOPE_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None


def check_image(path, prompt):
    key = get_api_key()
    if not key:
        return "ERR: 找不到 DASHSCOPE_API_KEY"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    body = {
        "model": "qwen-vl-plus",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": prompt},
            ]
        }],
        "max_tokens": 400,
    }
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
    return resp["choices"][0]["message"]["content"]


def collect_images(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files.extend(
                os.path.join(p, f)
                for f in sorted(os.listdir(p))
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
            )
        else:
            files.append(p)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="图片路径或目录")
    ap.add_argument("--prompt", default=DEFAULT_PROMPT)
    args = ap.parse_args()

    files = collect_images(args.paths)
    if not files:
        print("无图片文件")
        return 1

    for f in files:
        print("=" * 55)
        print("FILE:", f)
        try:
            print(check_image(f, args.prompt))
        except Exception as e:
            print("ERR:", e)
        time.sleep(0.5)  # 限流保护
    return 0


if __name__ == "__main__":
    sys.exit(main())
