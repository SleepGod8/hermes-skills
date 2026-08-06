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
| API | `http://127.0.0.1:8189` |

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
5. **必须重启 ComfyUI** 才注册 Subpack 节点：杀 main.py 进程（PID 见 netstat :8189）让 Comfy Desktop 自动拉起；验证 `curl http://127.0.0.1:8189/object_info/UltralyticsDetectorProvider` 非空
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

## ⚠️ 手部精修翻车案例与最优参数（athena_maid_detailer）

实测 4 轮迭代（2026-08，animagine-xl 1024×1536）发现的关键坑：

| 坑 | 症状 | 解法 |
|---|---|---|
| 手叠手姿势 `((one hand resting on the other hand))` 高权重 | 主图手部直接画糊，detailer 也救不回来 | 降权为 `hands gently resting in front of waist` |
| denoise 0.7 + `slender fingers/detailed finger joints` | 手被重绘成"机械义体"（金属质感、分段指节、手腕管道） | denoise 用 **0.62**，提示词改 `soft skin, natural skin texture, normal hand proportions`；负向加 `mechanical hands, robotic hands, metallic hands, claw hands, elongated fingers` |
| 指根蹼状粘连（连指） | 手指根部像鸭掌连在一起 | 正向加 `fingers spread apart, visible gaps between fingers, separated finger bases`；负向加 `webbed fingers, finger webbing, connected fingers, fused finger bases` |
| 手部区域小、放大倍数不足 | 细节修不精细 | guide_size 用 **640**（不要 896），max_size 896 |
| 只跑一遍手部 detailer | 漏修 | 三段链：主采样 → 手粗修(denoise 0.62, cycle 3, dilation 20, crop 3.2) → 脸(denoise 0.45) → 手收尾复查(denoise 0.5, cycle 2, dilation 18) |

最优手部 FaceDetailer 参数组合：`denoise 0.62, cycle 3, bbox_threshold 0.3, bbox_dilation 20, bbox_crop_factor 3.2, guide_size 640, max_size 896, sam_threshold 0.8, feather 10`。

**三 pass 交叉检测（成功率 50%→75%）**：单检测器对"画面左侧的手"漏检率高（手小+与围裙对比度低）→ FaceDetailer 跳过不修。双检测器交叉覆盖可显著提升：`手pass1(v9c, denoise 0.65, cycle 3, dilation 25, threshold 0.25) → 手pass2(v8s, denoise 0.6, cycle 2, dilation 20) → 脸(denoise 0.45) → 手pass3(v8s收尾, denoise 0.5, dilation 18)`。

**成功率天花板（重要认知）**：animagine-xl 下"双手交叠身前"姿势天然成功率仅 ~50%（6张3坏），detailer 只能修"接近正确"的手，主图太烂救不回。实测：2个手部pass=50%，3个pass=75%。要上 90% 必须：简化手势（双手垂下两侧）或 ControlNet openpose 或手部 LoRA（civitai 需 API key，国内直连/代理均拿不到）。
批量兜底脚本：`E:\ai1\comfyui_workflow\run_batch.py <workflow.json> <seed1> <seed2>...`（自动改 seed 提交 + 等待 + 裁剪手部区域）。75% 成功率下跑 4 张至少一张合格的概率 99.6%。
验证技巧：手部在整图中只占小区域，先用 PIL 按位置裁剪（如 x0~0.55, y0.35~0.72）放大 3 倍再喂视觉模型，避免整图缩放后看不清细节。构图漂移检测：euler_ancestral 比 dpmpp_2m 构图稳定；Hires fix 会引入构图漂移（手跑到画面边缘+幻视物件），不要盲目加。

## 🎯 构图稳定性与批量手部筛选（v3 实测 2026-08）

**核心现实**：animagine-xl 上"双手交叠身前"姿势单张手部成功率只有 ~50%（6 张 3 张合格），detailer 只能救"接近正确"的手，主图太烂救不回。**别再单张赌运气：批量多 seed + 视觉筛选才是可靠产出**（4-6 张必出 1-2 张完美手）。

### 构图漂移两大元凶（改错白跑 20 分钟）
| 改动 | 症状 | 教训 |
|---|---|---|
| 采样器 euler_ancestral → dpmpp_2m | 手部位置整体漂移（跑到画面右下/握物姿势），旧裁剪框全失效 | 构图稳定性优先用 **euler_ancestral + normal**；换采样器=换构图，先整图定位再裁剪 |
| Hires fix（768→1024 latent denoise 0.35） | 构图漂移 + 幻觉出提示词没有的"金色物件" | SDXL 此姿势下 Hires fix 弊大于利；手部放大靠 detailer 的 guide_size |

### 失败模式：总在"画面左侧手"并指/蹼指
疑似 hand_yolov8s 漏检左侧手（手小+与围裙低对比度）→ FaceDetailer 检测不到直接跳过。缓解：bbox_threshold 0.25、dilation 20-25；三 pass 交叉检测（v9c主力 denoise 0.65 → v8s补漏 0.6 → 脸 0.45 → v8s收尾 0.5）让双检测器互相兜底（v3.3 设计，待验证）。

### API 提交与等待坑
- POST /prompt 用 Python `urllib.request`（git-bash 的 `curl -d @file.json` 报 "No prompt provided"）
- `LatentUpscaleBy` 参数名是 **`upscale_method`**（写 method 会 400 required_input_missing）
- 手改 API JSON 时别丢 KSampler 的 `latent_image` 连接（validation 会报，但少一轮往返）
- 批量等 20+ 分钟：`execute_code` 只有 5 分钟上限，用 `terminal(background=true)` + notify_on_complete 轮询 `/history/{pid}` 的 `status.completed`
- 批量提交 = 每个 seed 深拷贝 workflow 改 seed 字段，一次全提交排队，再统一轮询

### 手部视觉验证
先整图定位手（构图会漂移，旧裁剪框会失效），裁剪后转 **~800px 宽 JPEG**（原图/3x 放大 PNG 触发 400 too-large）；辅助 vision 偶尔 404（glm-4.6v-flash）→ 重试即可。

工具：`scripts/batch_hand_screening.py`（提交→轮询→裁剪一键）；完整迭代参数表见 `references/hand-repair-iterations.md`。

## 输出路径坑

`run_workflow.py --output-dir /e/ai1/...`（MSYS 风格路径）会**拼接错误**（报告 `E:\e\ai1\...` 不存在）。实际文件在服务器配置的输出目录 `E:\Comfy-Desktop\ComfyUI-Shared\output\`。交付时用真实路径，别信脚本回显的相对拼接路径。

## 验证清单

- [ ] `curl http://127.0.0.1:8189/system_stats` 通
- [ ] `.venv` torch CUDA 可用
- [ ] `UltralyticsDetectorProvider` object_info 非空（Subpack 已加载）
- [ ] 输出图在 ComfyUI-Shared/output/，交付前用真实路径
