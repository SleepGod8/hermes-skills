# Hardware-to-Model Guide for Local LLMs

## Reference hardware (from session — AMD Ryzen 7 PRO 7730U)

| Component | Spec |
|-----------|------|
| CPU | AMD Ryzen 7 PRO 7730U, 8C/16T, 2.0GHz base (laptop) |
| RAM | 32GB DDR4 3200MHz |
| GPU | AMD Radeon integrated (1GB VRAM, no discrete GPU) |
| Storage | 80GB free (C:) / 200GB free (D:) |

## Models tested on this hardware

| Model | Size | Load time | Speed | Verdict |
|-------|------|-----------|-------|---------|
| glm-4.7-flash | 19 GB (30B MoE, Q4) | 1-2 min | Slow | ❌ Too heavy for CPU |
| qwen2.5:7b | 4.7 GB (7B, Q4) | <5 sec | Fast | ✅ Sweet spot |

## Recommended models for CPU-only

### Tier 1: Best for Chinese (7B, ~5GB, 32GB RAM required)
- `qwen2.5:7b` — best Chinese support, fast on CPU
- `qwen2.5:3b` — smaller, faster, good Chinese

### Tier 2: Best for English (3-9B, 2-6GB)
- `llama3.2:3b` — Meta's latest small model, very fast
- `gemma2:9b` — Google, strong English (~5.5GB)
- `phi3:mini` (3.8B) — Microsoft, efficient
- `mistral:7b` — well-rounded 7B

### Tier 3: Large (if you have a GPU or lots of patience)
- `qwen2.5:14b` (~9GB)
- `llama3.1:8b` (~4.9GB)
- `mixtral:8x7b` (~26GB, MoE)

## Disk space estimates
- Each 7B Q4 model: ~4-5GB
- Each 3B Q4 model: ~2GB
- glm-4.7-flash (30B MoE): ~19GB
