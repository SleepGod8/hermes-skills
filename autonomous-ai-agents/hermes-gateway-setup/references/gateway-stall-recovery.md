# Gateway Stall Recovery — Session Transcript

Detailed transcript of diagnosing and recovering from a WeChat gateway event-loop stall (GIL pressure) on Windows 10.

## Environment

- **OS**: Windows 10, Hermes Desktop (GUI mode)
- **Platform**: WeChat/Weixin (iLink bot)
- **Model**: deepseek-v4-pro
- **Date**: 2026-07-10

## Timeline

### 13:10:08 — Last successful message
Gateway processed a WeChat "在吗？" message and sent a 138-char response normally. Then gateway.log goes silent.

### 13:13:03 — Event loop stall detected
`errors.log`:
```
hermes_cli.web_server: event loop stalled 13.9s (GIL pressure suspected)
```

### 13:19 — User reports: "我的微信会话怎么卡住了没回应？"

### Diagnosis Attempts

**All `hermes` CLI commands timed out** — gateway process still alive but event loop blocked:
```bash
hermes gateway status 2>&1    # [Command timed out after 10s]
hermes doctor 2>&1            # [Command timed out after 30s]
hermes gateway list 2>&1      # [Command timed out after 10s]
```

**Process check** — 8 Hermes processes running, one bloated at 696MB:
```bash
$ tasklist | grep hermes
Hermes.exe   3192   Console   276,044 K
Hermes.exe  27188   Console   345,296 K
Hermes.exe  37516   Console    30,280 K
Hermes.exe  29640   Console   696,392 K   # ← bloated gateway
Hermes.exe  20420   Console    19,940 K
hermes.exe  28456   Console     1,204 K
hermes.exe  31996   Console     1,304 K
hermes.exe  25544   Console     1,468 K
```

**Log analysis** — gateway.log last entry at 13:10:08, confirming stall.

### Recovery Steps

**1. Kill attempt blocked (no /F):**
```bash
taskkill /PID 29640
# → "无法终止 PID 为 29640 的进程。原因: 只能强制终止此进程 (带 /F 选项)。"
```

**2. Force kill:**
```bash
taskkill /F /PID 29640
# → "成功: 已终止 PID 为 29640 的进程。"
```

**3. GUI didn't auto-restart** — `desktop.log` showed:
```
[renderer] render-process-gone reason=killed exitCode=1
```
But no auto-restart. Process count dropped from 8 to 7.

**4. Plain restart failed — stale lock file:**
```bash
hermes gateway run 2>&1
# → "Another gateway instance is already running (PID 31584)."
```
PID 31584 was a zombie reference — the actual process was gone, but `.__gateway.lock` persisted.

**5. Lock file removal failed:**
```bash
rm -f "$HERMES_HOME/logs/.__gateway.lock"
# → "Device or resource busy"
```

**6. `--replace` flag succeeded:**
```bash
hermes gateway run --replace 2>&1
```

**7. Gateway reconnected at 13:22:07:**
```
Starting Hermes Gateway...
[Weixin] Connected account=581ac597 base=https://ilinkai.weixin.qq.com
✓ weixin connected
Gateway running with 1 platform(s)
```

## Key Takeaways

1. **GIL stall ≠ crash**: Process stays alive, PID visible in tasklist, but event loop frozen. All Hermes CLI commands timeout.
2. **Kill externally, never from inside**: `hermes gateway restart` / `stop` are blocked within the process tree. Use `taskkill /F /PID <pid>`.
3. **Lock file survives kill**: `.__gateway.lock` persists after process death. `rm` fails with "Device or resource busy". `--replace` is the ONLY way to bypass.
4. **GUI doesn't auto-restart**: Desktop renderer logs the kill but doesn't respawn the gateway. Manual restart required.
5. **Look for the bloated process**: Normal Hermes processes are ~20-350MB. A gateway under GIL pressure bloats to ~700MB.

## Alternative: Full GUI Restart

If `--replace` also fails, restart the entire Hermes Desktop application. This is more disruptive but guarantees a clean slate.
