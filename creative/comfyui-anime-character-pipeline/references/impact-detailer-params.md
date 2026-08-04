# Impact Pack Detailer 必填参数（本机 ComfyUI 0.27.0 实测）

> 来源：2026-08 实战。旧版 detailer 工作流（gentle_maid_detailer_api.json 等）缺这些字段，
> 提交后报 `required_input_missing`。修法：`curl http://127.0.0.1:8188/object_info/<节点>` 拿全 required。

## UltralyticsDetectorProvider

```json
{
  "class_type": "UltralyticsDetectorProvider",
  "inputs": { "model_name": "bbox/hand_yolov8s.pt" }
}
```
- 由 ComfyUI-Impact-Subpack 提供（custom_nodes/ 需存在，且 `.venv` 装有 ultralytics 包）
- 模型放 `.../ComfyUI/models/ultralytics/bbox/hand_yolov8s.pt`
- 未注册时 `object_info/UltralyticsDetectorProvider` 返回 `{}`

## SAMLoader

```json
{
  "class_type": "SAMLoader",
  "inputs": {
    "model_name": "sam_vit_b_01ec64.pth",
    "device_mode": "AUTO"
  }
}
```
- `device_mode` 必填：`AUTO` / `Prefer GPU` / `CPU`（新版新增，旧工作流没有）
- 模型放 `.../ComfyUI/models/sams/sam_vit_b_01ec64.pth`（375MB）

## FaceDetailer（全部 required，缺一不可）

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

### 本轮踩过的缺失字段（新版才有的必填项）

| 字段 | 缺参报错原文 | 备注 |
|------|-------------|------|
| `sam_mask_hint_threshold` | required_input_missing | FLOAT，默认 0.7 |
| `sam_mask_hint_use_negative` | required_input_missing | 枚举 `False`/`Small`/`Outter` |
| `device_mode`（SAMLoader） | required_input_missing | 枚举 `AUTO`/`Prefer GPU`/`CPU` |

### 手部精修的 detailer 正负提示词（节点 12/13）

- 正向：`good hands, perfect hands, detailed hands, realistic hands, 5 fingers, elegant hands, slender fingers`
- 负向：`bad hands, missing fingers, extra fingers, fused fingers, too many fingers, poorly drawn hands, mutated hands, malformed hands, disfigured hands`

## 手部模型下载源（国内可用）

```bash
# hand_yolov8s.pt (22.5MB) — hf-mirror 直连 OK
curl -L -o hand_yolov8s.pt "https://hf-mirror.com/Bingsu/adetailer/resolve/main/hand_yolov8s.pt"
```
- Bingsu/adetailer 仓库只有 `.pt` 无 `.onnx`
- github releases / api.github.com 本机不稳定（15 字节错误页 / 空响应）
- 如需 onnx 走 ONNXDetectorProvider，得另找模型源（PINTO_model_zoo 等）

## 依赖安装（不破坏 torch）

```bash
VENV="/e/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/Scripts/python.exe"
PYTHONPATH="" "$VENV" -m pip install ultralytics --no-deps
PYTHONPATH="" "$VENV" -m pip install matplotlib opencv-python-headless dill
# 装完必须验证：torch.cuda.is_available() 仍为 True
```
