---
name: comfyui-anime-character-pipeline
description: "Generate anime characters via local ComfyUI (animagine)."
version: 1.0.0
author: agent
tags: [comfyui, animagine, anime, image-generation, maid, detailer]
platforms: [windows]
---

# ComfyUI Anime Character Pipeline (本机专用)

为本机（RTX 4060 Laptop 8GB）生成动漫角色图：animagine-xl-4.0 + Impact Pack 手部精修。
工作流文件存 `E:\ai1\comfyui_workflow\`（API 格式 JSON），输出落 `E:\Comfy-Desktop\ComfyUI-Shared\output\`。

## 环境真相（关键，先读）

- **ComfyUI 后端实际用 `.venv`**：`E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe`，torch 2.10.0+cu130，CUDA 正常。
- **`standalone-env` 是另一套环境**（`...\ComfyUI\standalone-env\python.exe`），ComfyUI 主进程**不用它**。往它 pip 装包会把它的 torch 换成 CPU 版（2.13.0+cpu）——不影响 ComfyUI 运行，但会造成困惑。
- 给 ComfyUI 装任何依赖 → 必须装进 `.venv`，且装完验证 `torch.cuda.is_available()`。
- 服务地址：`http://127.0.0.1:8188`（Comfy Desktop 托管）。模型在 `E:\Comfy-Desktop\ComfyUI-Shared\models\`（checkpoints 等）与 `...\ComfyUI\ComfyUI\models\`（sams/ultralytics/onnx 等）。

## 标准流程（txt2img + 手部精修）

1. 查服务：`curl -s http://127.0.0.1:8188/system_stats`
2. 写 API 格式工作流 JSON（平铺节点 ID，`class_type` + `inputs`，无 `nodes` 包装），参考 `templates/athena_maid_detailer_api.json`。
3. 关键节点链：
   ```
   CheckpointLoaderSimple(animagine-xl-4.0.safetensors)
     → CLIPTextEncode(正/负) → EmptyLatentImage(896×1152)
     → KSampler(euler_ancestral, cfg 7, steps 30-32)
     → VAEDecode
     → UltralyticsDetectorProvider(bbox/hand_yolov8s.pt)
     → SAMLoader(sam_vit_b_01ec64.pth, device_mode=AUTO)
     → FaceDetailer(全部必填参数见 references/impact-detailer-params.md)
     → PreviewImage + SaveImage
   ```
4. 运行：
   ```bash
   python "C:/Users/80704/AppData/Local/hermes/skills/creative/comfyui/scripts/run_workflow.py" \
     --workflow X.json --args '{"seed": -1}' --output-dir /e/ai1/comfyui_workflow/output --timeout 420
   ```
   ⚠️ 该脚本 stdout 报告的 `E:\e\ai1\...` 路径是错的——真实文件在 ComfyUI 的 output 目录，用 `find /e/Comfy-Desktop -name "*.png" -mmin -10` 找。

## 提示词配方（animagine = Danbooru 标签）

- 质量增强词：`masterpiece, best quality, very aesthetic, amazing quality, year 2024`
- 画师风格：`((artist:melon22)), artist:ikarin`
- 手部正向：`good hands, perfect hands, detailed hands, 5 fingers`
- 手部负向：`bad hands, missing fingers, extra fingers, fused fingers, too many fingers, poorly drawn hands, mutated hands, malformed hands, disfigured hands`
- 高大丰腴身材：`tall, voluptuous, curvy, wide hips, thick thighs, big breasts, hourglass figure`；负向加 `petite, skinny, thin, flat chest`
- 角色设定示例：Hermes=白短发巨乳眯眯眼；Athena=银长直发眯眯眼冷艳女仆（`athena_maid_workflow_api.json` 无精修 / `athena_maid_detailer_api.json` 带精修）

## Anima 模型（新，2026-08 添加）

**Anima**（circlestone-labs/Anima）＝ CircleStone Labs × Comfy Org 合作 2B 动漫文生图，基于 NVIDIA Cosmos-Predict2-2B，单文件 diffusion 格式，ComfyUI 原生支持。

- **三个文件**：`anima-base-v1.0.safetensors`（→ diffusion_models，3988MB）、`qwen_3_06b_base.safetensors`（→ text_encoders，1137MB）、`qwen_image_vae.safetensors`（→ vae，242MB）
- **工作流节点链**：`UNETLoader(unet_name=anima) → CLIPLoader(clip=qwen_3_06b, type=cosmos) → VAELoader(qwen_image_vae)`，另加 `ModelSamplingContinuousEDM(sampling=cosmos_rflow, sigma_max=120, sigma_min=0.002)`
- **参数**：分辨率 512²~1536²；30-50 steps / CFG 4-5；采样器 `er_sde`（默认）/ `euler_a` / `dpmpp_2m_sde_gpu`；调度器 sgm_uniform
- **提示词**：Danbooru 标签，小写+空格（score_* 用下划线）；质量前缀 `masterpiece, best quality, score_7, safe`；画师用 `@artist`；负向 `worst quality, low quality, score_1, score_2, score_3, artist name`
- **测试实测**：anima-base 30 steps/CFG4.5/er_sde/sgm_uniform/896×1152 → 30 秒出图（RTX 4060 8GB），质量良好

### ⚠️ Anima-2.9B（社区层扩展版）坑

**Anima-2.9B**（Gazingstars123）= 官方 Anima 层扩展微调（28→40层，~2.9B），知识截止 2026-07。

- 全精度 `Anima-2.9B-preview-v1.safetensors`（5843MB）
- int8 量化 `Anima-2.9B-preview-v1_int8_convrot.safetensors`（3082MB）
- **int8 量化版在 ComfyUI 输出灰图**！日志特征：`Detected mixed precision quantization` + `model weight dtype torch.bfloat16, manual cast: torch.bfloat16` → 量化权重被当普通 bfloat16 用，反量化没生效。v0.31.0 和 v0.34.2 都复现。**不要用 int8 版，用全精度版**（int8 版已删，避免误用）
- ComfyUI 旧版（<0.33.1）加载 2.9B 会报 `unet unexpected: blocks.28-39.*`（扩展层被忽略→灰图），需升级或装 ComfyUI-Anima-2.9B 插件
- **⚠️ 全精度版也灰图！** v0.34.2 + `manual cast: None` 加载正常（5572MB），但3组参数（无sigma / sigma=200 / sigma=120）全部饱和度<8。根因：ComfyUI UNETLoader 不读 `expand_manifest.json`（zeroed_tensors + 插入位置），40层扩展架构的计算图残缺。**需要专门的 `ComfyUI-Anima-2.9B` 自定义节点**（https://github.com/gazingstars123/ComfyUI-Anima-2.9B）
- 2.9B 推荐参数：euler/sgm_uniform（或 res-multistep/linear-quadratic），812×1216 / 1152×1536，28-50 steps，CFG 3.5-5；提示词越详细越好，推荐加 @artist
- **当前结论：2.9B 在 ComfyUI 原生跑不了，等装插件后再试。Anima 2B（官方）在 ComfyUI 里正常可用。**

## 踩坑记录

1. **pip 装依赖换掉 torch**：`pip install ultralytics`（带依赖）会把 torch 重装成 CPU 版。**必须 `--no-deps`**，再单独补轻量依赖（matplotlib opencv-python-headless dill）。恢复 CUDA torch 用阿里镜像 wheel：`https://mirrors.aliyun.com/pytorch-wheels/cu130/torch-2.13.0+cu130-cp313-cp313-win_amd64.whl`。
2. **FaceDetailer/SAMLoader 新版必填参数多**：缺参会报 `required_input_missing` 并列出字段名（本轮踩了 `sam_mask_hint_threshold`、`sam_mask_hint_use_negative`、`device_mode` 三处）。修法：`curl /object_info/<节点>` 拿全 required 再填。完整清单见 `references/impact-detailer-params.md`。
3. **git-bash 里 taskkill**：`//F //PID` 会报无效参数。用 `export MSYS_NO_PATHCONV=1` 后 `taskkill /F /PID <pid>`。
4. **杀掉 main.py 不会自动重启**：Comfy Desktop 不会拉起被杀掉的 python 后端，需手动用原命令行重启（`wmic process where "name='python.exe'" get ProcessId,CommandLine` 找回）。重启时 `--output-directory` 参数里的反斜杠会被 bash 吃掉 → 用正斜杠。
5. **手部模型下载源（国内可用）**：`https://hf-mirror.com/Bingsu/adetailer/resolve/main/hand_yolov8s.pt`（22.5MB）。Bingsu/adetailer 仓库只有 .pt 没有 .onnx；github releases / api.github.com 不稳定。
6. **验证节点注册**：`curl http://127.0.0.1:8188/object_info/UltralyticsDetectorProvider` 应返回 `model_name: [['bbox/hand_yolov8s.pt']]`。
7. **手动重启后路径错乱**：反斜杠参数会让输出落到拼接怪路径（如 `Comfy-DesktopComfyUI-Sharedoutput/`），改传正斜杠参数。

## 参考

- `references/impact-detailer-params.md` — 本机 ComfyUI 0.27.0 的 FaceDetailer / SAMLoader / UltralyticsDetectorProvider 全部必填参数
- `templates/athena_maid_detailer_api.json` — 已知可用的完整精修工作流模板
- 官方 comfyui 技能（hub，勿改）的 `references/animagine-prompts.md` 有完整 Danbooru 标签库
