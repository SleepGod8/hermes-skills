# 真人写实视频管线（Realistic_Vision → Wan 2.2 I2V，2026-08 实测）

在 Wan 2.2 I2V 上跑真人写实风格视频的两段式流程，RTX 4060 8GB 实测通过。

## 流程

```
1. Realistic_Vision_V5.1 (SD1.5 checkpoint) 文生图 768x768
   → 输出到 ComfyUI-Shared/output/
2. 复制到 input/（LoadImage 只认 input 目录）：
   cp output/realistic_maid_00001_.png input/realistic_maid.png
3. 改 Wan 2.2 工作流：LoadImage 指向新图 + 换写实 prompt
4. 提交 /prompt，轮询 /queue + /history
```

## 文生图 API 工作流（写实女仆示例）

```json
{
  "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "Realistic_Vision_V5.1.safetensors"}},
  "2": {"class_type": "CLIPTextEncode", "inputs": {
    "text": "professional photo of a beautiful asian maid in a white french maid uniform, standing in a sunlit elegant room, looking at camera, soft smile, realistic skin texture, detailed face, natural lighting, photorealistic, 8k, sharp focus, (best quality:1.2)",
    "clip": ["1", 1]}},
  "3": {"class_type": "CLIPTextEncode", "inputs": {
    "text": "cartoon, anime, illustration, painting, drawing, 3d render, cgi, deformed, bad anatomy, bad hands, extra fingers, blurry, lowres, worst quality, low quality, watermark, text",
    "clip": ["1", 1]}},
  "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 768, "height": 768, "batch_size": 1}},
  "5": {"class_type": "KSampler", "inputs": {
    "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
    "seed": 20260830, "steps": 30, "cfg": 7.0, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
  "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
  "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "realistic_maid"}}
}
```

## 要点

- **I2V 的最大优势是角色一致**：先固定角色出图 → 图生视频，脸不会崩、画风继承输入图。
- 真人写实 prompt 要加 `realistic skin texture, photorealistic, 8k`；负向必加 `cartoon, anime, illustration, painting, 3d render` 防止跑偏。
- Wan 2.2 I2V 输出 704x480 81帧（3.4s @24fps），生成约 6-10 分钟。
- 出图后建议先用 vision_analyze 检查画质（手/脸/风格），满意再进视频管线，避免白跑 10 分钟。
- NSFW 真人向：出图侧换 CyberRealisticPony（Pony 系 explicit 标签）等写实 NSFW 模型；Wan 2.2 侧本身无审查，I2V 直接动。
