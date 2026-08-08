---
name: nai3-deconstruction-codex
description: "《解构原典》NAI3.0 进阶魔法书：SDXL-NovelAI V3 专用提示词方法论 + 25 套角色还原/构图配方。NAI3 自然语言适应力强、构图能力飞跃、手部良品率高；咒语顺序=人物词+风格词+镜头词+特征+动作+质量词。来源：腾讯文档《解构原典——NAI3.0进阶魔法书》(2023-11)。"
version: 1.0.0
author: agent
tags: [nai3, novelai, sdxl, anime, comfyui, prompt, 角色还原, 构图, 解构原典]
platforms: [windows, macos, linux]
---

# 解构原典（NAI3.0 进阶魔法书）

《解构原典》（The Deconstruction of NAI）第壹卷，Chinese DON Production Committee，Ver. 20231128。**SDXL-NovelAI V3 时代**的提示词法术书。与 `novelai-element-codex`（NAI1 时代旧法典）互补：旧法典讲 tag 堆叠，本书讲 NAI3 的自然语言 + 角色还原 + 构图魔法。

## 触发条件

- 用户使用 NAI3 / SDXL 底模（animagine-xl 等）出图
- 需要角色还原（明日方舟等 2023.6 前角色）
- 需要特殊构图（倒立、坠落、飞行、对称、双人）
- 需要情绪/氛围类 prompt（NAI3 强项）

## NAI3.0 核心认知

- **基底**：SDXL 训练，使用 OpenCLIP ViT-bigG + OpenAI CLIP ViT-L，**自然语言适应力强**
- **能力飞跃**：构图（倒立吃面/手持武器）、细节、手部良品率大幅提升，"不再一眼 AI"
- **角色还原**：2023 年 6 月前的角色 + 网络素材量足够 → 可高质量还原
- **颜文字敏感**：`@_@`、`><` 等颜文字能获得很好的效果（务必试试）
- **情绪词有效**：prompt 中加入情绪词能改变脸部表情
- **不推荐堆叠 tag**：精简到能描述清楚构图即可；多尝试 SD1.5 时期的"无效 tag"有惊喜

### 咒语构筑顺序（推荐）
```
人物词 + 风格词 + 镜头词/环境词 + 人物特征描写 + 动作词 + 质量词
```
此顺序出图最稳定，也可尝试其他组合。

### 权重语法（NAI3）
- `{}` 加权重、`[]` 减权重（延续前代）
- `人物名(作品名)` 格式还原角色，如 `texas the omertosa (arknights)`
- 角色特征出不全 → ① `{}` 加权 ② 增加特征相关 tag ③ 用角色立绘反推

### NAI3 质量词（本书标准后缀）
```text
best quality, amazing quality, very aesthetic, absurdres
```

### NAI3 通用负面（本书标准反咒）
```text
nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts,
bad quality, watermark, unfinished, displeasing, chromatic aberration, signature,
extra digits, artistic error, username, scan, [abstract]
```

### 常用参数
- **Steps 28**（绝大多数配方）
- **Sampler**: Euler / Euler a / DPM++ SDE
- **CFG 5.0-7.0**
- **Size**: 832x1216（竖）/ 1216x832（横）
- **Clip skip 2, ENSD 31337**
- 冰剑兽/奥特曼怪兽等推荐开启 **SMEA 参数**

## 魔法配方库（25 套）

### 1. 角色还原 - 缄默德克萨斯（明日方舟）
```text
正面: {{texas the omertosa (arknights)}}, 1girl, solo, white background, dynamic pose, cute, smile, floating, floating hair, hand on own chest, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler, CFG 5.0, Seed 156263018, 832x1216, Clip skip 2, ENSD 31337
```

### 2. 安吉尔铁拳（铁拳选手）
```text
正面: very aesthetic, 1boy, 1girl, {{{ambriel (arknights)}}}, alternate costume, {armor}, gauntlets, pauldrons, thighhighs, excited, {{punching viewer}}, motion lines, action, best quality, amazing quality, very aesthetic, absurdres
负向: nsfw, lowres, jpeg artifacts, worst quality, watermark, blurry, very displeasing, weapon, earphones
参数: Steps 28, Euler a, CFG 6.0, Seed 2915172687, 832x1216, Clip skip 2, ENSD 31337
```

### 3. 倒立双人（back-to-back）
```text
正面: {2girl}, 1girl upside-down, circle, lying, floating hair, back-to-back, multiple girls, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler a, CFG 5.0, Seed 38316216, 832x1216, Clip skip 2, ENSD 31337
```

### 4. 库丘林（Fate）
```text
正面: cu chulainn (fate), 1boy, armor, black background, blue bodysuit, bodysuit, foreshortening, from side, furrowed brow, gae bolg (fate), holding, holding polearm, holding weapon, long hair, looking at viewer, male focus, parted lips, polearm, red eyes, shattered, shoulder armor, solo, spear, weapon, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler, CFG 5.0, 1216x832, Clip skip 2, ENSD 31337
```

### 5. 凯尔希 - 持花夜景
```text
正面: kal'tsit (arknights), 1girl, 8k wallpaper, extremely detailed figure, amazing beauty, detailed characters, indoor, black dress, holding flowers, light and shadow, depth of field, light spot, reflection, upper body, night, street
参数: Steps 28, Euler, CFG 5.0, Seed 2491320724, 832x1216, Clip skip 2, ENSD 31337
```

### 6. 倒立吃面（构图展示）
```text
正面: {1girl, {upside-down}, {ho'olheyak (arknights)}, 1girl, eatting noodle, holding chopsticks, head wings, alternate costume, aqua eyes, large breasts, pectoral apron, black choker, black dress, white hair, rolling up the hem of tights, black pantyhose, looking at viewer, {indoors background}, shirt, smile, solo, white shirt, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, DPM++ SDE, CFG 5.5, Seed 1877831658, 832x1216, Clip skip 2, ENSD 31337
要点: 只需 upside-down, eatting noodle 即可实现；加 holding chopsticks 等动作更稳定
```

### 7. 凯尔希 - 镜前背影
```text
正面: kal'tsit (arknights), 1girl, 8k wallpaper, extremely detailed figure, amazing beauty, detailed characters, indoor, from back, bare back, tied hair, Mirror, self reflected in the mirror, stool, sitting on the stool, table, mirror on the table, light and shadow, depth of field, light spot, reflection
参数: Steps 28, Euler, CFG 5.0, Seed 2024978526, 832x1216, Clip skip 2, ENSD 31337
```

### 8. 单手倒立（户外）
```text
正面: very aesthetic, 1girl, {one arm handstand}, outdoors, upside-down, armpits, asymmetrical legwear, black footwear, black jacket, black shorts, black socks, black thighhighs, blue sky, boots, breasts, pink hair, ribbon, short shorts, shorts, sky, smile, socks, solo, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler a, CFG 6.0, Seed 1815587863, 832x1216, Clip skip 2, ENSD 31337
要点: one arm handstand, upside-down 是核心
```

### 9. 冰剑兽（魔物/冰剑）
```text
正面: (arknights), {The scar on the eye}, ultra-detailed face, {{numen}}, {huge monster}, {no humans}, {{close up}}, {fighting stance}, {armored dress}, steam, {Armored gloves}, {armour}, {{glowing translucent ice sword}}, {closed up}, {glowing eyes}, Upper armlet, evil smile, cowboy shot, Ferocious eyes, illustration, beautiful detailed, finely detailed, dramatic light, intricate details, perfect anatomy, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, DPM++ SDE, CFG 5.0, Seed 2926542299, 1216x832, Clip skip 2, ENSD 31337
要点: 强烈建议开启 SMEA 参数，开与不开效果完全不同
```

### 10. 凯尔希 - 空中坠落
```text
正面: {kal'tsit (arknights)}, 1girl, solo, cat ears, white background, falling down, floating, in air, floating hair, Bubbles, refracted sunlight, light spots, sadness, lowered head, short hair
参数: Steps 28, Euler, CFG 5.0, Seed 3987263764, 1216x832, Clip skip 2, ENSD 31337
```

### 11. 德克萨斯 - 草地独坐
```text
正面: {{texas the omertosa (arknights)}}, 1girl, white background, White, sitting, grass, from side, head down, sad, solo
参数: Steps 28, Euler, CFG 7.0, Seed 3665045460, 1536x1024, Clip skip 2, ENSD 31337
```

### 12. 泥岩 - 全息镭射（year 2022 前置）
```text
正面: year 2022, 1girl, {mudrock (arknights)}, demon horns, white background, white hair, red eyes, bare shoulder, {{{holographic hair, iridescent, reflective clothes, holographic clothing}}}, jacket, reflection, upper body, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler a, CFG 5.0, Seed 1939040511, 832x1216, Clip skip 2, ENSD 31337
要点: year 2022 前置可减少特征混淆
```

### 13. 机娘（机械义肢全身）
```text
正面: {{1girl}}, eyes, cyborg, {Medium Breast}, joints, looking at viewer, Medium mechanical arms, {huge Mechanical claw}, mechanical hands, mechanical legs, Mechanical tail, Hydraulic rod, mechanical spine, mechanical parts, official alternate costume, robot joints, science fiction, Mechanical Horn, skin tight, {mask}, solo, barcode, robot, suspension, tube, {running}, Simple background, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler, CFG 7.0, Seed 1667590767, 832x1216, Clip skip 2, ENSD 31337
```

### 14. 苇草 - 头顶杰尼龟
```text
正面: reed (arknights), 1girl, solo, green eyes, track jacket, shorts, large breasts, squirtle on head, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler a, CFG 5.0, Seed 4003169650, 832x1216, Clip skip 2, ENSD 31337
要点: 用自然语言描述把杰尼龟放构图的各个位置
```

### 15. 奥特曼怪兽（信号灯小怪兽）
```text
正面: ultraman monster, bodysuit, claws, closed mouth, fighting, horns, kaijuu, mask, open mouth, sharp teeth, simple background, single horn, tail, teeth, tokusatsu, white background, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, DPM++ SDE, CFG 5.0, Seed 2685592338, 1216x832, Clip skip 2, ENSD 31337
要点: 建议开启 SMEA 参数获得带信号灯的小怪兽
```

### 16. 泥岩 - 镭射倒立
```text
正面: year 2022, 1girl, {mudrock (arknights)}, demon horns, white background, white hair, red eyes, bare shoulder, {{{holographic hair, iridescent, reflective clothes, holographic clothing}}}, jacket, reflection, upside-down, spread legs, lingerie, {reflection}, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler a, CFG 5.0, Seed 211739836, 832x1216, Clip skip 2, ENSD 31337
```

### 17. UMP45×UMP9 - 404 横幅（双人）
```text
正面: {2girls, {ump45 (girls' frontline) and ump9 (girls' frontline) holding a banner with "404" written on it}, apron, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, DPM++ SDE, CFG 7.0, Seed 827888098, 1216x832, Clip skip 2, ENSD 31337
要点: 双人法术尝试，NAI3 能良好区分双人特征
```

### 18. 麦哲伦 - 汉服持剑
```text
正面: muelsyse (arknights), 1girl, solo, hanfu, chinese clothes, splatter background, holding sword, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler, CFG 5.0, Seed 268888129, 832x1216, Clip skip 2, ENSD 31337
```

### 19. 透明机娘（半透明义体）
```text
正面: {{{translucent body}}}, 1girl, {{mask}}, aqua eyes, cyborg, Medium Breast, grey hair, joints, looking at viewer, mechanical arms, mechanical hands, mechanical legs, Hydraulic rod, mechanical spine, mechanical parts, medium hair, official alternate costume, robot joints, science fiction, skin tight, solo, translucent skin, barcode, quadruple amputee, robot, sparks, suspension, tube, wire, {cross section}, {Gnaku}, standing, Simple background, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler, CFG 7.0, Seed 2507223098, 768x1280, Clip skip 2, ENSD 31337
```

### 20. 召唤火焰（I am the embodiment of fire）
```text
正面: 1 girl, {{Floating Fire Magic Spell and a burst of flam}}, book, looking at viewer, close-up, cowboy shot, cinematic lighting, volume lighting, light particles, dynamic angle, ray tracing, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler, CFG 5.0, Seed 2940142354, 832x1216, Clip skip 2, ENSD 313
```

### 21. 蛛网的俘虏（巨型蛛网/失重 loli）
```text
正面: {{from below}}, {{{huge spider web}}}, {1 loli caught in a spider web}, {bind}, {full body}, {{floating loli}}, red dress, {tears}, {fear}, {Crazy angle}, grey eyes, {cute face}, solo, {{gravity-free}}, {{winding}}, Dead tree, Dark clouds, {an extremely detailed and beautiful}, ultra-detailed, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler, CFG 5.0, 832x1216, Clip skip 2, ENSD 313
```

### 22. 雷电将军×神子（原神双人背靠背）
```text
正面: [art:genshin impact], {{{{2 girls}}}}, Raiden Shogun(genshin impact) and Yae Miko(genshin impact), {upper body}, {{back to back}}, {{cool}}, grim expression, dynamic Angle, Japanese shrine with floating sakura background, {an extremely detailed and beautiful}, ultra-detailed, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, Euler, CFG 5.0, 832x1216, Clip skip 2, ENSD 313
要点: 双人角色不混淆；可改人设/加艺术风格尝试更多组合
```

### 23. 凯尔希 - 雨夜哭泣（长叙事）
```text
正面: kal'tsit (arknights), blurry, blurry foreground, by rella, Dark environment, from above, full body, 1girl, solo, curl up in bed, arms around her knees, in room, one of Her arm covered her eyes, very sad, she has long and smooth eyelashes, sad crying, tears drop from her face, wet clothes, White nightdress, raining outside, overcast sky, neon lights, lights, cyberpunk, windows, reflections, raindrops hitting the window at night
参数: Steps 28, DPM++ SDE, CFG 5.0, Seed 70294279, 1536x1024, Clip skip 2, ENSD 31337
要点: 长叙事式自然语言情绪描写（NAI3 强项）
```

### 24. 安吉尔踢击（午夜城市飞踢）
```text
正面: flying_kick, symmetrical clothing, fighting pose, spreading legs, legs up, from below, kicking, midnight city, 1girl, A tight muted color dress, taut_dress, bloomers
参数: Steps 28, Euler a, CFG 5.0, Seed 2300499362, 832x1216, Clip skip 2, ENSD 31337
```

### 25. 冬与咖啡（阿米娅咖啡厅）
```text
正面: amiya(arknights), 1girl, 8k wallpaper, extremely detailed figure, amazing beauty, detailed characters, {detailed background}, aestheticism, sitting, winter, coffee shop, corner, coat, scarf, large breasts, gray hair, red eyes, emotionless, obedient, thick eyebrows, small nose, full lips, long eyelashes, delicate neck, slender shoulders, bare arms, delicate hands, long fingers, pointed nails, high cheekbones, oval face, smooth skin, rosy cheeks, cup of coffee, saucer, steam, warm, cozy, comfortable, relaxed, calm, quiet, peaceful, serene, contemplative, close-up, best quality, amazing quality, very aesthetic, absurdres
参数: Steps 28, DPM++ SDE, CFG 5.0, Seed 390987945, 1216x832, Clip skip 2, ENSD 31337
要点: 大量情绪词 + 环境词（NAI3 情绪理解）
```

## 第二卷补充配方（23 套，详见 references/v2-recipes.md）

> 来源：《解构原典第二卷》（https://docs.qq.com/doc/DR2RhUWJ0alZIdWZU，Ver. 20231214）。**完整配方见 `references/v2-recipes.md`**，此处为索引：

| 配方 | 主题 | 亮点 |
|------|------|------|
| 2-1 | 芭芭拉铁拳 | incoming punch / emphasis lines |
| 2-2 | 圣诞少女 | 冬日街灯、呼气成雾、bokeh |
| 2-3 | 黑岩射手 | 蓝火之眼、碎屏、枪指观众 |
| 2-4 | 画中人 | 蓝灰条纹发、手持空相框 |
| 2-5 | 蒸汽朋克女仆狙击手 | 夜雨庭院、sniper rifle、cat ear |
| 2-6 | 鹿角少女 | 明日方舟、单膝跪地、黑鹿角 |
| 2-7 | 大蛇丸 | 火影、白蛇、直刀、sharingan |
| 2-8 | 愚者之行 | 塔罗牌边框、背袋、text:Fools |
| 2-9 | 胡桃香菱 | 原神双人、symmetrical composition |
| 2-10 | 神里长枪 | 白毛婚纱、holding spear |
| 2-11 | 凯尔希雨夜 | 黑雨衣、街头霓虹反射 |
| 2-12 | 持剑少女 | 黑校服、monochrome、chiaroscuro |
| 2-13 | 赛马娘平地摔 | !? 和 > < 颜文字、dutch angle |
| 2-14 | 初音未来 | 秋叶、incoming hug、spread arms |
| 2-15 | 神秘生物 | lineart、biomechanical tattoo、fetal position |
| 2-16 | 侠客 | 中国武侠、血日落日、梅树对决、SMEA |
| 2-17 | 午夜芭蕾 | 写实、dark background、reflection |
| 2-18 | Weird Core | 怪核、glitch art、pixel art |
| 2-19 | 琪亚娜美梦 | 睡眠、抱枕、波点睡衣、:3 |
| 2-20 | 琴柳持枪 | 明日方舟、m4a1、SMEA |
| 2-21 | 加班OL | 除夕、窗外烟花、疲惫 |
| 2-22 | 小野妹子 | lolita、黄色背景 |
| 2-23 | 睡前看手机 | 孤独、手机光照、冷色调 |

## 第三卷补充配方（58 套，详见 references/v3-recipes.md）

> 来源：《解构原典第三卷》（https://docs.qq.com/doc/DR09neE1QbGJCb2JQ，Ver. 20240118）。**完整配方见 `references/v3-recipes.md`**，此处为索引（第三卷分人物/构图/风格三专章）：

| 类别 | 配方 |
|------|------|
| 🎨 画风 | 宝石奇美拉、水彩无脸魔物、东方双人红白、弹丸论破 Weird Core、绫波丽蒸波、像素女孩、情绪渐变、赛博故障少女、莫斯提马极简、万圣节系列、胶片女孩 |
| 👘 国风 | 龙女烟斗（龙年）、江南道袍、旗袍江南、暮落水墨剑、史尔特尔水墨 |
| 🎭 角色还原 | 五条悟×玛奇玛、普拉纳系列、阿米娅抱枕、芙宁娜猫、圆焰之吻、拉普兰德×德克萨斯、莫斯提马系列、蓝毒 JOJO、日奈、NEEDY、岸边露伴、梅琳娜、龙裔圣骑 |
| 🏙️ 场景构图 | 超大吐司、冬鸟咖啡、废弃商场、赛博魔女、像素都市、EVA 03、魔女回廊、鲸鱼、侦探 |
| ⚔️ 战斗 | 喜多恐龙喷火、格温剪刀、死神镰刀、泥岩修车、W 塔罗 |

## 第四卷补充配方（53 套，详见 references/v4-recipes.md）

> 来源：《解构原典第四卷》（https://docs.qq.com/doc/DR0JBWm1VWGhZUGR2，Ver. 20240415）。**完整配方见 `references/v4-recipes.md`**，此处为索引：

| 类别 | 配方 |
|------|------|
| 🎭 角色还原 | 银狼（崩铁）、纳西妲像素、霜星膝枕、芙宁娜吻/水彩猫娘、林雨霞汉服、薄荷×澄闪、里欧手指心、甘雨滚下山、甜猫薄荷、麦哲伦河边、年兽、未花捶墙、蓝色天使、甘雨卷羊毛 |
| ⚔️ 战斗/奇幻 | 蒸汽朋克维修少女、A大狼希夫、索拉尔赞美太阳、骷髅牛仔、骷髅龙大战、屠龙魔法、骑士团、西部天使、无头骑士 |
| 🏙️ 场景构图 | 黑帽猫、游戏椅少女、扫帚女巫晨城、中国节庆龙灯、星际战争、龙在雾海、春雪四季、血红曼陀罗、阿伊努狼、金色大树艾尔登、篝火黑魂 |
| 🎨 画风 | 蝶翼魔女、泪光少女、东方双人樱花酒、和服花束双人、3D精灵、龙纹和服、水墨澄闪、水彩少女、向日葵花田、蓝花山丘、大葱居合斩 |

## 与旧法典（NAI1）的差异速查

| 维度 | NAI1（元素法典） | NAI3（解构原典） |
|------|----------------|-----------------|
| 权重语法 | `()`/`[]`/`{}` 混合 | `{}`/`[]` 为主，自然语言优先 |
| 提示词风格 | tag 堆叠 | 精简 + 自然语言 + 人物名(作品) |
| 构图 | 简单 | 倒立/坠落/飞行/对称/双人 轻松 |
| 手部 | 需 detailer | 良品率大幅提高 |
| 角色还原 | 难 | 2023.6 前角色高质量还原 |
| 情绪 | 弱 | 强（表情随情绪词变化） |
| 质量词 | masterpiece 系 | best quality, amazing quality, very aesthetic, absurdres |
| 通用反咒 | lowres 系 | nsfw, {bad}, error, missing, [abstract] 系 |

## 注意

- 本书针对 **NAI3 / SDXL 底模**；ComfyUI 用 animagine-xl 等 SDXL 模型时可平移使用
- 角色 tag 用 `人物名(作品名)` 格式（如 `texas the omertosa (arknights)`）
- 2023 年 6 月后出现的角色一般没被训练，出不了
- SMEA 参数：冰剑兽/奥特曼怪兽等魔法强烈建议开启
- 目录区魔法（单手倒立、情绪流、镭射泥岩、夜雨、床上的哥特萝莉等）tag 为图片不可提取，仅保留名称+作者索引

## 参考链接

- 原文（第一卷）：https://docs.qq.com/doc/DR1Z4VkFEZGl4Sk9S（《解构原典——NAI3.0进阶魔法书》）
- 原文（第二卷）：https://docs.qq.com/doc/DR2RhUWJ0alZIdWZU（《解构原典第二卷》，Ver. 20231214）
- 原文（第三卷）：https://docs.qq.com/doc/DR09neE1QbGJCb2JQ（《解构原典第三卷》，Ver. 20240118）
- 原文（第四卷）：https://docs.qq.com/doc/DR0JBWm1VWGhZUGR2（《解构原典第四卷》，Ver. 20240415）
- NAI1 时代配方：见 `novelai-element-codex` skill
- 提示词方法论：见 `sd-prompt-methodology` skill
- 本机 ComfyUI：见 `comfyui-character-workflow` skill
