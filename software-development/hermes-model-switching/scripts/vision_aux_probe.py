#!/usr/bin/env python
"""视觉能力探针：验证某模型能否读图 + Hermes 走的是 native 还是 aux 通道。

用法（在任意目录）：
    python vision_aux_probe.py                        # 默认 DeepSeek V4.1-Flash
    python vision_aux_probe.py --provider deepseek --model deepseek-v4-pro
    python vision_aux_probe.py --image C:/path/x.png  # 用自己的图（跳过生成）

输出三块：
  1. 生成/使用的测试图路径（含可验证内容：4位数字 + 汉字 + 红圆 + 蓝方块）
  2. 直连 OpenAI-compatible /chat/completions 的读图结果（含耗时、wire model、usage）
  3. decide_image_input_mode 的路由决策（native / text）

依赖：Pillow、pyyaml（Hermes venv 里都有）。
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERMES_HOME = os.environ.get("HERMES_HOME") or os.path.expanduser(
    r"~\AppData\Local\hermes"
)
HERMES_SRC = os.path.join(HERMES_HOME, "hermes-agent")
TMP = os.environ.get("LOCALAPPDATA", os.path.expanduser("~")) + os.sep + "Temp"

DIGITS = "7391"
HANZI = "虹"


def make_test_image(path: str) -> str:
    from PIL import Image, ImageDraw, ImageFont

    font_path = r"C:\Windows\Fonts\msyh.ttc"
    img = Image.new("RGB", (640, 360), (250, 250, 246))
    d = ImageDraw.Draw(img)
    f_big = ImageFont.truetype(font_path, 96)
    d.text((40, 30), DIGITS, font=f_big, fill=(20, 20, 20))
    d.text((40, 170), HANZI, font=f_big, fill=(20, 20, 20))
    d.ellipse([420, 60, 590, 230], fill=(220, 40, 40))      # 红圆
    d.rectangle([440, 255, 560, 330], fill=(40, 60, 220))   # 蓝方块
    img.save(path)
    return path


def read_key(provider: str) -> tuple[str, str]:
    """返回 (api_key, base_url)。从 $HERMES_HOME/.env 里找 <PROVIDER>_API_KEY。"""
    env_file = os.path.join(HERMES_HOME, ".env")
    want = f"{provider.upper().replace('-', '_')}_API_KEY"
    key = os.environ.get(want) or ""
    if not key and os.path.exists(env_file):
        for line in open(env_file, encoding="utf-8", errors="ignore"):
            if line.startswith(want + "="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    base = {
        "deepseek": "https://api.deepseek.com",
    }.get(provider, f"https://api.{provider}.com")
    return key, base


def probe_api(key: str, base_url: str, model: str, image_path: str) -> bool:
    b64 = base64.b64encode(open(image_path, "rb").read()).decode()
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "读出图中的4位数字和那个汉字，并说出圆形和方块的颜色。只回答事实。"},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}},
            ],
        }],
        "max_tokens": 200,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[API] HTTP {e.code}: {e.read().decode()[:400]}")
        return False
    dt = time.time() - t
    msg = body["choices"][0]["message"]
    text = (msg.get("content") or "").strip()
    print(f"[API] HTTP 200  {dt:.2f}s  wire_model={body.get('model')}")
    print(f"[API] answer={text[:300]}")
    print(f"[API] usage={body.get('usage')}")
    ok = DIGITS in text and HANZI in text
    print(f"[API] {'✅ 通过（数字与汉字都读出）' if ok else '❌ 未通过——检查是否真支持图片输入'}")
    return ok


def route_decision(provider: str, model: str) -> None:
    sys.path.insert(0, HERMES_SRC)
    os.environ.setdefault("HERMES_HOME", HERMES_HOME)
    try:
        import yaml
        from agent.image_routing import decide_image_input_mode
    except Exception as exc:  # noqa: BLE001
        print(f"[ROUTE] 跳过（无法导入 Hermes: {exc}）")
        return
    cfg_path = os.path.join(HERMES_HOME, "config.yaml")
    cfg = yaml.safe_load(open(cfg_path, encoding="utf-8"))
    aux = ((cfg.get("auxiliary") or {}).get("vision") or {})
    print(f"[ROUTE] auxiliary.vision = {json.dumps(aux, ensure_ascii=False)}")
    print(f"[ROUTE] agent.image_input_mode = {(cfg.get('agent') or {}).get('image_input_mode', 'auto')}")
    try:
        mode = decide_image_input_mode(provider, model, cfg, requested_provider=provider)
    except Exception as exc:  # noqa: BLE001
        print(f"[ROUTE] decide 失败: {type(exc).__name__}: {exc}")
        return
    print(f"[ROUTE] decide({provider}, {model}) -> {mode}")
    if mode == "native":
        print("[ROUTE] 提醒：主模型自己看图，auxiliary.vision 不参与——要验证 aux，请换 text-only 主模型再跑。")
    else:
        print("[ROUTE] 主模型是纯文本，会走 auxiliary.vision（这才是 aux 验证场景）。")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="deepseek")
    ap.add_argument("--model", default="deepseek-v4-flash")
    ap.add_argument("--image", default=None)
    args = ap.parse_args()

    image = args.image or make_test_image(os.path.join(TMP, "vision_probe_test.png"))
    print(f"[IMG] {image}  ({os.path.getsize(image)} bytes)")

    key, base_url = read_key(args.provider)
    if not key:
        print(f"[API] 跳过：未找到 {args.provider.upper()}_API_KEY")
        ok = False
    else:
        ok = probe_api(key, base_url, args.model, image)

    print()
    route_decision(args.provider, args.model)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
