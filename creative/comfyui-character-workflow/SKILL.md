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
| API | `http://127.0.0.1:8188`（重启后可能在 8188/8189 间变，先 curl system_stats 确认）|

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

## 后端启动与 KSampler 故障排查（2026-08-07 实测）

Comfy Desktop 挂掉时，从 Hermes 会话直接命令行启动后端：

- **必须 `PYTHONPATH=""`**：否则 Hermes 自己的 venv 的 PIL 会 shadow ComfyUI 的，`main.py` 启动报 `ImportError: cannot import name '_imaging'`（PIL 来自 hermes-agent venv）。启动命令：
  ```bash
  cd "/e/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI" && PYTHONPATH="" ./.venv/Scripts/python.exe main.py --port 8188
  ```
- **KSampler 报 `[Errno 22] Invalid argument` 根因（2026-08-07 已确认）= stderr 管道化**：启动命令写成 `main.py ... 2>&1 | head -40` 时，head 读完即关管道，tqdm 进度条写 stderr 时 `sys.stderr.flush()` 抛 OSError Errno 22（execution_error traceback 最后停在 tqdm `std.py status_printer` → `app/logger.py flush`）。正确启动：`PYTHONPATH="" ./.venv/Scripts/python.exe main.py --port 8188 > /tmp/comfyui_backend.log 2>&1`（stderr 落文件就没事）。⚠️ 已实测排除 `--disable-cuda-malloc` 和 `--disable-dynamic-vram`（不是 CUDA/aimdo 问题，别在这两个参数上白绕）；修复后任务正常出图（整体 8.5-9/10），只是三 pass detailer 单张 ~85 分钟偏慢。
- **Comfy Desktop 启动异常**：进程名变成 `Comfy Desktop Setup 1.0.3`（安装器）而非 `Comfy Desktop.exe` 时后端不会起。杀掉用 PowerShell：`Stop-Process -Name 'Comfy Desktop' -Force -ErrorAction SilentlyContinue`（git-bash 的 taskkill //F 双斜杠会转义报错）。
- **API 格式 JSON 别加非节点键**：加 `_iris_meta` 之类元信息键会 400 `Node 'ID #_iris_meta' has no class_type`——元信息放文件名或单独文档，不放 workflow JSON 里。

## 角色形象提示词配方（animagine-xl-4.0）

基础参数：896×1152（竖版）、euler_ancestral、cfg 7、steps 25-32、`((artist:melon22)), artist:ikarin`、`masterpiece, best quality, very aesthetic, amazing quality, year 2024` 结尾。

| 角色 | 区分特征（正面）| 负向要点 |
|---|---|---|
| Hermes | white hair, short hair, huge breasts, narrowed eyes | nsfw/sexy/lewd + 坏手全套 |
| Athena | **silver hair, long hair, straight hair**, narrowed eyes, calm, serene, mature, elegant | 加 petite, skinny, thin, flat chest |
| Iris（2026-08-08 主人改淡蓝长发）| **light blue hair, pale blue hair, long hair, straight hair**, gentle smile, warm smile, kind eyes, medium breasts, shy, delicate | 加 huge breasts, massive breasts, exaggerated figure；负向保留裸 `smile` 实测 OK（正向 gentle smile 权重胜出，成品"表情非常温柔、若有若无浅笑"），不用二选一 |
| 通用手部 | good hands, perfect hands, detailed hands, 5 fingers | fused fingers, extra fingers, mutated hands 等全套 |

Iris 设计依据（2026-08-07 定稿，2026-08-08 主人改发色）：彩虹女神意象 → 初稿薰衣草紫长发，**2026-08-08 主人改为淡蓝色长发（light blue hair, pale blue hair）**（与 Hermes 白短发、Athena 银长发区分）；温柔微笑+中等身材（与 Hermes 色气夸张区分）；手势沿用双手垂放（v4.0 优化）。成品 workflow：`E:\ai1\comfyui_workflow\iris_maid_detailer_api.json`（提示词已同步改为 light blue hair, pale blue hair）。

⚠️ **2026-08-08 按提示词方法论重构了 Iris 主 prompt**（质量词前置、发色整组加权 `((light blue hair, pale blue hair))`、去重、去 highly detailed、显式画师权重）。完整问题诊断+新版模板+落地要点见 `references/animagine-prompt-refactor.md`（该 skill 是 `sd-prompt-methodology` 的实战对照）。

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

**三 pass 交叉检测（成功率 50%→75%）**：单检测器对"画面左侧的手"漏检率高（手小+与围裙对比度低）→ FaceDetailer 检测不到直接跳过。双检测器交叉覆盖可显著提升：`手pass1(v9c, denoise 0.65, cycle 3, dilation 25, threshold 0.25) → 手pass2(v8s, denoise 0.6, cycle 2, dilation 20) → 脸(denoise 0.45) → 手pass3(v8s收尾, denoise 0.5, dilation 18)`。

**⚠️ bbox_threshold 0.25 的代价（2026-08-07 实测）**：threshold 降到 0.25 防漏检，会把围裙花边/袖口蕾丝误检为手——实测检测到 5~11 个 segment，每个 × cycle 重绘 → 单张 85 分钟（20+ 次 30 步采样）。提速方案：threshold 0.35 + cycle 3→2（主力）/ 2→1（补漏收尾），质量几乎不降、速度 85→35 分钟。改完用 `grep -c "Detailer: segment" 后端日志` 看 segment 数验证误检量。

**成功率天花板（重要认知）**：animagine-xl 下"双手交叠身前"姿势天然成功率仅 ~50%（6张3坏），detailer 只能修"接近正确"的手，主图太烂救不回。实测：2个手部pass=50%，3个pass=75%。要上 90% 必须：简化手势（双手垂下两侧）或 ControlNet openpose 或手部 LoRA（civitai 需 API key，国内直连/代理均拿不到）。

**⚠️ 垂放姿势（主人指定方案，2026-08-07 实测）**：主 prompt 改 `arms down, arms relaxed at sides, hands at sides, hands hanging down naturally, arms hanging straight down, hands by hips, fingers relaxed`；**关键陷阱：负向 prompt 里的 `arms at sides, hands at sides, hands hanging down, arms hanging down` 会压制垂放姿势，必须从主负向+手detailer负向全部删除**（用 remove_terms 宽松替换，注意词可能是列表结尾没有尾逗号）。实测 4 seed：3/4 合格（75%），seed 42 达 8/10（比交叠的 7 分更好），失败案例（seed 13579）是手垂到画面底部边缘（y0.87）被 detailer 漏检——可加 `hands near waist level` 或加大 bbox_dilation。注意：模型不会严格垂放，常自由发挥成"一手前伸一手搭腹"，但手部质量已达标（主人接受）。

**端口坑（2026-08-07）**：Comfy Desktop 重启后 API 端口会从 8189 变回默认 **8188**（netstat 确认；MCP 的 COMFY_URL 若之前改成 8189 需同步改回）。提交前先 `curl http://127.0.0.1:8188/system_stats` 确认。批量脚本 run_batch.py 已内置 8188。

## ⚠️ 命令行启动后端的 3 个致命坑（2026-08-07 实测）

1. **`[Errno 22] Invalid argument` 的根因是 stderr 管道**！`python main.py 2>&1 | head -40` 启动时，head 读完即关闭管道 → tqdm 进度条写 stderr 时 flush() 崩溃（traceback 最后一行 `app/logger.py flush → super().flush()`）。**解法：`> /tmp/comfyui_backend.log 2>&1` 重定向到文件**，绝不能 `| head` 截断。排查时被误导：先怀疑 aimdo（--disable-dynamic-vram）、再怀疑 cudaMallocAsync（--disable-cuda-malloc），全不是，看完整 traceback 才定位到 tqdm。
2. **PYTHONPATH 污染**：Hermes 会话里直接 `python main.py` 会 import Hermes venv 的 PIL（报 `cannot import name '_imaging'`）。**必须 `PYTHONPATH="" ./ .venv/Scripts/python.exe main.py`**。
3. **输出目录变化**：命令行启动（无 --output-directory 参数）输出到**默认目录** `ComfyUI\ComfyUI\output\`，不是共享目录 `E:\Comfy-Desktop\ComfyUI-Shared\output\`（那是 Desktop 的配置）。找输出图先查默认目录。
4. Comfy Desktop.exe 可能启动成 "Comfy Desktop Setup" 安装程序（后端不监听）→ 直接命令行启动后端更可控。
5. **git-bash 杀/启 Desktop**：`taskkill //F //IM` 和 `cmd //c` 在 MSYS 都转义坏；可靠杀法 = PowerShell `Stop-Process -Name 'Comfy Desktop' -Force` 或 python subprocess + DEVNULL；可靠拉起 GUI = PowerShell `explorer.exe 'E:\ComfyUI\Comfy Desktop\Comfy Desktop.exe'`（直接 `./exe &` 秒退、`Start-Process` 实测没起来）。详见 `references/desktop-templates-process-mgmt.md` §3。

## ⚠️ Iris 角色图的手部误检陷阱（2026-08-07 实测）

淡蓝色长发飘散 + 白围裙 + 浅背景构图会让 hand_yolov8s/v9c **大量误检**（实测 11 segments vs Athena 的 5），三 pass × cycle 3 导致单张 85 分钟还修不好（误检区域反复重绘）。解法：bbox_threshold 0.25→**0.35**、手部 pass cycle 3→2/1。Iris 角色 prompt 要点：`light blue hair, pale blue hair, long hair, gentle smile, medium breasts, arms down, hands at sides`（与 Hermes 白短发巨乳、Athena 银长发区分）。

### ✅ Iris 手部成功的最终配方（v3 简化构图, 2026-08-07 验证 9/10）

4 张全失败（手被紫发/围裙干扰）后成功的两个关键改动：

1. **主正向头发收束**（让手部区域干净）：在角色 prompt 里加
   `hair flowing behind body, hair swept back behind shoulders, hair not covering hands, hands clearly visible, unobstructed hands`
2. **手部 detailer 正负向加发丝反制**：
   - 正向头部加：`hands not covered by hair, unobstructed hands, clear hands`
   - 负向头部加：`hair over hands, hair covering hands, hair wrapped around hands, hair in front of hands`

3. **侧身构图是聪明解法**：让一只手自然入镜（轻放裙摆/垂放），另一只手不入镜——避开"双手都画"的难题。最终 seed 2024 = 左手 8/10 + 右手未入镜 + 整体 **9/10**（淡蓝长发还原度极高、温柔表情、女仆装 9/10）。加速收益：误检减少后单张从 85 分钟降到 3-16 分钟（seed 42 仅 200s）。
完整 Iris 迭代表见 `references/hand-repair-iterations.md`。
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

- `run_workflow.py --output-dir /e/ai1/...`（MSYS 风格路径）会**拼接错误**（报告 `E:\e\ai1\...` 不存在）。实际文件在服务器配置的输出目录 `E:\Comfy-Desktop\ComfyUI-Shared\output\`。
- **命令行启动的后端输出到默认目录** `E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\output\`，**不是**共享目录（extra_model_paths.yaml 只映射模型路径，不映射输出）。history 显示 success 但共享目录找不到图时，先 ls 后端默认 output/。交付时用真实路径，别信脚本回显的相对拼接路径。

## ✅ 已出图只修手部：局部重绘 hand_fix 工作流（2026-08-08 实测）

需求：「整体不错但手部有问题，只修手、其他地方一个像素都不动」。FaceDetailer 全链路重跑会连带改动周边；正确做法是**对已出图做局部 inpaint**。

成品：`E:\ai1\comfyui_workflow\hand_fix_api.json`（模板副本：`templates/hand_fix_api.json`）。

节点链：`LoadImage → VAEEncode → ImpactSimpleDetectorSEGS(hand_yolov8s+SAM) → SegsToCombinedMask → SetLatentNoiseMask → KSampler(denoise 0.5) → VAEDecode → SaveImage`

**核心原理**：`SetLatentNoiseMask` 把 mask 套到 latent 上，KSampler **只在 mask 区域内重绘**，mask 外的 latent 原封不动 → 解码出来整体不变，只有手被重画。

实测验证（iris_maid_detailer_00007 → iris_hand_fix_00001）：差异像素仅 1.44%，全部集中在两处手部（8×8 热力网格：中上部 4-6%、左下 21.9%，其余 0.0-0.5% 属 VAE 编码噪声级，肉眼不可见）。**验证技巧**：numpy 算 `abs(before-after).sum(axis=2)`，打 8×8 网格百分比，确认改动只落在检测到的手区域。

参数速调：`denoise` 0.3=微调手型 / 0.5=重画手 / 0.7=大改；`bbox_threshold` 0.35（检测灵敏度）；`bbox_dilation` 20（mask 外扩融合余地）；换 `seed` 多次跑挑最自然的手。

**⚠️ 三大坑（2026-08-08 实测）**：
1. **VAE 别用 `ae.safetensors`**！共享 vae 目录里的 `ae.safetensors` 是 Flux 的 16 通道 VAE，SDXL（animagine-xl）会报 `expected input to have 4 channels, but got 16 channels`。直接用 CheckpointLoaderSimple 内置 VAE（输出索引 `["3", 2]`），不要 VAELoader 节点。
2. **命令行启动的后端 LoadImage 只认默认 input 目录** `ComfyUI\ComfyUI\input\`，**不是** `ComfyUI-Shared\input\`。文件放错位置提交报 `Invalid image file: xxx.png`——先 `curl /object_info/LoadImage` 看它实际列出了哪些图，再按列表里出现的文件名填。
3. **Impact SEGS 节点名**：本机没有 `BBOXDetectorToSEGS`/`SegsToMask`；用 `ImpactSimpleDetectorSEGS`（bbox_detector + sam_model_opt）+ `SegsToCombinedMask`（输出 MASK 直接进 SetLatentNoiseMask）。`SAMDetectorCombined` 存在但需要 SEGS 输入，不适配直接从图像起的链路。

完整节点可用性清单 + 错误原文 + 差异热力网格验证代码见 `references/hand-fix-inpaint-workflow.md`。

## API 格式 → 桌面端 UI 格式转换（2026-08-08 实测）

`*_api.json`（`{class_type, inputs}`）只能在 Hermes/命令行里跑，**桌面端画布打不开**。桌面端要的是 LiteGraph UI 格式：顶层 `version/state/last_node_id/last_link_id/nodes/links/groups/config/extra`，节点带 `pos/size/order/mode/widgets_values`、输出带 `links` 数组、连线是 `{id, origin_id, origin_slot, target_id, target_slot, type}`。

转换脚本：`scripts/api_to_ui.py`（本机 `E:\ai1\comfyui_workflow\lewd_maid_workflow.json` 是现成 UI 格式参考）。要点：
- 每个 class_type 的输出端口名/连接型输入名要用硬编码映射表（`OUTPUT_DEFS`/`INPUT_DEFS`），API 引用的 `[node_id, slot]` 才能还原成连线
- **⚠️ `widgets_values` 必须是有值数组**：转换后凡是无 widget 的节点会得到 `null`，桌面端加载会异常 → 统一改成 `[]`
- 验证：把 UI 格式按 INPUT_DEFS 重建回 API 格式提交 `POST /prompt`，成功即桌面端可用（不必真的打开 GUI）

桌面端使用流程：
1. 复制到 `ComfyUI\user\default\workflows\` 目录 → Workflow→Open 列表可见；或直接把 .json 拖进画布
2. LoadImage 节点选图前，图片先放 `ComfyUI\input\`
3. 桌面端和命令行后端是两套进程，桌面端打开时若端口占用，先停掉命令行拉起的后端

## 模板库太少 / Browse Templates 空的（2026-08 实测）

`system_stats` 里 `installed_templates_version: null` = 核心模板数据包 `comfyui-workflow-templates` 没装（缩略图媒体包装了也没用，两者独立）。修复：`.venv` 装该包 + 重启 Desktop。⚠️ Desktop 重启时会自动更新后端并重装依赖到它锁定的版本（会覆盖你手动装的版本，属正常）。完整诊断/修复/验证 + 杀启进程正确姿势见 `references/desktop-templates-process-mgmt.md`。

## 验证清单

- [ ] `curl http://127.0.0.1:8188/system_stats` 通（8188 或 8189 任一，netstat 确认）
- [ ] `.venv` torch CUDA 可用
- [ ] `UltralyticsDetectorProvider` object_info 非空（Subpack 已加载）
- [ ] 输出图在 ComfyUI-Shared/output/，交付前用真实路径
