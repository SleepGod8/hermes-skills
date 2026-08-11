# 案例：群聊 @Athena 显示「操作已中断」（2026-08-11）

## 用户报告

Hermes Studio 群聊房间 @Athena 后显示「操作已中断」。

## 关键日志证据（~/AppData/Local/hermes/logs/desktop.log）

`[hermes]` 前缀行，无时间戳（按顺序读）：

```
⚠️  API call failed (attempt 1/3): APITimeoutError
🔌 Provider: nous  Model: tencent/hy3:free
🌐 Endpoint: https://inference-api.nousresearch.com/v1
📝 Error: Request timed out.   (24.21s → 47.73s → 74.67s, 3 retries all timeout)
❌ API failed after 3 retries — Request timed out.
💀 Final error: Request timed out.
⚡ Interrupted during API call.          ← 前端「操作已中断」的日志签名
```

Profile backend 生命周期抖动（LRU cap 3 / idle 600s）：

```
[hermes] Evicting idle profile backend "athena" (LRU cap 3)
[hermes] Reaping idle profile backend "athena" (idle > 600s)
[hermes] Hermes backend for profile "athena" exited (1)
[hermes] Hermes backend for profile "athena" exited (1073807364)
[hermes] Starting Hermes backend for profile "athena" via Hermes at C:\Users\80704\AppData\Local\hermes\hermes-agent ...
[hermes] HERMES_BACKEND_READY port=12735
[hermes] [renderer console] Uncaught (in promise) Error: Error invoking remote method 'hermes:api': Error: read ECONNRESET
```

群聊 run session 成批孤儿回收：

```
{"type": "session.reclaimed", "session_id": "...",
 "payload": {"stored_session_id": "gc_run_msj4sa3xsgaj6y_athena_Athena_fa3b01c0...",
             "reason": "ws_orphan_reap"}}
```

## state.db 群聊 run 模型确认

```
SELECT id, model, end_reason, message_count, input_tokens, output_tokens
FROM sessions WHERE id LIKE 'gc_run_%' ORDER BY rowid DESC;

gc_run_msj4sa3xsgaj6y_default_Hermes___Iris_92ee60fd... | model: deepseek-v4-flash | msgs: 7 | tokens: 33136/1209
```

- 群聊 run 实际走 deepseek-v4-flash（档案 config 正常），不是 nous 免费通道
- `gc_run_<room>_<profile>_<Agent>_<hash>` 命名规则：房间+档案+Agent 名
- profile_name 列在 athena 的 session 里为 None（session 归属 main db，profile 独立后端）

## 网络实测（当时）

```
nousresearch: 404 1.77s   (可达但慢 — 免费通道不稳定)
deepseek:     401 0.14s   (正常，主路径没问题)
```

## 结论与修复

- 主因：10 个女仆档案抢 LRU cap 3 槽位 → Athena 后端频繁被杀 → @ 时赶上
  冷启动/驱逐 → ECONNRESET → 操作已中断
- 诱因：nous 免费通道 74s 超时（若房间走了该通道会加剧）
- 修复：重试 @ → 减少房间活跃档案 → 完全重启 Studio（taskkill Hermes Studio.exe
  + python.exe 后端）→ 确认 Agent 模型用档案自己的 deepseek 配置
