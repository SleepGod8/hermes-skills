#!/bin/bash
# Auto-push skills to Git remote
# Runs via cron: detects local changes, commits and pushes

SKILLS_DIR="$HERMES_HOME/skills"
cd "$SKILLS_DIR" || exit 1

# Check if remote is configured
if ! git remote get-url origin &>/dev/null; then
    echo "[skills-sync] No git remote configured, skipping push"
    exit 0
fi

# Check for changes (including new/deleted files)
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    # No changes, nothing to push
    exit 0
fi

# Add all changes
git add -A

# Generate a meaningful commit message based on what changed
CHANGES=$(git diff --cached --stat | tail -1)
COMMIT_MSG="auto: sync skills ($(date '+%Y-%m-%d %H:%M')) — $CHANGES"

git commit -m "$COMMIT_MSG" 2>&1

# Push to remote
if git push origin master 2>&1; then
    echo "[skills-sync] Pushed changes to remote: $COMMIT_MSG"
else
    echo "[skills-sync] Push failed (network issue or no remote access)"
fi
