# Wan 2.2 TI2V-5B 8GB 实战全流程（2026-08 实测）

RTX 4060 Laptop 8GB 跑通 Wan 2.2 TI2V-5B 图生视频的完整记录：节点安装、
模型文件、8GB 显存配方、API 工作流 JSON、踩坑与排障。

## 1. 节点安装（git clone 到 custom_nodes/）

```bash
cd "E:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/custom_nodes"
git clone --depth 1 https://github.com/city96/ComfyUI-GGUF.git
git clone --depth 1 https://github.com/kijai/ComfyUI-WanVideoWrapper.git
```

依赖装进 **`.venv`**（真实后端环境），不是 standalone-env：

```bash
PY="E:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/Scripts/python.exe"
"$PY" -m pip install ftfy accelerate einops "diffusers>=0.33.0" "peft>=0.17.0" \
  sentencepiece protobuf pyloudnorm "gguf>=0.17.1" scipy
```

⚠️ protobuf 7.x 顶层 `import protobuf` 会失败，但 `import google.protobuf` 正常
（新版改名），不影响运行。

启动后端（注意正斜杠路径、PYTHONPATH=""）：

```bash
cd "E:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI"
PYTHONPATH="" ./.venv/Scripts/python.exe -s main.py \
  --feature-flag show_signin_button=true \
  --extra-model-paths-config "C:/Users/80704/AppData/Roaming/Comfy Desktop/shared_model_paths.yaml" \
  --input-directory "E:/Comfy-Desktop/ComfyUI-Shared/input" \
  --output-directory "E:/Comfy-Desktop/ComfyUI-Shared/output"
```

## 2. 模型文件（hf-mirror，大小实测）

| 文件 | 大小 | 放置目录 | 来源 repo |
|------|------|---------|-----------|
| `Wan2.2-TI2V-5B-Q4_K_M.gguf` | 3.2G | `models/unet/` | QuantStack/Wan2.2-TI2V-5B-GGUF |
| `umt5_xxl_fp16.safetensors` | 10.6G | `models/text_encoders/` | Comfy-Org/Wan_2.2_ComfyUI_Repackaged |
| `wan2.2_vae.safetensors` | 1.4G | `models/vae/` | Comfy-Org/Wan_2.2_ComfyUI_Repackaged |
| open-clip vit-h fp16（备用，实际用不到）| 1.2G | `models/clip_vision/` | Kijai/WanVideo_comfy |

下载 URL 模式：`https://hf-mirror.com/<org>/<repo>/resolve/main/<path>`。

⚠️ **TI2V-5B 必须配 `wan2.2_vae.safetensors`**（in_channels=12 高压缩版，
模型卡 vae/config.json 可验证），不是 `wan_2.1_vae`（那是 Wan2.1 的 4x8x8 VAE）。

⚠️ **`LoadWanVideoT5TextEncoder` 不支持 fp8_scaled 文件**：
`umt5_xxl_fp8_e4m3fn_scaled.safetensors`（6.3G）提交时报
`ValueError: fp8 scaled is not supported by this node`。必须用
fp16/bf16 权重 + 节点 `quantization=fp8_e4m3fn` 自己量化。白下 6.3G 的教训。

## 3. 8GB 显存配方

- `WanVideoBlockSwap`：blocks_to_swap=20（5B 共 30 个 transformer blocks）
- `WanVideoEncode`/`WanVideoDecode`：enable_vae_tiling=true，tile 272 / stride 144
- 分辨率：704x480，81 帧（Wan2.2 VAE 时间步长 4，帧数需 4n+1）
- `WanVideoSampler`：20 steps, cfg 5, shift 8, scheduler flowmatch_pusa
- `LoadWanVideoT5TextEncoder`：model=umt5_xxl_fp16.safetensors, precision=bf16,
  load_device=offload_device, quantization=fp8_e4m3fn
- `WanVideoModelLoader`：model=Wan2.2-TI2V-5B-Q4_K_M.gguf, quantization=disabled
  （GGUF 时 quantization 必须 disabled，节点自动识别 .gguf）

## 4. 工作流参数名对照（示例工作流 vs 实际 object_info）

example_workflows/wanvideo_2_2_5B_I2V_example_WIP.json 里的参数名和实际
节点定义不一致，构建 API 工作流前先 `GET /object_info` 核对：

| 节点 | 示例/直觉参数 | 实际参数（object_info） |
|------|-------------|----------------------|
| WanVideoVAELoader | model | **model_name** |
| WanVideoEmptyEmbeds | length | **num_frames** |
| WanVideoTextEncode | positive / negative | **positive_prompt / negative_prompt** |
| WanVideoEasyCache | coefficient / steps_to_cache / device | **easycache_thresh / start_step / end_step / cache_device** |
| WanVideoSLG | layers / gamma / beta | **blocks / start_percent / end_percent** |
| ImageResizeKJv2 | —（节点不存在）| 用内置 **ImageScale**（image/upscale_method/width/height/crop）|

## 5. API 工作流 JSON（/prompt 端点直接提交）

```json
{
  "11": {"class_type": "LoadWanVideoT5TextEncoder", "inputs": {
    "model_name": "umt5_xxl_fp16.safetensors", "precision": "bf16",
    "load_device": "offload_device", "quantization": "fp8_e4m3fn"}},
  "200": {"class_type": "WanVideoBlockSwap", "inputs": {
    "blocks_to_swap": 20, "offload_img_emb": false, "offload_txt_emb": false}},
  "22": {"class_type": "WanVideoModelLoader", "inputs": {
    "model": "Wan2.2-TI2V-5B-Q4_K_M.gguf", "base_precision": "fp16_fast",
    "quantization": "disabled", "load_device": "offload_device",
    "attention_mode": "sdpa", "block_swap_args": ["200", 0]}},
  "38": {"class_type": "WanVideoVAELoader", "inputs": {
    "model_name": "wan2.2_vae.safetensors", "precision": "bf16"}},
  "16": {"class_type": "WanVideoTextEncode", "inputs": {
    "positive_prompt": "a woman in a white maid outfit stands in a sunlit room, slowly turning to look at the camera",
    "negative_prompt": "Bright tones, overexposed, static, blurred details, subtitles, worst quality, low quality",
    "t5": ["11", 0], "model_to_offload": ["22", 0],
    "force_offload": true, "device": "gpu"}},
  "58": {"class_type": "LoadImage", "inputs": {"image": "human.png"}},
  "71": {"class_type": "ImageScale", "inputs": {
    "image": ["58", 0], "upscale_method": "lanczos", "width": 704, "height": 480, "crop": "center"}},
  "70": {"class_type": "WanVideoEncode", "inputs": {
    "vae": ["38", 0], "image": ["71", 0], "enable_vae_tiling": true,
    "tile_x": 272, "tile_y": 272, "tile_stride_x": 144, "tile_stride_y": 128}},
  "78": {"class_type": "WanVideoEmptyEmbeds", "inputs": {
    "extra_latents": ["70", 0], "width": 704, "height": 480, "num_frames": 81}},
  "94": {"class_type": "WanVideoEasyCache", "inputs": {
    "easycache_thresh": 0.015, "start_step": 10, "end_step": -1, "cache_device": "offload_device"}},
  "91": {"class_type": "WanVideoSLG", "inputs": {
    "blocks": "7,8,9", "start_percent": 0.1, "end_percent": 0.7}},
  "27": {"class_type": "WanVideoSampler", "inputs": {
    "model": ["22", 0], "image_embeds": ["78", 0], "steps": 20, "cfg": 5.0,
    "shift": 8.0, "seed": 47, "force_offload": true, "scheduler": "flowmatch_pusa",
    "riflex_freq_index": 0, "text_embeds": ["16", 0],
    "cache_args": ["94", 0], "slg_args": ["91", 0]}},
  "28": {"class_type": "WanVideoDecode", "inputs": {
    "vae": ["38", 0], "samples": ["27", 0], "enable_vae_tiling": true,
    "tile_x": 272, "tile_y": 272, "tile_stride_x": 144, "tile_stride_y": 128}},
  "92": {"class_type": "VHS_VideoCombine", "inputs": {
    "images": ["28", 0], "frame_rate": 24, "loop_count": 0,
    "filename_prefix": "wan22_5b_i2v", "format": "video/h264-mp4",
    "pingpong": false, "save_output": true}}
}
```

## 6. 排障

- **提交 400 custom_validation_failed**：LoadImage 图片不在 input/ 目录。
  把测试图复制到 `E:/Comfy-Desktop/ComfyUI-Shared/input/`。
- **执行 error**：`GET /history` 里 execution_error 的 exception_message
  定位；`GET /object_info/<节点>` 核对参数名。
- **OOM**：降低分辨率（704x480→624x352）、减少帧数（81→49）、
  blocks_to_swap 调大（20→25）、去掉 EasyCache/SLG 后再试。
- **WanVideoWrapper 报 `fp8 scaled is not supported`**：换 fp16 权重 + 节点量化。
- **模型下载 error 18 后文件不完整**：`ls -l` 核对大小；重拉 `-C -` 续传。
