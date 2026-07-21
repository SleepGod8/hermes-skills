# Hermes QQ Bot Gateway Setup

## Config Format (Critical)

The platform key is **`qqbot`** (not `qq`). Credentials go under **`extra`**:

```yaml
platforms:
  qqbot:
    enabled: true
    extra:
      app_id: "your-app-id"
      client_secret: "your-secret"
```

Set via CLI:
```bash
hermes config set platforms.qqbot.enabled "true"
hermes config set platforms.qqbot.extra.app_id "APP_ID"
hermes config set platforms.qqbot.extra.client_secret "SECRET"
```

**DO NOT use `platforms.qq.*` — that's a wrong key ignored by the gateway.**

## Minimal Config Rule (新增 — v1.2)

**最简配置即可工作，不要加多余设置。**

有效的配置只需：
```yaml
qqbot:
  enabled: true
  extra:
    app_id: "..."
    client_secret: "..."
```

默认的 `dm_policy: pairing` + 已批准用户 = 正常工作。

**不要画蛇添足**：加了 `group_policy: "open"`、`allow_all: true` 等多余字段反而会破坏默认配对机制，导致私聊也收不到消息。

如果 QQ 连上但不回消息，先精简配置到最小，重启网关：
```bash
hermes config set platforms.qqbot.dm_policy ""
hermes config set platforms.qqbot.group_policy ""
hermes config set platforms.qqbot.allow_all ""
hermes gateway run --replace
```

## Code Fix: `is_reconnect` Parameter

QQAdapter.connect() signature in v0.18.2 may lack the `is_reconnect` keyword argument that newer gateway runners pass. Symptom:
```
✗ qqbot error: QQAdapter.connect() got an unexpected keyword argument 'is_reconnect'
```

Fix (in `gateway/platforms/qqbot/adapter.py` line ~281):
```python
# Before:
async def connect(self) -> bool:

# After:
async def connect(self, is_reconnect: bool = False) -> bool:
```

## Pairing / Allowlist

QQ gateway defaults to **pairing mode**. Approved users persist across restarts (`hermes pairing list`).

To approve a pending user:
```bash
hermes pairing approve qqbot <CODE>
```

**Open policy requires env var** — setting `dm_policy: open` without `QQ_ALLOW_ALL_USERS=true` will **refuse to start**:
```
ERROR: qqbot has dm_policy set to 'open' but QQ_ALLOW_ALL_USERS is not enabled
```

Write to `.env` for persistence:
```bash
echo "QQ_ALLOW_ALL_USERS=true" >> ~/AppData/Local/hermes/.env
```

**Warning**: Setting `dm_policy: open` via `hermes config` may silently toggle `enabled: false`. Always verify with:
```bash
python3 -c "import yaml; cfg=yaml.safe_load(open('config.yaml')); print(cfg['platforms']['qqbot'])"
```

**Recovery**: If QQ disappeared after policy change:
```bash
hermes config set platforms.qqbot.dm_policy ""
hermes config set platforms.qqbot.group_policy ""
hermes config set platforms.qqbot.enabled "true"
hermes gateway run --replace
```

## QQ Open Platform Requirements

The bot must be **published** on [q.qq.com](https://q.qq.com), not in sandbox mode. 
- Sandbox → only developer can message
- Production → all users can message after adding bot as friend

In QQ app: search bot name → add as friend → send message.

## QQ 群聊限制 (新增)

QQ 开放平台目前**不支持 AIGC 机器人进入社群场景**。沙箱配置页面明确标注：
> 暂不支持群相关配置，敬请期待

Bot 只能用于私聊，不能加入 QQ 群。这是 QQ 平台限制，不是 Hermes 配置问题。

## Startup Log Signals

Healthy startup:
```
Connecting to qqbot...
Access token refreshed, expires in 7200s
WebSocket connected to wss://api.sgroup.qq.com/websocket
Ready, session_id=...
Gateway running with 2 platform(s)
```

Silent skip (config issue): No "Connecting to qqbot" line → check `enabled: true` and `extra.app_id/client_secret` presence.
