# 群聊「正在总结」深层根因 — PYTHONPATH 污染导致 bridge python 崩溃 (2026-08-16)

## Symptom (after DB-level fixes still recur)

Room chat shows 「正在总结」/ summarizing forever even after clearing
`gc_room_summaries` (see `group-chat-summarize-deadlock-2026-08.md`) and
restarting. Messages @Agent stay `queued`. Agent messages may contain:

```
Error: Failed to initialize OpenAI client: No module named 'pydantic_core._pydantic_core'
```

## True root cause: PYTHONPATH contamination

**The Hermes desktop agent (Hermes.exe) runs with `PYTHONPATH` pointing at the
Hermes main venv (Python 3.11):**

```
PYTHONPATH=C:\Users\<user>\AppData\Local\hermes\hermes-agent;C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages
```

Studio's per-profile bridge processes (`hermes_bridge.py --worker-profile X`,
Python 3.12 from `~\.hermes-web-ui\desktop-runtime\hermes\<ver>\win-x64\python\venv`)
**inherit that PYTHONPATH** (Studio index.js explicitly builds
`e.PYTHONPATH=[stagingDirectory, process.env.PYTHONPATH]`). When the bridge imports
`pydantic_core`, Python finds the 3.11-compiled binary from the Hermes main venv
first → `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`
(binary ABI mismatch) → every Agent LLM call dies → auto-summary can never
complete → frontend shows 「正在总结」 forever.

Evidence: `powershell (Get-Process -Id <bridgePid>).StartInfo.EnvironmentVariables['PYTHONPATH']`
returns the Hermes paths on every Studio/node/bridge process — inherited, not
injected by Studio's own code. Clearing the DB row only helps until the next
summary trigger (Studio re-enables `summaryGeneration` on its own; turns counter
kept climbing 291 → 709 → 1099).

## Fix: sitecustomize.py in the Studio venv

Write `sitecustomize.py` into the Studio venv site-packages; Python auto-imports
it at startup, so it strips the polluted paths before any Hermes import:

File: `C:\Users\<user>\.hermes-web-ui\desktop-runtime\hermes\<ver>\win-x64\python\venv\Lib\site-packages\sitecustomize.py`

```python
# sitecustomize.py — strip Hermes main-venv PYTHONPATH pollution (3.11 ABI vs 3.12)
import sys, os

def _fix_pythonpath():
    bad_roots = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "hermes-agent"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "hermes-agent", "venv", "Lib", "site-packages"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "hermes-agent", "venv"),
    ]
    bad_roots = [os.path.normcase(os.path.normpath(p)) for p in bad_roots if p]
    kept, removed = [], []
    for p in sys.path:
        if not p:
            kept.append(p); continue
        np = os.path.normcase(os.path.normpath(p))
        if any(np == br or np.startswith(br + os.sep) for br in bad_roots):
            removed.append(p)
        else:
            kept.append(p)
    if removed:
        sys.path[:] = kept
        print(f"[sitecustomize] removed: {removed}", file=sys.stderr)
    pp = os.environ.get("PYTHONPATH", "")
    if pp:
        parts, dirty = [], False
        for seg in pp.split(os.pathsep):
            if not seg: continue
            np = os.path.normcase(os.path.normpath(seg))
            if any(np == br or np.startswith(br + os.sep) for br in bad_roots):
                dirty = True; continue
            parts.append(seg)
        if dirty:
            os.environ["PYTHONPATH"] = os.pathsep.join(parts)

_fix_pythonpath()
```

Verify the fix without touching Studio:
```bash
env PYTHONPATH="C:\Users\<user>\AppData\Local\hermes\hermes-agent;C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages" \
  "C:\Users\<user>\.hermes-web-ui\desktop-runtime\hermes\<ver>\win-x64\python\venv\Scripts\python.exe" \
  -c "import pydantic_core; print(pydantic_core.__version__)"
# Before fix: ModuleNotFoundError. After fix: [sitecustomize] ... OK 2.46.4
```

Then fully restart Studio. Room auto-summary returns to `success` status within
~1-2 min instead of hanging forever.

## Also worth doing (secondary)

- Kill zombie bridge processes left by repeated restarts: `wmic process where
  "name='python.exe'" get ProcessId,CommandLine | grep hermes_bridge.py` → one
  pair per profile; old Studio instances accumulate multiples. Kill stragglers
  before relaunching (they fight over the same agent socket).
- Starting Studio with `cmd /c "set PYTHONPATH=&& start ..."` does NOT prevent
  the pollution (Studio still builds PYTHONPATH from its own env); the
  sitecustomize.py shim is the reliable fix.
- The system registry has NO PYTHONPATH (session-only variable from Hermes) —
  the pollution is not a machine-wide misconfiguration.

## Pitfalls / distractors

- `summaryGeneration=0` in `gc_rooms` is NOT sticky — Studio re-enables it
  internally; don't rely on it as a permanent fix.
- `hermes mcp test` / Agent ping show healthy even when the bridge LLM init is
  broken — the failure only appears when the agent actually calls the model.
- `Auxiliary: marking openrouter/nous unhealthy` in errors.log is unrelated noise.
