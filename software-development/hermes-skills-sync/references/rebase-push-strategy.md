# Rebase-First Push Strategy & Conflict Resolution

## Why rebase-first?

When two machines push to the same skills repo, simple `git push` fails with:

```
! [rejected]        master -> master (fetch first)
hint: Updates were rejected because the remote contains work that you do not
hint: have locally.
```

The solution: **pull rebase before push** (rather than merge commit).

## The strategy

```
Machine A: git pull --rebase → commit local changes → git push
Machine B: git pull --rebase → commit local changes → git push
```

Both machines use the same script (`skills-sync-push-rebase.sh`) which:
1. `git pull --rebase origin master` — reapply local commits on top of remote
2. If clean → exit silently
3. If dirty → `git add -A`, commit, push

## Conflict resolution during rebase

When both machines modified the same file, rebase produces a CONFLICT.
The push script auto-resolves using `--ours` (local version):

### How auto-resolution works (in skills-sync-push-rebase.sh)

```
1. git pull --rebase origin master
2. Capture output to variable, check exit code
3. On CONFLICT: grep output for "CONFLICT"
4. Find conflicted files: git diff --name-only --diff-filter=U
5. Resolve with local version: git checkout --ours <files>
6. Stage resolved files: git add <files>
7. Continue rebase: GIT_EDITOR=true git rebase --continue
8. If continue fails (unmerged paths remain): git rebase --skip
```

### Why --ours (local) is correct for push

The push machine's local changes are what we want to send to remote.
The remote changes were already fetched via `git pull --rebase` before the conflict,
so `--ours` = the new local commit being applied on top of remote.

### What happens when continue fails

`git rebase --continue` can fail when there are still unmerged paths after checkout.
In that case, `git rebase --skip` tells git "skip this patch entirely" — meaning the
local version for THIS commit is dropped (the remote version is kept instead).
This is acceptable because the important step is keeping the repos in sync; the
dropped change will appear in the next push cycle if it still exists locally.

### Manual recovery

If auto-resolution fails:

```bash
cd "$HERMES_HOME/skills"
git rebase --abort

# Retry manually
git pull --rebase origin master
# Fix conflicts manually
git add <resolved-files>
git rebase --continue
git push origin master
```

## The pull script (daily at 9:00) is simpler

The `skills-sync-pull.sh` script uses `git pull --ff-only` (fast-forward only).
It stashes local changes before pulling, then restores them after.
This is safe because pull only adds/updates — never deletes local-only files.
