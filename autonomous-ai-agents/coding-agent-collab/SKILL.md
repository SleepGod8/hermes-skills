---
name: coding-agent-collab
description: "Hermes orchestrates external coding agents (OpenCode, Claude Code, Codex) in multi-turn conversational workflows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, OpenCode, Orchestration, Multi-Turn]
    related_skills: [opencode, claude-code, codex]
---

# Coding Agent Collaboration

Hermes ↔ external coding agent 联动模式。Hermes 作为调度者，驱动外部编码 agent 完成多轮迭代任务。

## When to Use

- User wants an external coding agent to implement/refactor/review code
- Multi-turn iterative development (写代码 → 加测试 → 改需求 → 验证)
- User wants to see the "dialogue" between Hermes and the coding agent
- Complex tasks that benefit from context-carrying across rounds

## Core Pattern: `run` + `--continue`

**Prefer `opencode run --continue` over TUI/PTY for multi-turn conversations.** The TUI (`opencode --mini` or `opencode` without args) has PTY interaction issues in Hermes — messages may not submit reliably. The `run --continue` pattern works deterministically and produces clean, readable output.

### Round 1: Initial task
```bash
terminal(command="opencode run 'Write a Python function X with type hints and docstring' --model deepseek/deepseek-chat")
```
OpenCode creates files, runs code, returns results. Output is self-contained.

### Round 2: Follow-up (same session, full context)
```bash
terminal(command="opencode run 'Add pytest tests for X, run them' --continue --model deepseek/deepseek-chat")
```
OpenCode remembers Round 1's files and context. It reads existing code, writes tests, installs deps, runs tests.

### Round 3: Iterate
```bash
terminal(command="opencode run 'Add optional parameter Y to function X, update tests' --continue --model deepseek/deepseek-chat")
```
Continues the chain. Each round builds on all prior rounds.

## Presenting the Dialogue

When the user asks to "see the conversation", present the exchange as a dialogue log:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👩‍💼 Hermes                  🤖 OpenCode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"Write palindrome checker"  →  ✍️ Created is_palindrome.py ✅
"Add 6+ pytest cases"       →  📦 Installed pytest
                                🧪 6/6 passed ✅
"Add reverse parameter"     →  🔧 Patched both files
                                🧪 9/9 passed ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

This format makes the collaboration visible and shows context continuity.

## Recommended Provider: DeepSeek

For Chinese users, DeepSeek is the best default:
- Cheap, fast, good at coding
- Direct connection from China (no proxy needed)
- Model: `deepseek/deepseek-chat`

```bash
# One-time setup
export DEEPSEEK_API_KEY=sk-...
# Or persist for desktop app (Windows):
# [Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', 'sk-...', 'User')
```

## Desktop App (OpenCode)

OpenCode has a desktop app (Beta) available as a ZIP — no installer, extract anywhere:
- Download: https://opencode.ai/download
- Shares `~/.local/share/opencode/auth.json` with CLI
- Windows shortcut via PowerShell (see references/shortcut.md)

## Pitfalls

- **Don't use `--mini` TUI in Hermes PTY** — Enter key submission is unreliable. Use `opencode run --continue` for multi-turn instead.
- **`opencode` without args** opens full TUI which exits immediately in Hermes background PTY. Use `opencode run` for one-shots.
- **`/exit`** is not a command — it opens the agent selector. Use Ctrl+C or kill.
- GitHub downloads from China are slow; use browser or download manager for the ~68MB desktop ZIP.

## Verification

```bash
opencode run "Respond with exactly: COLLAB_OK" --model deepseek/deepseek-chat
```

Expected: output contains `COLLAB_OK`.
