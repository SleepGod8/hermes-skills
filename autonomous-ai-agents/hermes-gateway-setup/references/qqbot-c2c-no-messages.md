# QQ Bot C2C 消息收不到 — 完整排查实录

## 症状

- `✓ qqbot connected` + WebSocket 正常 + Identify → Ready
- Gateway running with 2 platform(s)
- 但 `gateway.log` 中**没有任何 C2C_MESSAGE_CREATE 事件**
- `hermes pairing list` 显示用户已批准
- QQ 里给机器人发私聊，机器人完全不回复

## 排查过程

### 第一阶段：检查 Hermes 侧配置

1. **回调地址** — 必须为空（WebSocket 模式）。填了任何 URL → WebSocket 停用
2. **沙箱配置** — QQ 用户需为管理员
3. **事件订阅** — C2C_MESSAGE_CREATE 等全部勾选 ✅
4. **dm_policy/group_policy** — 不能是 `open`（会导致 Gateway 拒绝启动），需设 `allowlist`
5. **`hermes pairing approve qqbot <CODE>`** — 用户已批准 ✅
6. **Adapter 源码检查** — intents 正确: `(1<<25)|(1<<30)|(1<<12)|(1<<26)`
7. **全新 Identify** (非 Resume) — 依然没有 C2C 事件

### 第二阶段：检查 Gateway 状态

- `hermes gateway status` → Gateway 运行正常
- WebSocket 连接正常，每 30 分钟 timeout + reconnect
- Access token 刷新正常
- 偶尔收到 guild (频道) Interaction 事件，证明连接是活的
- **但没有任何 C2C_MESSAGE_CREATE** — QQ 服务端根本没推

### 第三阶段：根因定位

打开 QQ 开放平台 → 管理 → **发布上架** → Step 01:

```
已配置0个功能，0个指令，0个快捷菜单
```

QQ 平台要求机器人至少配置 1 个功能/指令，才会推送 C2C 消息事件。

### 修复

点击「配置 >」→ 添加至少一个功能（哪怕是空壳占位）→ 提交审核按钮激活。

配置后 C2C 消息立即开始推送 — **无需审核通过**。

## 关键教训

| 检查项 | 正确配置 |
|--------|----------|
| 回调地址 | **留空**（WebSocket 模式） |
| 沙箱 | 管理员 QQ 号正确 |
| 事件订阅 | C2C_MESSAGE_CREATE 已勾选 |
| dm_policy | `allowlist`（不是 `open`） |
| 发布上架→功能配置 | **≥1 个功能** ← 最容易漏！ |

## 相关 QQ 开放平台页面路径

- 沙箱配置: 开发 → 沙箱配置
- 回调配置: 开发 → 回调配置
- 功能配置与提审: 管理 → 发布上架
- 功能配置详情: 管理 → 发布上架 → Step 01 → 配置 >
