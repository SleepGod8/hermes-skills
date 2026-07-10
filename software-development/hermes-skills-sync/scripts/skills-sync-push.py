#!/usr/bin/env python3
"""Auto-push new/modified skills to GitHub."""
import subprocess, sys
from datetime import datetime
import os

SKILLS_DIR = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")) + "/skills"
# On Windows, HERMES_HOME might be %LOCALAPPDATA%\hermes
if os.name == 'nt' and not os.path.isdir(SKILLS_DIR):
    SKILLS_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "skills")

def run(cmd):
    return subprocess.run(cmd, shell=True, cwd=SKILLS_DIR, capture_output=True, text=True)

# Pull first to avoid conflicts
run("git pull --rebase")

# Check for any changes (unstaged, staged, untracked)
diff = run("git diff --quiet")
staged = run("git diff --cached --quiet")
untracked = run("git ls-files --others --exclude-standard")

has_changes = diff.returncode != 0 or staged.returncode != 0 or bool(untracked.stdout.strip())

if not has_changes:
    sys.exit(0)  # Nothing to do, stay silent

# Stage everything
run("git add -A")

# Check if anything staged
staged2 = run("git diff --cached --quiet")
if staged2.returncode == 0:
    sys.exit(0)  # Nothing staged

# Commit
ts = datetime.now().strftime("%Y-%m-%d_%H:%M")
run(f'git commit -m "auto: sync skills {ts}"')

# Push
result = run("git push origin HEAD")
if result.returncode == 0:
    print("✅ 技能已推送到 GitHub")
else:
    print(f"❌ 推送失败: {result.stderr}")
    sys.exit(1)
