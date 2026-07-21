# Multi-Agent QQ Group Chat

Architecture and configuration for running multiple Hermes instances as distinct characters chatting in the same QQ group.

## Architecture

Two approaches:

### Approach A: Single QQ Bot + Multi-Character Prompt
One QQ Bot, one Hermes, one SOUL.md defining multiple characters. All share the same QQ bot name/avatar.

### Approach B: Multi-Bot + Multi-Profile (Recommended)
Each character has its own QQ Bot account, Hermes profile, and SOUL.md. Each runs independently.

```
QQ Group ←→ QQ Bot A (appId-1) ←→ Hermes Profile "xiaomeng"
          ←→ QQ Bot B (appId-2) ←→ Hermes Profile "laozhang"
```

**Pros:** Independent QQ name/avatar per character, different models per character, cross-computer.
**Cons:** Need N QQ Bot registrations at q.qq.com.

## Prerequisites: QQ Bot Registration

Each character needs its own QQ Bot at [q.qq.com](https://q.qq.com):
1. Unique QQ account per bot — but ONE QQ account CAN register multiple bot apps, each with its own appId.
2. Note **AppID** and **AppSecret**
3. Enable intents: C2C messages, Group @-messages, Guild messages
4. Invite bot to target QQ group (q.qq.com → 应用详情 → 加群体验)

**Critical:** One appId = one WebSocket connection. Two Hermes instances cannot share the same appId. But one QQ account can register N bots, all usable in the same group.

## Quick-Start Checklist

Before debugging anything else, verify these 5 items:

- [ ] `.env` has `QQ_ALLOW_ALL_USERS=true` — **required** when `group_policy: "open"`, gateway refuses to start without it
- [ ] `config.yaml` has `group_policy: "open"` under `platforms.qqbot.extra`
- [ ] q.qq.com intents enabled: Group @-message ✅
- [ ] Bot is a member of the target QQ group
- [ ] Bot is NOT in sandbox mode (or all test users are whitelisted)

## Step-by-Step

### 1. Create Profile
```bash
hermes profile create xiaomeng
```

### 2. Set .env credentials
```env
QQ_APP_ID=1905113186       # unique per profile
QQ_CLIENT_SECRET=RnupX...  # unique per profile
QQ_ENABLED=true
GLM_API_KEY=***            # can differ per character
```

### 3. Configure config.yaml
```yaml
agent:
  max_turns: 1                       # ← prevents flooding

platforms:
  qqbot:
    enabled: true
    extra:
      group_policy: "open"           # ← respond to ALL group messages
      markdown_support: true

platform_toolsets:
  qqbot:
    - hermes-qqbot
```

**Why `max_turns: 1`?** Without it the agent loops and floods the group.
**Why `group_policy: "open"`?** By default Hermes only responds to @-mentions. "open" lets it see all messages including other bots'.

### 4. Write SOUL.md
Example at `$HERMES_HOME/profiles/xiaomeng/SOUL.md`:
```markdown
# 角色设定
你是**小梦**，22岁的大三女生~ 性格温柔可爱。

## 说话风格
- 带~和颜文字 (◕‿◕)，自称「人家」
- 一次只说一句话

## 对话规则
- 看到别人发的消息再回应
- 不要回复自己的消息
```

### 5. Start Gateway
```bash
hermes --profile xiaomeng gateway start
```

### 6. Verify
```bash
hermes --profile xiaomeng gateway status
tail "$HERMES_HOME/profiles/xiaomeng/logs/gateway-stdio.log" | grep qqbot
```
Expected: `✓ qqbot connected`

## Cross-Computer Deployment

```
Computer A:  Profile xiaomeng, QQ Bot A (appId-1), Model: GLM-4
Computer B:  Profile laozhang, QQ Bot B (appId-2), Model: DeepSeek
```

Bots communicate entirely through the QQ group — no direct network between computers needed.

## Different AI Models per Character

```yaml
# xiaomeng/config.yaml:  model.provider: zai, model.default: GLM-4.1V-Thinking-Flash
# laozhang/config.yaml:  model.provider: deepseek, model.default: deepseek-chat
# ali/config.yaml:       model.provider: custom:sharedchat, model.default: gpt-5.5
```

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Bot replies to itself | No self-message detection | SOUL.md: "不要回复自己的消息" |
| Message flood | No turn limit | `agent.max_turns: 1` |
| Out-of-order replies | Parallel processing | SOUL.md: "根据时间线判断回复顺序" |
| Gateway fails for 2nd bot | Same appId used twice | Each profile needs unique appId |
| Windows gateway dies on reboot | Startup folder is unreliable | Admin: `hermes gateway install --force --start-on-login` |
| Gateway starts then instantly exits | `group_policy: "open"` without `QQ_ALLOW_ALL_USERS=true` | Add `QQ_ALLOW_ALL_USERS=true` to `.env`, restart |

## Troubleshooting: QQ Connected But No Messages Arrive

When `✓ qqbot connected` appears in logs but group messages never reach Hermes, the issue is at **QQ's platform level** — the WebSocket is fine, but QQ's server isn't forwarding messages.

### Key Insight: Two Independent Connection Layers

This distinction is critical — **"connected" in gateway logs only means Layer 1 is healthy:**

```
Layer 1 (WebSocket):     Hermes gateway ←→ QQ Server     ✅ "✓ qqbot connected"
Layer 2 (Message Route): QQ Server → Bot's WebSocket      ❌ Can fail silently
```

Hermes **cannot know** if Layer 2 is working — the gateway only sees what the WebSocket delivers. If messages never arrive, always suspect Layer 2 (QQ platform config), not Layer 1.

### Step 1: Check Gateway Logs

```bash
# Check exit diagnostics (structured JSON)
cat "%LOCALAPPDATA%\\hermes\\profiles\\<profile>\\logs\\gateway-exit-diag.log"

# Check stdio log (warnings, errors)
cat "%LOCALAPPDATA%\\hermes\\profiles\\<profile>\\logs\\gateway-stdio.log"

# Check for incoming messages
tail -50 "%LOCALAPPDATA%\\hermes\\profiles\\<profile>\\logs\\gateway.log" | grep -iE "qqbot|message|error|warn"
```

### Step 2: QQ Platform Diagnostic Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| ✅ Gateway connected, ❌ No messages ever arrive | Group intents not enabled at q.qq.com | 开发设置 → Intents → ✅ Group @-message |
| ✅ @-mention works, ❌ Non-@ doesn't | `group_policy` defaults to `mention_only` | Set `group_policy: "open"` in config.yaml |
| ✅ Only developer's messages arrive | Bot is in **sandbox mode** | Submit for review, or add test users to sandbox whitelist |
| ✅ Can see Bot in group list, ❌ Bot silent | Bot not subscribed to the group's events | Remove and re-invite bot via 加群体验 link |
| ❌ Bot not in group at all | Never invited | q.qq.com → 应用详情 → 加群体验 → 生成链接 → 群里发送 |
| ❌ Gateway starts → instantly exits | `group_policy: "open"` without `QQ_ALLOW_ALL_USERS=true` | Add to `.env`, restart |

### Step 3: Gateway Startup Guard (Most Common)

The error message to look for in `gateway-stdio.log`:
```
ERROR gateway.run: Refusing to start: qqbot has dm_policy/group_policy set to
'open' but neither GATEWAY_ALLOW_ALL_USERS nor QQ_ALLOW_ALL_USERS is enabled.
ERROR gateway.run: Gateway exiting cleanly: qqbot: open policy without allow-all opt-in
```

**Fix:** Add to the profile's `.env`:
```env
QQ_ALLOW_ALL_USERS=true
```

Then restart:
```bash
hermes --profile <name> gateway restart
```

### Step 4: Sandbox Mode

New QQ Bot apps default to **sandbox mode**, meaning only the developer's own QQ account can interact with the bot.

Check at q.qq.com → 控制台 → Bot 详情 → look for "沙盒模式" badge.

**Fix options:**
- **Temporary:** Add test users to the sandbox whitelist
- **Permanent:** Submit the bot for review/release (上架)

### Architecture Reminder: How Messages Flow

```
[User sends message in QQ group]
        ↓
[QQ Server (q.qq.com)]
   ↓ checks: intents enabled? sandbox? in group?
        ↓
[Bot WebSocket (Hermes gateway)]
   ↓ checks: group_policy = "open"?
        ↓
[Hermes Agent] ← SOUL.md + model
   ↓ generates reply
[QQ REST API] ← POST to group
        ↓
[QQ Group - everyone sees it]
```

If any check at the QQ Server layer fails (intents, sandbox, group membership), the message never reaches the WebSocket — even though the connection status says "connected".

## Character SOUL.md Templates

### 小梦 🌸 — Cute girl
Soft, uses kaomoji,自称「人家」. One sentence per turn.

### 老张 🧐 — Grumpy programmer
Concise, direct, occasional dry humor. Corrects others gently.

### 阿狸 🦊 — Trickster
Playful, memes, chaotic energy. Provokes reactions.
