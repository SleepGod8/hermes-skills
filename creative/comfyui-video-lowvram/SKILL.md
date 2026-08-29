---
name: comfyui-video-lowvram
description: "Use when 8GB 显存 ComfyUI 选视频模型/盘点模型库/溯源模型来源。"
license: MIT
metadata:
  hermes:
    tags: [comfyui, video, vram, wan, animatediff, ltx, svd, nsfw, 8gb]
    category: creative
---

# ComfyUI 8GB 显存视频生成选型

为 RTX 4060 Laptop 8GB 的本机 ComfyUI 选择视频生成模型、评估可行性、溯源模型来源。覆盖 AnimateDiff / Wan 2.2 GGUF / LTX-Video / SVD-XT 等方案。

## When to Use / 使用场景

- 用户问「本机 ComfyUI 有什么模型可用」→ 先盘点模型库（见下）
- 用户问「X 视频模型 8GB 跑得动吗」→ 查 `references/8gb-video-models-2026.md` 实测结论
- 用户问「XX 模型从哪来的/什么时候下的」→ 用创建时间溯源法
- 用户问真人/动漫 NSFW 图片或视频用什么模型

## 本机模型库盘点（E:\Comfy-Desktop\ComfyUI-Shared\models，2026-08 状态）

- checkpoints/: animagine-xl-4.0 (6.5G)、NoobAI-XL-v1.1 (6.7G)、Realistic_Vision_V5.1 (4.0G)
- diffusion_models/: z_image_turbo_bf16 (12G = **Z-Image Turbo 6B，不是 FLUX**)、Anima-2.9B-preview、anima-base（**都是图像模型，不是视频**）
- text_encoders/: qwen_3_4b、qwen_3_06b_base；vae/: ae.safetensors、qwen_image_vae
- 空目录: loras/ controlnet/ upscale_models/ embeddings/ clip_vision/ ultralytics/ onnx/
- 已装节点: ComfyUI-AnimateDiff-Evolved、ComfyUI-VideoHelperSuite、impact-pack、Anima-2.9B；**缺 ComfyUI-GGUF、ComfyUI-WanVideoWrapper**

## 快速结论（详细实测数据见 references/8gb-video-models-2026.md）

| 方案 | 8GB 可行性 | 一句话 |
|------|-----------|--------|
| AnimateDiff + NoobAI/animagine | ✅ 已装节点只缺 motion module | 动漫微动（呼吸/颤动/眨眼），无审查 |
| AnimateDiff + Realistic_Vision | ✅ 同上（SD1.5 版）| 真人微动 |
| Wan 2.2 TI2V-5B GGUF Q4 | ✅ 社区实测（3060Ti 8GB 跑 14B 峰值 <7GB）| 高质量自然运动，需 GGUF+WanVideoWrapper 节点、TE 必须 fp8 |
| SVD-XT | ✅ ComfyUI 原生支持 | 官方图生视频 25 帧，真人写实强 |
| LTX-Video 2B | ✅ 轻快 | 社区 NSFW 版 CarolVorders **作者自评不可用，跳过** |
| HunyuanVideo 1.5 / Wan 14B / Mochi | ❌ 不推荐 | 除非双段 GGUF 切换方案 |

## 真人 NSFW 图片模型

- **首选 CyberRealisticPony**（SDXL Pony 系，rating:explicit 控制，无审查）
- 本机已有 Realistic_Vision_V5.1 可直接用；Juggernaut-XL v9、majicMIX/chilloutmix（亚洲真人）

## 模型来源溯源法

1. `stat -c "%n | 创建:%w | 修改:%y" 模型文件` 看**创建时间**
2. 多个配套文件创建时间同一秒 + 与 ComfyUI-Cache/download-cache 环境包目录时间一致
   → 是 **ComfyUI Desktop 首次安装时自带下载器**拉取的，不是 Hermes 经手
3. 佐证：会话历史搜不到下载记录 + 早期盘点误判模型家族

## 查证技巧

- huggingface.co 国内直连失败 → 用 **hf-mirror.com**：`curl -s "https://hf-mirror.com/api/models?search=XXX&sort=downloads&direction=-1&limit=N"`
- HF API siblings 无 size → `curl -sIL <resolve/main/文件>` 抓最后一个 content-length
- 读模型卡 README 验证能力/限制（如 animagine 官方列 nsfw/explicit 标签）
- GitHub 搜实测案例：mcp__github__search_repositories + get_file_contents 读 README

## Pitfalls

- z_image_turbo 曾长期被误判为「FLUX 系」——先读模型卡 tags/README 再下结论
- Anima-2.9B 是图像模型（动漫插画微调），不是视频模型
- LTX 帧数须 8+1 整除，分辨率 <720×1280 最佳
- Wan 5B 配套 TE 必须用 fp8（umt5_xxl_fp8_e4m3fn_scaled），bf16 会爆 8GB
- 8GB 视频推荐管线：低分辨率生成 → 外部放大（Topaz），不要本机硬上 720p
