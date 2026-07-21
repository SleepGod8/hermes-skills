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
Machine A ──(auto-push every 10min)──▶ Git Repo ◀──(auto-pull every 5min)── Machine B
```

Two cron jobs run on each machine:
- **pull** (every 5 min): fetches remote changes, stashes local uncommitted work first
- **push** (every 10 min): detects local changes, commits with auto-generated message, pushes

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

```bash
# Linux/macOS — use .sh scripts (bash always available)
hermes cron create "5m" --name "Skills Auto-Pull" --script skills-sync-pull.sh --no-agent
hermes cron create "10m" --name "Skills Auto-Push" --script skills-sync-push.sh --no-agent

# Windows — use .py scripts (bash not on cron PATH)
hermes cron create "every 60m" --name "Skills Auto-Pull" --script skills-sync-pull.py --no-agent
hermes cron create "every 60m" --name "Skills Auto-Push" --script skills-sync-push.py --no-agent
```

Both jobs use `--no-agent` (script-only, zero tokens). They output nothing when there's no work to do. On Windows, longer intervals (60m) are recommended since git operations are slower.

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

**Push script** (`skills-sync-push.sh`):
1. `cd $HERMES_HOME/skills`
2. Check for changes (`git diff` + untracked files)
3. If clean → exit silently (no output)
4. If dirty → `git add -A`, commit with timestamp, `git push`

## Pitfalls

- **Private repo is essential**: Skills may contain project-specific paths, API endpoints, or internal tool configurations. Never use a public repo.
- **China network / GitHub blocked**: Use a local proxy (Clash/V2Ray). Configure: `git config --global http.proxy http://127.0.0.1:PORT`. See `references/git-proxy.md` for full guide.
- **Cron jobs need repeat=forever**: Newly created cron jobs default to `once`. Update them: `hermes cron edit <job_id>` and set repeat to 0 (forever).
- **Script-only jobs are silent by design**: With `no_agent=true`, empty stdout means no message is delivered. This is intentional — you don't want a notification every 5 minutes when nothing changed.
- **Git authentication**: The machine must have Git push access to the remote (SSH key or credential helper). Without it, push silently fails.
- **GitHub token expiration (classic PAT)**: Classic personal access tokens expire. When this happens, push fails with `remote: Permission denied ... 403`. Fix: generate a new token at https://github.com/settings/tokens with `repo` scope, then update the remote URL: `git remote set-url origin "https://USER:NEW_TOKEN@github.com/USER/REPO"`. The token embedded in the remote URL overrides the credential helper.
- **Conflicts**: The pull script uses `git stash` before pull and `git stash pop` after. If the pop produces a conflict, the local changes are preserved in the stash for manual resolution.
- **Windows path separators**: Always use `$HERMES_HOME` not `~/.hermes` in scripts. On Windows, `HERMES_HOME` defaults to `%LOCALAPPDATA%\\hermes`, not `~/.hermes`.
- **Windows: use .py scripts, not .sh**: The cron scheduler does not have bash on its PATH. Scripts must be Python (`.py`) on Windows. The `.sh` versions are for Linux/macOS only.

## Verification

```bash
# Check cron jobs are running
hermes cron list

# Test push script manually (Linux/macOS)
bash "$HERMES_HOME/scripts/skills-sync-push.sh"

# Test push script manually (Windows)
python "$HERMES_HOME/scripts/skills-sync-push.py"

# Check remote has the latest
git -C "$HERMES_HOME/skills" log --oneline -3
```
