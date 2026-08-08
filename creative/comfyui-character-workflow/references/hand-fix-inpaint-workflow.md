# 手部局部修复工作流（只修手部、整体不动）— 2026-08 实测

与 FaceDetailer 精修链互补的独立方法：**对已生成的图做局部重绘**，mask 外像素 100% 不变。
Workflow: `E:\ai1\comfyui_workflow\hand_fix_api.json`（API 格式，可直接提交）

## 适用场景
- 整体构图满意，只有手部畸形（手指粘连/多指/麻花），不想重跑整个 txt2img 链
- 需要可量化的「整体不动」保证（不是 detailer 的 crop-重绘-贴回，而是 latent 级 mask）

## 节点链（核心原理）
```
LoadImage → VAEEncode
  → UltralyticsDetectorProvider(bbox/hand_yolov8s.pt)
  → ImpactSimpleDetectorSEGS(bbox_detector, image, bbox_threshold 0.35, bbox_dilation 20,
       sam_model_opt=SAMLoader)   # SAM 抠手部 silhouette
  → SegsToCombinedMask → SetLatentNoiseMask(samples=latent, mask)
  → KSampler(denoise 0.5, 只重绘 mask 内) → VAEDecode → SaveImage
```
关键节点可用性（ComfyUI 0.31 + Impact Pack 实测）：
`SetLatentNoiseMask` ✅ / `SAMDetectorSegmented` ✅ / `ImpactSimpleDetectorSEGS` ✅ / `SegsToCombinedMask` ✅
`BBOXDetectorToSEGS` ❌ 不存在（用 ImpactSimpleDetectorSEGS 直接产出 SEGS）

## 踩坑记录（都实际踩过）

### 1. VAE 通道数：`ae.safetensors` 是 Flux 的 16 通道 VAE！
本机 `models/vae/ae.safetensors`（335MB）是 Flux 用的 16 通道 VAE，SDXL 检查点用它报：
```
RuntimeError: Given groups=1, weight of size [320, 4, 3, 3],
expected input[2, 16, 192, 128] to have 4 channels, but got 16 channels
```
解法：**别用 VAELoader**，直接取 CheckpointLoaderSimple 的自带 VAE（输出索引 2）：
`VAEEncode.vae = ["3", 2]`（CheckpointLoaderSimple 输出: 0=MODEL, 1=CLIP, 2=VAE）

### 2. VAEEncode 引用写错输出索引
第一次写 `"vae": ["5", 2]`（VAELoader 节点 5 只有一个输出）→ `tuple index out of range`。
VAELoader 输出索引是 0，不是 2。

### 3. 命令行启动的后端 input 目录 ≠ 共享目录
`LoadImage` 只认后端默认 `ComfyUI\input\`（命令行 `python main.py` 启动时），
不认 `ComfyUI-Shared\input`。报 `Invalid image file: xxx.png`。解法：把图复制到
`E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\input\` 再提交。

### 4. /validate 端点不接受 POST（405）
`POST /validate` 报 405 Method Not Allowed。工作流校验方式：直接 `POST /prompt`，
400 会返回 `node_errors` 带具体错误（节点 id + message），比离线 JSON 检查靠谱。

## 验证方法（可量化「只修了手」）
用 numpy 对比原图/修复图，生成 8×8 差异热力网格：
```python
diff = np.abs(np.array(im1).astype(int) - np.array(im2).astype(int)).sum(axis=2)
# 每格统计 (diff > 30).mean()*100，期望：差异集中在手部格子，其余 ≈0
```
实测 1024×1536：差异像素仅 1.44%，全部集中在检测到的两处手部（中上部 4-6% + 左下 21.9%），
其余 90%+ 画面 0.0-0.5%（VAE 编码噪声级，肉眼不可见）。

## 参数调节
| 参数 | 值 | 说明 |
|---|---|---|
| denoise | 0.3 微调 / 0.5 重画 / 0.7 大改 | 越大改动越狠 |
| bbox_threshold | 0.35 | 手部检测灵敏度（Iris 场景 0.25 会误检爆炸，见 hand-repair-iterations） |
| bbox_dilation | 20 | mask 外扩，给手周融合留余地 |
| seed | 换值 | 同参数不同修复结果，多跑挑最佳 |

## 局限
- 只能修检测器找得到的手；手垂到画面边缘/被遮挡 → 漏检跳过
- 大色块/发丝覆盖手部 → SAM mask 不准，修复无效（构图层解决比参数层更根本）
- 与「高步数修手」（主采样 80+ 步）互补，但局部修复不用重跑整图，性价比更高
