---
name: comfyui-lowvram-video
description: "Use when 8GB显存GPU用ComfyUI跑AI视频(Wan2.2/LTX/AnimateDiff)生成."
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [comfyui, video, wan, ltx, animatediff, gguf, lowvram, rtx4060, vram, 8gb]
    category: creative
---

# ComfyUI 低显存视频生成（8GB VRAM）

在 RTX 4060 Laptop 8GB 这类低显存 GPU 上，通过 ComfyUI 跑开源视频生成模型
（Wan 2.2 TI2V-5B / LTX-Video / AnimateDiff）的完整方法。核心思路：**GGUF 量化
+ block swap（显存↔内存换块）+ VAE tiling + 低分辨率生成后外部放大**。

## When to Use / 使用场景

- 用户要在 8GB 显存上本地生成视频（图生视频/文生视频）
- 用户问哪些视频模型在低显存 GPU 上跑得动
- Wan 2.2 / LTX-Video / AnimateDiff 节点安装、模型下载、工作流报错排查
- 已有图片 → 视频（I2V）保持角色一致性

## 模型选型（8GB 显存实测结论）

| 模型 | 能否跑 | 说明 |
|------|--------|------|
| **Wan 2.2 TI2V-5B GGUF Q4/Q5** | ✅ 推荐 | 720P 原生上限，8GB 跑 480p~832×480，81~121 帧 |
| Wan 2.1 T2V-1.3B | ✅ | 轻量，GGUF 后更省 |
| LTX-Video 2B distilled | ✅ | 轻快，但 NSFW 社区版质量差（作者自认 unusable）|
| AnimateDiff (SD1.5/SDXL) | ✅ | 给静态图加微动（呼吸/颤动/眨眼），不是真视频 |
| SVD-XT | ✅ | 官方图生视频，25 帧短片段，写实强 |
| Wan 2.2 A14B / HunyuanVideo 1.5 | ⚠️ 勉强/不推荐 | 需重度 offload，极慢（14B 有 8GB 双段切换社区方案）|

## 8GB 三件套：GGUF + Block Swap + VAE Tiling

1. **GGUF 量化**：主干模型下 GGUF 档（Wan2.2-5B 各档实测大小见 references/wan2-2-video-8gb.md），
   文本编码器用 fp16 权重 + 节点加载时量化 fp8。
2. **Block Swap**：`WanVideoBlockSwap` 节点把 transformer blocks 换到 CPU 内存。
   Wan 2.2 5B 有 30 个 blocks，81 帧用 20、121 帧用 25，峰值显存 <7.5G。
3. **VAE Tiling**：`WanVideoEncode`/`WanVideoDecode` 开 `enable_vae_tiling=true`
   （tile 272×272，stride 144×128），解码阶段显存从 7.7G 降到 2-4G。

## 核心流程（以 Wan 2.2 TI2V-5B I2V 为例）

1. 装节点：`ComfyUI-GGUF` + `ComfyUI-WanVideoWrapper`（git clone 到 custom_nodes）
2. **依赖必须装进 `<ComfyUI>/ComfyUI/.venv`，不是 standalone-env**（后者会污染成 CPU torch）
3. 下模型（hf-mirror，**必须 `-C -` 断点续传**，hf-mirror 大文件约 11 分钟断连一次）
4. 提交 API 格式工作流到 `/prompt`，轮询 `/queue` + `/history` 看进度
5. 出片后低分辨率 → 外部放大（Topaz Video AI / 超分模型）→ 1080P+

详细安装命令、文件大小表、参数对照、实测显存曲线：见
`references/wan2-2-video-8gb.md`（本会话 2026-08 完整验证）。

## Pitfalls / 坑（按踩坑频率排序）

1. **pip 装错环境**：ComfyUI Desktop 真实后端是 `.venv`（torch 2.10+cu130），
   `standalone-env` 是备用环境。装错后 torch 变 CPU 版、CUDA False。
2. **hf-mirror 大文件断连**：curl error 18「end of response with X bytes missing」，
   约 11 分钟后必断。必须 `curl -L --retry 5 --retry-delay 3 -C - --max-time 5400`。
   断点续传 + 长 max-time，断了重拉即可（多个文件并行下会抢带宽）。
3. **T5 编码器格式**：`LoadWanVideoT5TextEncoder` **不支持 fp8_scaled 权重文件**，
   报 `"fp8 scaled is not supported"`。必须用 fp16 文件 + `quantization=fp8_e4m3fn`。
4. **节点参数名 ≠ 官方示例**：example_workflows 里的 WIP JSON 参数名常与安装版不一致
   （model→model_name、length→num_frames、positive→positive_prompt 等）。
   **改工作流前先 `GET /object_info` 核对真实参数名**。
5. **VAE 选错**：Wan2.2 TI2V-5B 必须配 wan2.2_vae（in_channels=12 高压缩），
   wan_2.1_vae 维度不匹配。查官方 `vae/config.json` 的 in_channels 确认。
6. **ModelScope 下载 0 字节**：`resolve/master/...` 直接 curl 会 HTTP 200 但 0 字节
   （需登录/防护），别浪费时间，hf-mirror 稳定可用。
7. **ComfyUI 后台进程会被回收**：terminal background 起的 main.py 会随会话结束而停，
   重新提交前先 `curl /system_stats` 确认在线。

## Verification / 验证

- [ ] `curl http://127.0.0.1:8188/system_stats` 返回 JSON（后端在线）
- [ ] `GET /object_info/<NodeType>` 能看到目标节点（节点装好）
- [ ] `GET /object_info/<Loader>` 的 model_name 下拉含目标模型（文件放对目录）
- [ ] `/prompt` 提交后 `node_errors: {}`（schema 通过）
- [ ] `/history` 对应 prompt_id 状态 `success`，output 有 mp4/gif 路径
- [ ] 生成中显存峰值 <7.8G（`nvidia-smi` 观察，采样阶段最高）

## 相关工作流文件（本机已验证）

- `E:\Hermes workspace\comfyui_workflow\wan2.2_ti2v_5b_i2v_8gb_api.json`（Wan 2.2 5B I2V，API 格式）
- `E:\Hermes workspace\comfyui_workflow\wan2.2_5b_i2v_nsfw_121f.json`（121 帧升级版）
- `E:\Hermes workspace\comfyui_workflow\pony_nsfw_txt2img.json`（CyberRealisticPony 出图）
