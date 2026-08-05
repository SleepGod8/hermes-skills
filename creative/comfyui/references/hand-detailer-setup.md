# ComfyUI 手部精修：Subpack + Ultralytics 检测器 + FaceDetailer 搭建

实战验证（2026-08）：为 animagine-xl-4.0 女仆角色工作流搭建手部精修链路，
消除畸形手。含完整安装、模型下载（国内网络）、工作流 JSON 配置。

## 架构

```
KSampler → VAEDecode → FaceDetailer → SaveImage
                          ├─ bbox_detector = UltralyticsDetectorProvider(hand_yolov8s.pt)
                          ├─ sam_model_opt = SAMLoader(sam_vit_b_01ec64.pth)
                          └─ positive/negative = 手部特化提示词
```

FaceDetailer 用 YOLO 检测手部区域 → SAM 生成遮罩 → 局部重绘修复。

## 前置检查（先做！）

```bash
# 节点是否已注册（Impact Pack 是否装了）
curl -s http://127.0.0.1:8188/object_info/UltralyticsDetectorProvider
curl -s http://127.0.0.1:8188/object_info/FaceDetailer
curl -s http://127.0.0.1:8188/object_info/SAMLoader
# {} = 未注册；有内容 = 已注册
```

- `FaceDetailer`/`SAMLoader` 来自 **comfyui-impact-pack**（custom_nodes 目录）
- `UltralyticsDetectorProvider` 来自 **ComfyUI-Impact-Subpack**（独立仓库！）
- 注意：Impact Pack 本体**不含** UltralyticsDetectorProvider

## 安装步骤

### 1. 克隆 Subpack（到 custom_nodes）

```bash
cd <ComfyUI>/custom_nodes
git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git
```

### 2. 装 ultralytics 到**正确的 Python 环境**

⚠️ 关键：先确认 ComfyUI 用哪个 python！
`wmic process where "name='python.exe'" get ProcessId,CommandLine | grep main.py`
→ Comfy Desktop 实际用 `<安装目录>/ComfyUI/.venv`，**不是** standalone-env！

```bash
VENV="<安装目录>/ComfyUI/.venv/Scripts/python.exe"
# --no-deps 防止 pip 顺带重装 torch（会把 CUDA 版覆盖成 CPU 版！）
PYTHONPATH="" "$VENV" -m pip install ultralytics --no-deps
PYTHONPATH="" "$VENV" -m pip install matplotlib opencv-python-headless dill
```

⚠️ **血泪教训**：直接 `pip install ultralytics`（不带 --no-deps）会装
torch/torchvision 到 standalone-env 并把 torch 覆盖成 `2.13.0+cpu`。
即使 ComfyUI 主环境 .venv 不受影响，也会污染备用环境。

### 3. 下载检测器模型

```bash
mkdir -p "<安装目录>/ComfyUI/models/ultralytics/bbox"
cd "<安装目录>/ComfyUI/models/ultralytics/bbox"
# 国内用 hf-mirror（22.5MB）
curl -L -o hand_yolov8s.pt "https://hf-mirror.com/Bingsu/adetailer/resolve/main/hand_yolov8s.pt"
```

其他可用模型（Bingsu/adetailer 仓库）：face_yolov8s.pt、hand_yolov8n.pt、
person_yolov8s-seg.pt 等。路径规范：bbox 模型放 `models/ultralytics/bbox/`。

### 4. SAM 模型（一般已随 Impact Pack 自动下载）

```bash
ls "<安装目录>/ComfyUI/models/sams/sam_vit_b_01ec64.pth"
# 缺失时手动下载（375MB，Impact Pack install.py 也会自动拉）
```

### 5. 重启 ComfyUI 加载新节点

Subpack 和 ultralytics 都要重启才生效。重启后验证：
```bash
curl -s http://127.0.0.1:8188/object_info/UltralyticsDetectorProvider | grep -o "hand_yolov8s"
```

## 工作流 JSON（API 格式关键节点）

### UltralyticsDetectorProvider（节点 10）

```json
{
  "class_type": "UltralyticsDetectorProvider",
  "inputs": { "model_name": "bbox/hand_yolov8s.pt" }
}
```

### SAMLoader（节点 14）—— 新版需要 device_mode！

```json
{
  "class_type": "SAMLoader",
  "inputs": {
    "model_name": "sam_vit_b_01ec64.pth",
    "device_mode": "AUTO"
  }
}
```

### FaceDetailer（节点 11）—— 新版必填字段很多！

```json
{
  "class_type": "FaceDetailer",
  "inputs": {
    "image": ["6", 0],
    "model": ["1", 0],
    "clip": ["1", 1],
    "vae": ["1", 2],
    "bbox_detector": ["10", 0],
    "sam_model_opt": ["14", 0],
    "guide_size": 768,
    "guide_size_for": true,
    "max_size": 1152,
    "seed": 0,
    "steps": 24,
    "cfg": 6,
    "sampler_name": "dpmpp_2m",
    "scheduler": "karras",
    "denoise": 0.4,
    "feather": 5,
    "noise_mask": true,
    "force_inpaint": true,
    "bbox_threshold": 0.5,
    "bbox_dilation": 10,
    "bbox_crop_factor": 3.0,
    "sam_detection_hint": "mask-point-bbox",
    "sam_dilation": 0,
    "sam_threshold": 0.93,
    "sam_bbox_expansion": 0,
    "sam_mask_hint_threshold": 0.7,
    "sam_mask_hint_use_negative": "False",
    "drop_size": 10,
    "wildcard": "",
    "cycle": 1,
    "inpaint_model": false,
    "noise_mask_feather": 20,
    "positive": ["12", 0],
    "negative": ["13", 0]
  }
}
```

⚠️ 缺字段会报 `required_input_missing`（实测踩过：
sam_mask_hint_threshold / sam_mask_hint_use_negative / device_mode）。
用 `curl /object_info/FaceDetailer` 拉最新 schema 对照补齐。

### 手部特化提示词

```json
{ "class_type": "CLIPTextEncode", "inputs": {
  "text": "good hands, perfect hands, detailed hands, realistic hands, 5 fingers, elegant hands, slender fingers",
  "clip": ["1", 1] } }
{ "class_type": "CLIPTextEncode", "inputs": {
  "text": "bad hands, missing fingers, extra fingers, fused fingers, too many fingers, poorly drawn hands, mutated hands, malformed hands, disfigured hands",
  "clip": ["1", 1] } }
```

## 主采样提示词加固（配合 Detailer）

正向加：`good hands, perfect hands, detailed hands, 5 fingers` + 明确手部姿态
（`hands clasped` / `hands on thighs`）
负向加：`bad hands, missing fingers, extra fingers, fused fingers, poorly drawn hands, mutated hands, malformed hands, disfigured hands, cropped hands`

## 验证

- [ ] `curl /object_info/UltralyticsDetectorProvider` 返回 model_name 含 hand_yolov8s
- [ ] 跑工作流后日志出现 `Detailer: segment upscale ... crop region`（说明精修执行了）
- [ ] 输出图手部无畸形/缺指

## 已知限制

- 手部修复有概率性——同一 prompt 换 seed 结果不同，多跑几张挑最佳
- FaceDetailer 只对检测框内区域重绘，手势复杂时可能仍有瑕疵
- 检测器模型文件是执行代码的 .pt，只从可信源（Bingsu/adetailer）下载

## 眼部精细精修（不要夸张！）实战配方

用户反馈「瞳孔糊、睫毛太长」后的修正（2026-08 实战）：

**核心教训**：`long eyelashes` / `big eyes` 这类词会导致夸张睫毛；
「要精细不要长」的正确写法：

正向（主提示词 + detailer positive 都要）：
```
detailed eyes, detailed pupils, clear iris, visible pupils,
detailed eyelashes, fine eyelashes, delicate eyelashes,
sharp eyes, focused eyes, sparkling eyes, detailed face
```

负向（主负向 + detailer negative）：
```
blurry eyes, blurred pupils, indistinct pupils, no pupils, unfocused eyes,
blurry eyelashes, simplified eyes, long eyelashes, exaggerated eyelashes,
thick eyelashes, huge eyelashes, fake eyelashes, bad eyes, deformed eyes
```

**关键：瞳孔模糊通常是 FaceDetailer 重绘力度不够**，不是提示词问题：
- denoise 0.35 → 0.45（低于 0.4 等于没精修）
- steps 20 → 28
- guide_size 768 → 896（脸部检测框更高分辨率重绘）

**脸部精修第二道 Detailer**（face_yolov8s.pt，从 Bingsu/adetailer 下载到
models/ultralytics/bbox/）：主采样 → 手部 detailer → 脸部 detailer → 输出。
脸部 detailer 的 bbox_detector 用 `bbox/face_yolov8s.pt`，positive/negative
用上面的眼部精细词。

**手势控制三层引导**（防止模型自由发挥手势）：
1. 主正向加权重：`((arms at sides)), ((hands at sides)), hands hanging down naturally`
2. 主负向：`arms up, hands up, arms raised, hands raised, arms crossed, arms in air, hands on head, magic circle, holding object, holding tray, hands together, hands clasped, hands folded`
3. 手部 detailer 的 positive/negative 也注入同样的手势词（局部重绘跟着走）

