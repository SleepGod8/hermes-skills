---
name: comfyui-image-quality
description: "Tune ComfyUI image quality: hand/eye/pose or MCP bridge."
version: 1.0.0
author: agent
tags: [comfyui, image-generation, quality-tuning, stable-diffusion, sdxl, hand-fix, detailer, mcp]
platforms: [windows, linux, macos]
---

# ComfyUI 图像质量调教

在 ComfyUI 生成图上做「缺陷修正 + 细节提升」的实战配方库。与 `comfyui` 技能互补：comfyui 负责安装/生命周期/REST 脚本，本技能负责**质量决策**（手部、眼部、手势、构图、细节）。

## 触发条件

- 用户说「手部有问题」「手指畸形」「眼睛糊」「睫毛太长」「手势不对」「画面不精细」
- 需要精修 AI 生成图的脸/手/姿态
- 需要验证 ComfyUI 相关的 MCP 桥是否生效

## 核心架构：双道 Detailer 精修

```
KSampler → VAEDecode → FaceDetailer(手部) → FaceDetailer(脸部) → SaveImage
                          ├─ bbox_detector = UltralyticsDetectorProvider(hand_yolov9c.pt)
                          ├─ sam_model_opt = SAMLoader(sam_vit_b_01ec64.pth)
                          └─ positive/negative = 部位特化提示词
```

依赖：comfyui-impact-pack（FaceDetailer/SAMLoader）+ comfyui-impact-subpack（UltralyticsDetectorProvider）+ ultralytics 包（必须 `--no-deps` 安装防 torch 被覆盖成 CPU）+ 检测器模型（Bingsu/adetailer 仓库，国内用 hf-mirror）。

## 手部精修六项强化参数（消畸形）

| 参数 | 强化值 | 作用 |
| --- | --- | --- |
| 检测器 | hand_yolov9c.pt | 更强检测（51MB） |
| denoise | 0.5 | 重绘彻底（<0.4 等于没精修） |
| cycle | 2 | 两轮精修 |
| bbox_threshold | 0.4 | 更敏感检测到手 |
| bbox_dilation | 15 | 检测框覆盖完整 |
| bbox_crop_factor | 3.5 | 裁剪上下文更大 |
| drop_size | 20 | 过滤小误检 |

手部仍是概率性——最终保险是跑 2-3 个随机种子挑最稳一张。

## 眼部精细精修（要精细不要夸张）

用户踩坑：`long eyelashes` / `big eyes` 导致夸张睫毛。正确写法：

- 正向：`detailed eyes, detailed pupils, clear iris, visible pupils, detailed eyelashes, fine eyelashes, delicate eyelashes, sharp eyes, focused eyes`
- 负向：`blurry eyes, blurred pupils, indistinct pupils, no pupils, long eyelashes, exaggerated eyelashes, thick eyelashes, huge eyelashes, fake eyelashes`
- **瞳孔糊通常是 Detailer 力度不够**：denoise ≥0.45、steps ≥28、guide_size ≥896

## 手势控制三层引导

1. 主正向加权重：`((one hand resting on the other hand)), right hand on left hand, hands in front of waist`
2. 主负向锁死：`arms up, hands raised, arms crossed, hands clasped, hands folded, interlaced fingers, holding pillow, magic circle, arms at sides, hands hanging down`
3. 手部 Detailer 的 positive/negative 同步注入手势词

**手势词调教记录**（「身前叠放」4轮迭代结论）：
- ✅ 有效：`one hand resting on the other hand` + 位置限定 `hands in front of waist`
- ❌ `palms stacked`/`hands placed on top of each other` → 画成掌心向上张开
- ❌ `hands clasped`/`hands folded`/`hands together` → 交握祈祷
- ⚠️ `hands resting in front` 可能被理解成抱东西 → 模型塞枕头，负向必须锁 pillow/plushie
- **教训**：手势词越直白越好，一个核心表达 + 位置限定就够；堆同义词模型反而全错

## 细节提升组合拳

- 分辨率：SDXL 896×1152 → 1024×1536（显著提升细节）
- steps：32 → 40
- 正向加：`ultra detailed, intricate details, highly detailed, detailed hair, detailed eyes`
- 单人构图：正向 `solo, single character` + 负向 `2girls, multiple characters, background character`
- 侧身：`three-quarter view, slight turn, body slightly angled` 稳定有效

## MCP 桥验证（hermes-comfyui 类 stdio 桥）

Codex/外部交付的 ComfyUI MCP 桥，验证三步：

1. **安装检查**：skill 目录在 `skills/creative/<name>/`；config.yaml 的 `mcp_servers.<name>` 注册，command 用 Hermes venv python，args 指向 server.py 绝对路径
2. **握手测试**：精确 Content-Length 帧发 initialize + tools/list，验证返回 serverInfo 和工具列表。MCP 帧格式：`Content-Length: <len>\r\n\r\n<json>`，长度必须字节精确
3. **功能测试**：`tools/call` 调 `comfy_server_info` 和 `comfy_inventory`，确认能连真实 ComfyUI（8188）并扫描节点

注意：MCP 配置写入后**当前会话不热加载**，需重启 Hermes/新开会话才出现在工具列表。

可复用脚本：`scripts/mcp_bridge_probe.py` —— 一键跑握手 + tools/list + comfy_server_info 功能测试。

## 环境真相（本机 ComfyUI）

- ComfyUI 真实运行环境是 `<安装目录>/ComfyUI/.venv`（torch 2.10.0+cu130 CUDA 正常）
- `standalone-env` 是备用环境——**不要**往里面 pip 装包（会污染成 CPU torch）
- 判断真后端：`wmic process where "name='python.exe'" get ProcessId,CommandLine | grep main.py`
- 启动后端路径参数用**正斜杠**，反斜杠会被 bash 转义成乱拼接目录
- Desktop 版反复「自动更新后自动关闭」：清 `settings.json` 的 `pendingDownloadedUpdateVersion`
