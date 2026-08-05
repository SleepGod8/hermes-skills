---
name: comfyui-character-workflows
description: "Generate anime maid images via local ComfyUI Desktop."
version: 1.0.0
author: agent
tags: [comfyui, image-generation, animagine, anime, character, maid, windows, desktop]
platforms: [windows]
---

# ComfyUI 角色出图工作流（本机）

本机（RTX 4060 Laptop 8GB / ComfyUI Desktop）用 animagine-xl-4.0 生成女仆家族角色图，含手部精修（FaceDetailer）管线与 ComfyUI Desktop 排障。

## 触发条件

- 给女仆角色（Hermes/Iris/Eos/Hebe/Athena/Artemis/Nemesis）出图、优化工作流、修手部
- ComfyUI Desktop「自动更新后自动关闭」「反复重启」「后端不启动」
- 手部精修（FaceDetailer/UltralyticsDetector/SAM）环境搭建或排障

## 关键环境真相（踩过坑才发现的）

1. **ComfyUI 真实后端环境是 `.venv`，不是 standalone-env**
   - 后端：`E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe`
   - `.venv` 里 torch 是 `2.10.0+cu130`（CUDA 正常）。standalone-env 是备用环境，ComfyUI 根本不跑它——往 standalone-env 装东西、改 torch 都不影响 ComfyUI（也别为此浪费时间）。
   - 确认进程用哪个环境：`wmic process where "name='python.exe'" get ProcessId,CommandLine | grep main.py`，看 `\.venv\Scripts\python.exe -s ComfyUI\main.py`。

2. **给 .venv 装 ultralytics 必须 `--no-deps`**
   - `pip install ultralytics` 默认会重装 torch → 把 CUDA 版换成 **CPU 版**（2.13.0+cpu），ComfyUI 变龟速。
   - 正确：`"$VENV" -m pip install ultralytics --no-deps`，再补 `matplotlib opencv-python-headless dill`。
   - 验证：`PYTHONPATH="" "$VENV" -c "import torch; print(torch.cuda.is_available())"` 必须 True。注意 PYTHONPATH 会被 Hermes venv 污染，必须清空。

3. **Comfy Desktop「自动更新后自动关闭」循环的根因与修复**
   - 症状：Desktop 反复启动→关闭，日志停在 `cloud-capacity init`，release-cache 里有新版本。
   - 根因：`%APPDATA%\Comfy Desktop\settings.json` 里 `pendingDownloadedUpdateVersion` 卡住（更新下载了装不上，每次启动都尝试应用→失败→退出）。
   - 修复：删掉该键（用 write_file 重写整个 JSON，patch 可能产生重复键），重启 Desktop 即稳定停在当前版本。**别用 Desktop 里的更新按钮**（国内网络装不上 v1.0.35）。
   - 日志位置：`%APPDATA%\Comfy Desktop\logs\app.log`（UTF-8，时间戳 UTC）。
   - Desktop 本体在 `E:\ComfyUI\Comfy Desktop\Comfy Desktop.exe`，安装清单 `%APPDATA%\Comfy Desktop\installations.json`（含 autoUpdateComfyUI 标志）。

4. **手动启动后端：路径必须正斜杠**
   ```bash
   cd /e/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI && PYTHONPATH="" ./.venv/Scripts/python.exe -s main.py --enable-manager --extra-model-paths-config "C:\Users\80704\AppData\Roaming\Comfy Desktop\shared_model_paths.yaml" --input-directory "E:/Comfy-Desktop/ComfyUI-Shared/input" --output-directory "E:/Comfy-Desktop/ComfyUI-Shared/output"
   ```
   - 反斜杠路径会被拼接成乱目录（如 `Comfy-DesktopComfyUI-Sharedoutput`）——这是本机之前出图「找不到文件」的原因。
   - Desktop GUI 被杀后端进程后不会自动拉起（GUI 还在但日志停在初始化），需要命令行手动拉起或让用户点 GUI。
   - 输出目录：`E:\Comfy-Desktop\ComfyUI-Shared\output`（run_workflow.py 报告的文件路径可能拼接错误，实际按此目录找）。

5. **Subpack 检测器模型位置**
   - 手部检测器：`ComfyUI/models/ultralytics/bbox/hand_yolov8s.pt`（hf-mirror.com/Bingsu/adetailer 下载，22MB）
   - SAM：`ComfyUI/models/sams/sam_vit_b_01ec64.pth`（375MB，Impact Pack install.py 自动下载）
   - 验证节点注册：`curl http://127.0.0.1:8188/object_info/UltralyticsDetectorProvider` → `model_name: [['bbox/hand_yolov8s.pt']]`

## 手部精修工作流（FaceDetailer）

节点链：CheckpointLoaderSimple → CLIPEncode(pos/neg) → EmptyLatent(896×1152) → KSampler → VAEDecode → FaceDetailer → SaveImage。FaceDetailer 额外接 `UltralyticsDetectorProvider(bbox/hand_yolov8s.pt)` + `SAMLoader(sam_vit_b_01ec64.pth, device_mode=AUTO)` + 手部专用正负提示词。

**新版 Impact Pack 必填参数**（缺了报 `required_input_missing`）：
- FaceDetailer: `bbox_threshold, bbox_dilation, bbox_crop_factor, sam_detection_hint, sam_dilation, sam_threshold, sam_bbox_expansion, sam_mask_hint_threshold, sam_mask_hint_use_negative, drop_size`
- SAMLoader: `device_mode: "AUTO"`
- 手部 positive: `good hands, perfect hands, detailed hands, realistic hands, 5 fingers, elegant hands, slender fingers`
- 手部 negative: `bad hands, missing fingers, extra fingers, fused fingers, too many fingers, poorly drawn hands, mutated hands, malformed hands, disfigured hands`

## 出图参数与提示词

- 模型 animagine-xl-4.0.safetensors；896×1152（竖版）；euler_ancestral / normal；CFG 7；steps 30–32；Danbooru 标签格式。
- 质量后缀：`masterpiece, best quality, very aesthetic, amazing quality, year 2024`。
- 身材高大丰腴正向：`tall, voluptuous, curvy, wide hips, thick thighs, big breasts, hourglass figure`；负向：`petite, skinny, thin, flat chest`。
- 角色区分：
  - Hermes：white hair, short hair, narrowed eyes, huge breasts, seductive
  - Athena：silver hair, long hair, narrowed eyes, calm/serene, mature, elegant（沉着大姐姐）
  - 服装通用：maid, apron, frilled headband, long dress, classic maid uniform
- 手部基础提示词（主 KSampler 也加）：`good hands, perfect hands, detailed hands, 5 fingers` + 手部姿势标签（hands clasped / hands in front）。
- 完整流程：详情见 comfyui 技能（bundled）的 animagine-prompts.md 与 windows-tqdm-flush-bug.md；本技能补充本机环境与 Detailer 具体差异。

## 验证清单

- [ ] `.venv` torch CUDA=True（`PYTHONPATH=""`）
- [ ] `UltralyticsDetectorProvider` 在 object_info 中注册且 model_name 含 hand_yolov8s.pt
- [ ] 8188 `/system_stats` 返回 comfyui_version
- [ ] Desktop settings.json 无 `pendingDownloadedUpdateVersion`
- [ ] 出图后到 `E:\Comfy-Desktop\ComfyUI-Shared\output` 找文件（别信脚本报告路径）
