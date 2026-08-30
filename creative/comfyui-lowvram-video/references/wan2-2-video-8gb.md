# Wan 2.2 TI2V-5B 视频生成（RTX 4060 8GB 实测可跑）

2026-08 实测验证：Wan 2.2 TI2V-5B（I2V 图生视频）通过 GGUF 量化可在 8GB 显存跑通，
704×480×81 帧约 6 分钟，832×480×121 帧也压得住（block swap 拉高）。

## 需要的自定义节点

```bash
cd <ComfyUI>/custom_nodes
git clone --depth 1 https://github.com/city96/ComfyUI-GGUF.git
git clone --depth 1 https://github.com/kijai/ComfyUI-WanVideoWrapper.git
```

- WanVideoWrapper 主加载器（WanVideoModelLoader）**原生支持 .gguf**（自动检测扩展名），
  不需要 ComfyUI-GGUF 的包装节点；ComfyUI-GGUF 装了也不冲突。

## 依赖安装 — 必须装进 .venv，不是 standalone-env！

ComfyUI Desktop 真实后端是 `<安装目录>/ComfyUI/.venv`（torch 2.10+cu130，CUDA 正常）。
`standalone-env` 是备用环境，往里 pip 会污染（torch 变 CPU 版）。用：

```bash
PY=<ComfyUI>/ComfyUI/.venv/Scripts/python.exe
"$PY" -m pip install ftfy accelerate einops "diffusers>=0.33.0" "peft>=0.17.0" sentencepiece protobuf pyloudnorm "gguf>=0.17.1" scipy
```

注意：protobuf 7.x 顶层 `import protobuf` 会失败，但 `import google.protobuf` 正常，不影响使用。

## 模型文件（hf-mirror，全走断点续传）

| 文件 | 大小 | 目标目录 | 来源 |
|------|------|---------|------|
| Wan2.2-TI2V-5B-Q4_K_M.gguf | 3.20G | models/unet/ | QuantStack/Wan2.2-TI2V-5B-GGUF |
| Wan2.2-TI2V-5B-Q5_K_M.gguf（画质档）| 3.55G | models/unet/ | 同上 |
| umt5_xxl_fp16.safetensors | 10.59G | models/text_encoders/ | Comfy-Org/Wan_2.2_ComfyUI_Repackaged |
| wan2.2_vae.safetensors | 1.34G | models/vae/ | 同上 |

- Q 档大小实测：Q2_K 1.73G / Q3_K_M 2.37G / Q4_0 2.82G / Q4_K_M 3.20G / Q5_K_M 3.55G / Q6_K 3.92G / Q8_0 5.03G。
- **TI2V-5B 必须用 wan2.2_vae（高压缩 VAE，in_channels=12），不能用 wan_2.1_vae**（latent 维度不匹配）。
- CLIP Vision（open-clip-xlm-roberta-large-vit-huge-14_visual_fp16）**本工作流不需要**
  （Wan 2.2 I2V 走 VAE latent 的 extra_latents 路径），可不下。

## ⚠️ 关键坑：T5 文本编码器

- `LoadWanVideoT5TextEncoder` 节点**不支持 fp8_scaled 文件**：
  `umt5_xxl_fp8_e4m3fn_scaled.safetensors` 直接报错
  `"Invalid T5 text encoder model, fp8 scaled is not supported by this node"`。
- 正确做法：下载 `umt5_xxl_fp16.safetensors`，节点加载时自己量化：
  `precision=bf16, quantization=fp8_e4m3fn`。

## ⚠️ 关键坑：节点参数名 ≠ 官方示例工作流

安装的节点版本参数名与 example_workflows 里的 WIP 示例不一致。**改工作流前先查
`GET /object_info` 拿真实参数名**。实测差异：

| 节点 | 示例工作流写法 | 实际参数名 |
|------|--------------|-----------|
| WanVideoVAELoader | model | **model_name** |
| WanVideoEmptyEmbeds | length | **num_frames** |
| WanVideoTextEncode | positive / negative | **positive_prompt / negative_prompt** |
| WanVideoEasyCache | coefficient / steps_to_cache / device | **easycache_thresh / start_step / end_step / cache_device** |
| WanVideoSLG | layers / gamma / beta | **blocks / start_percent / end_percent** |
| ImageResizeKJv2 | 不存在 | 用内置 **ImageScale** |
| VHS_VideoCombine | 传 pix_fmt/crf 等 | 只传 required：images/frame_rate/loop_count/filename_prefix/format/pingpong/save_output |

## 8GB 优化配置（API 格式工作流）

```jsonc
// WanVideoModelLoader
{"model": "Wan2.2-TI2V-5B-Q4_K_M.gguf", "base_precision": "fp16_fast",
 "quantization": "disabled", "load_device": "offload_device",
 "attention_mode": "sdpa", "block_swap_args": ["200", 0]}
// WanVideoBlockSwap (id 200)
{"blocks_to_swap": 20, "offload_img_emb": false, "offload_txt_emb": false}  // 121帧用 25
// LoadWanVideoT5TextEncoder
{"model_name": "umt5_xxl_fp16.safetensors", "precision": "bf16",
 "load_device": "offload_device", "quantization": "fp8_e4m3fn"}
// WanVideoEncode / WanVideoDecode: enable_vae_tiling=true, tile 272/272/144/128
// WanVideoSampler: steps 20, cfg 5, shift 8, scheduler flowmatch_pusa,
//   text_embeds, cache_args, slg_args
// 分辨率：ImageScale → 704×480 或 832×480；WanVideoEmptyEmbeds num_frames 81 或 121
```

- 5B 模型共 30 个 transformer blocks；block swap 20（81帧）~ 25（121帧）可压住 8GB。
- 实测显存曲线：采样阶段 GPU 99% / ~7.7G；VAE 解码 tiling 阶段回落到 2-4G。
- 完整可用工作流文件：`E:\Hermes workspace\comfyui_workflow\wan2.2_ti2v_5b_i2v_8gb_api.json`。

## 真人写真管线（角色一致性强）

1. SD1.5/SDXL 出真人图（如 Realistic_Vision_V5.1，768² 或 CyberRealisticPony 1024²）→ SaveImage
2. 把 output 图片复制到 ComfyUI input 目录（`models/../input/`）
3. Wan I2V 工作流 LoadImage 指向该图 → 视频（**脸/画风不变**，这是 I2V 路线的核心优势）

## 低显存社区参考

- v8turbo420517-prog/vram8gb_comfyui_wan2.2（GitHub）：3060 Ti 8GB 跑 **14B** 的参考实现，
  双 KSampler 动态切换 GGUF（HighNoise/LowNoise），峰值 <7GB。5B 不需要这么折腾。
- 14B 作者管线：低分辨率生成 → Topaz Video AI 放大 → 后期调色。720P 是生成上限不是成品上限。

## CyberRealisticPony（真人 NSFW 出图）

- 文件名是 `CyberRealisticPony_V18.0_F16.safetensors`（V3.1 不存在，会 404 只下到 15 字节错误页）。
- Pony 系提示词：`score_9, score_8_up, score_7_up, rating:explicit, ...`，28 步 CFG 7 dpmpp_2m karras 1024²。
