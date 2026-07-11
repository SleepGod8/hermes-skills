# Comfy Desktop Windows Pitfalls (0.27.0+)

## 1. Workflow JSON Format (API mode)

ComfyUI Desktop expects node IDs as **top-level keys**, NOT wrapped in a `"nodes"` object:

```json
// ❌ WRONG — Comfy Desktop says "无法找到工作流"
{
  "nodes": {
    "1": {"class_type": "...", "inputs": {...}},
    "2": {"class_type": "...", "inputs": {...}}
  }
}

// ✅ CORRECT — API format
{
  "1": {"class_type": "...", "inputs": {...}},
  "2": {"class_type": "...", "inputs": {...}}
}
```

Remove all extra fields (`description`, `version`, `_meta`) — they confuse the parser.

## 2. tqdm OSError [Errno 22] — Practical Reality

The `references/windows-tqdm-flush-bug.md` fix (SafeStderr wrapper + bytecode cleanup) **frequently fails** on Comfy Desktop 0.27.0. Multiple attempts (logger.py patch, `PYTHONDONTWRITEBYTECODE=1`, standalone-env restart) may still produce the same crash.

**Pragmatic workaround:** Use the Comfy Desktop GUI (drag-and-drop workflow JSON → Queue Prompt). The GUI-triggered KSampler path does NOT use tqdm's asyncio variant and works reliably.

If API access is essential, killing all python.exe + restarting the Desktop app (which manages its own backend) sometimes helps, but isn't guaranteed.

## 3. Impact Pack / FaceDetailer — Dependency Hell

Installing Impact Pack for Adetailer (hand fix) on Comfy Desktop has cascading issues:

1. `FaceDetailer` requires: `image`, `model`, `clip`, `vae`, `positive`, `negative`, `bbox_detector`, `sam_model_opt`
2. `UltralyticsDetectorProvider` needs `bbox/hand_yolov8s.pt` — but models auto-download may fail
3. `SAMLoader` needs `sam_vit_b_01ec64.pth` — another download
4. `install.py` requires `torchvision` — may not be in venv

**Pragmatic alternative to Adetailer on Windows:**
- Resolution 1024×1536 (more pixels for hands)
- Sampler: `dpmpp_2m` + `karras` (better anatomy than euler_ancestral)
- Lower CFG: 5.5 (less distortion)
- Steps: 30
- Hand-positioning tags: `hands on thighs`, `hands clasped`, `hands on ground`
- Positive: `good hands`, `perfect hands`, `detailed hands`
- Negative: `bad hands, missing fingers, extra fingers, fused fingers, poorly drawn hands, mutated hands, malformed hands, disfigured hands`
- Generate 4-8 seeds, pick the best one

For hand detection models, manually download from ultralytics/assets GitHub releases and place in `models/ultralytics/bbox/`.

## 4. Comfy Desktop Python Path

- Desktop uses `standalone-env/python.exe` (NOT `.venv/Scripts/python.exe`)
- Starting manually: `PYTHONPATH="" "path/to/standalone-env/python.exe" main.py --listen 127.0.0.1 --port 8188`
- Kill + Desktop auto-restart sometimes conflicts — close Desktop fully before manual restart

## 5. Hand Improvement Prompt Tags (Animagine XL 4.0)

Verified effective for reducing hand deformities:

| Tag | Effect |
|-----|--------|
| `good hands`, `perfect hands` | Quality boost for hands |
| `detailed hands` | More rendering attention |
| `hands on thighs` | Anchors hand position (use with `leaning forward`) |
| `hands clasped` | Natural resting pose (standing) |
| `hands on ground` | For kneeling poses |
| `simple background` | Reduces model distraction → better anatomy |
| `looking at viewer` | Simplifies pose complexity |
