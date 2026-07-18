#!/usr/bin/env python3
"""
Multi-Agent QQ Group Bridge
============================
Bridges Hermes ↔ OpenCode in QQ group chats.

Commands (in QQ group, @mention the bot):
  /oc <message>  → forwards to OpenCode, posts reply
  /talk [turns]  → Hermes and OpenCode have a conversation (default 3 turns)
  /status        → show message state
"""

import json
import time
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

MESSAGES_FILE = Path.home() / ".hermes-opencode-chat" / "messages.json"

# --- OpenCode binary path (Hermes-managed node installation on Windows) ---
_NODE_DIR = str(Path.home() / "AppData" / "Local" / "hermes" / "node")
os.environ["PATH"] = _NODE_DIR + os.pathsep + os.environ.get("PATH", "")
OPENCODE_BIN = str(Path.home() / "AppData" / "Local" / "hermes" / "node" / "opencode.cmd")


def init_messages():
    MESSAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MESSAGES_FILE.exists():
        data = {"conversation": [], "unread_from": None}
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def read_messages():
    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"conversation": [], "unread_from": None}


def write_messages(data):
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def send_to_opencode(message):
    """Send a message to OpenCode and get response."""
    cmd = f'"{OPENCODE_BIN}" run "{message}" --continue --model deepseek/deepseek-chat'
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=str(Path.home()), shell=True,
        )
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "⏰ OpenCode 超时了..."
    except FileNotFoundError:
        return "❌ OpenCode CLI 未安装。"


def talk_cycle(turns=3):
    """Have Hermes and OpenCode chat for N turns."""
    conversation = []
    for i in range(turns):
        if i == 0:
            msg = "你好OpenCode！我是Hermes，我们在QQ群里聊天呢。随便聊点什么吧~"
        else:
            last = conversation[-1] if conversation else ""
            msg = f"OpenCode刚才说：「{last}」。请以Hermes的身份简短回复，像朋友聊天一样自然。"
        response = send_to_opencode(msg)
        conversation.append(response)
        time.sleep(1)
    return conversation


if __name__ == "__main__":
    init_messages()
    if len(sys.argv) < 2:
        print("Usage: bridge.py <command> [args]")
        print("  /oc <msg>    - forward to OpenCode")
        print("  /talk [N]    - start N-turn agent conversation (default 3)")
        print("  /status      - show message status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "/oc" and len(sys.argv) > 2:
        msg = " ".join(sys.argv[2:])
        print(f"🤖 转发给 OpenCode: {msg}")
        reply = send_to_opencode(msg)
        print(f"💬 OpenCode: {reply}")

    elif command == "/talk":
        turns = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        print(f"🎭 启动 {turns} 轮对话...")
        conv = talk_cycle(turns)
        for i, msg in enumerate(conv):
            role = "OpenCode" if i % 2 == 1 else "Hermes"
            print(f"\n{'─' * 40}")
            print(f"  [{role}] {msg[:200]}...")

    elif command == "/status":
        data = read_messages()
        unread = data.get("unread_from")
        count = len(data.get("conversation", []))
        print(f"📬 消息总数: {count}")
        print(f"📩 未读来自: {unread or '无'}")

    else:
        print(f"未知命令: {command}")
