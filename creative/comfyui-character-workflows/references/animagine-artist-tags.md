# animagine-xl-4.0 画师词条 + 模型选型（2026-08-30 实测）

> ⚠️ 修正：`mcp-curl-fallback.md` 里「本机二次元画像首选 NoobAI-XL-v1.1」的旧结论**已被用户否决**，
> 以本文件的最终结论为准（主力 animagine-xl-4.0）。

## 画师词条（实测有效）

- **格式**：`{画师名}` 花括号。animagine-xl-4.0 README（hf-mirror 拉取）无 artist tags 章节，
  但模型用 Danbooru 8.4M 图集 tag-ordering 训练（identity and style training），画师标签天然被收录。
- **实测有效画师**（同 seed 42 / 同参数 / 只换词条 → 画风分化显著）：
  - `{melon22}` → 水彩晕染、淡雅梦幻、柔美上色
  - `{ikarin}` → 明亮高饱和、线条清晰锐利、青春活力
- **强化权重**：`({melon22}:1.3)` 有效；别超 1.5 容易崩。
- **双画师叠加**：`({melon22}:1.3), {ikarin}` → 同 seed 实测 melon22 占 60-70%、ikarin 占 30-40%，
  效果≈「水彩上色 + 精细线稿」。平衡配比可试 `({melon22}:1.15), ({ikarin}:1.1)`。
- 画师词条是「风格倾向」不是「完全复刻」；想更贴画风可补该画师常用场景/配色词。

## 模型选型最终结论（用户拍板）

- 本机二次元画像**主力 = animagine-xl-4.0**。同 seed 42 / 896×1152 / euler_ancestral / 30 步 / CFG 6 实测对比：
  - NoobAI-XL-v1.1：头发层次、服装细节、光影过渡更精细，但纯色背景、缺场景氛围
  - animagine-xl-4.0：带场景氛围（蓝天白云等）、清新明亮
  - 用户判断「氛围感 > 细节堆砌」→ **偏好 animagine**；不要主动推 NoobAI 换主力。
- NoobAI-XL-v1.1 仅备用参考（danbooru 标签同系，提示词写法与 animagine 一致，可无缝切换）。
- Realistic_Vision_V5.1 = SD1.5 写实向，不做二次元。
- DiT 系（Z-Image-Turbo 6B / Anima-2.9B-preview）：8GB 卡 bf16 跑不动或未实测；Z-Image 官方要 16G VRAM，跳过。

## 对比出图方法（可复用）

1. `comfy_build_txt2img` 构建两个 workflow，只换 ckpt_name，其余（prompt/seed/尺寸/steps/CFG/采样器）完全一致。
2. 8GB 卡串行提交（ComfyUI 队列自动排队），896×1152/30 步约 40-70s/张。
3. 判据 = 视觉模型质检（五官/手部/构图/细节）+ 用户肉眼验收 + 社区共识，三者结合。
