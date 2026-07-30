# Ollama Local LLM Provider

Configure Hermes Agent to use a local LLM via Ollama.

## Quick Setup

```bash
# 1. Install Ollama (Windows)
# Download from https://ollama.com/download, run OllamaSetup.exe

# 2. Pull a model
ollama pull qwen3:8b        # ~5GB, best Chinese support
ollama pull glm4:9b         # ~5.5GB, Zhipu GLM
ollama pull deepseek-r1:8b  # ~5GB, strong reasoning

# 3. Start Ollama (auto-starts as system service, or manually)
ollama serve

# 4. Verify API works
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3:8b","messages":[{"role":"user","content":"hi"}],"max_tokens":50}'

# 5. Add as Hermes custom provider
# In config.yaml:
custom_providers:
  - name: ollama
    base_url: http://localhost:11434/v1
    model: qwen3:8b

# 6. Switch to local model
hermes config set model.provider custom:ollama
hermes config set model.base_url http://localhost:11434/v1
hermes config set model.default qwen3:8b
# Start a new session with /new
```

## Recommended Models by Hardware

| Hardware | Model | Size | RAM/VRAM | Notes |
|----------|-------|:----:|:--------:|-------|
| No GPU, 8GB RAM | Qwen3:4B | ~2.5GB | 8GB | Slow but usable |
| No GPU, 16GB RAM | Qwen3:8B | ~5GB | 16GB | Best balance for CPU |
| No GPU, 32GB RAM | GLM4:9B | ~5.5GB | 32GB | Good Chinese, faster on CPU |
| No GPU, 32GB RAM | GLM-4.7-Flash (Q4) | ~19GB | 32GB+ | **Slow on CPU** (~2-5 tok/s), very capable if patient. 30B MoE model |
| 6GB+ VRAM | Qwen3:8B (GPU offload) | ~5GB | 6GB+ | Much faster than CPU |
| 12GB+ VRAM | Qwen3:14B | ~9GB | 12GB+ | Strongest local option |

## Available Models on Ollama

| Model | Sizes | Chinese | Tools | Vision | Type | Notes |
|-------|-------|:-------:|:-----:|:------:|------|-------|
| **Qwen3** | 0.6B/4B/8B/14B/30B/32B/235B | ⭐⭐⭐⭐⭐ | ✅ | ✅ (VL) | Local | Best all-rounder. VL variants for vision |
| **Qwen2.5** | 0.5B/1.5B/3B/7B/14B/32B/72B | ⭐⭐⭐⭐⭐ | ✅ | ✅ (VL) | Local | Mature, well-tested |
| **GLM-4.7-Flash** | ~30B MoE (Q4=19GB) | ⭐⭐⭐⭐⭐ | ✅ | ❌ | Local | 🆕 Latest, strong tools+thinking, heavy on CPU |
| **GLM4** | 9B | ⭐⭐⭐⭐⭐ | ✅ | ✅ (4V) | Local | Good Chinese, vision variant available |
| **GLM-5.1 / 5.2** | — | ⭐⭐⭐⭐⭐ | ✅ | ❌ | Cloud only | Latest flagship, too large for local |
| **DeepSeek-R1** | 1.5B/7B/8B/14B/32B/70B/671B | ⭐⭐⭐⭐ | ✅ | ❌ | Local | Strong reasoning (chain-of-thought) |
| **Llama 3.1** | 8B/70B/405B | ⭐⭐⭐ | ✅ | ❌ | Local | Meta flagship, English strong |
| **Llama 3.2** | 1B/3B | ⭐⭐⭐ | ✅ | ❌ | Local | Lightweight |
| **Gemma 3** | 1B/4B/12B/27B | ⭐⭐⭐ | ❌ | ✅ | Local | Google, vision support |
| **Kimi K2.5/2.6/2.7** | 1.04T | ⭐⭐⭐⭐⭐ | ✅ | ✅ | **Cloud only** | Tagged `cloud`, too large for local |

## Migration: Move Ollama from C: to D:

Ollama defaults to storing models in `C:\Users\<user>\.ollama\models`. To move to another drive:

### Method A: Environment variables (before install)

1. Set **System environment variables** (not User):
   - `OLLAMA_HOME` = `D:\\Ollama`
   - `OLLAMA_MODELS` = `D:\\Ollama\\models`
2. Install Ollama — it will auto-detect these and store models on D:\

> ⚠️ Note: Environment variables must be set **before** install. Setting them after install may not redirect existing models — they stay at the default path.

> ⚠️ Note: Even if system env vars like `OLLAMA_HOME`/`OLLAMA_MODELS` are set correctly,
> Ollama may still install the program binary to `%LOCALAPPDATA%\\Programs\\Ollama\\` (C drive)
> instead of `%ProgramFiles%\\Ollama\\` (system drive). This happens because the installer
> chooses the user-local path by default regardless of env vars. The env vars only control
> where **model data** is stored — check `ollama list` after install and verify model blobs
> land on D: drive (not C:\Users\\.ollama). If models erroneously go to C:
> (old default path), the symbolic link method below is the simplest fix — no reinstall needed.

### Method B: Symbolic link (after install, no reinstall needed)

Run as **Administrator** in cmd.exe:

```cmd
:: 1. Stop Ollama (exit from system tray or taskkill)
taskkill /f /im ollama.exe
taskkill /f /im "ollama app.exe"

:: 2. Move the .ollama folder
move C:\\Users\\<YOUR_USERNAME>\\.ollama D:\\Ollama

:: 3. Create a junction (directory symlink)
mklink /J C:\\Users\\<YOUR_USERNAME>\\.ollama D:\\Ollama

:: 4. Start Ollama (from Start Menu or reboot)
```

If `move` fails with "access denied":
1. Kill Ollama processes: `taskkill /f /im ollama.exe && taskkill /f /im "ollama app.exe"`
2. Verify no cmd/PowerShell window has `C:\Users\...\.ollama` as its working directory
3. Ensure D: drive has a clean target — delete `D:\\Ollama\\models\\blobs` and `D:\\Ollama\\models\\manifests` empty subdirs first, then `D:\\Ollama\\models`, then `D:\\Ollama`
4. If `move` still fails, use `xcopy` + `rmdir` instead:

```cmd
:: Remove empty remnants on D: first
rmdir D:\\Ollama\\models\\blobs
rmdir D:\\Ollama\\models\\manifests
rmdir D:\\Ollama\\models
rmdir D:\\Ollama

:: Copy and replace
xcopy C:\\Users\\<YOUR_USERNAME>\\.ollama D:\\Ollama /E /I /H
rmdir /S /Q C:\\Users\\<YOUR_USERNAME>\\.ollama
mklink /J C:\\Users\\<YOUR_USERNAME>\\.ollama D:\\Ollama
```

> ✅ After migration, verify with: `ls -la C:\\Users\\<YOUR_USERNAME>\\.ollama`
> — it should show a junction pointing to D: and contain the model blobs.

### Verifying the migration

```bash
ollama list                  # should show your models
dir D:\Ollama\models\blobs   # should contain model data
```

## Known Limitations

- **Tool calling support varies**: Older local models may not support function/tool calling properly. Qwen3 and GLM4:9B are reliable. Test with a simple tool call first.
- **GLM-4.7-Flash has strong tool support**: It supports `tools` and `thinking` capabilities (confirmed via Ollama API capabilities field). Good candidate for agent workflows.
- **CPU-only is slow**: Expect 5-10 tokens/s for 8B models on CPU. Fine for chat, painful for long documents. GLM-4.7-Flash (30B MoE) on CPU is only ~2-5 tok/s — expect 30-60s response times for tool calls.
- **No vision**: Local models without vision capability can't process images.
- **Ollama auto-starts on login** (Windows service). No manual `ollama serve` needed after install.
- **OLLAMA_HOME/OLLAMA_MODELS env vars may not be on git-bash PATH**: Set as **System** env vars (not User). Git-bash needs restart to pick them up, but PowerShell/cmd detect them immediately.
