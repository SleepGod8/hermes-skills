---
name: comfyui-video-generation
description: "Use when 用户要在 ComfyUI 跑视频生成或问哪个视频模型适合本机。"
license: MIT
metadata:
  hermes:
    tags: [comfyui, video-generation, animatediff, ltx-video, wan, cogvideox, low-vram, rtx4060]
    category: creative
---

# ComfyUI 视频生成选型与部署

在 ComfyUI 里跑视频生成模型：按"确认本机已有资产 → 按显存选模型 → 装节点/补模型 → 低分辨率短片段验证 → 交付"执行。覆盖 AnimateDiff、LTX-Video、Wan（2.1/2.2）、CogVideoX、HunyuanVideo、SVD 等。

## When to Use / 使用场景

- 用户问"本机能跑什么视频模型"、"哪个视频模型适合我"。
- 用户要在 ComfyUI 里配置视频工作流（文生视频/图生视频）。
- 用户报告视频节点缺失、显存不足、motion module 缺失、模型加载失败。
- 用户问某个模型文件"是哪来的/什么时候下的"（来源溯源，见 references/model-provenance-forensics.md）。

## 关键事实（本机 2026-08 实测）

- 共享模型目录 `E:\Comfy-Desktop\ComfyUI-Shared\models`；后端 `E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI`；自定义节点在后端 `custom_nodes/`（不是共享目录）。
- 本机已装视频相关节点：`ComfyUI-AnimateDiff-Evolved`、`ComfyUI-VideoHelperSuite`；还有 `ComfyUI-Anima-2.9B`（**注意：Anima-2.9B 是图像模型不是视频模型**，别被节点名误导）。
- 本机 `animatediff_models/` 为空 → 跑 AnimateDiff 必须先下 motion module（SD1.5: `v3_sd15_mm.ckpt`；SDXL: `mm_sdxl_v10_beta.ckpt`）。
- 国内网络：huggingface.co 直连不通（curl 返回 000），一律用 `https://hf-mirror.com`（API 和 raw 都可用）。

## 模型选型矩阵（8GB VRAM 实测/官方数据）

| 模型 | 大小/显存 | 8GB 结论 | 来源 |
|------|----------|---------|------|
| AnimateDiff + 已有 SDXL/SD1.5 | motion module 1-2GB | ✅ 首选，配合已有 animagine/NoobAI 画风无缝 | hf: guoyww/animatediff-motion-adapter-v1-5-2 |
| LTX-Video 2B (ltxv-2b-0.9.8-distilled) | ~4-6GB | ✅ 轻快，秒级起步 | hf: Lightricks/LTX-Video (47万下载) |
| Wan 2.1 T2V-1.3B | ~4-6GB | ✅ GGUF 量化更稳 | hf: Wan-AI/Wan2.1-T2V-1.3B-Diffusers (21万) |
| CogVideoX-2B | FP16 4GB 起 / INT8 3.6GB | ✅ 官方数据 | hf: zai-org/CogVideoX-2b |
| Wan 2.2 TI2V-5B | 官方标 24GB | ⚠️ 8GB 需 GGUF+低分辨率+offload，很慢 | hf: Wan-AI/Wan2.2-TI2V-5B-Diffusers；Comfy-Org/Wan_2.2_ComfyUI_Repackaged (480万) |
| Wan 2.2 A14B / Wan Animate 2 14B | 27B MoE/14B | ❌ 8GB 没戏 | hf: Wan-AI/Wan2.2-Animate-2-14B |
| HunyuanVideo 1.5 | 13B | ❌ 能加载但每帧几分钟，不推荐 | hf: Comfy-Org/HunyuanVideo_1.5_repackaged (45万) |
| Mochi 1 / SVD | 10B / 2B | ❌ / 老 | - |

完整调研数据（下载量、README 关键句、ComfyUI 适配）见 [references/video-model-landscape.md](references/video-model-landscape.md)。

## Procedure / 标准流程

1. **盘点本机**：`nvidia-smi` 确认显存；列出 `custom_nodes/` 和 `models/` 各子目录（checkpoints/diffusion_models/text_encoders/vae/animatediff_models/loras），记录已有与缺失。
2. **查模型卡**：用 hf-mirror API 确认规格与显存——
   - 列表：`curl -s "https://hf-mirror.com/api/models?search=<关键词>&sort=downloads&direction=-1&limit=10"`
   - 详情：`curl -s "https://hf-mirror.com/api/models/<org>/<name>"`
   - README：`curl -s "https://hf-mirror.com/<org>/<name>/raw/main/README.md" | grep -iE "vram|memory|GB|GPU"`
   - 官方显存数据优先于社区传言；标注"官方标 24GB"与"8GB 实测"的差异。
3. **按矩阵选型**：8GB 首选 AnimateDiff（已装节点只缺 motion module）→ 想要真·视频用 LTX-2B 或 Wan2.1-1.3B。
4. **装节点/补模型**：AnimateDiff motion module 走 hf-mirror 下载到 `animatediff_models/`；LTX/Wan 需装对应 ComfyUI 节点。
5. **验证**：低分辨率（≤512）短片段（≤2s）batch 1 起步，记录峰值显存与耗时；确认输出能保存、能预览。

## Pitfalls / 坑

- **Anima-2.9B ≠ 视频模型**：它是 circlestone-labs 的动漫图像模型，节点名 `ComfyUI-Anima-2.9B` 会让人误以为是视频。
- **模型目录有两处**：共享目录 `ComfyUI-Shared\models` 放模型；自定义节点在后端 `ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes`。找节点别去共享目录。
- **hf 直连必挂**：huggingface.co 返回 000/401，hf-mirror.com 是唯一可用镜像（用户偏好见 memory）。
- **官方"能跑"≠8GB 能跑**：Wan2.2-5B 官方说单消费级 GPU（4090/24GB），8GB 必须量化降级，别承诺速度。
- **先确认节点再推模型**：节点缺失时模型下载了也跑不了；先 `ls custom_nodes` 再规划。

## References

- [references/video-model-landscape.md](references/video-model-landscape.md) — 2026-08 视频模型全景调研（下载量/显存/README 要点）
- [references/model-provenance-forensics.md](references/model-provenance-forensics.md) — 模型来源溯源技术（文件时间戳+下载缓存+会话历史交叉验证）
