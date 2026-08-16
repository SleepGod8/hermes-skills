# 群聊「消息队列加载中」after Studio update — diagnosis (2026-08-16)

## Symptom

After a Hermes Studio update, sending a message in a group-chat room shows
「消息队列加载中」/ "message queue loading" forever. New messages never render,
no agent replies appear. Distinct from「操作已中断」(see
`group-chat-interrupted-2026-08.md`).

## Root cause (from evidence)

The agents are NOT dead. `~/.hermes-web-ui/logs/server.log` shows every profile
backend joining its rooms:

```
[AgentClients] Athena joined room: msj4sa3xsgaj6y
[GroupChat] Restored 9 agent(s) across 2 room(s)
```

The stuck state is the **frontend chat-run-socket repeatedly resuming a stale
session**:

```
[chat-run-socket] socket OrIHpt3CaHIiq7C-AAAg resumed session msu1jmopxqnwlb (working: false, messages: 150)
```

`working: false` = backend has no active task, yet the frontend keeps re-attaching
to that old session (an old tab open before the update) and never refreshes the
room view → the message sits in the queue forever.

## Evidence chain used

1. `~/AppData/Local/hermes/logs/bootstrap-installer.log` — confirm the update
   happened (`✓ Update complete`, per-profile skill sync e.g. `nemesis: +12 new`).
2. `~/.hermes-web-ui/logs/server.log` — grep:
   - `resumed session .*working: false` → the looping session id
   - `AgentClients .* joined room` → agents healthy
   - `GroupChat] Restored N agent(s)` → rooms restored
3. `~/AppData/Local/hermes/state.db` — identify the stale session:
   ```sql
   SELECT id, title, started_at, last_activity_at, message_count
   FROM sessions WHERE id='<sessionId>';
   ```
   It's usually an ordinary (non-room) chat tab left open before the update.
4. Distractors to ignore (not the cause): `Auxiliary: marking openrouter/nous
   unhealthy (payment / credit error)` in agent.log, `RuntimeError: No response
   returned` in desktop.log, `ws closed` spam in gui.log, gateway QQ/weixin
   reconnect noise in gateway.log.

## Fix

1. **Full Studio restart** — `taskkill /F /IM "Hermes Studio.exe"` and
   `taskkill /F /IM "Hermes.exe"` (kills stale python backends too), reopen.
   Clears the socket resume loop.
2. **Close the stale tab** — find the session title via state.db, close that
   tab in Studio before using the room.
3. If it persists: mark the stale session ended in state.db (backup first):
   ```sql
   UPDATE sessions SET end_reason='killed' WHERE id='<sessionId>';
   ```

## Note

The same day the update also auto-started a gateway per profile (10 backends for
10 maid-family profiles) — that's expected Studio behavior, not itself a fault.
