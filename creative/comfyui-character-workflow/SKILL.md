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

## ⭐ 主人偏好（2026-08 反复确认）：新角色图用纯 txt2img，不要精修链

女仆家族**新画像/新姿势一律用 7 节点纯净 txt2img 模板**（CheckpointLoader→CLIP×2→EmptyLatent→KSampler→VAEDecode→SaveImage；animagine-xl-4.0，1024×1536，steps 45，cfg 6.5，euler_ancestral），**不主动上 detailer 精修链**。首张 seed 42 探路 + qwen-vl-plus 视觉验证，通过即交付；只有手部明显崩了才考虑 hand_fix 局部重绘。参考现成模板：`hebe_new_api.json`、`artemis_badgirl_api.json`（`E:\Hermes workspace\comfyui_workflow\`）。

## 🎯 女仆画像完整流水线（2026-08 实战 7+ 次，照此执行）

给女仆家族跑新画像/新姿势的标准流程（每次角色都走这套，全角色零返工依赖它）：

1. **读档案定形象**：`profiles/<名>/SOUL.md` 有无外貌描述；没有或细节不足 → **clarify 让主人选方案**（发色/服装/气质整体方案 3-4 选 1），主人选完可能追加修改（如「胸部大一点」「要长发」）——先按最终要求出图再写档案。
2. **防重合检查**：对照「已定稿分布」（见角色表下方），发色+发型+服装+气质全维度避开已有姐妹。主人会主动抓撞车（「形象是不是和hebe有些重合？」）。
3. **搭 7 节点纯净 txt2img 工作流** `<名>_api.json` 存 `E:\Hermes workspace\comfyui_workflow\`（animagine-xl-4.0, 1024×1536, steps 45, cfg 6.5, euler_ancestral, seed 42 首张）。
4. **出图 → qwen-vl-plus 验证**（DashScope compatible-mode，key 在 Hermes 根 .env 的 DASHSCOPE_API_KEY；检查发色/表情/道具/服装/手部/气质，返回通过/不通过）。
5. **主人确认 → 才写档案**：SOUL.md 升版（v1.0→v1.1）加「## 外貌形象」段落 + config.yaml system_prompt 镜像同步（yaml 库读改写，patch 工具会被拒）+ 记忆同步；先 `cp config.yaml config.yaml.bak-image-<月日>` 备份。档案写入流程详见 `hermes-profile-personas` skill。
6. **主人确认后批量姿势/立绘**：CHAR_CORE（角色固定描述）+ variants（姿势/表情/背景差异），每姿势 1 seed 探路→全过再补 seed；负向按姿势联动删冲突词（见「姿势变体批 + 负向联动修剪」）。姿势优先选**档案标志行为**（Ares 扛米袋、Aphrodite 端茶点评、Dionysus 端杯），模型还原度高。
7. **归档**：`output/<名>/` 子目录；ComfyUI 后端默认 output/ 是唯一真源（工作副本可能丢，cp 前先 mkdir -p）。

⚠️ **主人对画像的微调指令（高频）**：改一处就重跑一张验证再定稿，别一次改多处；filename_prefix 区分版本（_new/_big/_pose_x/_portrait_x），旧版保留作对比。**抽象属性词（衣冠不整/醉酒/微醺/大胸）在 animagine 响应弱**：正向用具体描述词+高权重 `(xxx:1.3-1.4)`，同时检查负向是否在压制目标特征（要醉→删负向 drunk；要抱臂→删 arms crossed；要大胸→正向 large breasts, big breasts, generous bust）。

| 项 | 路径/值 |
|---|---|
| 后端 | `E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\` |
| **运行环境** | **`.venv`**（`ComfyUI\.venv\Scripts\python.exe`，torch 2.10.0+cu130 CUDA ✅）|
| 备用环境 | `standalone-env\python.exe`（**不是 ComfyUI 实际用的**，别往这里装东西）|
| 共享模型 | `E:\Comfy-Desktop\ComfyUI-Shared\models\`（checkpoints 等）|
| Impact/SAM 模型 | `ComfyUI\ComfyUI\models\sams\`、`...\models\ultralytics\bbox\`、`...\models\onnx\`（注意在**后端目录内**，不在共享目录）|
| 输出 | `E:\Comfy-Desktop\ComfyUI-Shared\output\` |
| 工作流 | `E:\Hermes workspace\comfyui_workflow\`（API 格式 JSON；output/ 下按角色分子目录，如 output/hebe、output/artemis、output/nemesis、output/eos）|
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
| Iris（2026-08-08 主人改淡蓝长发）| **light blue hair, pale blue hair, long hair, straight hair**, gentle smile, warm smile, kind eyes, medium breasts, shy, delicate | 加 huge breasts, massive breasts, exaggerated figure；负向保留裸 smile 实测 OK（正向 gentle smile 权重胜出，成品"表情非常温柔、若有若无浅笑"），不用二选一 |
| Hypnos（2026-08-08 睡神妹）| **messy silver hair, fluffy silver hair, bedhead**, half-closed eyes, drowsy eyes, sleepy expression, yawning, soft smile, loose maid uniform, apron slightly crooked | 加 wide awake, alert, energetic, excited, hyper, running, jumping, dancing（反清醒/反活力）；负向保留 half-closed eyes（正向权重胜出） |
| Hebe（2026-08-11 辣妹四姐）| **golden blonde twin tails, pink hair highlights, high twintails, long twintails**, cheerful smile, bright smile, sparkling eyes, energetic, lively, short maid dress, mini maid dress, shortened maid dress, devil horn hair accessory, heart accessories, platform shoes, fair skin | 加 tan skin, tanned skin, dark skin（防 gyaru 被画成小麦/深肤色，破坏女仆家族白肤统一）、sleepy, drowsy, tired, gloomy, sad, angry, frown（反安静低沉）；负向保留 long eyelashes 系（精细偏好） |
| Artemis（2026-08-11 傲娇不良女仆；2026-08-11 主人改短发定稿）| **short hair, short bob hair, bob cut, dark purple hair, purple hair highlights, purple eyes, violet eyes**, band-aid on cheek, lollipop in mouth, tsundere expression, pouting, slight frown, side glance, slight blush, arms crossed, arms folded, short maid dress, leather jacket draped over shoulders, platform shoes, motorcycle in background | ⚠️ 负向必须删 arms crossed / arms folded（姿势就是抱臂，留会压制）、删 frown（傲娇撇嘴是特征）；加 cheerful, overly happy, huge smile, wide grin（反元气）；保留 tan skin 反制 + long eyelashes 系（精细偏好）；发型是**短发 bob**（不要 long hair，主人定稿） |
| Nemesis（2026-08-11 雌小鬼六姐）| **platinum blonde hair, very light blonde hair, twin tails, twintails, blue eyes, azure eyes, short stature, petite height, small build**, smug expression, teasing smile, arrogant smirk, tongue out, cheeky, condescending, black maid dress, black maid uniform, gothic maid outfit, black frilled headband, platform shoes | ⚠️ 负向**绝不能加 petite**（矮个子是主人钦定特征，加了直接压制）；反幼化用 loli, child, kid, underage（矮≠幼，Nemesis 是成年六姐）；加 happy, cheerful, sunny（反元气甜系——要欠揍挑衅感不是元气） |
| Eos（2026-08-11 黎明女神小妹；2026-08-12 主人补矮个子）| **orange to pink gradient hair, dawn colored hair, sunrise hair, gradient hair, medium length hair, short stature, petite height, small build**, amber eyes, warm orange eyes, sparkling eyes, bright smile, cheerful smile, energetic, white maid dress, white maid uniform, frilled apron, white frilled headband, small sun hair accessory | 反幼化 loli, child, kid, underage + petite, skinny, thin, flat chest（16岁少女体型，防幼化防瘦弱）；加 sad, gloomy, angry, frown, tired, sleepy（反非元气）；long eyelashes 系照旧（精细偏好） |
| Ares（2026-08-12 假小子五姐）| **silver hair, silver-gray hair, short hair, short bob, spiky hair, tan skin, light tan skin, olive skin, athletic body, toned muscles, fit, lean muscular, golden brown eyes**, toothy grin, showing fangs, canine teeth, sports tank top, athletic tank top, black sports top, athletic shorts, shorts, maid apron over sports clothes, frilled maid apron, white frilled apron, maid headband | ⚠️ **绝不加 tan skin/tanned skin/dark skin 反制**（她是全家族唯一要小麦肤的，其他女仆都加反制防小麦，她反过来！）；加 pale skin, white skin（反白肤）、bodybuilder, muscular man, male, masculine（假小子≠男性）；运动系姿势（举哑铃/扛米袋/拳击）时删 holding object, carrying object, holding tray |
| Aphrodite（2026-08-13 魅魔爱神三姐）| **pink hair, light pink hair, rose pink hair, wavy hair, long wavy hair, soft waves, crimson eyes, rose red eyes, perfect figure, hourglass figure, curvy, voluptuous, large breasts, big breasts, generous bust**, alluring, enchanting, aloof, cold beauty, elegant, composed, subtle smile, seductive maid dress, modified maid uniform, high slit skirt, slit dress, black lace maid dress, pink accents, frilled headband | ⚠️ 她是家族唯一「大胸」女仆——首版 medium breasts 主人要求改大（「胸部大一点」→ large breasts, big breasts, generous bust），改完重跑验证再定稿；负向加 nude, topless, bottomless, exposed nipples, see-through clothes, underwear only（魅魔+开衩裙易滑向露骨，画像保持适度性感）；**绝加 angel wings, devil wings, horns, tail, halo**（主人只选粉发+微卷+性感女仆装，不要角/翅膀/尾巴）；frown 要删（高冷是 subtle smile 不是皱眉） |
| Dionysus（2026-08-13 微醺酒神三姐）| **grape purple hair, purple hair, long flowing hair, hair down, very long hair（主人改版：长发披散，不要发髻）, violet eyes, purple eyes, rosy cheeks, tipsy blush, blush on cheeks, tipsy smile, soft sweet smile, dreamy eyes, watery eyes, slightly drunk, large breasts, big breasts（主人要求加大）, classic maid dress, black maid uniform, white apron, white frilled apron, black and white maid dress, white frilled headband** | ⚠️ 首版是松挽发髻（loosely tied up hair, loose bun）+ medium breasts，主人要求改「长发+大胸」→ 正向删 bun/updo 词换 long flowing hair, hair down，胸部换 large breasts, big breasts, generous bust，改完重跑验证再定稿；负向加 drunk, vomiting, hangover, sick, nauseous, dizzy（微醺≠宿醉难受），crying, tears；frown 删（甜笑不皱眉） |
| 通用手部 | good hands, perfect hands, detailed hands, 5 fingers | fused fingers, extra fingers, mutated hands 等全套 |

Iris 设计依据（2026-08-07 定稿，2026-08-08 主人改发色）：彩虹女神意象 → 初稿薰衣草紫长发，**2026-08-08 主人改为淡蓝色长发（light blue hair, pale blue hair）**（与 Hermes 白短发、Athena 银长发区分）；温柔微笑+中等身材（与 Hermes 色气夸张区分）；手势沿用双手垂放（v4.0 优化）。成品 workflow：`E:\Hermes workspace\comfyui_workflow\iris_maid_detailer_api.json`（提示词已同步改为 light blue hair, pale blue hair）。

Hypnos 设计（2026-08-08）：睡神妹，18 岁软萌慵懒。形象：蓬松微乱浅银色长发（messy silver hair, bedhead）、半眯月牙眼（half-closed eyes, drowsy）、软乎乎微笑、宽松睡衣风女仆装、围裙系歪（apron slightly crooked）。纯跑图 workflow：`E:\Hermes workspace\comfyui_workflow\hypnos_new_api.json` + 桌面端 `hypnos_new_ui.json`（7 节点纯净 txt2img，45 步）。负向特色：反「清醒/活力」词族（wide awake, energetic, hyper, running）。实测顶部亮色 69.5%（RGB 234,227,223 银白暖调）✅。

Hebe 设计（2026-08-11）：辣妹四姐，元气小太阳。形象：金发双马尾+粉色挑染（golden blonde twin tails, pink hair highlights，与 Hermes 白短发、Athena 银长发、Iris 淡蓝长发、Hypnos 浅银乱发区分）、元气微笑（cheerful smile, sparkling eyes）、短裙女仆装+粉色爱心图案（short maid dress, heart accessories）、小恶魔发饰（devil horn hair accessory）、厚底鞋（platform shoes）。纯跑图 workflow：`E:\Hermes workspace\comfyui_workflow\hebe_new_api.json`（7 节点纯净 txt2img，45 步，seed 42 首张即 qwen-vl-plus 视觉验证全过：发色/表情/服装爱心/手部 5 指 ✅，1.5MB PNG）。⚠️ **gyaru 类角色负向必须加 `tan skin, tanned skin, dark skin`**——模型默认把辣妹往小麦/深肤色画，与女仆家族白肤设定冲突；负向照旧保留 long eyelashes 系（主人精细偏好：要精细不要夸张）。姿势变体 5 连（比心/捧脸/回眸/挥手/比耶）已存入 `output\hebe\`，全部 qwen 验证通过零废图。

Artemis 设计（2026-08-11 傲娇不良女仆）：五姐傲娇+主人新加的街头不良属性（创可贴/机车/棒棒糖/不良口头禅）。形象：**深紫短发 bob + 紫色渐变挑染（short hair, short bob hair, bob cut, dark purple hair, purple hair highlights）**、紫瞳、傲娇表情（pouting, side glance, slight blush）、脸颊创可贴（band-aid on cheek）、叼粉色棒棒糖（lollipop in mouth）、短裙女仆装+皮夹克披肩（leather jacket draped over shoulders）+厚底靴、机车背景（motorcycle in background）。**2026-08-11 首版是长发，主人要求改短发并同步写入 SOUL.md v1.2「外貌形象」段**——角色形象变更时：工作流 prompt（去掉 long dark hair 换 short hair, short bob hair, bob cut）+ SOUL.md 外貌段 + config.yaml 镜像 + 记忆，四处必须一起改，画像才和档案一致。纯跑图 workflow：`E:\Hermes workspace\comfyui_workflow\artemis_badgirl_api.json`（7 节点纯净 txt2img，45 步）。seed 42 首张即 qwen-vl-plus 验证全过（深紫发+紫挑染/傲娇侧眼+脸红/创可贴/棒棒糖/皮夹克/抱臂手部正常/摩托背景 ✅）。⚠️ **姿势相关负向必须联动修剪**：抱臂姿势→负向删 arms crossed, arms folded；frown 是傲娇特征→负向删；反元气词族加 cheerful, huge smile, wide grin。

Nemesis 设计（2026-08-11 雌小鬼六姐）：嘴毒欠揍的报应女神。形象：**白金双马尾（platinum blonde twin tails，黑蝴蝶结固定）+ 蓝眸 + 矮个子（short stature, petite height, small build）+ 黑色系哥特女仆装（black maid dress, gothic maid outfit）+ 欠揍挑衅表情（smug expression, teasing smile, tongue out）**。纯跑图 workflow：`E:\Hermes workspace\comfyui_workflow\nemesis_api.json`（7 节点纯净 txt2img，45 步）。seed 42 首张即验证全过（白金双马尾/蓝眸/娇小/吐舌挑衅/黑女仆装/比耶手正常 ✅）。

Eos 设计（2026-08-11 黎明女神小妹）：16 岁元气女仆妹妹，排行第八全家最小，希腊神话黎明女神。主人 clarify 选定「朝霞渐变发+白色女仆装+元气笑脸」方案（黎明女神锚点）。形象：**朝霞渐变发（orange to pink gradient hair, dawn colored hair，头顶粉→发梢橙像黎明天空）+ 琥珀星瞳（amber eyes, sparkling eyes）+ 元气笑脸 + 白色女仆装（white maid dress, frilled apron, white frilled headband）+ 小太阳发饰 + 晨光背景**。⚠️ 16 岁 = 少女体型，正向别加 petite（防幼化），负向反幼化用 loli, child, kid, underage + 防瘦弱 petite, skinny, thin, flat chest。纯跑图 workflow：`E:\Hermes workspace\comfyui_workflow\eos_api.json`（7 节点纯净 txt2img，45 步）。seed 42 首张 qwen-vl-plus 验证全过（粉→橙渐变/琥珀星瞳/白女仆装/少女感/手正常 ✅）。⚠️ **2026-08-12 主人补充 Eos 也是矮个子**（与 Nemesis 同为矮个，但气质区分：Nemesis 挑衅雌小鬼 vs Eos 元气妹妹）——正向加 `short stature, petite height, small build`，负向反幼化措辞不变（loli, child, kid, underage；注意 Eos 负向里**要保留 petite, skinny, thin** 防瘦弱幼化，与 Nemesis 不同——Nemesis 负向绝加 petite 会压矮个，Eos 正向已有 short stature 兜底所以负向 petite 反瘦弱不冲突）。

Ares 设计（2026-08-12 假小子体力怪五姐）：战神阿瑞斯，与 Artemis 同龄五姐。主人 clarify 选定「运动背心+短裤+女仆围裙混搭+银灰短发+虎牙笑」方案（档案本身已有形象：银灰短发/小麦肤/肌肉/运动装当女仆装被管家训）。形象：**银灰短发（silver hair, silver-gray hair, short hair, spiky hair）+ 小麦色皮肤（tan skin, light tan skin, olive skin）+ 肌肉线条（toned muscles, athletic body, fit）+ 虎牙笑（toothy grin, showing fangs, canine teeth）+ 黑色紧身运动背心 + 白色蕾丝女仆围裙（模型自己印了 "SILVER 22" 字样，被当专属装备号）+ 深蓝白条纹短裤**。⚠️ **肤色反制是反的（全家族独一份）**：其他女仆负向加 tan skin 防小麦肤，Ares 正向要 tan skin、负向加 pale skin, white skin 防画白。⚠️ 假小子≠男性：负向加 bodybuilder, muscular man, male, masculine 防男性化，正向保留女性特征词。纯跑图 workflow：`E:\\Hermes workspace\\comfyui_workflow\\ares_api.json`（7 节点纯净 txt2img，45 步）。seed 42 首张 qwen-vl-plus 验证全过（银灰短发/小麦肤/肌肉/虎牙/运动装+围裙混搭 SILVER 22/女性感 ✅）。运动系姿势 6 连（举哑铃/拳击/扛米袋/叉腰/胜利/运动场）全过零废图——「扛米袋」是档案梗「搬家具、修水管、抗大米」，姿势设计优先选角色档案里的标志性行为，模型还原度高。

Aphrodite 设计（2026-08-13 冷感魅魔爱神三姐）：主人 clarify 选定「粉发（爱神粉经典）+微卷长发+性感改良女仆装」方案（**明确不要角/翅膀/尾巴**，只要粉发+微卷+性感女仆装）。形象：**粉发微卷长发（pink hair, wavy hair, long wavy hair, soft waves）+ 深红瞳（crimson eyes）+ 完美身材（hourglass figure, curvy, voluptuous）+ 大胸（large breasts——首版 medium 主人要求改大「胸部大一点」后定稿）+ 高冷优雅表情（aloof, cold beauty, elegant, subtle smile）+ 黑色蕾丝改良女仆装（seductive maid dress, high slit skirt 开衩裙, 领口心形蝴蝶结）**。⚠️ **魅魔+开衩裙的露骨风险**：负向必须加 nude, topless, bottomless, exposed nipples, see-through clothes, underwear only 防止滑向露骨（画像层面保持适度性感即可）；且负向加 angel wings, devil wings, horns, tail, halo 明确反掉主人没选的魅魔元素。纯跑图 workflow：`E:\\Hermes workspace\\comfyui_workflow\\aphrodite_api.json`（7 节点纯净 txt2img，45 步）。seed 42 首张验证通过后主人要求调大胸部（medium→large breasts, big breasts, generous bust）→ 重跑 `aphrodite_big` 验证过再定稿。优雅姿势 6 连（端茶/撩发/倚墙/坐姿/叉腰/沙发慵躺）全过零废图——「端茶点评」是档案梗（毒舌艺术家端茶杯点评别人），姿势优先选档案标志行为。

Dionysus 设计（2026-08-13 微醺直球酒神三姐）：酒神狄俄尼索斯，与 Aphrodite 同龄三姐。主人 clarify 选定「葡萄紫长发松挽+酒晕+酒杯+经典黑白女仆装」方案（女仆感为主）。形象：**葡萄紫长发（grape purple hair）+ 紫罗兰瞳 + 脸颊酒晕（rosy cheeks, tipsy blush）+ 微醺甜笑（tipsy smile, dreamy eyes, watery eyes）+ 永远喝不完的酒杯（holding wine glass）+ 经典黑白女仆装（classic maid dress, black maid uniform, white frilled apron）**。首版 seed 42 验证全过（发髻上模型自己加了串葡萄装饰=酒神彩蛋/酒晕/酒杯/黑白女仆装/水汪汪眼 ✅）。⚠️ **2026-08-13 主人要求改「长发+大胸」**：正向删 loosely tied up hair, loose bun, hair bun（发髻词），换 long flowing hair, hair down, very long hair；胸部 medium→large breasts, big breasts, generous bust；重跑 `dionysus_big` 验证（葡萄紫长发到腰/大胸/酒晕/酒杯/黑白装/微醺 ✅）再定稿。负向必加 drunk, vomiting, hangover, sick, nauseous, dizzy（微醺≠宿醉难受）。纯跑图 workflow：`E:\Hermes workspace\comfyui_workflow\dionysus_api.json`（7 节点纯净 txt2img，45 步）。⚠️ **2026-08-13 主人再改「微醺甜笑→醉醺醺痴笑」**：正向换 `(a drunk giggling wine goddess maid girl with grape purple hair:1.3), (drunken silly grin:1.3), goofy drunk expression, blissful drunk laugh, open mouth laughing, half-closed eyes, unfocused glazed eyes, heavily intoxicated, flushed face, giggling`；**负向必须删 drunk**（要的就是 drunk 表情，留了会压制）——首版正向只写了没加权的 tipsy/drunken 词得到「清醒自信微笑」，加 (drunk:1.3)+(drunken silly grin:1.3) 后 3 seed 全出张嘴+眼神迷离痴笑。⚠️ **「衣冠不整」animagine 响应很弱**：抽象 disheveled clothes/messy uniform 几乎不生效（3 张全整洁），要具体描述+高权重（`(disheveled maid dress:1.4), loose unbuttoned collar, collarbone visible, crooked apron, apron slightly untied, wrinkled dress, rumpled skirt, headband tilted`）才得到「围裙+发带轻微不规整」——预期只能轻微程度，别指望大尺度衣衫不整（负向 nsfw 防护在兜底）。

⚠️ **新角色形象防重合检查（2026-08-11 主人亲抓）**：设计新女仆形象前，先查女仆家族已有发色/发型/服装分布，发色+发型+服装+气质全维度避开，再给主人 clarify 确认。本次踩坑：第一版方案「金发双马尾+小恶魔角」与 Hebe（金黄高双马尾+粉挑染+粉色小恶魔发饰）高度重合，主人一眼看出。已定稿分布：Hermes 白短发巨乳、Athena 银长发成熟、Iris 淡蓝长发温柔、Hebe 金黄高双马尾+粉挑染+粉甜系、Hypnos 浅银乱发慵懒、Artemis 深紫短发+皮夹克不良、Nemesis 白金双马尾+黑哥特女仆装+矮个雌小鬼、Eos 粉→橙朝霞渐变中长发+白甜系妹妹、Ares 银灰短发+小麦肤运动系、Aphrodite 粉发微卷+黑蕾丝高冷大胸、Dionysus 葡萄紫长发披散+黑白经典女仆装+酒晕微醺。发色撞车时换色相/明度（金黄→白金），发型撞车时换高低/长短（Nemesis 双马尾 vs Hebe 双马尾靠白金 vs 金黄区分），服装撞车时换色系（粉甜→黑哥特），气质撞车时换表情方向（元气 vs 挑衅 vs 高冷）。

⚠️ **矮个子≠幼女，负向措辞要分清**：主人钦定「矮个子」时正向用 short stature, petite height, small build，负向**绝不能加 petite**（会压制特征），反幼化用 loli, child, kid, underage——Nemesis 是成年六姐，只矮不小。

⚠️ **2026-08-08 按提示词方法论重构了 Iris 主 prompt**（质量词前置、发色整组加权 `((light blue hair, pale blue hair))`、去重、去 highly detailed、显式画师权重）。完整问题诊断+新版模板+落地要点见 `references/animagine-prompt-refactor.md`（该 skill 是 `sd-prompt-methodology` 的实战对照）。

⚠️ **2026-08-08 第二次优化（v11，NAI3 方法论）**：加 `artstyle, year 2024` 前缀、质量词升级 `best quality, amazing quality, very aesthetic, absurdres`、发色长咏唱绑定 `(a gentle maid girl with light blue hair and pale blue hair:1.2)`、负向精简去重 1368→1143 字、KSampler steps 40→35 cfg 7→6.5、FaceDetailer denoise 微调（手 0.55/0.45、整体 0.6）。实测发色 49.9% 淡蓝像素通过。落地细节见 `references/hand-inpaint-and-ui-format.md` §3。

Detailer 二次精修提示词：positive `good hands, perfect hands, detailed hands, realistic hands, 5 fingers, elegant hands, slender fingers`；negative 坏手全套。

⚠️ **2026-08-08 第三次优化（v13，高步数修手）**：主人反馈手部细节仍不行。按《元素同典》结论「修手要 80 步起步」大幅提升精修步数：主采样 35→45、手部精修 26-30→**80/80/100**、guide_size 640→768、手部正负向按法典级手指细节强化（正向加 `clean fingernails, delicate fingers, slender fingers, proper thumb position, natural finger joints, visible knuckles, natural palm, ✋`；负向加 `thumb on wrong side, broken fingers, crooked fingers, twisted fingers, no knuckles, flat hands, mitten hands, blob hands, melted fingers`）。实测整图差异 38%（全图细节提升）。**速度折中实测（重要）**：手部 80/80/100 + cycle 2 → 手部 60/60/70 + cycle 1，两版差异仅 **1.27%**（60 步几乎无损），耗时 6→4.1 分钟。**结论：手部精修 60 步是甜点，80-100 步边际收益极小**（同典「边际效应」验证）。落地细节见 `references/hand-inpaint-and-ui-format.md` §3。

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
6. **⚠️ 双后端同时跑 = access violation 崩溃（2026-08-11 实测）**：上次会话命令行拉起的后端进程没杀，又启动第二个（或 Comfy Desktop 也在跑），两个进程抢 GPU/端口 → 加载 SDXL CLIP 时报 `Windows fatal exception: access violation`，进程 exit 139（SIGSEGV），之后 8188 全部连接拒绝。**启动前必查残留**：`wmic process where "name='python.exe'" get ProcessId,CommandLine | grep -i main.py`（注意过滤 Hermes gateway/bridge/MCP 自己的 python.exe），有残留先杀干净再启。崩后同样先清残留再重启，别盲目重试。症状：日志尾部 `model_patcher.py → sd.py encode_from_tokens → access violation`。

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
批量兜底脚本：`E:\Hermes workspace\comfyui_workflow\run_batch.py <workflow.json> <seed1> <seed2>...`（自动改 seed 提交 + 等待 + 裁剪手部区域）。75% 成功率下跑 4 张至少一张合格的概率 99.6%。
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
- **姿势变体批 + 负向联动修剪（2026-08-11 实测，5 张零废图）**：同一角色多姿势（比心/捧脸/回眸/挥手/比耶）批量跑时，每姿势 = 核心 prompt + 姿势专属正向段（如 `finger heart, one hand making finger heart in front of chest`），且**负向必须按姿势联动删除冲突词**——挥手/比耶→删 `arms up, hands up, arms raised`；回眸→删 `looking back`；抱臂→删 `arms crossed, arms folded`。否则负向会压制目标姿势（模型不画你指定的动作）。每姿势先 1 seed 探路，视觉验证通过后再补 seed。
- **提交与等待拆开**：5 张串行渲染约 10 分钟，`execute_code` 300s 上限必超——脚本只做「全部提交 + 立刻返回」，轮询 /history 单独用短脚本分多次查（或 terminal background + notify_on_complete）。超时后先查 `/queue` + `/history` 确认是否已出图，别直接重跑。

### 手部视觉验证
先整图定位手（构图会漂移，旧裁剪框会失效），裁剪后转 **~800px 宽 JPEG**（原图/3x 放大 PNG 触发 400 too-large）；辅助 vision 偶尔 404（glm-4.6v-flash）→ 重试即可。

**✅ 主力视觉验证 = DashScope qwen-vl-plus**（本机免翻墙、有免费额度，2026-08-11 四轮验证全过）：key 在 Hermes 根 `.env` 的 `DASHSCOPE_API_KEY`；POST `dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`，图片 base64 → `image_url: data:image/png;base64,...`。完整可复用代码（含全角色/姿势批量检查提示词模板）见 `references/qwen-vl-verification.md`。检查点：发色/发型、表情、脸部细节（创可贴/棒棒糖等道具）、服装元素、**手部**（手指数/畸形/抱臂自然度）；姿势图重点查手，通过才交付。

工具：`scripts/batch_hand_screening.py`（提交→轮询→裁剪一键）；完整迭代参数表见 `references/hand-repair-iterations.md`。

## 输出路径坑

- `run_workflow.py --output-dir /e/Hermes workspace/...`（MSYS 风格路径）会**拼接错误**。实际文件在服务器配置的输出目录（命令行后端 → `ComfyUI\ComfyUI\output\`）。
- **命令行启动的后端输出到默认目录** `E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\output\`，**不是**共享目录（extra_model_paths.yaml 只映射模型路径，不映射输出）。history 显示 success 但共享目录找不到图时，先 ls 后端默认 output/。交付时用真实路径，别信脚本回显的相对拼接路径。
- **⚠️ 工作副本 output/ 可能整体丢失，真源永远在后端默认 output/（2026-08-11 实测）**：`E:\Hermes workspace\comfyui_workflow\output\` 只是工作副本，曾整个消失（hebe/、artemis/ 全没了，原因不明，疑似被清理）。恢复方法：从后端默认 output/ 全部 cp 回去重建。**cp 目标目录不存在的坑**：`cp 源.png output/` 当 `output` 目录已不存在时，cp 不会报错而是把源**复制成名为 `output` 的文件**（一个 PNG！），后续所有引用全乱。教训：cp 到目录前先 `mkdir -p 目标/`；交付前 `ls 目标/` 确认是目录；画像文件以 ComfyUI 后端默认 output/ 为唯一真源。

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

转换脚本：`scripts/api_to_ui_v3.py`（**最终修复版**，含 control_after_generate/tiled_* 顺序；`scripts/api_to_ui.py` 是早期 buggy 版，别用）。本机 `E:\Hermes workspace\comfyui_workflow\lewd_maid_workflow.json` 是现成 UI 格式参考。要点：
- 每个 class_type 的输出端口名/连接型输入名要用硬编码映射表（`OUTPUT_DEFS`/`INPUT_DEFS`），API 引用的 `[node_id, slot]` 才能还原成连线
- **⚠️ `widgets_values` 必须是有值数组**：转换后凡是无 widget 的节点会得到 `null`，桌面端加载会异常 → 统一改成 `[]`
- **⚠️⚠️ LiteGraph 槽位约定（2026-08-08 第二次转换踩坑，第一次转换桌面端连接全乱）**：节点 `inputs` 数组里**连接型输入必须排在开头（0..n-1）**，widget 值独立存 `widgets_values`；links 的 `target_slot` 索引的是「连接型输入数组」的位置，**不是节点定义的绝对输入顺序**。按"全部输入绝对顺序"生成会错位（例：KSampler 的 model/positive/negative/latent_image 连接指向 6-9 但 inputs 数组只有 4 个元素 → 桌面端打开连接全断）。正确做法：`CONN_INPUTS` 映射表只列连接型输入名，按该顺序排序连接、slot 从 0 编号；widget 名用单独的 `WIDGET_NAMES` 映射表按序回填。
- **⚠️⚠️⚠️ widget 顺序 = 前端实际生成顺序，不是 API JSON 字段顺序（2026-08-08 第三次转换踩坑，桌面端报 47 个错误）**：LiteGraph 生成节点 widgets 数组时会**在 `seed` 后自动插入 `control_after_generate` combo，FaceDetailer 末尾还会追加 `tiled_encode`/`tiled_decode`**。缺失这 3 个会让 widgets_values 整体错位 → 桌面端报「输入超出范围 / 无效输入 / 输入值类型错误」（cycle 超范围、sampler_name 无效、cfg 类型错是典型症状）。权威顺序获取法：浏览器打开运行中的 ComfyUI，console 执行 `LiteGraph.createNode('FaceDetailer')` 读 `node.widgets[i].name`（这是唯一可靠来源，object_info 的 required/optional 顺序≠前端生成顺序）。已确认：
  - FaceDetailer 真实顺序（29 个）：`guide_size, guide_size_for, max_size, seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise, feather, noise_mask, force_inpaint, bbox_threshold, bbox_dilation, bbox_crop_factor, sam_detection_hint, sam_dilation, sam_threshold, sam_bbox_expansion, sam_mask_hint_threshold, sam_mask_hint_use_negative, drop_size, wildcard, cycle, inpaint_model, noise_mask_feather, tiled_encode, tiled_decode`
  - KSampler（7 个）：`seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise`
  - `control_after_generate` 填 `'randomize'`；tiled_* 填 `False`；API 重建回时跳过这 3 个
  - 验证三重奏：① 浏览器 `LiteGraph.createNode` 模拟赋值检查每个 widget 值落位；② 从 UI 重建 API（跳过 control_after_generate/tiled_*）POST /prompt 后端接受；③ 实际出图成功。前端报错排查用浏览器 console 远比读前端 JS 源码快。
- 验证：把 UI 格式按 INPUT_DEFS 重建回 API 格式提交 `POST /prompt`，成功即桌面端可用（不必真的打开 GUI）；**再加一道「越界检查」**：每个 link 的 `target_slot` 必须 < 目标节点 `inputs` 长度（0 错误才算过），否则桌面端加载必乱。

桌面端使用流程：
1. 复制到 `ComfyUI\user\default\workflows\` 目录 → Workflow→Open 列表可见；或直接把 .json 拖进画布
2. LoadImage 节点选图前，图片先放 `ComfyUI\input\`
3. 桌面端和命令行后端是两套进程，桌面端打开时若端口占用，先停掉命令行拉起的后端

## 模型下载与网络路由（2026-08 实测）

- **大模型下载首选 hf-mirror.com 直连**（`https://hf-mirror.com/<org>/<repo>/resolve/main/<file>`），无需代理。代理（127.0.0.1:12450）可能未监听/掉线——**先 `netstat -ano | grep 12450` 确认端口在监听，再决定走代理还是直连**（`curl -x http://127.0.0.1:12450 -o /dev/null -w "%{http_code}" https://huggingface.co` 快速探测）。
- 下载命令：`curl -L --max-time 5400 -C - -o <file> "<hf-mirror url>"`（`-C -` 断点续传），后台 `terminal(background=true)` + `notify_on_complete=true`；用 `stat -c %s` 轮询文件大小估算速度/ETA（6.8GB 模型 1.5-4MB/s 波动）。
- **⚠️ 探测直链的坑**：`curl -sI`（HEAD）对 HF `resolve/main` 可能返回空；用 `curl -r 0-2047`（range GET）测，HTTP 206 = 可下载。API 能访问（`/api/models?search=`）不代表大文件 CDN 通——分别测。
- 下载校验：safetensors 文件头部应为 `safetensors` 魔数（`head -c 8 | xxd`），下完重启 ComfyUI 刷新模型列表。
- 候选动漫 SDXL 模型（8GB 显存可跑）：`animagine-xl-4.0`（主力，魔法书配方已调优）、`Illustrious-XL-v1.0`（6.6GB，更精细）、`NoobAI-XL-v1.1`（6.8GB，色彩细节强，HF: `Laxhar/noobai-XL-1.1`）。

## 模板库太少 / Browse Templates 空的（2026-08 实测）

`system_stats` 里 `installed_templates_version: null` = 核心模板数据包 `comfyui-workflow-templates` 没装（缩略图媒体包装了也没用，两者独立）。修复：`.venv` 装该包 + 重启 Desktop。⚠️ Desktop 重启时会自动更新后端并重装依赖到它锁定的版本（会覆盖你手动装的版本，属正常）。完整诊断/修复/验证 + 杀启进程正确姿势见 `references/desktop-templates-process-mgmt.md`。

## 验证清单

- [ ] `curl http://127.0.0.1:8188/system_stats` 通（8188 或 8189 任一，netstat 确认）
- [ ] `.venv` torch CUDA 可用
- [ ] `UltralyticsDetectorProvider` object_info 非空（Subpack 已加载）
- [ ] 输出图在 ComfyUI-Shared/output/，交付前用真实路径
