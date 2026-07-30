#!/bin/bash
# Auto-push skills to Git remote with rebase-first strategy
# User's preferred sync method:
#   1. git pull --rebase 先同步远程（本地优先解决冲突）
#   2. 再提交并推送本地独有的修改
#
# This script is designed for the cron job:
#   📤 push-skills  —  every 60 min

SKILLS_DIR="$HERMES_HOME/skills"
cd "$SKILLS_DIR" || exit 1

# Check if remote is configured
if ! git remote get-url origin &>/dev/null; then
    echo "[skills-sync] No git remote configured, skipping push"
    exit 0
fi

# Step 1: git pull --rebase 先同步远程
echo "[skills-sync] Pulling latest from remote (rebase)..."
GIT_RESULT=$(git pull --rebase origin master 2>&1)
PULL_EXIT=$?

if [ $PULL_EXIT -ne 0 ]; then
    # Check if there are conflicts
    if echo "$GIT_RESULT" | grep -q "CONFLICT"; then
        echo "[skills-sync] Merge conflict detected. Resolving with local (--ours) version..."
        # Get list of conflicted files
        CONFLICTED=$(git diff --name-only --diff-filter=U)
        echo "[skills-sync] Conflicted files: $CONFLICTED"
        # Resolve using local version
        git checkout --ours $CONFLICTED 2>/dev/null
        git add $CONFLICTED 2>/dev/null
        GIT_EDITOR=true git rebase --continue 2>&1
        if [ $? -ne 0 ]; then
            echo "[skills-sync] Auto-resolution failed, trying --skip..."
            git rebase --skip 2>/dev/null
        fi
        echo "[skills-sync] Conflicts resolved with local version"
    else
        echo "[skills-sync] Rebase failed — aborting. Output: $GIT_RESULT"
        git rebase --abort 2>/dev/null
        exit 1
    fi
fi

# Step 2: 检查本地是否有改动
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo "[skills-sync] No local changes to push"
    exit 0
fi

# Step 3: 提交本地独有的修改
git add -A
CHANGES=$(git diff --cached --stat | tail -1)
COMMIT_MSG="auto: sync local skills ($(date '+%Y-%m-%d %H:%M')) — $CHANGES"
git commit -m "$COMMIT_MSG" 2>&1

# Step 4: 推送到远程
if git push origin master 2>&1; then
    echo "[skills-sync] Pushed local changes to remote: $COMMIT_MSG"
else
    echo "[skills-sync] Push failed (network issue or no remote access)"
    exit 1
fi
