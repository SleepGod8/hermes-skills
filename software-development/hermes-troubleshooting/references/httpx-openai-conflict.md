# httpx / openai version conflict

## Error signature

```
Failed to initialize OpenAI client: cannot import name 'URL' from 'httpx' (unknown location)
```

## Root cause chain

1. `httpx` >= 0.28.0 removed the `URL` class (moved to a submodule)
2. Older `openai` packages (pre-1.55-ish) import `URL` from `httpx` root
3. When Hermes Desktop bundles a new httpx with an old openai → crash on import

## Which component is affected?

Hermes Desktop bundles its own Python runtime with pip-installed packages. The conflict
happens in that bundled environment, not in the system Python or user conda envs.

## Finding Hermes's bundled Python

Typical paths on Windows:
- `C:\Users\<user>\AppData\Local\hermes\python\python.exe`
- `<Hermes Desktop install dir>\python\python.exe`

## Compatible version matrix

| httpx | openai | Status |
|-------|--------|--------|
| 0.27.x | any | ✅ Compatible |
| 0.28.x | < 1.55 | ❌ Conflict |
| 0.28.x | >= 1.55 | ✅ Compatible |

## Resolution

Preferred: `pip install httpx==0.27.2` in Hermes's bundled Python.
Alternative: `pip install --upgrade openai` to get a new enough openai.

If the bundled Python is not writable, reinstall Hermes Desktop from the latest installer.
