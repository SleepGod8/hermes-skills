---
name: opencode-china-workflow
description: "OpenCode CLI usage in China — mirror install, desktop setup, DeepSeek model, Hermes message bridge."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [OpenCode, China, Coding-Agent, DeepSeek]
    related_skills: [opencode, hermes-agent]
---

# OpenCode China Workflow

Extensions to the bundled `opencode` skill for users in China.

## Installation (China Mirror)

```bash
npm i -g opencode-ai@latest --registry=https://registry.npmmirror.com
```

Direct GitHub downloads are extremely slow (~30KB/s). Always use npmmirror.

## Desktop Version

Official installer from https://opencode.ai/download installs to:
```
C:\Users\<user>\AppData\Local\Programs\@opencode-aidesktop\
```
- ~307MB, full Electron app
- Auto-update, extensions, multi-account isolation
- Shares `auth.json` with CLI
- Desktop shortcut auto-created

Prefer the official installer over manual ZIP download (~176MB bare exe, no auto-update).

## Recommended Model: DeepSeek

```bash
opencode run "task" --model deepseek/deepseek-chat
```

DeepSeek is censorship-light for roleplay/literary content. Set `DEEPSEEK_API_KEY` env var or auth via `opencode auth login`.

Model format is `provider/model` — NOT `--model-name`.

## Hermes ↔ OpenCode Message Bridge

File: `~/.hermes-opencode-chat/messages.json`

```json
{
  "conversation": [
    {"from": "hermes", "content": "...", "timestamp": "..."},
    {"from": "opencode", "content": "...", "timestamp": "..."}
  ],
  "unread_from": null
}
```

Protocol:
1. Before every user response, read messages.json. If `unread_from: "opencode"`, process OpenCode's message first.
2. To forward a message: `opencode run "msg" --continue --model deepseek/deepseek-chat`
3. Write reply to conversation array, set `unread_from: "opencode"`

## Session Continuity

`--continue` preserves full context across multiple `opencode run` calls. Use `opencode session list` to see past sessions, `--session <id>` to resume specific ones, `opencode export <id>` to export.

## Pitfalls

- GitHub downloads from China are extremely slow — always use npmmirror
- `--mini` TUI mode is unstable with PTY — prefer `opencode run` for one-shot tasks
- The `--model-name` flag does not exist; use `--model provider/model`
- Two `opencode` instances (CLI + Desktop) are independent sessions unless `--continue` is used
