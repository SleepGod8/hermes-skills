# Feishu / Lark Gateway Setup & Multi-Agent Group Chat

> Session-proven (2026-08-09): Feishu connected on Hermes default profile, permissions
> debugged via live 99991672 errors, multi-profile token conflict fixed.
> v2: removed `im:message.reaction` — user confirmed the scope does NOT exist on the
> platform (reactions are covered by `im:message`). 7 tenant scopes now.
> v3: added API-based permission verification + full 19-scope group-chat list + the
> "group @ no reply" diagnostic path (require_mention trap).

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

**Full 19-scope list for group-chat ALL-messages mode** (user-provided, 2026-08-09,
used for Hebe; includes per-scenario granular scopes beyond the 7 core):

```json
{
  "scopes": {
    "tenant": [
      "contact:user.base:readonly", "docx:document", "drive:drive",
      "im:chat", "im:chat.members:bot_access", "im:chat:readonly",
      "im:message", "im:message.group_at_msg.include_bot:readonly",
      "im:message.group_at_msg:readonly", "im:message.group_msg",
      "im:message.group_msg.include_bot:read", "im:message.p2p_msg:readonly",
      "im:message.reactions:read", "im:message:readonly",
      "im:message:send_as_bot", "im:message:send_multi_depts",
      "im:message:send_multi_users", "im:message:send_sys_msg",
      "im:resource"
    ],
    "user": ["im:chat:readonly"]
  }
}
```
Key group-chat scopes beyond the core 7: `im:message.group_at_msg:readonly`
(群 @ 消息 — the one that makes group replies work), `im:message.group_msg`
(群全量消息, 敏感权限, 自主接话推荐), `im:chat` (群信息读写),
`im:chat.members:bot_access` (机器人进出群事件).

### Verify permissions via API (when console shows 已开通 but behavior is wrong)

The console showing "已开通" + "当前修改均已发布" is not proof — hit the APIs directly
(2026-08-09: all showed 已开通 yet group events were still not flowing until
require_mention was fixed; the API check confirmed permissions themselves were fine):

```python
# 1. tenant token
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
{"app_id": "...", "app_secret": "..."}

# 2. bot info — activate_status: 2 means enabled
GET https://open.feishu.cn/open-apis/bot/v3/info

# 3. read a group — proves im:chat:readonly (bot_count reveals all bots in group)
GET https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}

# 4. send a group message — proves im:message:send_as_bot
POST https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id
{"receive_id": "...", "msg_type": "text", "content": "{\"text\":\"hi\"}"}
```

**⚠️ `receive_id_type` MUST be a query parameter**, not in the JSON body —
body placement returns `99992402 field validation failed`.

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

**Per-agent onboarding loop** (proven 6× in one session — user publishes app in
console, hands over App ID/Secret, agent wires it up in ~30s):
1. User gives `App ID` + `App Secret` (they created+published the app in console)
2. Append to `profiles/<name>/.env`: `FEISHU_APP_ID`, `FEISHU_APP_SECRET`, `FEISHU_ALLOW_ALL_USERS=true`
3. Edit `profiles/<name>/config.yaml`: `platforms.feishu = {enabled: true, extra: {require_mention: false}}`
4. Find that profile's gateway PID via psutil (`HERMES_HOME` contains profile name), `taskkill /F /PID`
5. Verify new process env has `FEISHU_APP_ID`; grep profile gateway.log for `✓ feishu connected`

**Naming note**: creating a Feishu app for a maid profile — name `Hebe`, description
"X 女仆 · Hermes 女仆家族成员". App ID URL slug appears at `/app/cli_xxx/capability/`
right after creation; user still must publish (创建版本) before it works.

### ⚠️ Symptom: "群里 @ 机器人没反应" — require_mention trap (2026-08-09 实测)

**完整诊断路径**（default 档案实战）：

1. 私聊正常（`Inbound dm message received` 有日志）、机器人已进群（`Bot added to chat`
   有日志）、群发/读群 API 都成功——**但群消息事件日志 = 0 条**，群里 @ 机器人无反应。
2. **先查 config 的 `require_mention`**：adapter 默认 `require_mention: bool = True`
   （`adapter.py` ~line 438），群消息**必须 @ 机器人**才被接受。之前给 default 配飞书时
   只设了 `enabled: true` 忘了设 `require_mention: false`（其他女仆档案都设了 false）→
   @ 时 `_admit` 返回 `group_policy_rejected`，且该拒绝只打 **debug 级别**日志
   （`logger.debug("[Feishu] dropping inbound event: %s", reason)`），info 日志完全看不到！
3. **修复**：config.yaml 补 `extra.require_mention: false` + 重启 gateway。重启后群消息即恢复。

**排查要点**：
- `_admit` 的拒绝全是 debug 级，默认日志看不到 → 别用 `grep inbound` 找原因，直接核对配置。
- 群消息要进来还需要平台侧三件套齐全：权限（`im:message.group_at_msg:readonly` 或
  `im:message.group_msg`）+ 事件订阅（`im.message.receive_v1` + 长连接）+ 已发布版本。

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

## 5. Browser automation of open.feishu.cn (Hermes Studio browser MCP)

Full app-creation path proven 2026-08-09 (Agent creates app, user only logs in):

1. **Login is JS-rendered — user must log in manually** in the Desktop browser tab.
   Snapshot shows only RootWebArea, screenshot is 1×1 until login completes.
2. Create app: `https://open.feishu.cn/app` → 「创建企业自建应用」 dialog → name (≤32) + description (≤120).
   **Pitfall:** dialog textboxes' refs are misordered — verify via snapshot that the right field got the value
   (user reported "应用名称是空的" when ref pointed at the description box). Re-snapshot after every type.
3. On success URL becomes `/app/cli_xxx/capability/` → add 机器人 capability.
4. Permissions: navigate directly to `https://open.feishu.cn/app/cli_xxx/auth` → 「批量导入/导出权限」.
   **Pitfall:** the JSON editor is Monaco-like — `type` APPENDS at cursor instead of replacing.
   Clear first: `press Control+a` then `press Backspace`, then type. 「下一步」stays disabled until JSON parses;
   re-snapshot to confirm it lights up. → 「申请开通」→ confirm data-range dialog → done (7 scopes show 已开通).
5. Events: `https://open.feishu.cn/app/cli_xxx/event` → 「订阅方式」→ 长连接 radio → 保存 →
   「添加事件」→ category 消息与群组 → 接收消息 (`im.message.receive_v1`) → 添加 →
   「推荐开通以下权限」dialog → 确认开通权限.
6. Publish: top-right 「创建版本」→ submit (permissions/events only take effect after publish).

**Generic browser-MCP rules (any SPA, not just Feishu):**
- Snapshots go stale after every interaction — always re-snapshot before click/type; nested dialogs renumber ALL refs.
- Long lists truncate (>15k chars) — `scroll down` in pages, then re-snapshot to reach bottom items.
- Monaco/code-editor type = append-at-cursor, never replace — Ctrl+A + Backspace to clear first.
