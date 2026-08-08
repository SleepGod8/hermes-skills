# Feishu / Lark Gateway Setup & Multi-Agent Group Chat

> Session-proven (2026-08-09): Feishu connected on Hermes default profile, permissions
> debugged via live 99991672 errors, multi-profile token conflict fixed.
> v2: removed `im:message.reaction` — user confirmed the scope does NOT exist on the
> platform (reactions are covered by `im:message`). 7 tenant scopes now.

## 1. Enabling the platform

Feishu ships as a **bundled plugin** (`$HERMES_HOME/hermes-agent/plugins/platforms/feishu/`),
kind=platform, name=feishu-platform. No `hermes gateway setup` menu entry needed.

**`.env` (at `$HERMES_HOME/.env`, or per-profile `profiles/<name>/.env`):**
```bash
FEISHU_APP_ID=cli_aafddea0c2f89be2
FEISHU_APP_SECRET=xxx
FEISHU_ALLOW_ALL_USERS=true        # dev only; or FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
FEISHU_DOMAIN=feishu               # default feishu; use lark for international
```
**config.yaml:**
```bash
hermes config set platforms.feishu.enabled true
```
**Restart & verify:**
```bash
# two separate calls (restart blocked from inside process tree)
taskkill -F -PID <pid>     # from: hermes gateway status
hermes gateway start
tail -20 "$LOCALAPPDATA/hermes/logs/gateway.log" | grep -i feishu
# Expected: [Feishu] Connected in websocket mode (feishu)  →  ✓ feishu connected
```

**DO NOT add `hermes-feishu` to `platform_toolsets`** — the plugin has no toolset;
`hermes-feishu` appears only as an SDK thread-name prefix. Adding it causes gateway startup errors.

## 2. Permission scopes (99991672 Access denied)

**Symptom:** inbound DM arrives, agent generates reply, send fails:
```
[99991672] Access denied. One of the following scopes is required:
[im:message:send, im:message, im:message:send_as_bot]
```
Hermes side is fine — this is open.feishu.cn 权限管理. Also commonly missing for group
replies: `im:chat:readonly` (adapter calls `im.v1.chat.get` to resolve chat name for
replies; the same 99991672 error appears at inbound time).

**⚠️ `im:message.reaction` DOES NOT EXIST on the platform** (user confirmed 2026-08-09:
批量导入 reports "该权限不存在"). Reactions are covered by `im:message`. Do NOT include it.

**Required tenant scopes for group multi-agent dev chat (7):**

| Scope | Purpose | Code evidence |
|-------|---------|---------------|
| `im:message` | receive/read messages + reactions (event base) | `im.message.receive_v1` event |
| `im:message:send_as_bot` | send as bot | `im.v1.message.create` |
| `im:chat:readonly` | read chat info/name | `im.v1.chat.get` |
| `im:resource` | image/file/voice upload+download | `image.create`, `file.create`, `message_resource.get` |
| `docx:document` | cloud doc read/write (dev docs) | dev-collab scenario |
| `drive:drive` | drive + doc comments | `feishu_comment.py` drive endpoints |
| `contact:user.base:readonly` | identify group members | multi-agent needs to know who's who |

Optional: `wiki:wiki` for knowledge-base access.

**Batch import format (open.feishu.cn → 权限管理 → 批量导入):**
```json
{
  "scopes": {
    "tenant": [
      "im:message",
      "im:message:send_as_bot",
      "im:chat:readonly",
      "im:resource",
      "docx:document",
      "drive:drive",
      "contact:user.base:readonly"
    ],
    "user": []
  }
}
```
Template file: `templates/feishu-scopes-batch-import.json`.

**⚠️ Enterprise self-built apps: after adding scopes you MUST 创建版本 → 发布**
(版本管理与发布). Permissions only take effect for the published version. This is the
#1 "I added the scope but it still fails" cause.

**Event subscriptions** (WebSocket mode still needs these): `im.message.receive_v1`,
`im.message.reaction.created_v1` / `deleted_v1` at 事件订阅.

**回调配置 (callback config): LEAVE ALL EMPTY in WebSocket mode** — URL / Encrypt Key /
Verification Token must stay blank. Filling any of them disables the WebSocket connection
(same trap as QQ Bot). Webhook mode (`FEISHU_CONNECTION_MODE=webhook`, default
`127.0.0.1:8765/feishu/webhook`) is the only case needing token/key + public URL.

## 3. Multi-agent group chat (like QQ Approach B, but no AIGC ban)

Feishu allows AIGC bots in normal groups — unlike QQ open platform which refuses
AIGC bots in ordinary group chats. Architecture:

```
Feishu group
 ├─ bot app-1 ←→ Hermes profile default (Hermes×Iris)
 ├─ bot app-2 ←→ Hermes profile artemis
 ├─ bot app-3 ←→ Hermes profile athena
 └─ ...
```
One Feishu app per agent profile; each has its own app_id so there is **no token
conflict** (unlike shared WeChat/QQ credentials). Per profile:
- `profiles/<name>/.env`: own `FEISHU_APP_ID`/`FEISHU_APP_SECRET` (+ `FEISHU_ALLOW_ALL_USERS=true`)
- `profiles/<name>/config.yaml`:
  ```yaml
  platforms:
    feishu:
      enabled: true
      extra:
        require_mention: false   # autonomous group chat (default true = only @-replies)
  ```
- Group rules per chat: `extra.group_rules: {<chat_id>: {require_mention: false}}`
- Repeat permission grant + publish per app in the Feishu console.

## 4. Multi-profile token-conflict trap (affects WeChat/QQ, not Feishu)

`gateway/config.py` auto-enables platforms from `.env` credentials —
`WEIXIN_TOKEN`/`WEIXIN_ACCOUNT_ID` → `platforms.weixin.enabled = True` (~line 2333),
`QQ_APP_ID`+`QQ_CLIENT_SECRET` → `platforms.qqbot.enabled = True` (~line 2415),
**overriding `enabled: false` in config.yaml**. If config sync copied default's
credentials into all 9 maid profiles, every profile's gateway fights for the same
token: default loses WeChat/QQ to whoever starts first.

**Fix (3 steps):**
1. `profiles/<name>/config.yaml`: `platforms.weixin.enabled: false`, `platforms.qqbot.enabled: false`
2. **Delete** `WEIXIN_*`, `QQ_*`, `QQBOT_*` keys from `profiles/<name>/.env` (backup first as `.bak-wechat-qq`) — editing config alone is NOT enough
3. Kill non-default gateway processes (Desktop respawns them with clean env; verify via psutil `environ` that `WEIXIN_TOKEN` is gone)
