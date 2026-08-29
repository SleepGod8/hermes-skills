# 本机 ComfyUI 模型库存与 Z-Image-Turbo 档案（2026-08 盘点）

## 本机模型清单（E:\Comfy-Desktop\ComfyUI-Shared\models）

| 类型 | 文件 | 大小 | 说明 |
| --- | --- | ---: | --- |
| checkpoint | animagine-xl-4.0.safetensors | 6.5G | 动漫二次元（Danbooru 标签系），角色图首选 |
| checkpoint | NoobAI-XL-v1.1.safetensors | 6.7G | 动漫全能 |
| checkpoint | Realistic_Vision_V5.1.safetensors | 4.0G | SD1.5 写实人像 |
| diffusion_model | z_image_turbo_bf16.safetensors | 11.5G | Z-Image Turbo 6B DiT 主干 bf16 |
| diffusion_model | Anima-2.9B-preview-v1.safetensors | 5.4G | Anima 2.9B 预览版 |
| diffusion_model | anima-base-v1.0.safetensors | 3.9G | Anima 基础版 |
| text_encoder | qwen_3_4b.safetensors | 7.5G | Qwen3-4B（Z-Image Turbo 配套 TE） |
| text_encoder | qwen_3_06b_base.safetensors | 1.1G | Qwen3-0.6B（轻量 TE，Anima 配套） |
| vae | ae.safetensors | 320M | Qwen-Image VAE（FLUX 系命名） |
| vae | qwen_image_vae.safetensors | 243M | Qwen-Image VAE |

空目录（无模型）：loras / controlnet / upscale_models / embeddings / clip_vision / ultralytics / onnx。

## Z-Image-Turbo 档案（官方模型卡确认）

- Tongyi-MAI（阿里通义）6B 单流 Diffusion Transformer；Apache-2.0；论文 arXiv:2511.22699；官方站 tongyi-mai.github.io/Z-Image-blog。
- 蒸馏加速版仅需 8 NFE（步）；官方标称 16G VRAM 消费卡舒适运行；强项=写实照片级+中英文文字渲染+指令跟随。
- ComfyUI 加载：UNETLoader + CLIPLoader(Qwen3-4B) + VAELoader，steps 4~8。
- **8GB 卡适配**：bf16 全精度必爆显存；可行路线=GGUF 量化（Q4/Q5 后主干约 4~5GB）或 Nunchaku 后端，或降级 TE 到 qwen_3_06b_base。未实测不承诺可跑。

## 国内网络查 HF 模型档案

`huggingface.co` 直连超时（curl 000），`hf-mirror.com` REST API 可用：

```bash
curl -s "https://hf-mirror.com/api/models/<org>/<repo>"                       # 元数据
curl -s "https://hf-mirror.com/<org>/<repo>/raw/main/README.md"               # 模型卡原文
```

流程：GitHub repo 搜索确认存在 → hf-mirror 拉元数据（siblings 看组件/精度/分片）→ README 看官方参数。下载同样用 hf-mirror 前缀。
