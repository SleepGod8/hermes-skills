# Windows Port Conflict Debugging

When `hermes gateway start` fails with:

```
[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8001):
通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
```

## Root Cause

The gateway process tree holds multiple Python processes. The **parent** (uvicorn reloader) is killed by `process(kill)`, but the **child** (uvicorn worker) often survives because `taskkill` or `process(kill)` targets the parent PID. The child continues listening, so the next `hermes gateway start` (which may use a different port offset) finds the port taken.

## Diagnosis

Find which PID holds the port:

```bash
netstat -ano | grep PORT | grep LISTENING
# Example output:
# TCP    127.0.0.1:8001    0.0.0.0:0    LISTENING    30192
```

The last column is the PID. Kill it:

```bash
taskkill -F -PID 30192
```

## Prevention

When restarting the gateway on Windows, always do a two-step kill:
1. Kill the session background process: `process(action="kill", session_id="<id>")`
2. Check which orphan PID holds the port: `netstat -ano | grep <port>`
3. Kill orphans: `taskkill -F -PID <orphan_pid>`
4. Then start fresh: `hermes gateway start` (separate terminal call)

Avoid combining kill + start in one command — the terminal session may re-run both in the same process tree and the `hermes gateway start` call will be blocked as "inside the gateway process".
