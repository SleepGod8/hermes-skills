# 群聊「正在总结」/ summarize-queue deadlock — diagnosis & DB fix (2026-08-16)

## Symptom

After a Hermes Studio update, a group-chat room shows **「正在总结」/ summarizing
forever** (and/or「消息队列加载中」). Messages @Agent never execute. This is a
**database-level deadlock**, deeper than the stale-tab socket resume loop
(`group-chat-message-queue-loading-2026-08.md`) — both can co-occur, but the
summarize deadlock needs a DB write to clear, not just a restart.

## Root cause (from evidence)

1. The room auto-summarizes every N turns (`gc_rooms.summaryEveryTurns`, e.g. 20).
2. The summarize run started (`gc_room_summaries.status = 'summarizing'`) and
   **Studio restarted mid-run** → the summary task never finished.
3. Messages @Agent'd while summarizing are parked in `gc_execution_queue` with
   `status='queued'`; on restart they die with
   `lastError='Studio restarted before queued work started'` but the summary
   lease stays stuck → frontend shows「正在总结」forever, new messages never dispatch.

## Diagnosis (all in the WebUI DB, NOT state.db)

DB: `C:\Users\<user>\.hermes-web-ui\hermes-web-ui.db` (sqlite3, WAL mode).
The Hermes state.db has `gc_run_%` sessions but no summary/queue state — don't
waste time there for this symptom.

```sql
-- 1) Stuck summary? status stays 'summarizing' (lease long expired)
SELECT roomId, status, summarizedTurnCount, summaryRunToken,
       summaryLeaseExpiresAt, lastError
FROM gc_room_summaries;

-- 2) Queued-but-never-started executions?
SELECT id, roomId, targetAgentName, textSummary, sequence,
       status, lastError
FROM gc_execution_queue WHERE status IN ('queued','failed')
ORDER BY sequence;

-- 3) Room summary config (how often it summarizes)
SELECT id, name, summaryEveryTurns, summaryModel FROM gc_rooms;
```

Supporting log evidence:
- `~/.hermes-web-ui/logs/server.log` — `[GroupChat] Restored N agent(s)` means
  agents ARE alive (not the fault); `[chat-run-socket] ... resumed session ...
  working: false` is the stale-tab loop; group-chat dispatch happens via
  Socket.IO `/group-chat`.
- `~/AppData/Local/hermes/logs/bootstrap-installer.log` — confirms the update.

## Fix (backup first, then UPDATE the WebUI DB)

```python
import sqlite3, datetime
src = r'C:\Users\<user>\.hermes-web-ui\hermes-web-ui.db'
bak = src + '.bak-YYYYMMDD-HHMM'
# WAL-safe backup via sqlite3 backup API (do NOT copy the file while Studio runs)
s = sqlite3.connect(src); d = sqlite3.connect(bak); s.backup(d); d.close(); s.close()

db = sqlite3.connect(src)
now_ms = int(datetime.datetime.now().timestamp() * 1000)

# 1) Clear stuck summary -> 'completed'
db.execute("""
    UPDATE gc_room_summaries
    SET status='completed',
        summaryRunToken='',           -- NOT NULL, default '' — cannot use NULL
        summaryLeaseExpiresAt=0,      -- NOT NULL, default 0
        lastError='cleared manually YYYY-MM-DD (stuck summarizing after Studio update)'
    WHERE status='summarizing'
""")

# 2) Parked queue tasks -> 'failed' so frontend stops waiting
db.execute("""
    UPDATE gc_execution_queue
    SET status='failed',
        lastError='cleared manually YYYY-MM-DD (stuck queued after Studio update)',
        finishedAt=?
    WHERE status='queued'
""", (now_ms,))
db.commit(); db.close()
```

Then **fully restart Studio** (`taskkill /F /IM "Hermes Studio.exe"`), reopen,
and verify `server.log` shows `[GroupChat] Restored N agent(s)`. The @Agent
message that was stuck must be re-sent by the user.

## Pitfalls

- `gc_room_summaries.summaryRunToken` is NOT NULL — use `''` not `NULL`
  (same for `summaryLeaseExpiresAt` → `0`).
- config.yaml is protected; the WebUI DB is NOT — direct UPDATE is the fix path.
- Backup via `sqlite3.Connection.backup()` (WAL-safe), not a raw file copy.
- `errors.log` may show `Auxiliary: marking openrouter/nous unhealthy (payment /
  credit error)` — that is a distractor, unrelated to the summarize deadlock.
- Restarting alone does NOT clear the stuck `summarizing` row; the DB write is
  the actual fix (the session's first restart attempt confirmed tasks die with
  "Studio restarted before queued work started" and the summary stayed stuck).
