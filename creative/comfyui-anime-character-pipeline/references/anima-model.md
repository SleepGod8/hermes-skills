# Anima (circlestone-labs) — 动漫文生图模型参考

## 是什么
- CircleStone Labs × Comfy Org 合作的 **2B 参数动漫文生图模型**（基于 NVIDIA Cosmos-Predict2-2B-Text2Image 微调）
- 单文件 diffusion 格式，**ComfyUI 原生支持**（无需额外插件）
- 训练：数百万动漫图 + ~80 万非动漫艺术图，无合成数据；动漫数据截止 2025-09
- 只擅长动漫/插画/艺术风格，不适合写实
- 许可证：**非商用**（circlestone-labs-non-commercial-license）

## 版本
| 版本 | 特点 | 用法 |
|------|------|------|
| Anima-Base | 基础版，多样性/风格遵循最强 | 训练 LoRA 用这个 |
| Anima-Aesthetic | 高质量画风微调，一致性更好 | 30-50 steps, CFG 4-5 |
| Anima-Turbo | 蒸馏版，快+稳定（官方推荐起手） | CFG 1, 8-12 steps |

社区衍生 **Anima-2.9B** (Gazingstars123)：官方 Anima 的层扩展微调（28→40 层，~2.9B），额外 1.7M 样本、知识截止 2026-07，无 score 标签（仍可用）。ComfyUI ≥0.33.1 原生；老版本需装 `ComfyUI-Anima-2.9B` 自定义节点。有 int8 量化版省显存（4060 8GB 推荐 int8，全精度 5.8GB 偏紧）。

## 本机已下载文件（E:\Comfy-Desktop\ComfyUI-Shared\models\）
- `diffusion_models/anima-base-v1.0.safetensors` (4.18GB) — 官方 2B
- `diffusion_models/Anima-2.9B-preview-v1_int8_convrot.safetensors` (3.08GB) — 社区 2.9B
- `text_encoders/qwen_3_06b_base.safetensors` (1.19GB) — **两个模型共用**
- `vae/qwen_image_vae.safetensors` (242MB) — **两个模型共用**

## 生成设置
- 分辨率 512²~1536²
- 30-50 steps, CFG 4-5（Turbo: CFG 1, 8-12 steps）
- 采样器推荐：`er_sde`（中性风格） / `euler_a`（细线 2.5D）/ `dpmpp_2m_sde_gpu`
- 2.9B 版：`euler + sgm-uniform`（作者偏好），50 steps 最高质，CFG 3.5-5，分辨率 812×1216 / 1152×1536

## 提示词
- Danbooru 标签体系：小写 + 空格（`score_*` 除外），画师用 `@artist` 前缀
- 推荐正向前缀：`masterpiece, best quality, score_7, safe,`
- 推荐负向：`worst quality, low quality, score_1, score_2, score_3, artist name, blurry, jpeg artifacts, chromatic aberration`
- 支持 `safe/sensitive/nsfw/explicit` 安全标签（对女仆玩法出图友好）
- 2.9B：提示越详细越好，短提示易出平淡背景

## 官方工作流
- README 里嵌的 example.png 可直接拖入 ComfyUI（图即工作流）
- `anima_comparison.json` 是官方提供的多模型对比工作流

## HF 文件清单查询（hf-mirror，拿目标字节数用）
```bash
curl -sL 'https://hf-mirror.com/api/models/<owner>/<repo>/tree/main?recursive=true' | \
  python -c "import sys,json; d=json.load(sys.stdin); [print(f\"{x['path']}  {x.get('size','?')}\") for x in d if x.get('type')=='file']"
```

## 大文件下载坑（hf-mirror + 后台 curl）
- 多文件并发后台 curl 可能中途停滞/进程退出，文件停留在中间大小（本次 anima-base 停在 94.8%、encoder 停在 15.5%）
- 修复：`curl -sSL -C - --retry 5 --retry-delay 3 -o <目标> '<hf-mirror resolve URL>'` 断点续传
- 验证：用 tree API 的目标字节数，`python -c "import os; os.path.getsize(...)"` 逐个确认 >= 目标才算完成
- 后台任务用 `notify_on_complete=true`，不要跨调用频繁 sleep 轮询
