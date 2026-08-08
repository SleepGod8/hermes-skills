---
name: hermes-gateway-watchdog
description: "Gateway watchdog setup and QQ Bot startup pitfalls."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [hermes, gateway, watchdog, scheduled-task, qqbot, auto-recovery]
---

# Hermes Gateway Watchdog & Platform Startup

Automatic recovery for the Hermes messaging gateway (WeChat/Weixin, QQ Bot, etc.) on Windows, plus platform-config pitfalls that take the whole gateway down. Companion to `hermes-troubleshooting` (diagnosis) and `hermes-gateway-setup` (initial platform setup) — this skill covers the *self-healing* layer.

## When to Use

- Gateway keeps stalling (event loop stalled) or dying and the user is tired of manual restarts
- User asks to make the gateway auto-restart / install as a service / "以后不用管它"
- A platform config change caused `Gateway exiting cleanly` / refusal to start
- Diagnosing why QQ Bot connects but receives nothing

## Core fact: cronjob tool refuses gateway lifecycle commands

The Hermes `cronjob` tool blocks jobs containing gateway restart/stop/kill commands (SIGTERM respawn-loop protection). **Do not fight it** — use a Windows Scheduled Task for watchdogs.

## Watchdog via Windows Scheduled Task (no admin rights needed)

Create the task **without admin** by OMITTING `/ru` and `/rl highest` — including them triggers `拒绝访问` / access denied (exit 1) unless elevated.

```bash
schtasks /create /tn "Hermes Gateway Watchdog" /tr "python C:\Users\80704\AppData\Local\hermes\scripts\gateway-health-check.py" /sc minute /mo 5 /f
```

Verify: `schtasks /query /tn "Hermes Gateway Watchdog" /fo LIST` → expect `模式: 就绪` and a `下次运行时间`.
If taken/deleted: `schtasks /delete /tn "Hermes Gateway Watchdog" /f` then recreate.
Read task output with `schtasks /query /fo CSV /v` (UTF-16; pipe through `iconv -f gbk -t utf-8` on Chinese Windows to read it).

Place the health-check script via `scripts/gateway-health-check.py` in this skill → copy to `%HERMES_HOME%\scripts\`.

**Design contract for the health-check script** (watchdog / no_agent pattern):
- `hermes gateway status` with 10s timeout; if stdout contains "running" → `sys.exit(0)` (healthy, silent)
- On timeout / not-running → `taskkill /F /FI "IMAGENAME eq hermes.exe" /FI "MEMUSAGE gt 300000"` (kill only the bloated stuck process), then `hermes gateway run --replace`, print a restart notice
- Empty stdout = silent when healthy; non-empty = alert/notice when action taken
- Tune the MEMUSAGE threshold to the bloated-process size you observe in Task Manager

## ⚠️ 多档案抢 token：.env 凭据强制启用平台（2026-08-09 实测）

**症状**：default 档案的微信/QQ 突然断连，日志显示 `Weixin bot token already in use (PID xxx)` / `QQBot app ID already in use (PID xxx)`，占用者是非 default 档案的 gateway 进程。改了 `profiles/<名>/config.yaml` 的 `enabled: false` 也没用。

**根因**：`gateway/config.py` 有自动启用逻辑——**只要 .env 里有 `WEIXIN_TOKEN`/`WEIXIN_ACCOUNT_ID` 或 `QQ_APP_ID`+`QQ_CLIENT_SECRET`，就会强制 `platforms.weixin.enabled = True` / `platforms.qqbot.enabled = True`，覆盖 config.yaml 的 false**（config.py ~2333 行 weixin、~2415 行 qqbot）。多档案同步配置时把 default 的 .env 凭据复制给了所有档案 → 每个档案的 gateway 进程都抢同一个 token。

**修复**（三步）：
1. `profiles/<名>/config.yaml` 里 `platforms.weixin.enabled: false` + `platforms.qqbot.enabled: false`
2. **删掉** `profiles/<名>/.env` 里的 `WEIXIN_*`、`QQ_*`、`QQBOT_*` 全部键（先备份 `.bak-wechat-qq`）——光改 config 无效！
3. 杀掉非 default 的 gateway 进程（Desktop 会自动用新配置重启；验证：`psutil` 查进程 environ 里 `WEIXIN_TOKEN` 应为 False）

**飞书（Feishu）接入要点**：插件在 `plugins/platforms/feishu/`（官方自带），`.env` 配 `FEISHU_APP_ID` + `FEISHU_APP_SECRET` + `FEISHU_ALLOW_ALL_USERS=true`，config.yaml 加 `platforms.feishu.enabled: true` 即可。**无独立 toolset**（`hermes-feishu` 只是线程名前缀，不要加进 platform_toolsets 否则启动报错）。飞书支持多 agent 协作（Approach B：每档案一个飞书应用 + profile，群 @ 触发），比 QQ 强——AIGC 机器人也能进普通飞书群。**完整接入步骤、7 项权限清单（99991672 Access denied 排查）、完整 19 项群聊权限清单、API 实测验证权限（`receive_id_type` 必须 query 参数）、「群里 @ 没反应」的 require_mention 诊断路径、Monaco 编辑器自动化坑全部见 `references/feishu-setup.md`**（v3，2026-08-09 实战），批量导入 JSON 模板在 `templates/feishu-scopes-batch-import.json`。⚠️ `im:message.reaction` 在飞书平台**不存在**（实测批量导入报错），表情回应由 `im:message` 涵盖——不要把它加进权限清单。**⚠️ `require_mention` 默认是 True**：群聊自主接话必须显式配 `extra.require_mention: false`，否则群里 @ 机器人没反应（拒绝只打 debug 日志，info 日志看不到）。

## ⚠️ 看门狗误杀 Desktop 的致命坑（2026-08-07 实测）

**症状**：Hermes Desktop 端每 5 分钟断开一次；agent.log 显示 `gateway.lifecycle_ledger: Previous gateway life ... exited UNCLEANLY (SIGKILL / OOM / VM death)` 每 5 分钟一条，`suspected_oom=False`。

**根因**：看门狗脚本 `gateway-health-check.py` 的 taskkill 条件是
`taskkill /F /FI "IMAGENAME eq hermes.exe" /FI "MEMUSAGE gt 300000"`——两个致命缺陷：
1. **IMAGENAME 误杀**：`hermes.exe` 同时匹配 **Hermes Desktop（Electron）主进程** 和 gateway venv 入口进程；Desktop 主进程内存 **300-600MB 是正常水平**，300MB 阈值必杀 → Desktop 整个被杀 → 桌面端断开 + gateway 重启。
2. **`hermes gateway status` 10s 超时太紧**：gateway 忙（API 慢/大会话）时 status 超时 → 看门狗误判"无响应" → 走 taskkill 分支。

**修复**（已验证）：`timeout=10`→`timeout=30`，`MEMUSAGE gt 300000`→`MEMUSAGE gt 1500000`（只杀真正内存爆炸的）。改完计划任务下次运行即生效，无需重启任务。验证：观察 Hermes 进程连续两个 5 分钟周期不被杀。

**经验**：看门狗宁可"漏杀"不可"误杀"——误杀 Desktop 的代价是用户桌面端整个断开，比 gateway 卡住更糟。

## ⚠️ status 误报 → 看门狗反复杀真 gateway（2026-08-07 追加，止血已验证）

**症状**：修复 MEMUSAGE 阈值后 gateway 仍每 5 分钟 SIGKILL 一次（agent.log `lifecycle_ledger ... exited UNCLEANLY (SIGKILL)` 每 5 分钟一条，`suspected_oom=False`）。

**根因**：`hermes gateway status` 对 **Desktop/计划任务(Hermes_Gateway) 启动的 gateway 间歇性误报 "✗ No gateway process detected"**——手动 `hermes gateway run --replace` 启动的能检测到（`✓ Gateway process running (PID: ...)`），Desktop 拉起的检测不到。看门狗误判 not running → 走脚本第 3 步 `gateway run --replace` → **杀掉真实 gateway** → 新 gateway 起来 → 5 分钟后重复。这是比 300MB 阈值更深的坑：即使 status 大部分时间正常，只要某次误报就会触发杀进程。

**止血方案（已验证有效）**：
```bash
schtasks /change /tn "Hermes Gateway Watchdog" /disable   # 禁用计划任务
hermes gateway run --replace                              # 手动拉起（确认无残留进程）
# 验证：gateway status 显示 running + agent.log 出现 ✓ weixin connected + response ready
```
禁用看门狗后 gateway 稳定（代价：失去自动恢复能力，需 Desktop 或手动接管）。

**根治方向（未完成，勿当已验证方案）**：查 `hermes gateway status` 的进程检测实现（PID 文件 vs 进程名匹配，为何 Desktop 启动方式检测不到）；或把看门狗改为"status 误报时只告警不杀，连续 N 次才重启"。

## Platform-config pitfall: QQ Bot 'open' policy kills the WHOLE gateway

**Symptom**: `gateway.log` shows `ERROR gateway.run: Refusing to start: qqbot has dm_policy/group_policy set to 'open' but neither GATEWAY_ALLOW_ALL_USERS nor QQ_ALLOW_ALL_USERS is enabled` then `Gateway exiting cleanly`. **ALL platforms go down** (WeChat too), because the refusal happens at gateway startup.

**Fix** (verified working):
```bash
hermes config set platforms.qqbot.dm_policy allowlist
hermes config set platforms.qqbot.group_policy allowlist   # MUST set BOTH — startup check reads both
hermes gateway run --replace
```
Alternative: enable `GATEWAY_ALLOW_ALL_USERS=true` / `QQ_ALLOW_ALL_USERS=true` to keep 'open'.

## QQ Bot platform facts (verified by observation)

- **WebSocket code 4009 "Session timed out" every ~30 min is NORMAL.** The server sends `op 7` (request reconnect) → close 4009 → adapter reconnects in 2s → `Resume sent` → `Session resumed`. Do not treat as a failure or chase it.
- **Hermes QQ Bot is WebSocket-based.** In the QQ developer platform (q.qq.com), the HTTPS callback URL field must stay **EMPTY** — the platform warns that configuring an HTTPS callback disables the WebSocket callback service, after which Hermes receives nothing.
- QQ Bot needs the sending user approved: `hermes pairing list` shows approved qqbot users; sandbox page (沙箱配置) must list the sending QQ account as member/admin.
- Access-token DNS errors (`getaddrinfo failed` on refresh) are transient — next refresh succeeds.

## QQ Bot C2C messages stopped arriving — diagnostic checklist (partially UNVERIFIED)

Observed: C2C messages flowed (13:41–13:58), then a full day of zero deliveries despite connected+Ready+Identify. None of these were confirmed to fix it by session end — treat as candidates, verify each:

1. Delete the bot conversation in the QQ client, re-search the bot, send fresh (clears client-side stale connection cache)
2. Check q.qq.com 回调配置: callback URL must be empty (WebSocket mode)
3. Check 沙箱配置: sending account listed as admin/member
4. 功能配置/发布上架: platform requires ≥1 configured feature before 提审; "已配置0个功能" is normal for sandbox testing but review gates on it
5. Restart gateway with a fresh Identify (kill process, `hermes gateway run --replace` — a Resume may carry stale session state)

## ✅ VERIFIED (2026-07-20): minimal config is the fix that worked

After a full day of C2C silence, the fix that actually restored QQ replies was **REMOVING every extra policy flag** and going back to the minimal config — identical to the user's other machine that "just works" with no QQ-platform-side settings:

```yaml
platforms:
  qqbot:
    enabled: True
    app_id: 1905221985
    client_secret: <secret>
    extra:
      app_id: 1905221985
      client_secret: <secret>
    dm_policy: pairing
    # NO group_policy, NO allow_all — leave them unset/empty
```

**What did NOT help / actively hurt:**
- Setting `dm_policy: open` / `group_policy: open` → gateway refuses to start unless `QQ_ALLOW_ALL_USERS=true` is actually picked up by the process. Writing it to `~/.hermes/.env` did **NOT** get picked up by the gateway process → still `Refusing to start` → then `qqbot.enabled` was silently flipped to `False` when the policy keys were cleared with empty strings.
- `allow_all: True` in config did not enable messaging; user's working machine has none of it.

**Restore sequence that worked:**
```bash
hermes config set platforms.qqbot.enabled "true"        # check it didn't flip to False
hermes config set platforms.qqbot.dm_policy "pairing"
hermes config set platforms.qqbot.group_policy ""       # clear
hermes config set platforms.qqbot.allow_all ""          # clear
hermes gateway run --replace
```
Then confirm in logs: `✓ qqbot connected` + `Ready, session_id=...` + **fresh `inbound message: platform=qqbot`** after the user sends.

**QQ group chat is NOT supported for AIGC bots** (QQ platform restriction, 2026-07): "暂不支持 AIGC 机器人进入社群场景" — the q.qq.com 沙箱配置 page shows 群配置 as 暂不支持. Do not chase group_policy for AIGC bots; C2C (private message) is the working channel. QQ 频道 (guild/channel) config exists separately on the platform and is the only community-ish surface.

**Also: 把机器人拉进普通群必须用「加群体验」链接，不是「群成员邀请」**（2026-08-09 实测）：
官方机器人（AIGC 类）不能用普通「邀请新成员」拉群——即使机器人出现在成员列表里，QQ 服务器也不会推送
`GROUP_AT_MESSAGE_CREATE`/`GROUP_MESSAGE_CREATE` 事件（网关日志事件计数恒为 0，连接却正常）。
正确姿势：q.qq.com → 应用详情 → **加群体验** → 生成链接 → 群成员点链接添加。
且 AIGC 机器人的「群配置」在沙箱页本来就是灰的（平台禁止进普通群），所以普通群这条路基本无解，
替代方案：QQ 私聊（C2C）/ QQ 频道 / 飞书（飞书无此限制）。

## Pitfalls

- `hermes gateway run` (no `--replace`) fails with "Another gateway instance is already running (PID ...)" when the lock file survives a killed process — always use `--replace` after killing.
- `hermes gateway restart/stop` are blocked from inside the gateway process tree — kill externally + `--replace` instead.
- After killing a process, the Desktop GUI logs `render-process-gone reason=killed` but does **NOT** auto-restart the gateway — the Scheduled Task is what brings it back.

## Profile routing pitfall (gateway.profile_routes)

Hermes supports per-chat routing to independent profiles (`gateway/profile_routes` in config.yaml, see `gateway/profile_routing.py` — hierarchical match on platform + chat_id + thread_id, most specific wins). **Pitfall**: routes are chat_id-bound — one chat routes to exactly one profile. If you route the chat the user is *currently talking in* to another profile, the current persona is replaced instantly (user suddenly talks to a different character). Confirm which chat a chat_id belongs to before adding a route; leave the active conversation un-routed. For switching personas within the SAME chat, use `/personality <name>` (main profile's preset library), not profile routes. Profile routes suit "different chat/group → different profile" setups only.

Full multi-profile editing recipe (sub-profile SOUL.md + config.yaml `agent.system_prompt` two-place sync, underage-profile safety boundary): `references/multi-profile-personas.md`.
