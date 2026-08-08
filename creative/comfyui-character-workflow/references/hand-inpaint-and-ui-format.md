# 手部局部重绘（只修手、整体不动）+ API→UI 格式转换

2026-08 实测，适用于 Iris 等角色图「整体不错但手部有问题」的场景。

## 1. 手部局部重绘工作流（hand_fix_api.json）

**目标**：已生成满意的图，只重画手部区域，其余像素 100% 不变。

### 节点链（API 格式）
```
LoadImage → VAEEncode → SetLatentNoiseMask → KSampler → VAEDecode → SaveImage
                 ↑              ↑
                 │              └── SegsToCombinedMask ←── ImpactSimpleDetectorSEGS
                 │                                   ↑           ↑
                 └── VAE(检查点内置)          SAMLoader       UltralyticsDetectorProvider(hand_yolov8s)
```

- `ImpactSimpleDetectorSEGS`（不是 BBOXDetectorToSEGS——本机 Impact 版本里那个节点名不存在）：bbox_detector + image + sam_model_opt → SEGS
- `SegsToCombinedMask`：SEGS → MASK
- `SetLatentNoiseMask(samples, mask)`：mask 内加噪重绘，mask 外 latent 原样 → 解码后整体不动
- KSampler `denoise 0.5`（0.3=微调，0.7=大改）

### 实测数据
- 原图 1024x1536，改动像素仅 1.2-1.4%（集中在手部检测框内），其余 90%+ 画面 0.0-0.5% 差异（VAE 编码噪声级，肉眼不可见）

### 坑
- **`ae.safetensors` 是 Flux 的 16 通道 VAE**，SDXL 模型不能用（KSampler 报 `expected input to have 4 channels, but got 16`）——用 `CheckpointLoaderSimple` 内置 VAE（输出索引 2），不要用 VAELoader
- LoadImage 只认后端 `ComfyUI\input\` 目录，命令行启动的后端不映射共享 input 目录——把测试图复制到后端 input/，且改图后重新提交（LoadImage 每次提交重新扫描）
- API 格式引用 `["5", 2]` 是 [node_id, output_slot]；VAELoader 只有一个输出 slot 0

## 2. API 格式 → 桌面端 UI 格式转换

`hand_fix_api.json` 是 API 格式（class_type+inputs），桌面端画布要 UI 格式（nodes+links），直接拖会打不开。

### UI 格式结构
```json
{
  "version": 1, "last_node_id": N, "last_link_id": N,
  "nodes": [{"id":1, "type":"LoadImage", "pos":[x,y], "size":[w,h], "flags":{},
             "order":1, "mode":0, "inputs":[{"name":"...","type":"...","link":id}],
             "outputs":[{"name":"IMAGE","type":"IMAGE","links":[id]}],
             "properties":{"Node name for S&R":"LoadImage"},
             "widgets_values":["iris_hand_fix_test.png"]}],
  "links": [{"id":1, "origin_id":1, "origin_slot":0, "target_id":2, "target_slot":0, "type":"IMAGE"}],
  "groups": [], "config": {}, "extra": {}
}
```

### 转换要点
- 每个节点需要 OUTPUT_DEFS（输出端口名/类型）和 INPUT_DEFS（输入端口名顺序）映射表，按 class_type 查表
- 链接类型用源节点输出端口类型（MODEL/CLIP/VAE/LATENT/IMAGE/MASK/SEGS 等）
- widget 值（非连接输入）按 INPUT_DEFS 顺序进 `widgets_values`；**无 widget 的节点也要给 `[]`，不能 None**（前端读 None 会出问题）
- `properties` 必须有 `{"Node name for S&R": type}`
- SaveImage 的 filename_prefix 是 widget；LoadImage 的 image 是 widget
- 转换后把文件复制到 `ComfyUI\user\default\workflows\` 即可在桌面端 Workflow→Open 看到；也可直接拖进画布
- **验证**：写个反向脚本从 UI 重建 API（按 links 还原引用），提交到 `/prompt` 跑通才算成功——这是最可靠的验证，不要只看 JSON 结构

### 2.1 widget 顺序 = 前端实际生成顺序（2026-08-08 三次迭代后终解）

桌面端报「5 个节点 — 47 个错误：输入超出范围 / 无效输入 / 输入值类型错误」的根因不是连接问题，而是 **widgets_values 顺序与前端生成顺序错位**。

前端（LiteGraph）创建节点时 widgets 数组与 object_info 的 required/optional 顺序**不一致**：
- `seed` widget 后**自动插入 `control_after_generate`** combo（值 `'randomize'`）
- FaceDetailer 末尾**追加 `tiled_encode`/`tiled_decode`**（默认 `False`）

**权威顺序获取法**（比读前端 JS 源码快 10 倍）：浏览器打开运行中的 ComfyUI 页面，console 执行：
```js
LiteGraph.createNode('FaceDetailer').widgets.map(w => w.name + ':' + w.type).join(' | ')
```
返回即该节点前端真实的 widgets 顺序（FaceDetailer 29 个、KSampler 7 个）。

**已确认顺序**：
- FaceDetailer（29）：`guide_size, guide_size_for, max_size, seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise, feather, noise_mask, force_inpaint, bbox_threshold, bbox_dilation, bbox_crop_factor, sam_detection_hint, sam_dilation, sam_threshold, sam_bbox_expansion, sam_mask_hint_threshold, sam_mask_hint_use_negative, drop_size, wildcard, cycle, inpaint_model, noise_mask_feather, tiled_encode, tiled_decode`
- KSampler（7）：`seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise`

**验证三重奏**（都通过才算桌面端 OK）：
1. 浏览器 `LiteGraph.createNode('FaceDetailer')` 逐个 `node.widgets[i].value = widgets_values[i]`，读回确认每个值落位正确
2. 从 UI 重建 API（跳过 control_after_generate/tiled_* 三个合成 widget）POST `/prompt` 后端接受
3. 实际出图成功，输出文件名与 API 版一致

前端报错排查第一选择是浏览器 console 直接建节点模拟，不要翻 frontend package 的压缩 JS。

## 3. 一般工作流优化（NAI3 方法论落地）

Iris 主工作流 2026-08 优化（v11）：
- 主提示词加 `artstyle, year 2024` 前缀 + NAI3 质量词 `best quality, amazing quality, very aesthetic, absurdres`
- 发色用长咏唱绑定：`(a gentle maid girl with light blue hair and pale blue hair:1.2)`（元素同典长咏唱法）
- 负向词精简去重（1368→1143 字），去矛盾词
- KSampler steps 40→35, cfg 7→6.5（NAI3 推荐 Euler a 28-35 步 CFG 5-7）
- FaceDetailer denoise 微调：手部 0.6→0.55 / 0.5→0.45，整体 0.65→0.6（更精细，避免过度重绘）

详见 `sd-prompt-methodology` / `novelai-element-codex` / `nai3-deconstruction-codex` skills。
