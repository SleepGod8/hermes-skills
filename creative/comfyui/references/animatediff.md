# AnimateDiff Reference

## Node compatibility matrix

| ComfyUI Version | Working Nodes | Broken Nodes |
|-----------------|--------------|--------------|
| 0.27.0+ (current) | `ADE_LoadAnimateDiffModel` + `ADE_ApplyAnimateDiffModelSimple` | `ADE_AnimateDiffLoaderV1Advanced` (AttributeError) |
| < 0.27.0 | `ADE_AnimateDiffLoaderV1Advanced`, `ADE_AnimateDiffLoaderGen1` (takes model_name directly) | — |

## Error → Fix mapping

| Error | Cause | Fix |
|-------|-------|-----|
| `'ModelPatcherDynamic' object has no attribute 'motion_models'` | Deprecated node on ComfyUI 0.27.0+ | Use `ADE_LoadAnimateDiffModel` + `ADE_ApplyAnimateDiffModelSimple` |
| `Return type mismatch: received_type(MODEL) mismatch input_type(LATENT)` | VAE Decode connected to ADE loader output instead of KSampler | Connect `VAEDecode.samples` to `KSampler[0]`, not to ADE node |
| `ModuleNotFoundError: No module named 'PIL'` or pydantic import error | PYTHONPATH contamination from Hermes venv | Run with `PYTHONPATH=""` before ComfyUI's Python |
| `Required input is missing: seed_offset, batch_offset, noise_type, seed_gen` | `ADE_AnimateDiffSamplingSettings` node missing inputs | Omit the sampling settings node entirely — default params apply |
| `Required input is missing: beta_schedule, model_name` | `ADE_AnimateDiffLoaderGen1` used with external motion model | Use `ADE_AnimateDiffLoaderGen1` alone (takes model_name as string param), or use `ADE_LoadAnimateDiffModel` + `ADE_ApplyAnimateDiffModelSimple` |

## Test workflow (API format — ready to POST)

```json
{
  "prompt": {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "Realistic_Vision_V5.1.safetensors"}},
    "4": {"class_type": "LoadImage", "inputs": {"image": "test_input.png"}},
    "10": {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["1", 2]}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "cinematic, high quality, detailed, motion", "clip": ["1", 1]}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "blurry, low quality", "clip": ["1", 1]}},
    "7": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["1", 2]}},
    "11": {"class_type": "VHS_VideoCombine", "inputs": {"frame_rate": 8, "loop_count": 0, "filename_prefix": "AnimateDiff", "format": "video/h264-mp4", "pingpong": false, "save_output": true, "images": ["7", 0]}},
    "2": {"class_type": "ADE_LoadAnimateDiffModel", "inputs": {"model_name": "mm_sd_v15_v2.ckpt"}},
    "3": {"class_type": "ADE_ApplyAnimateDiffModelSimple", "inputs": {"motion_model": ["2", 0]}},
    "9": {"class_type": "KSampler", "inputs": {"seed": 42, "steps": 20, "cfg": 4.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["1", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["10", 0]}}
  }
}
```

### How to test

```bash
# 1. Start ComfyUI
cd /path/to/ComfyUI && PYTHONPATH="" ./.venv/Scripts/python main.py --listen 127.0.0.1 --port 8188

# 2. Create test image
python -c "
from PIL import Image, ImageDraw
img = Image.new('RGB', (512, 512), (50, 80, 180))
img.save('/path/to/ComfyUI/input/test_input.png')
"

# 3. Submit workflow
curl -s -X POST http://127.0.0.1:8188/prompt -H 'Content-Type: application/json' -d '<JSON above>'

# 4. Wait and check
curl -s http://127.0.0.1:8188/queue
ls -lh /path/to/ComfyUI/output/AnimateDiff*.mp4
```

## Motion module storage

Motion modules (`.ckpt`) go in `models/animatediff_models/`, NOT in `checkpoints/` or `loras/`.

On Comfy Desktop (Windows), the shared models path is separate:
- SD checkpoints: `E:\Comfy-Desktop\ComfyUI-Shared\models\checkpoints\`
- Motion modules: `E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\animatediff_models\`

Verify the search path is wired by checking `extra_model_paths.yaml`:
```yaml
animatediff:
  base_path: E:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/models/animatediff_models
```
