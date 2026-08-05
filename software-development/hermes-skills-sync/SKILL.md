---
name: hermes-skills-sync
description: "Auto-sync Hermes Agent skills across machines via Git + cron — init repo, scripts for auto-push/pull, and cron job configuration."
version: 1.0.0
author: Hermes Agent (learned from session)
tags: [hermes, skills, git, sync, cron, multi-machine]
---

# Hermes Skills Auto-Sync

Keep skills synchronized across multiple Hermes instances using a Git repository with automated push/pull via cron. No manual `git pull` — the system detects local changes and syncs them on a schedule.

## Trigger Conditions

Use when:
- Setting up Hermes on a second machine and want skills to stay in sync
- Want to back up skills to a remote Git repo
- Need multi-machine skill consistency without manual intervention

## Architecture

```
Machine A ──(auto-push every 60min, rebase-first)──▶ Git Repo ◀──(auto-pull daily at 9:00)── Machine B
```

Two cron jobs run on each machine:
- **pull** (daily at 9:00): `git pull` — merges remote changes, keeps local unique skills intact
- **push** (every 60 min): `git pull --rebase` first to sync remote → then commit+push local-only changes

**Key design principle**: pull and push use different strategies.
- **Pull** (`git pull`): Fast-forward merge from remote. Does NOT delete local-only skills — it only adds/updates skills that exist in remote.
- **Push** (`git pull --rebase` first, then push): Before pushing local changes, rebase on top of remote to avoid conflicts. This ensures the remote always has both machines' contributions.

## Setup

### 1. Create a private Git repo

On GitHub or Gitee, create a **private** repository (skills may contain sensitive project context). Get the clone URL.

### 2. Initialize skills as a Git repo

```bash
cd "$HERMES_HOME/skills"

# Create .gitignore to exclude runtime files
cat > .gitignore << 'EOF'
.bundled_manifest
.curator_state
.usage.json
.usage.json.lock
.archive/
__pycache__/
*.pyc
EOF

git init
git add .
git commit -m "Initial skills sync"
git remote add origin <your-repo-url>
git push -u origin master
```

### 3. Deploy sync scripts

Choose the right script format for your OS:

| OS | Push Script | Pull Script |
|----|-------------|-------------|
| **Linux/macOS** | `scripts/skills-sync-push.sh` | `scripts/skills-sync-pull.sh` |
| **Windows** | `scripts/skills-sync-push.py` | `scripts/skills-sync-pull.py` |

Copy the appropriate scripts from this skill's `scripts/` directory into `$HERMES_HOME/scripts/`.

> ⚠️ **Windows users**: The `.sh` scripts require bash which is not on the cron scheduler's PATH — cron jobs will fail with "bash not found on PATH". Always use the `.py` versions on Windows. The Python scripts auto-detect `HERMES_HOME` and fall back to `%LOCALAPPDATA%\hermes\skills` on Windows.

### 4. Create cron jobs

The user's preferred setup (used in production):

| Job | Frequency | Strategy | Script |
|-----|-----------|----------|--------|
| 📥 pull-skills | **Daily at 9:00** (`0 9 * * *`) | `git pull` — merge remote, **keep local unique skills** | `skills-sync-pull.sh` |
| 📤 push-skills | **Every 60 min** (`60m`) | `git pull --rebase` → commit + push | `skills-sync-push-rebase.sh` |

**Key principle**: pull and push use different strategies.
- **Pull** (`git pull`, `--ff-only`): Fast-forward merge from remote. Does NOT delete local-only skills — it only adds/updates skills that exist in remote. **Stashes local changes first**, pulls, then restores them.
- **Push** (`git pull --rebase` first, then push): Before pushing local changes, rebase on top of remote to avoid conflicts. **Auto-resolves conflicts with `--ours` (local version)** since local skills are the source of truth for the push machine. This ensures the remote always has both machines' contributions.

Create both with `no_agent=true`:

```bash
# Use cronjob tool (not CLI) — the 'hermes cron create' CLI command may not exist
# Instead, use the cronjob tool's create action with these parameters:

# Pull: daily at 9am — simple git pull, keeps local-only skills
cronjob(action='create',
        name='📥 pull-skills',
        schedule='0 9 * * *',
        script='skills-sync-pull.sh',
        no_agent=True,
        repeat=0)

# Push: every 60 min — rebase-first, then push local changes
cronjob(action='create',
        name='📤 push-skills',
        schedule='60m',
        script='skills-sync-push-rebase.sh',
        no_agent=True,
        repeat=0)
```

**Important**: New cron jobs default to `repeat=once`. You MUST set `repeat=0` either at creation time (as shown above) or update after:
```bash
hermes cron edit <job-id> --repeat 0
```

> ⚠️ **`hermes cron update` 不存在**（实测 2026-08）：合法子命令只有 `list, create, add, edit, pause, resume, run, remove, rm, delete, status, runs, history, tick`。凡是要"改已有任务"一律用 `hermes cron edit <job-id> [--script X] [--repeat N] [--schedule "..."]`。无参数 `edit` 报 `No updates provided`。

**创建任务的正确 CLI 语法**（实测 2026-08）：schedule 是**位置参数**，不是 `--schedule`（`--schedule` 报 unrecognized arguments）；`--no-agent` 使脚本 stdout 直接交付（空输出静默）；`--repeat 0` = 无限循环。
```bash
hermes cron create "0 9 * * *" --name "📥 pull-skills" --script skills-sync-pull.py --no-agent --repeat 0
hermes cron create "60m" --name "📤 push-skills" --script skills-sync-push.py --no-agent --repeat 0
```
如需把 .sh 任务改为 .py（Windows cron 无 bash），优先 `hermes cron edit <id> --script skills-sync-pull.py`，不要 remove+create（重建需重填全部参数）。

**After Hermes restart, verify cron jobs are still `enabled=true` and `state=scheduled`**:
```bash
hermes cron list
# If a job shows enabled=false and state=completed, re-enable it:
hermes cron edit <job-id> --schedule "0 9 * * *"  # re-schedule to reactivate
```

**Conflict resolution during push** (`skills-sync-push-rebase.sh`):
The rebase-push script now includes automatic conflict resolution:
1. Attempt `git pull --rebase origin master`
2. On CONFLICT: identify conflicted files, resolve with `git checkout --ours` (local version is source of truth)
3. `git add` resolved files, `git rebase --continue`
4. If continue fails (unmerged paths remain), fall back to `git rebase --skip`
5. After successful rebase, commit and push local changes

### 5. On the second machine

```bash
cd "$HERMES_HOME"
mv skills skills.bak        # backup existing skills
git clone <repo-url> skills
# Then repeat steps 3-4 above
```

## How It Works

**Pull script** (`skills-sync-pull.sh`):
1. `cd $HERMES_HOME/skills`
2. Stash any local uncommitted changes
3. `git pull --ff-only origin master`
4. Restore stashed changes
5. Notify Hermes to reload skills

**Push script** (uses rebase-first strategy — the user's preferred approach, see `references/rebase-push-strategy.md`):

The push script (`skills-sync-push-rebase.sh`) follows this sequence to avoid losing either machine's changes:
1. `git pull --rebase origin master` — sync remote changes first, re-apply local commits on top
2. Check for local changes (`git diff` + untracked files). If clean → exit silently
3. If dirty → `git add -A`, commit with timestamp
4. `git push origin master` — push local-unique skills to remote

The key difference from a simple `git push` is **Step 1**: the rebase-first approach ensures local and remote changes merge cleanly before pushing. This prevents the "rejected" error when the remote has diverged.

## Prerequisites

### Git Identity (REQUIRED for push)

Without this, `git push` fails with `Author identity unknown`:

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

## Pitfalls

- **Git identity not set → push fails**: `Author identity unknown / unable to auto-detect email address`. Fix: `git config --global user.email "..."` and `user.name`. See Prerequisites above.
- **Private repo is essential**: Skills may contain project-specific paths, API endpoints, or internal tool configurations. Never use a public repo.
- **China network / GitHub blocked**: Use a local proxy (Clash/V2Ray). Configure: `git config --global http.proxy http://127.0.0.1:PORT`. See `references/git-proxy.md` for full guide.
- **Cron jobs need repeat=forever**: Newly created cron jobs default to `once`. Update them: `hermes cron edit <job_id>` and set repeat to 0 (forever).
- **Script-only jobs are silent by design**: With `no_agent=true`, empty stdout means no message is delivered. This is intentional — you don't want a notification every 5 minutes when nothing changed.
- **Cron jobs silently accumulate `last_status=error` after Hermes restart**: After a Hermes Desktop restart or profile change, cron jobs may stop running silently — they appear in the list with `last_status: error` and `enabled: false`. Always verify after a restart: `hermes cron list`. If jobs show as `completed`/`error` instead of `scheduled`, re-enable them with `hermes cron edit <job_id> --schedule "..."` (set the schedule to re-activate).
- **Git authentication**: The machine must have Git push access to the remote (SSH key or credential helper). Without it, push silently fails.
- **Transient push failure through proxy — just retry**: `git push` can fail once with `fatal: unable to access '...': Recv failure: Connection was reset` (especially via China proxy) even when `git pull --rebase` in the same run succeeded. The commit is already made locally, so simply re-running `git push origin master` usually succeeds on the second attempt. Do NOT assume the remote or credentials are broken — retry before diagnosing. (Seen live 2026-08: first push reset, immediate retry pushed fine.)
- **GitHub token expiration (classic PAT)**: Classic personal access tokens expire. When this happens, push fails with `remote: Permission denied ... 403`. Fix: generate a new token at https://github.com/settings/tokens with `repo` scope, then update the remote URL: `git remote set-url origin "https://USER:NEW_TOKEN@github.com/USER/REPO"`. The token embedded in the remote URL overrides the credential helper.
- **Conflicts**: The pull script uses `git stash` before pull and `git stash pop` after. If the pop produces a conflict, the local changes are preserved in the stash for manual resolution.
- **Windows path separators**: Always use `$HERMES_HOME` not `~/.hermes` in scripts. On Windows, `HERMES_HOME` defaults to `%LOCALAPPDATA%\\hermes`, not `~/.hermes`.
- **Windows: use .py scripts, not .sh**: The cron scheduler does not have bash on its PATH. Scripts must be Python (`.py`) on Windows. The `.sh` versions are for Linux/macOS only.
- **Cron jobs go `enabled: false` after error state**: When a cron job fails (e.g. due to network), Hermes may mark it as `enabled: false` and move it to `completed` state. The job stops running entirely — no retry. To recover: `hermes cron edit <job_id> --enabled true`. Monitor with `hermes cron list` after any network outage or Hermes Desktop restart.
- **Initial setup on second machine needs proxy for git clone**: During `git clone` of the skills repo, GitHub may be blocked. Use `git -c http.proxy=... clone ...` or ensure VPN is active before running the clone command.

## Linked Files

This skill ships with the following scripts and references:

**Scripts:**
- `scripts/skills-sync-pull.sh` — Pull script (standard `git pull --ff-only`)
- `scripts/skills-sync-push.sh` — Simple push script (no rebase)
- `scripts/skills-sync-push-rebase.sh` — **User's preferred** push script (rebase-first strategy)
- `scripts/skills-sync-pull.py` — Windows variant of pull script
- `scripts/skills-sync-push.py` — Windows variant of push script

**References:**
- `references/rebase-push-strategy.md` — Why rebase-first and conflict resolution
- `references/git-proxy.md` — Git proxy config for China/GitHub access
- `references/sqlalchemy-pitfalls.md` — (unrelated, legacy)

## Verification

```bash
# Check cron jobs are running
hermes cron list

# Test push script manually (Linux/macOS)
bash "$HERMES_HOME/scripts/skills-sync-push-rebase.sh"

# Test push script manually (simple variant)
bash "$HERMES_HOME/scripts/skills-sync-push.sh"

# Test pull script manually
bash "$HERMES_HOME/scripts/skills-sync-pull.sh"

# Check remote has the latest
git -C "$HERMES_HOME/skills" log --oneline -3
```
