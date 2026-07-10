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

Copy `scripts/skills-sync-pull.sh` and `scripts/skills-sync-push.sh` from this skill's scripts directory into `$HERMES_HOME/scripts/`.

### 4. Create cron jobs

```bash
# Pull from remote every 5 minutes
hermes cron create "5m" --name "Skills Auto-Pull" --script skills-sync-pull.sh --no-agent

# Push local changes every 10 minutes  
hermes cron create "10m" --name "Skills Auto-Push" --script skills-sync-push.sh --no-agent
```

Both jobs use `--no-agent` (script-only, zero tokens). They output nothing when there's no work to do.

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
- **Cron jobs need repeat=forever**: Newly created cron jobs default to `once`. Update them: `hermes cron edit <job_id>` and set repeat to 0 (forever).
- **Script-only jobs are silent by design**: With `no_agent=true`, empty stdout means no message is delivered. This is intentional — you don't want a notification every 5 minutes when nothing changed.
- **Git authentication**: The machine must have Git push access to the remote (SSH key or credential helper). Without it, push silently fails.
- **Conflicts**: The pull script uses `git stash` before pull and `git stash pop` after. If the pop produces a conflict, the local changes are preserved in the stash for manual resolution.
- **Windows path separators**: Always use `$HERMES_HOME` not `~/.hermes` in scripts. On Windows, `HERMES_HOME` defaults to `%LOCALAPPDATA%\hermes`, not `~/.hermes`.

## Verification

```bash
# Check cron jobs are running
hermes cron list

# Test push script manually
bash "$HERMES_HOME/scripts/skills-sync-push.sh"

# Check remote has the latest
git -C "$HERMES_HOME/skills" log --oneline -3
```
