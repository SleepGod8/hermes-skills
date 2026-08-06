#!/usr/bin/env python3
"""MCP stdio 桥快速验证：握手 + tools/list + 功能调用。

用法：
    python mcp_bridge_probe.py <server.py 路径> [python 路径]

默认 python 用 Hermes venv。测试三步：
1. initialize 握手 → 验证 serverInfo
2. tools/list → 列出工具
3. tools/call comfy_server_info → 验证能连真实 ComfyUI

MCP 帧格式：Content-Length: <len>\r\n\r\n<json>，长度必须字节精确。
"""
import json
import re
import subprocess
import sys
import time

SERVER = sys.argv[1] if len(sys.argv) > 1 else r"C:\path\to\mcp\server.py"
PYTHON = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\80704\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"


def frame(msg: dict) -> bytes:
    body = json.dumps(msg).encode("utf-8")
    return f"Content-Length: {len(body)}\r\n\r\n".encode() + body


def call(proc, msgid, method, params=None):
    req = {"jsonrpc": "2.0", "id": msgid, "method": method}
    if params is not None:
        req["params"] = params
    proc.stdin.write(frame(req))
    proc.stdin.flush()


def parse_frames(raw: bytes) -> list:
    frames = []
    data = raw
    while data:
        m = re.match(rb"Content-Length: (\d+)\r\n\r\n", data)
        if not m:
            break
        length = int(m.group(1))
        header_end = m.end()
        body = data[header_end:header_end + length]
        try:
            frames.append(json.loads(body))
        except Exception:
            pass
        data = data[header_end + length:]
    return frames


def main():
    proc = subprocess.Popen(
        [PYTHON, SERVER],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    call(proc, 1, "initialize", {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "probe", "version": "1.0"},
    })
    time.sleep(1.0)
    call(proc, 2, "tools/list", {})
    time.sleep(1.0)
    call(proc, 3, "tools/call", {"name": "comfy_server_info", "arguments": {}})
    time.sleep(2.0)
    proc.stdin.close()
    out = proc.stdout.read()
    err = proc.stderr.read().decode("utf-8", errors="replace")
    proc.wait(timeout=10)

    frames = parse_frames(out)
    print(f"收到 {len(frames)} 个响应帧")
    for f in frames:
        fid = f.get("id")
        if fid == 1:
            print("✅ initialize:", f.get("result", {}).get("serverInfo"))
        elif fid == 2:
            names = [t["name"] for t in f.get("result", {}).get("tools", [])]
            print(f"✅ tools/list ({len(names)}): {', '.join(names)}")
        elif fid == 3:
            for c in f.get("result", {}).get("content", []):
                print("✅ comfy_server_info:", c.get("text", "")[:300])
        elif "error" in f:
            print("❌ 错误:", json.dumps(f["error"], ensure_ascii=False)[:500])
    if err.strip():
        print("=== STDERR ===")
        print(err[:800])


if __name__ == "__main__":
    main()
