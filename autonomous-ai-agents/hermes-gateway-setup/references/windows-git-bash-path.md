# Windows Git Bash Path: Fixing "Git Bash not found" in Hermes

Hermes terminal tool on Windows requires `bash.exe` from Git for Windows to run commands. If Git is installed at a non-standard location (e.g., `D:\Program Files\Git` instead of `C:\Program Files\Git`), the terminal tool fails with:

```
RuntimeError: Git Bash not found. Hermes Agent requires Git for Windows on Windows.
```

## Diagnosis

Check if bash.exe exists and where:

```python
import os, subprocess

# Check common paths
for p in [
    r"C:\Program Files\Git\bin\bash.exe",
    r"D:\Program Files\Git\bin\bash.exe",
]:
    print(f"{'✅' if os.path.exists(p) else '❌'} {p}")

# Check via where
result = subprocess.run(["where", "bash"], capture_output=True, text=True, shell=True)
print(f"where bash: {result.stdout}")
```

Also check for Git bundled with GitHub Desktop:
```
C:\Users\<user>\AppData\Local\GitHubDesktop\app-*\resources\app\git\usr\bin\sh.exe
```
Note: GitHub Desktop ships `sh.exe`, NOT `bash.exe`. Hermes requires `bash.exe` specifically.

## Fix: Set HERMES_GIT_BASH_PATH

### Method A: Set in Hermes .env (recommended)

Append to `$HERMES_HOME/.env`:
```env
# Git Bash path — needed when Git is at non-standard location
HERMES_GIT_BASH_PATH=D:\Program Files\Git\bin\bash.exe
```

### Method B: Set Windows user environment variable

```cmd
setx HERMES_GIT_BASH_PATH "D:\Program Files\Git\bin\bash.exe"
```

Verify in registry:
```cmd
reg query HKCU\Environment /v HERMES_GIT_BASH_PATH
```

### Method C: Temporary per-session (for testing)

```bash
export HERMES_GIT_BASH_PATH="D:\Program Files\Git\bin\bash.exe"
```

## Verification

After setting the variable, restart Hermes (the env var is read at startup):

```python
import subprocess
bash_path = r"D:\Program Files\Git\bin\bash.exe"
result = subprocess.run([bash_path, "-c", "git --version"], 
                       capture_output=True, text=True, timeout=10)
print(result.stdout.strip())  # Should show git version
```

Then the Hermes `terminal` tool should work.

## Root Cause

Hermes on Windows discovers Git Bash via:
1. `HERMES_GIT_BASH_PATH` env var (checked first)
2. Default install path `C:\Program Files\Git\bin\bash.exe`
3. PATH lookup

If Git is installed to a non-C: drive or custom path, only option 1 works.
