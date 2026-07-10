# Windows tqdm OSError Fix (ComfyUI Desktop)

## Symptom

When submitting workflows via the REST API (`POST /prompt`), the KSampler
node crashes immediately with:

```
OSError: [Errno 22] Invalid argument
```

The traceback passes through:
```
tqdm/asyncio.py  →  tqdm/std.py (status_printer)
→ app/logger.py (LogInterceptor.flush)
→ TextIOWrapper.flush()  ← CRASHES HERE
```

## Root Cause

ComfyUI's `app/logger.py` replaces `sys.stderr` with a `LogInterceptor`
(which extends `TextIOWrapper`). When tqdm's **asyncio** version initializes
a progress bar inside the KSampler, it calls `sys.stderr.flush()`.
On Windows, `TextIOWrapper.flush()` on this wrapped stderr raises
`OSError: [Errno 22] Invalid argument`.

The error only occurs during **API-triggered** execution (not GUI
interaction) because the API path uses tqdm's `asyncio` variant, and
the desktop GUI render thread may interfere with the flush handle.

## Fix Recipe (Two-Part)

### ⚠️ Known Limitation — Fix Often Fails

On Comfy Desktop 0.27.0 Windows, **the fix frequently does not take effect**
even after applying all steps correctly. Common failure modes:

1. **Python loads stale bytecode from an unknown location** — clearing
   `__pycache__` and using `PYTHONDONTWRITEBYTECODE=1` is often insufficient.
   The traceback will show the **comment line** from the patched file as the
   error source, proving old bytecode is executing despite cleanup.

2. **Comfy Desktop auto-restarts** — killing `python.exe` in Task Manager
   may not be enough; the Desktop app can respawn the backend process from
   its own copy of the code, undoing any file patches.

3. **Hermes venv contamination** — starting ComfyUI from a Hermes bash
   session can cause the standalone Python to import `tqdm` from Hermes's
   own venv instead of its bundled copy, producing different behavior.

**Practically, when all fixes fail, use the ComfyUI Desktop GUI instead**
of the REST API. The GUI-triggered KSampler path doesn't call tqdm's asyncio
variant and works reliably on Windows. Workflow JSON files can be
drag-and-dropped into the Desktop canvas.

### Part 1: SafeStderr wrapper (try first — may not work on all setups)

Create `ComfyUI/fix_stderr.py` in the ComfyUI source directory:

```python
"""
Pre-load fix for ComfyUI Windows tqdm OSError bug.
Must be imported before ComfyUI's logger wraps stderr.
"""
import sys

_original_stderr = sys.__stderr__

class SafeStderr:
    """Wrapper that prevents tqdm flush OSError on Windows"""
    def __init__(self, real_stderr):
        self._real = real_stderr
        self.buffer = getattr(real_stderr, 'buffer', None)
        self.encoding = getattr(real_stderr, 'encoding', 'utf-8')
        self.errors = getattr(real_stderr, 'errors', 'strict')
        self.line_buffering = getattr(real_stderr, 'line_buffering', False)
        self.closed = False

    def write(self, s):
        try:
            self._real.write(s)
        except OSError:
            pass

    def flush(self):
        try:
            self._real.flush()
        except OSError:
            pass

    def close(self):
        self.closed = True

    def __getattr__(self, name):
        return getattr(self._real, name)

sys.stderr = SafeStderr(_original_stderr)
```

### Part 2: Import before setup_logger

In `ComfyUI/main.py`, add the import BEFORE `from app.logger import setup_logger`:

```python
import folder_paths
import time
from comfy.cli_args import enables_dynamic_vram
# Fix: prevent tqdm OSError on Windows stderr flush
import fix_stderr  # noqa: F401
from app.logger import setup_logger
```

### Part 3: Clean bytecode cache & restart

```bash
# Kill all Python processes
taskkill //F //IM "python.exe"

# Clean ALL bytecode caches
find "<ComfyUI_root>" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find "<ComfyUI_root>" -name "*.pyc" -delete 2>/dev/null

# Restart using standalone-env Python (NOT .venv on Comfy Desktop!)
cd "<ComfyUI_root>/ComfyUI"
PYTHONDONTWRITEBYTECODE=1 \
  "<ComfyUI_root>/standalone-env/python.exe" \
  main.py --listen 127.0.0.1 --port 8188
```

**IMPORTANT:** `PYTHONDONTWRITEBYTECODE=1` prevents stale `.pyc` from being
re-generated. Without it, the old bytecode persists and the fix appears to
not work (traceback will show comment lines as error sources — dead giveaway
of stale bytecode).

### Alternative: Patch logger.py directly

If the SafeStderr approach doesn't work, directly modify
`app/logger.py` → `LogInterceptor.flush()`:

```python
def flush(self):
    # Skip super().flush() on Windows to avoid OSError [Errno 22]
    for cb in self._flush_callbacks:
        cb(self._logs_since_flush)
        self._logs_since_flush = []
```

But this is less reliable than the SafeStderr approach because:
- `super().flush()` is needed for proper stream behavior
- Other code paths may still call `flush()` on other wrapped streams
- Bytecode caching makes testing this approach confusing

## ComfyUI Desktop Path Note

ComfyUI Desktop uses `standalone-env/python.exe`, **not** `.venv/Scripts/python.exe`.
When restarting manually, always verify the correct path:

```bash
ls "<ComfyUI_root>/standalone-env/python.exe"  # Desktop installations
ls "<ComfyUI_root>/.venv/Scripts/python.exe"    # Manual/custom installations
```

Running with the wrong Python will import packages from a different
environment (e.g., the system Python or Hermes venv), causing cryptic
import errors or the tqdm bug to re-surface.

### Hermes venv contamination

When starting ComfyUI from within a Hermes agent session on Windows, the
`standalone-env/python.exe` may still resolve packages from Hermes' own venv
(`C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages`).
Verify with:

```bash
"<ComfyUI_root>/standalone-env/python.exe" -c "import tqdm; print(tqdm.__file__)"
```

If the output points to `hermes-agent/venv/...` instead of
`standalone-env/Lib/...`, use `PYTHONPATH=""` when launching:

```bash
cd "<ComfyUI_root>/ComfyUI"
PYTHONPATH="" "<ComfyUI_root>/standalone-env/python.exe" main.py --listen 127.0.0.1 --port 8188
```

### Diagnosing stale bytecode

If the traceback shows a **comment line** as the error source (e.g.,
`File "logger.py", line 69, in flush     # Skip super().flush()...`),
stale `.pyc` bytecode is being loaded. Even after clearing `__pycache__`,
check:
- `standalone-env/Lib/site-packages/` for cached `.pyc` of installed packages
- Whether `PYTHONDONTWRITEBYTECODE=1` was actually set in the launch command
- If the ComfyUI process auto-restarted from the Desktop app (killing
  `python.exe` may not be enough — close the Desktop app too)
