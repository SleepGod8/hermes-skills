---
name: hermes-studio-troubleshooting
description: "Diagnose Hermes Studio desktop runtime failures: group-chat @Agent shows 操作已中断 / Interrupted during API call, profile backend LRU churn, chat-run ECONNRESET, stale zombie backends. Use when Studio room chat errors or per-profile backends misbehave."
version: 1.0.0
author: agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [hermes, studio, desktop, group-chat, troubleshooting, backend]
    category: software-development
    related_skills: [hermes-studio, hermes-troubleshooting, hermes-gateway-troubleshooting]
---

# Hermes Studio Runtime Troubleshooting

Class-level diagnostics for failures inside **Hermes Studio desktop** (the Electron
product): room/group-chat request failures, per-profile backend lifecycle churn,
chat-run interruptions. Distinct from gateway/platform issues (see
`hermes-gateway-troubleshooting` / `qq-bot-gateway-troubleshooting`) and from
Studio usage/config questions (see `hermes-studio` — which is manually authored and
cannot be patched by the agent; keep overlap notes there, full detail here).

## Trigger conditions

- Studio room chat: @Agent →「操作已中断」/ "Interrupted during API call"
- Per-profile backend processes exiting (1) repeatedly, `exited (1073807364)`
- `Evicting idle profile backend` / `Reaping idle profile backend` in desktop.log
- chat-run session ids (`gc_run_<room>_<profile>_<Agent>_*`) being reclaimed as orphans
- Room chat works for some Agents but not others
- 「重启以完成更新」banner keeps coming back after every restart

## Core mechanism you must know: profile backend lifecycle

Studio runs **one headless backend (`hermes serve`) per profile**, and keeps only:
- **LRU cap 3** — at most 3 idle profile backends cached; beyond that → evict & kill
- **idle > 600s** — any idle backend is reaped after 10 minutes

With many profiles in one room (e.g. 10+ maid-family profiles), backends are killed
and cold-restarted constantly. @-ing an Agent whose backend is mid-restart or was
just evicted → the chat-run HTTP/WS request dies with ECONNRESET → frontend toast
「操作已中断」. A second trigger: a free-tier nous channel (`tencent/hy3:free` @
`inference-api.nousresearch.com`) can time out 3×~74s and produce the same toast.

## Diagnosis recipe

Logs: `~/AppData/Local/hermes/logs/desktop.log` (lines prefixed `[hermes]`).

```bash
grep -a "Interrupted during API call" desktop.log          # log signature of 操作已中断
grep -a "Evicting idle profile backend\|Reaping idle profile backend" desktop.log  # LRU churn
grep -a "exited (1)\|ECONNRESET\|Request timed out" desktop.log
grep -a "<profile>" desktop.log | tail -30                 # per-profile backend lifecycle
```

state.db (`~/AppData/Local/hermes/state.db`, sqlite3):
```sql
SELECT id, model, model_config, end_reason, message_count
FROM sessions WHERE id LIKE 'gc_run_%' ORDER BY rowid DESC LIMIT 8;
-- session_model_usage has model/provider per run
```
`gc_run_`-prefixed sessions = group chat runs. Their model column shows what the
room actually used (e.g. deepseek-v4-flash) vs. what timed out.

Also verify the target profile's config is sane:
`~/AppData/Local/hermes/profiles/<name>/config.yaml` (model/provider/base_url) and
that SOUL.md exists — a missing SOUL.md surfaces as IO errors during backend boot.

## Stale「重启以完成更新」banner that no restart clears

Popup text is the zh i18n key `bundleSwapPending` (`apps/desktop/src/i18n/zh.ts`);
**not** the boot update gate, and not the `bundleOutOfSync` banner (that one says
「应用版本过旧」and links to the installer).

Its source (`electron/main.ts` handler `hermes:version`):

```
bundleSwapPending = IS_PACKAGED && detectBundleSwap(INSTALL_STAMP,
                       readBundleSwapStamp(process.resourcesPath))
```

- `INSTALL_STAMP` is **baked into the bundle at build time**
  (`__HERMES_INSTALL_STAMP__` global, from `apps/desktop/build/install-stamp.json`).
  It is a constant of the artifact — a restart can never change it.
- `readBundleSwapStamp()` re-reads `apps/desktop/release/win-unpacked/resources/install-stamp.json`
  at every call.
- `detectBundleSwap` (`electron/bundle-swap.ts`) returns true when `commit` differs
  **or** `builtAt` differs at the same commit.

So if the packaged `resources/install-stamp.json` was never refreshed when the
bundle was rebuilt (typical after a manual `app.asar` repair: unpack asar into
`resources/app/` and rebuild `dist/`, but forget the stamp), the file says the old
commit while the binary says the new one → **true forever, banner after every
restart.**

Diagnose:

```bash
cd ~/AppData/Local/hermes/hermes-agent/apps/desktop
cat build/install-stamp.json                                # stamp baked into the bundle
cat release/win-unpacked/resources/install-stamp.json       # stale? old commit/builtAt
grep -a -o -E '"[0-9a-f]{40}"' release/win-unpacked/resources/app/dist/electron-main.mjs | sort -u   # baked commit (unpacked layout)
```

Fix — make the resources stamp equal the baked stamp, keeping a backup:

```bash
R=release/win-unpacked/resources
cp "$R/install-stamp.json" "$R/install-stamp.json.bak-$(date +%Y%m%d-%H%M%S)"
cp build/install-stamp.json "$R/install-stamp.json"
```

Verify with the pure predicate (no need to boot Electron): rebuild
`detectBundleSwap(baked, disk)` in node and confirm it prints `false`; the renderer
re-queries `hermes:version` when the About/Updates panel opens, so a restart or
reopening that panel clears the banner. Never "fix" this by relaunching again —
the mismatch is file-vs-binary, not memory-vs-disk.

## Fix priority

1. **Retry the @** — backend restarts, usually recovers (transient).
2. **Reduce concurrent profiles in the room** — don't @all; remove unused maids
   from the room. Fewer profiles → fewer LRU evictions.
3. **Full Studio restart** — `taskkill /F /IM "Hermes Studio.exe"` + kill the
   python.exe backend children (they respawn with Studio), then reopen. Clears
   zombie backends and stale sockets.
4. **Check Agent model choice** — the room Agent should use its own profile config
   (e.g. deepseek-v4-flash), not a nous free channel (`tencent/hy3:free`).

## Distinguish from other failure classes

| Symptom | Class | Where handled |
|---|---|---|
| @Agent → 操作已中断, backend exited | profile backend churn | this skill |
| @all → 429 rate limits | concurrency/quota | hermes-studio skill |
| WeChat/QQ/Feishu not responding | gateway | hermes-troubleshooting / qq-bot-gateway-troubleshooting |
| Desktop won't start / 15s timeout | gateway port conflict | hermes-troubleshooting |
| Update check red / can't reach server | git/PATH/network | hermes-troubleshooting |

## References

- `references/group-chat-interrupted-2026-08.md` — full transcript of the
  @Athena 操作已中断 diagnosis (evidence, session ids, fix applied).
