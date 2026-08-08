---
name: sd-prompt-methodology
description: "SD/NovelAI 提示词撰写方法论：权重语法、高低阶语法、元素分类（短/中/长咏唱）、词序公式（标准/通用顺序公式）。编写 ComfyUI 工作流 prompt 时按此组织，可显著提高构图稳定性与元素绑定准确率。来源：《元素同典：确实不完全科学的魔导书》(cv19505389)。"
version: 1.0.0
author: agent
tags: [prompt, sd, stable-diffusion, novelai, animagine, comfyui, prompt-engineering, 提示词]
platforms: [windows, macos, linux]
---

# SD/NovelAI 提示词撰写方法论

面向动漫系模型（Animagine-XL 等，danbooru tag 体系）的 prompt 工程方法。**编写 ComfyUI 工作流时，正负向提示词一律按此方法论组织**。来源：《元素同典：确实不完全科学的魔导书》（B站 cv19505389，2022-11）。

## 触发条件

- 编写/修改 ComfyUI txt2img、img2img、detailer 工作流的 positive/negative 提示词
- 出图出现元素串色（元素污染）、构图失衡、主体丢失、手部畸形
- 需要精确绑定「元素↔颜色/属性」关系（如红裙+黑袜+蓝眼）

## 一、权重语法（低阶语法）

| 语法 | 效果 | 备注 |
|------|------|------|
| `(word)` | 权重 ×1.1 | WEB-UI/ComfyUI 均有效 |
| `((word))` | ×1.21 | 多层嵌套相乘 |
| `[word]` | ÷1.1（×0.91） | 减弱 |
| `(word:1.5)` | 直接指定权重 | **推荐**，清晰可读 |
| `{word}` | ×1.05 | **仅 NovelAI 官方有效**；WEB-UI 中当作文本解析，别用 |
| `(word:1.1)==(word)` | 等价 | `(word:1.21)==((word))`，`(word:0.91)==[word]` |
| `white long (messy:1.2) hair` | 部分权重 | 只对 messy 加权，其余不受影响 |

**权重纪律**：
- 权重影响「画面占比/存在感/数量」——高权重元素占画面更大
- 一般 1.3 已强，1.6 很极端，2.0 会「召唤古神」（构图崩坏）
- 不要写 `((red hair:1.5))` 这种嵌套+显式混合写法，某些情况权重会失效
- 若需要给多数元素加权重 → 不如整体拉高 CFG Scale（12-14），而不是堆括号
- 不建议重复输入同一 prompt（语义复杂难控）

## 二、高阶语法

### 分步描绘（前期引导构图，有视觉延后性）
```
[from:to:step]     # step>1 为步数；0<step<1 为总步数百分比
[from::step]       # 无 to → 后半段为空
[to:step]          # 无 from → 前半段为空
```
例：`a girl with [green hair:red hair flower:0.2]` → 前 20% 步画绿发，后 80% 画红花饰。
- 擅长**画面初期建立引导**，大幅影响构图；不擅长细化细节
- 可嵌套 `[from:[to:end:step2]:step1]`；支持逗号分割
- 注意颜色溢出：后段无限定词时 AI 可能自由发挥

### 融合描绘（混合两种事物）
```
[A | B]            # 交替：step1 画 A，step2 画 B，step3 画 A...
[A | B | C | ...]  # 无限延长版循环
[A:w1 | B:w2]      # 带比例版（NAIFU 独占；WEB-UI 会当文本读）
[(A:w1) | (B:w2)]  # WEB-UI 等效写法：嵌套加权，作用域是整个咒语
```
例：`a [dog | frog] in black background` → 狗与蛙的融合体。
- **不可嵌套**，支持逗号分割
- 与分步描绘本质区别：分步=有分立感的 A 带 B 特征；融合=完全化在一起的融合体

## 三、元素分类与三种咏唱

假设目标：黄发+蓝眼+白衣+红裙+黑袜的坐姿全身美少女，强调服饰颜色：

| 咏唱方式 | 写法 | 特点 |
|----------|------|------|
| 直接咏唱（pitch 式） | `masterpiece, best quality, 1 girl, (blue eyes), (yellow hair), (white clothes), (red skirt), (black leggings), sitting, full body` | 最常用；元素颜色绑定弱，易串色 |
| 短句咏唱（AND 强调） | `masterpiece, best quality, 1 girl, (blue eyes) AND (yellow hair), (white clothes) AND (red skirt) AND (black leggings), sitting, full body` | 介于两者之间；**AND 必须大写**；DDIM 采样不支持会报错 |
| 长咏唱（自然语言） | `masterpiece, best quality, (1 girl with blue eyes and yellow hair wearing white clothes and red skirt with black leggings), sitting, full body` | **元素绑定最强**（蓝黄白红黑试验）；必须整个句子用小括号包住（权重略>1.0 最佳）；稳定性略低 |

**选择原则**：
- 有明确「元素↔属性」绑定需求（如特定颜色服饰）→ **长咏唱**
- 关系要求不强、想要多样化场面 → **直接咏唱**
- 长咏唱 = 元素污染问题的根本解法：把颜色/属性与元素写进同一短语

## 四、词序公式（构图的关键！）

### 核心原理：顺序叠加论
- prompt **顺序影响画面组织方式**，越靠前越「重」，对构图影响越大
- 顺序对构图的影响**通常大于权重**（「少女与壶」试验：blue pot 在前时人物退为配角，甚至加权也无法反超）
- 靠后的词成为靠前词的点缀/附加物

### 标准顺序公式（人像）
```
前缀 + 重点突出的物件/背景 + 人 + 人物特征/元素 + 人物动态
     + 服饰整体 + 服饰细节元素 + 大背景 + 背景元素
     + 光照效果 + 画风滤镜 + 微小辅助元素 + 后缀
```

### 通用顺序公式（最终版，入门标志）
```
质量前缀 + 前置画风引导 + 前置镜头效果 + 前置光照效果
+ [带描述的物x + 物x的各种次要物 + 镜头效果和光照(如必要)] × X
+ 全局光照效果 + 全局镜头效果 + 画风滤镜
```

**要点**：
- 物 = 一切可被描绘的对象（人/挂饰/建筑/背景都算「物」）
- 物的排序按**预期构图主次**排列；次要物紧跟其附着对象之后
- 颜色/形状等属性**并入物本身**（写 `red clothes` 而非 `clothes, red`），避免污染其他元素
- 镜头/光照/画风均为可选项，**各不超过 3 种**
- 微小次要物（耳环等）天生难做主角，但可用来打破叠加式构图（AI 会强制聚焦）
- 镜头插入位点：一切物之前=大幅影响整个画面；所修饰的物之后=主要影响该物

### 镜头与光照常用词
- 镜头：`close up, close shot, medium view, medium shot, panorama, full body`
- 光照：`backlight, rembrandt lighting, soft lighting, sunlight, moonlight, rim light`
- 画风：`sketch, oil painting, illustration, anime, wallpaper, watercolor, highly detailed`
  - ⚠️ `highly detailed` 会让画面偏厚涂/油画；`ultra-detailed` 是流传的以讹传讹，未必有用
  - `wallpaper`/`illustration` 看似质量词实则能质变画面，混合使用有化学反应

## 五、步数与采样（与 prompt 配合）

| 场景 | 推荐 |
|------|------|
| 简单场景标准画布 | Euler A：30-40 步；DDIM：25-35 步 |
| 复杂场景/细化需求 | 提高步数；**修手要 80 步起步，复杂场景 120 起步** |
| 采样方法 | Euler A 兼顾速度质量；DPM2 A 也不错；**不推荐** LMS / DPM fast / LMS Karras / PLMS |

**重要发现**：高步数对手部等细小复杂区块效果拔群（20 步=错位麻花，80 步=基本成型）——与 detailer 精修互补。

## 六、通用反咒（Negative Prompt）

```text
lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit,
fewer digits, cropped, worst quality, low quality, normal quality,
jpeg artifacts, signature, watermark, username, blurry, bad feet
```
（ComfyUI 工作流中可在此基础上按需追加：bad hands 细分、hair over hands、long eyelashes 等）

## 七、黑图/元素溢出排障

| 症状 | 原因 | 解法 |
|------|------|------|
| 黑图 | 显存爆（CUDA out of memory） | 降画布 |
| 黑图 | 咒语太精简 + 画布太大 → 自由度超出模型理解 | 按画布扩增咒语 |
| 黑图 | 咒语太繁杂 + 画布太小 | 酌情精简 |
| 1 girl 画出 2 个 | 元素溢出：画布太空，AI 重复已有对象填充 | 加长咒语限制自由度（补背景/物件词） |

## 八、Emoji 彩蛋（强到可怕）

- **Emoji 可直接作为 prompt**（SD 框架原样处理，不转义英文），信息密度极高，加权效果惊人
- `✋`修手、`👪`群像、`🎇`烟花背景、`💀`骷髅、`✏`铅笔画风、`🎏`浮世绘、`🏴☠️`海盗船
- 一对小括号 ≈ (prompt:1.35) 的效果
- emoji 大全：https://www.emojiall.com/zh-hans

## 九、tag 来源

- **danbooru.donmai.us**：NAI 主要训练来源，引用数 >2000 的 tag 直接用即可出效果（需跨域）
- 英语水平好可直接用自然语言大段描写（训练数据贴合日常英语）
- 自建「魔导书」：收集整理有效 tag 与技巧

## 十、验证方法（定性定量分析）

- SD 基于 seed：prompt+seed 相同则图必然相同 → 固定 seed，只改一个变量，对比效果
- WEB-UI 用 Script 的 X/Y plot + Prompt S/R 批量对比（ComfyUI 可用 batch/seed 遍历替代）
- 通过排列组合统计多元素间的相互作用

## 参考链接

- 原文：《元素同典：确实不完全科学的魔导书》 https://www.bilibili.com/opus/724243069538402304 （cv19505389）
- 标准三段术式及绚丽术入门与解析v2：https://docs.qq.com/doc/DSHBGRmRUUURjVmNM
- 配合本机 ComfyUI 使用：见 `comfyui-character-workflow` 技能（animagine-xl-4.0 + FaceDetailer 精修链）
