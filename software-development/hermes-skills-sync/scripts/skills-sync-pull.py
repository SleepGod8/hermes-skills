#!/usr/bin/env python3
"""Auto-sync hermes-skills from GitHub."""
import subprocess, sys
import os

SKILLS_DIR = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")) + "/skills"
if os.name == 'nt' and not os.path.isdir(SKILLS_DIR):
    SKILLS_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "skills")

def run(cmd):
    return subprocess.run(cmd, shell=True, cwd=SKILLS_DIR, capture_output=True, text=True)

# Get current HEAD
before = run("git rev-parse HEAD").stdout.strip()

# Pull
result = run("git pull")
if result.returncode != 0:
    print(f"❌ git pull failed: {result.stderr}")
    sys.exit(1)

# Check if changed
after = run("git rev-parse HEAD").stdout.strip()

if before != after and before and after:
    print("🔄 Skills 已更新！")
    log = run("git log --oneline {}..{}".format(before[:8], after[:8]))
    print("变更日志:")
    print(log.stdout.strip())
else:
    # No changes — stay silent
    pass
