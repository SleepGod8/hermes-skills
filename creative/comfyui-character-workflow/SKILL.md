---
name: comfyui-character-workflow
description: "ComfyUI 角色图生成与手部精修：本机环境坑、detailer、CUDA torch 修复。"
version: 1.0.0
author: agent
tags: [comfyui, image-generation, animagine, detailer, windows, character]
platforms: [windows]
---

# ComfyUI 本地角色图工作流（Windows Desktop）

在本机 ComfyUI Desktop 上为动漫角色（女仆家族等）生成/精修形象。与 hub 的 `comfyui` 技能互补——本技能记录**本机环境特有的坑与已验证配方**。

## 触发条件

- 用户要求用 ComfyUI 生成/优化某个角色的图
- 需要手部精修（FaceDetailer + hand_yolov8s）
- 遇到 ComfyUI Desktop 环境问题（torch、自定义节点、输出路径）

## 本机环境速查

| 项 | 路径/值 |
|---|---|
| 后端 | `E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\` |
| **运行环境** | **`.venv`**（`ComfyUI\.venv\Scripts\python.exe`，torch 2.10.0+cu130 CUDA ✅）|
| 备用环境 | `standalone-env\python.exe`（**不是 ComfyUI 实际用的**，别往这里装东西）|
| 共享模型 | `E:\Comfy-Desktop\ComfyUI-Shared\models\`（checkpoints 等）|
| Impact/SAM 模型 | `ComfyUI\ComfyUI\models\sams\`、`...\models\ultralytics\bbox\`、`...\models\onnx\`（注意在**后端目录内**，不在共享目录）|
| 输出 | `E:\Comfy-Desktop\ComfyUI-Shared\output\` |
| 工作流 | `E:\ai1\comfyui_workflow\`（API 格式 JSON）|
| 检查点 | `animagine-xl-4.0.safetensors`（角色图主力）|
| API | `http://127.0.0.1:8188` |

## ⚠️ 最大陷阱：`.venv` 才是运行环境，不是 standalone-env

ComfyUI Desktop 装了两个 Python。**装自定义节点依赖必须用 `.venv`**：
- `pip install ultralytics` 到 standalone-env 会把它的 torch 覆盖成 CPU 版（2.13.0+cpu），污染备用环境（不影响运行但留垃圾）
- 判断真实环境：查进程命令行 `wmic process where "name='python.exe'" get CommandLine | grep main.py` → 看用的是哪个 python.exe
- 装 ultralytics 到 `.venv` 用 `--no-deps`，再单独补轻量依赖，避免 pip 动 torch：
  ```bash
  VENV="E:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/Scripts/python.exe"
  PYTHONPATH="" "$VENV" -m pip install ultralytics --no-deps
  PYTHONPATH="" "$VENV" -m pip install matplotlib opencv-python-headless dill
  ```
- standalone-env 被污染后**无需恢复**（ComfyUI 不用它）；验证 .venv torch 仍 CUDA：
  `PYTHONPATH="" "$VENV" -c "import torch; print(torch.__version__, torch.cuda.is_available())"`

## 手部精修（FaceDetailer）搭建流程

`FaceDetailer` 的 `bbox_detector` 是 **required**，检测器来自 **ComfyUI-Impact-Subpack**（不是 Impact Pack 本体）：

1. 克隆到 custom_nodes：
   ```bash
   cd "E:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/custom_nodes"
   git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git
   ```
2. `.venv` 装 ultralytics（见上，--no-deps）
3. 下载手部模型（hf-mirror，22MB）：
   ```bash
   mkdir -p "ComfyUI/models/ultralytics/bbox"
   curl -L -o hand_yolov8s.pt "https://hf-mirror.com/Bingsu/adetailer/resolve/main/hand_yolov8s.pt"
   ```
4. SAM 模型 `sam_vit_b_01ec64.pth` 放 `models/sams/`（Impact Pack install.py 会自动下载，已有）
5. **必须重启 ComfyUI** 才注册 Subpack 节点：杀 main.py 进程（PID 见 netstat :8188）让 Comfy Desktop 自动拉起；验证 `curl http://127.0.0.1:8188/object_info/UltralyticsDetectorProvider` 非空
6. 节点链：`CheckpointLoader → KSampler → VAEDecode → UltralyticsDetectorProvider(bbox/hand_yolov8s.pt) → FaceDetailer(denoise 0.4, guide_size 768, max_size 1152, 手部正负提示词) + SAMLoader → SaveImage`

可复用模板：`templates/detailer_txt2img_api.json`（完整可跑）。

## CUDA torch 被覆盖成 CPU 的修复

若 pip 把 torch 重装成 `+cpu` 版：
- 驱动 CUDA 版本：`nvidia-smi`（本机 13.1）；Python 版本决定 cp 标记（.venv 是 cp313）
- 阿里镜像 wheel **直链安装**（`--index-url` 方式会报 "from versions: none"，镜像不支持 PEP 503 列表）：
  ```bash
  "$VENV" -m pip install --no-cache-dir \
    "https://mirrors.aliyun.com/pytorch-wheels/cu130/torch-2.13.0%2Bcu130-cp313-cp313-win_amd64.whl" \
    "https://mirrors.aliyun.com/pytorch-wheels/cu130/torchvision-0.28.0%2Bcu130-cp313-cp313-win_amd64.whl"
  ```
- 大文件下载易断连（阿里对 >1GB 限速重置）：用 curl `-C -` 断点续传，后台 background=true；先查 wheel 列表：`curl -s <mirror>/cu130/ | grep -o 'torch-2\.13[^"]*cp313[^"]*win_amd64\.whl'`

## 角色形象提示词配方（animagine-xl-4.0）

基础参数：896×1152（竖版）、euler_ancestral、cfg 7、steps 25-32、`((artist:melon22)), artist:ikarin`、`masterpiece, best quality, very aesthetic, amazing quality, year 2024` 结尾。

| 角色 | 区分特征（正面）| 负向要点 |
|---|---|---|
| Hermes | white hair, short hair, huge breasts, narrowed eyes | nsfw/sexy/lewd + 坏手全套 |
| Athena | **silver hair, long hair, straight hair**, narrowed eyes, calm, serene, mature, elegant | 加 petite, skinny, thin, flat chest |
| 通用手部 | good hands, perfect hands, detailed hands, 5 fingers | fused fingers, extra fingers, mutated hands 等全套 |

Detailer 二次精修提示词：positive `good hands, perfect hands, detailed hands, realistic hands, 5 fingers, elegant hands, slender fingers`；negative 坏手全套。

## 输出路径坑

`run_workflow.py --output-dir /e/ai1/...`（MSYS 风格路径）会**拼接错误**（报告 `E:\e\ai1\...` 不存在）。实际文件在服务器配置的输出目录 `E:\Comfy-Desktop\ComfyUI-Shared\output\`。交付时用真实路径，别信脚本回显的相对拼接路径。

## 验证清单

- [ ] `curl http://127.0.0.1:8188/system_stats` 通
- [ ] `.venv` torch CUDA 可用
- [ ] `UltralyticsDetectorProvider` object_info 非空（Subpack 已加载）
- [ ] 输出图在 ComfyUI-Shared/output/，交付前用真实路径
