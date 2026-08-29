# 视频模型全景调研（2026-08，hf-mirror 数据）

调研方法：`hf-mirror.com/api/models?search=<关键词>&sort=downloads&direction=-1` 按下载量排序，再拉 README grep 显存关键词。

## Wan 系列（阿里通义，最热）

| Repo | 下载量 | 说明 |
|------|--------|------|
| Comfy-Org/Wan_2.2_ComfyUI_Repackaged | 480万 | Wan 2.2 全家桶（ComfyUI 官方打包） |
| Wan-AI/Wan2.2-TI2V-5B-Diffusers | 19万 | TI2V-5B：5B dense，720P@24fps，官方称"单消费级 GPU 如 4090"（即 24GB）；README 明写 `at least 24GB VRAM` |
| QuantStack/Wan2.2-I2V-A14B-GGUF | 23万 | A14B GGUF 量化（I2V） |
| QuantStack/Wan2.2-T2V-A14B-GGUF | 17万 | A14B GGUF 量化（T2V） |
| Wan-AI/Wan2.1-T2V-1.3B-Diffusers | 21万 | 轻量文生视频，8GB 可行 |
| Comfy-Org/Wan-Animate-2 | 33万 | Wan Animate 2（14B，图生动画） |
| Wan-AI/Wan2.2-Animate-2-14B | - | 原始 14B，需 clip_vision + loras + TE 全套 |

关键 README 句（Wan2.2）：
> "Wan2.2 introduces Mixture-of-Experts (MoE)... A14B series adopts a two-expert design... 27B total but only 14B active"
> "TI2V-5B... 5-second 720P video in under 9 minutes on a single consumer-grade GPU"
> "This command can run on a GPU with at least 24GB VRAM (e.g, RTX 4090 GPU)"

结论：8GB 只能玩 Wan2.1-1.3B 或 Wan2.2-5B GGUF 低分辨率；A14B 系列全部放弃。

## LTX-Video（Lightricks）

- Lightricks/LTX-Video 47万下载
- 版本线：ltxv-2b-0.9.6（低显存）→ ltxv-2b-0.9.8-distilled（蒸馏，更快）→ ltxv-13b-0.9.8-dev（高质量高显存）
- README 原文："ltxv-2b... Smaller model, slight quality reduction compared to 13b distilled. Ideal for light VRAM usage"
- 官方 ComfyUI 节点：Lightricks/ComfyUI-LTXVideo，example_workflows/ 有 i2v/t2v 模板

结论：8GB 首选之一，生成速度秒级起步，真·视频（自然运动）体验最好。

## CogVideoX（智谱 zai-org）

- CogVideoX-2b：2万下载，README 官方显存表：**diffusers FP16 4GB 起 / INT8(torchao) 3.6GB 起**
- CogVideoX-5b / 5b-I2V：各 1.5万/1万，BF16 5GB 起
- CogVideoX1.5-5B：4千
- alibaba-pai/CogVideoX-Fun-2b-InP：2千（文生视频 Fun 版）

结论：CogVideoX-2B 是 8GB 最无压力的官方认证选项（3.6-4GB）。

## HunyuanVideo（腾讯）

- Comfy-Org/HunyuanVideo_1.5_repackaged：45万下载（1.5 版比 1.0 的 9.9万 更热）
- 13B 参数：8GB 能加载但每帧几分钟级，体验差，不推荐

## 其他

- Mochi 1（genmo/mochi-1-preview 3千）：10B，太大
- SVD（Stable Video Diffusion）：老模型，社区多用于配合 AnimateDiff
- Kling/Seedance：闭源 API 或 webui 壳（GitHub 上的 seedance-ai-video 等是壳不是模型），不适用本地 ComfyUI
- AnimateDiff：ByteDance/AnimateDiff-Lightning 1.4万；guoyww/animatediff-motion-adapter-v1-5-2 7千。SD1.5 motion module 是 v1-5 系列，SDXL 是 mm_sdxl_v10_beta

## 本机 2026-08 实际资产

- 已装节点：ComfyUI-AnimateDiff-Evolved、ComfyUI-VideoHelperSuite、ComfyUI-Anima-2.9B、comfyui-impact-pack、ComfyUI-Impact-Subpack
- Anima-2.9B 是图像模型（Gazingstars123/Anima-2.9B，基于 circlestone-labs/Anima，动漫插画 fine-tune），不是视频
- animatediff_models/ 空 → 缺 motion module
- 已装图像模型：animagine-xl-4.0、NoobAI-XL-v1.1、Realistic_Vision_V5.1、Z-Image-Turbo 6B、Anima 2.9B/base
