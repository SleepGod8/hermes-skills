#!/bin/bash
# Auto-pull skills from Git remote
# Runs via cron to sync skills from remote

SKILLS_DIR="$HERMES_HOME/skills"
cd "$SKILLS_DIR" || exit 1

# Check if remote is configured
if ! git remote get-url origin &>/dev/null; then
    echo "[skills-sync] No git remote configured, skipping pull"
    exit 0
fi

# Stash any local uncommitted changes before pulling
git stash -q 2>/dev/null

# Pull from remote
if git pull --ff-only origin master 2>&1; then
    echo "[skills-sync] Pulled latest skills from remote"

    # Restore stashed local changes
    git stash pop -q 2>/dev/null

    # Notify Hermes to reload skills
    if command -v hermes &>/dev/null; then
        hermes skills check 2>/dev/null || true
    fi
else
    echo "[skills-sync] Pull failed or no updates"
    git stash pop -q 2>/dev/null
fi
