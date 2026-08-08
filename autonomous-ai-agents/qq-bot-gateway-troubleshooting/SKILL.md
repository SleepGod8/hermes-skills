---
name: qq-bot-gateway-troubleshooting
description: "QQ 官方机器人（q.qq.com）接入 Hermes 网关的排障：连接正常但收不到消息、群聊无反应、C2C 私聊不通、AIGC 机器人平台限制。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
tags: [qqbot, gateway, troubleshooting, qq-group, c2c, aigc-bot]
related_skills: [hermes-gateway-setup, hermes-gateway-watchdog]
---

# QQ Bot 网关排障（q.qq.com 官方机器人）

QQ 官方机器人接入 Hermes gateway 的完整排障入口。**核心认知：`✓ qqbot connected` 只代表 WebSocket 连上了，不代表消息会推送** —— 事件要经过 QQ 服务器层检查（intents / 沙盒 / 进群方式 / 功能配置）才会到达 WebSocket。

## 症状 → 根因速查

| 症状 | 根因 | 修复 |
|------|------|------|
| connected + Ready，但私聊/群聊都无消息 | QQ 后台「发布上架」未配置 ≥1 个功能 | q.qq.com → 管理 → 发布上架 → Step 01 → 配置一个功能（空壳占位即可，无需过审） |
| 群聊无反应，私聊正常 | 机器人是 AIGC 类型，平台禁止进普通群；或进群方式错误 | 见下方「群聊专节」 |
| 群聊无反应，机器人已在群成员列表 | 用「邀请新成员」拉进群，未建立事件订阅 | 移除后用「加群体验」链接重新加 |
| 反复 timeout(4009) | QQ 服务器 30 分钟 session 超时，属正常；若拖死 Gateway 需禁用 | 记忆/经验：QQ 不稳时 `platforms.qqbot.enabled false` |
| WebSocket 正常但事件全无 | 回调地址填了 URL（WebSocket 模式被停用） | 回调地址**留空** |

## 诊断流程（按顺序执行）

```bash
# 1. 连接状态（只看这个会误判！）
hermes gateway status

# 2. 群事件计数 —— 0 = 平台根本没推，问题在 QQ 服务器层
grep -ciE "GROUP_AT_MESSAGE_CREATE|GROUP_MESSAGE_CREATE" "$HERMES_HOME/logs/gateway.log"

# 3. 任何 qqbot 入站（私聊能通 = 连接是活的，更说明是群路由断了）
grep -iE "inbound message: platform=qqbot" "$HERMES_HOME/logs/gateway.log" | tail -5

# 4. WebSocket 健康（token 刷新 / Ready / resume 都在这里）
grep -iE "qqbot" "$HERMES_HOME/logs/gateway.log" | tail -20
```

三层链路：`QQ 服务器层检查`（intents 开启? 沙盒? 在群里? 功能配置?）→ `WebSocket 连接` → `Hermes 适配器分发`。**服务器层任何一项不过，消息就到不了 WebSocket**，此时改 Hermes 配置毫无意义。

## 群聊专节（普通 QQ 群 vs 频道）

**普通 QQ 群：**
- AIGC 机器人（q.qq.com 后台标 AIGC，接了大模型）**平台明文禁止进普通群**：「暂不支持 AIGC 机器人进入社群场景」，沙箱配置「群配置」栏是灰的。此路不通，别折腾配置。
- 非 AIGC 机器人也必须用官方方式进群：**q.qq.com → 应用详情 → 加群体验 → 生成链接 → 群里发链接添加**。用「邀请新成员」（像拉好友那样）即使出现在成员列表，也没有事件订阅 → 群消息永远不会推。
- 加回后确认：开发设置 → Intents → 勾选「群 @消息」(GROUP_AT_MESSAGE_CREATE)；回调地址留空；沙盒模式（新机器人默认沙盒，只有开发者能交互）。

**QQ 频道（guild）：** 官方支持，Hermes 适配器处理 `GUILD_MESSAGE_CREATE` / `GUILD_AT_MESSAGE_CREATE`。想「群聊感」且要官方通道 → 频道是唯一社群类表面。

**适配器能力（adapter.py 已实测）：** intents `(1<<25)|(1<<30)|(1<<12)|(1<<26)`；事件分发覆盖 C2C_MESSAGE_CREATE / GROUP_AT_MESSAGE_CREATE / GUILD_MESSAGE_CREATE / GUILD_AT_MESSAGE_CREATE / DIRECT_MESSAGE_CREATE。注意：**不处理 `GROUP_MESSAGE_CREATE`（全量群消息，2026-07 官方文档已上线）**——想不 @ 也响应需要改 adapter 加这个事件类型 + 过滤 `author.bot` + 后台开「接收所有消息」+ `group_policy: open`。

## 配置检查点

```bash
# config.yaml → platforms.qqbot
#   app_id / client_secret / extra 同源
#   dm_policy: pairing | allowlist（不能是 open，会导致 Gateway 拒绝启动，除非配 QQ_ALLOW_ALL_USERS=true）
#   group_policy: 空=pairing（只响应 @）
# .env → QQ_ALLOW_ALL_USERS=true（group_policy: open 时必需）
# 多档案：每个 profile 一个 appId，一个 appId 只能一条 WebSocket
```

## 相关参考（已有技能，注意可能是手动作者创建、后台 curator 无法修改）

- `hermes-gateway-setup` → references/qq-multi-agent-chat.md（多机器人群聊架构 + 排查清单）、references/qqbot-c2c-no-messages.md（私聊收不到完整实录）
- `hermes-gateway-watchdog` → QQ Bot 启动坑、4009 反复断连

## Pitfalls

- **「机器人显示在群里」≠「能收群消息」**：进群方式错（邀请新成员）或 AIGC 限制，群事件计数永远为 0。
- **别在 Hermes 侧瞎调**：先看 gateway.log 有没有事件进来，0 条就去 q.qq.com 后台查，方向反了浪费时间。
- **回调地址填了 URL = WebSocket 停用**：WebSocket 模式必须留空。
- **沙盒模式**：新机器人默认只有开发者本人能交互，测试要加白名单或提审上架。
- **AIGC 机器人普通群无解**：不要追 group_policy 配置，直接告知用户换频道或第三方方案（NapCat/Lagrange/OneBot 是另一套体系，接不上官方 adapter）。
