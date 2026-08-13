# 弱概念图：坏图自查 + img2img 精修（2026-08-14 实测：Dionysus 衣冠不整）

## 背景

animagine-xl-4.0 对抽象属性（衣冠不整、醉酒程度、复杂服饰状态等）的 txt2img 响应极不稳定。Dionysus「衣冠不整」迭代：抽象 disheveled clothes/messy uniform 几乎不生效（3 张全整洁）→ 具体描述+高权重（`(disheveled maid dress:1.4), loose unbuttoned collar, collarbone visible, crooked apron, apron slightly untied, wrinkled dress, rumpled skirt, headband tilted`）→ 只有个别 seed 碰巧画出（seed 42 出「滑肩+围裙半解+扣子松开」，换 seed 又回整洁）。

## 坏图自查（渲染「成功」≠ 图是好的）

症状：ComfyUI 报 `completed/success`、文件是有效 PNG（1024×1536、3-4MB 反而比正常 1.3-2MB 大），但 qwen-vl-plus 答「抽象图案/纯色纹理/无法确定/没有人」。
（本次实测 bal 批：`dionysus_bal_0/1/2` 全部如此。）

**PIL 灰度 std 判据（最快确认）**：

```python
from PIL import Image
img = Image.open(path).convert("L").resize((64, 96))
px = list(img.getdata())
mean = sum(px) / len(px)
std = (sum((p - mean) ** 2 for p in px) / len(px)) ** 0.5
# 正常图 >25（Hebe health_test 38.3、v3 批 36-48）
# 雾气/纯色坏图 <10（bal 批 18.1/2.7/7.7 —— 全坏）
```

坏图元凶 = **抽象属性词叠太猛**：`(completely disheveled:1.6)` + `fully off-shoulder` + `open front` + `skirt hiked up` 全上必翻车——渲染成功但 latent 炸成噪声/纯色。回退到能出图的保守版：`(very disheveled maid dress:1.5), one shoulder slipping off, exposed shoulder, unbuttoned collar, buttons undone, half-untied apron, apron string loose, clothes hanging loosely, bunched up wrinkled skirt`（该组合 seed 42 出过好图）。

## img2img 精修（突破 txt2img 上限）

把 txt2img 能出的最好 seed 图作为底图，img2img 用更强的概念词重绘，保留构图只增强目标属性。

步骤：
1. 底图复制到命令行后端 input 目录：`cp 定稿图.png "E:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/input/base.png"`
   （命令行后端 LoadImage 只认默认 input 目录，不是 ComfyUI-Shared/input）
2. 工作流：`LoadImage → VAEEncode → KSampler(denoise 0.45-0.55) → VAEDecode → SaveImage`
   - checkpoint 用 CheckpointLoaderSimple 内置 VAE（`["1",2]`），**别用 VAELoader 的 ae.safetensors**（Flux 16 通道会 4ch 报错）
3. 正向：角色核心描述不变 + 更强概念词（`(completely disheveled maid dress:1.6), fully off-shoulder dress, both shoulders bare, apron completely untied, apron hanging off, unbuttoned top, open front shirt, skirt hiked up`）
4. denoise：0.45 保守微调 / 0.5 中改 / 0.55 大改；多 seed 跑 2-3 张挑

实测：3 seed（denoise 0.45/0.55/0.5）全部出现「围裙解开/扣子松开/滑肩+裙皱」+ 醉醺醺痴笑，r1/r2 通过 qwen 验证（r0 被标「不通过」但原因未明、std 31.6 正常，属细节瑕疵可再精修）。比 txt2img 极限（只能轻微不规整）高一档。

## 程度分级（别无限叠词）

1. txt2img 单 seed 探路（seed 42 首张 + qwen 验证）→ 满意即交付
2. 不够 → img2img 精修（denoise 阶梯 + 多 seed）
3. 再不够 = 模型能力上限：animagine 衣冠不整到「半解」即极限（负向 nsfw 防护在兜底）。向主人说明模型限制，**不要继续叠更极端的词**（越叠越容易出坏图，且浪费 3-7 分钟/张）。

## 经验总结

- qwen-vl-plus 说「抽象/纯色」时先跑 PIL std 确认，别改 prompt 瞎猜（本次先误判为后端问题，重启后端 + 换 seed 白跑 3 张）
- 后端健康测试：随便跑一张已知好 prompt（如 hebe_new_api.json seed 42），PIL std>25 即后端正常——排除环境因素后再怀疑 prompt
- 负向「放开」要谨慎：删 cleavage/underboob 换 nude/topless/exposed nipples 防护，仍能防止露点/全裸，但别删太多（本次 NEG_LOOSE 与坏图同时出现，保守起见弱概念迭代用原负向 + 正向强词）
