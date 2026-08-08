---
name: novelai-element-codex
description: "《元素法典》Novel AI 元素魔法全收录：58 种魔法配方（水/冰/核爆/星空/虹彩/废土等）+ 通用起手式 + 通用反例 + 采样参数速查。编写 ComfyUI/NAI 工作流时按魔法类别选取配方。来源：腾讯文档《元素法典——Novel AI 元素魔法全收录》第一卷。"
version: 1.0.0
author: agent
tags: [novelai, sd, stable-diffusion, animagine, comfyui, prompt, 元素法典, 魔法配方]
platforms: [windows, macos, linux]
---

# Novel AI 元素法典（元素魔法全收录）

《元素法典》（The Code of Quintessence）第一卷。**面向 Novel AI / SD 动漫系模型的"魔法配方"合集**——每一法 = 一套可复用的 prompt 配方（正面 tag / 反面 tag / 参数）。与 `sd-prompt-methodology`（方法论）互补：方法论讲**怎么写**，本 skill 讲**用什么**。

## 触发条件

- 用户要求"用 XX 风格/元素出图"（水、冰、火焰、星空、彩虹、废土、水晶、樱花、魔法阵……）
- 需要特定画风配方（浮世绘、水彩、ink、Gothic、蒸汽朋克……）
- 编写 ComfyUI 工作流需要成熟可复现的 prompt
- 需要在 58 种魔法配方中挑选

## 通用起手式（Quality Prefix）

```text
((masterpiece)), (((best quality))), ((ultra-detailed)), ((illustration)), ((disheveled hair))
```

**通用反例（Negative）**：
```text
lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits,
cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark,
username, blurry, missing fingers, bad hands, missing arms, long neck, Humpbacked
```

## 常用参数速查

| 魔法 | Steps | Sampler | CFG |
|------|-------|---------|-----|
| 通用 | 28-50 | Euler a | 4.5-7 |
| 星空类 | 50-60 | Euler a / DDIM | 7-12 |
| 虹彩/彩虹 | 极低 CFG（2-4） | Euler a | 成功率最高 |
| 细节场景 | 40-50 | Euler a | 4.5-5.5 |
| 摄影法 | 26-30 | Euler a | 6 |
| NAIFU 专用 | 20-23 | DDIM | 4.5-12 |

**要点**：
- Euler a 兼顾速度质量，绝大多数魔法用它
- 彩虹/虹彩系要求**极低 CFG**（约 2-4），成图不稳定但成功率经过调优
- NAIFU 端常用 `{word}` 大括号（官方 ×1.05），WebUI 端不适用
- 画布比例：竖版 512×768 / 768×1024 / 832×1216 效果佳；横版 1280×720 适合风景类

## 魔法配方库（62 套文本配方）

> 以下配方从《元素法典》第一卷文本区提取，正面 tag 已标准化为可复制格式。**使用前先套用「通用起手式」前缀**（配方里已含的除外）。

### 一、元素/自然系

#### 1. 水魔法（万恶之源）
```text
正面: ((masterpiece)), (((best quality))), ((ultra-detailed)), ((illustration)), ((disheveled hair)), ((frills)), (1 girl), (solo), dynamic angle, big top sleeves, floating, beautiful detailed sky, on beautiful detailed water, beautiful detailed eyes, overexposure, (fist), expressionless, side blunt bangs, hairs between eyes, ribbons, bowties, buttons, bare shoulders, (((small breast))), detailed wet clothes, blank stare, pleated skirt, flowers
参数: CFG 5.5, euler_a, step 30
```

#### 2. 冰魔法（万恶之源之二）
```text
正面: (((masterpiece))), best quality, illustration, (beautiful detailed girl), beautiful detailed glow, detailed ice, beautiful detailed water, (beautiful detailed eyes), expressionless, beautiful detailed white gloves, (floating palaces:1.2), azure hair, disheveled hair, long bangs, hairs between eyes, (skyblue dress), black ribbon, white bowties, midriff, {{{half closed eyes}}}, big forhead, blank stare, flower, large top sleeves, (((ice crystal texture wings)))
参数: Steps 50, Euler a, CFG 5.5
```

#### 3. 核爆法
```text
正面: (((masterpiece))), best quality, illustration, (beautiful detailed girl), beautiful detailed glow, ((flames of war)), (((nuclear explosion behide))), rain, detailed lighting, detailed water, (beautiful detailed eyes), expressionless, palace, azure hair, disheveled hair, long bangs, hairs between eyes, (whitegrey dress), black ribbon, white bowties, midriff, big forhead, blank stare, flower, long sleeves
参数: Steps 28, Euler a, CFG 7
```

#### 4. 星空法（星云魔法师）
```text
正面: ((masterpiece)), (((best quality))), ((ultra-detailed)), ((illustration)), ((disheveled hair)), beautiful detailed eyes, (1girl:1.2), (solo), dynamic angle, dark magician girl, (black kneehighs:1.1), (starry tornado:1.4), starry Nebula, ((frills)), beautiful detailed sky, beautiful detailed eyes, evil smile, expressionless, hairs between eyes, white hair, pleated skirt, ((disreveled hair))
参数: CFG 6.0, euler_a, steps 50
```

#### 5. 流沙法（沙漠悬浮）
```text
正面: cinematic lighting, ((best quality)), ((extremely_detailed_eyes_and_face)), ((((ink)))), ((illustration)), depth of field, ((extremely detailed)), ((watercolor)), ((anime face)), (((dramatic_angle))), medium_breast, (8k_wallpaper), ((bright_eyes)), (looking_at_viewers), (an detailed organdie dress), (((((very_close_to_viewers))))), ((sleepy)), ((masterpiece)), ((((((surrounded_by_heavy_floating_sand_flow_and_floating_sharp_stones)))))), (((((messy_long_hair))))), ((((veil)))), focus_on_face, (upper_body), (bare_shoulder), ((((1girl)))), (golden_bracelet), (long yarn), ((sunset)), lens_flare, light_leaks, ((detailed_beautiful_desert_with_cactus)), medium_wind, (detailed_beautiful_sky)
参数: CFG 5.5, euler_a, step 30
```

#### 6. 白骨法（骷髅教堂）
```text
正面: cinematic lighting, ((best quality)), ((single_human_girl)), ((((upper_body)))), ((extremely_detailed_eyes_and_face)), ((church)), ((annoyed)), ((ink)), ((illustration)), depth of field, ((frown)), ((expression)), ((red_eyes)), ((((white_hair)))), ((extremely detailed)), ((watercolor)), ((anime face)), (skull_on_dress), (((yokozuwari))), ((detailed_skeleton_church)), (((beautiful_detailed_black_gothic_Empire_Waist_Dress))), (((dramatic_angle))), medium_breast, (8k_wallpaper), ((bright_eyes)), (looking_at_viewers), ((close_to_viewers)), ((masterpiece)), (((((messy_long_hair))))), ((((1girl)))), lens_flare, light_leaks
参数: CFG 6.5, 其他随意
```

#### 7. 森林冰
```text
正面: ((((ink)))), ((watercolor)), world masterpiece theater, ((best quality)), depth of field, ((illustration)), (1 girl), anime face, medium_breast, floating, beautiful detailed sky, looking_at_viewers, an detailed organdie dress, very_close_to_viewers, bare_shoulder, golden_bracelet, focus_on_face, messy_long_hair, veil, upper_body, lens_flare, light_leaks, bare shoulders, detailed_beautiful_Snow_Forest_with_Trees, spirit, grey_hair, White clothes, ((Snowflakes)), floating sand flow, navel, (beautiful detailed eyes), (8k_wallpaper)
参数: Steps 30, Euler a, CFG 7
```

#### 8. 冰火法（冰火交融）
```text
正面: ((ink)), ((watercolor)), {{best quality}}, (expressionless), ((illustration)), (beautiful detailed girl), (beautiful detailed eyes), world masterpiece theater, depth of field, (blue spark), anime face, black gauze skirt, (red and blue hair), blue eyes, focus_on_face, medium_breasts, (((((messy_long_hair))))), Bare shoulder, very_close_to_viewers, burning sky, navel, ((bustier)), flame, Rainbow in the sky, ((Flames burning ice)), (((Fire butterflys))), (((ice crystal texture wings))), (Flying sparks), (detailed ice), {{a lot of luminous ice crystals}}, ((burning feathers)), {feathers_made_of_ice}, (frozen feathers), {{{ice and fire together}}}
参数: steps 23, scale 4.5, euler, 832x512
```

#### 9. 森火法（燃烧教堂/火蝶）
```text
正面: ((((ink)))), ((watercolor)), ((best quality)), (spirit), ((illustration)), (((1 girl))), (beautiful detailed eyes), world masterpiece theater, depth of field, (Burning forest), spark, anime face, Black gauze skirt, (red_hair), blue_eyes, focus_on_face, medium_breasts, (((((messy_long_hair))))), Bare shoulder, very_close_to_viewers, veil, light_leaks, Burning sky, navel, ((bustier)), flame, Red Gem Necklace, Rainbow in the sky, Flames burning around, A burning church, (((Fire butterflys))), (Flying sparks)
参数: Steps 30, Euler a, CFG 5.5
```

#### 10. 废土法
```text
正面: (((masterpiece))), (((best quality))), ((ultra-detailed)), (illustration), (1 girl), (solo), ((an extremely delicate and beautiful)), little girl, ((beautiful detailed sky)), beautiful detailed eyes, side blunt bangs, hairs between eyes, ribbons, bowties, buttons, bare shoulders, (small breast), blank stare, pleated skirt, close to viewer, ((breeze)), Flying splashes, Flying petals, wind
参数: CFG 5.5, euler, step 50
```

#### 11. 水森法（森林水世界）
```text
正面: (extremely detailed CG unity 8k wallpaper), (((masterpiece))), (((best quality))), ((ultra-detailed)), (best illustration), (best shadow), ((an extremely delicate and beautiful)), dynamic angle, floating, fairyland, dynamic angle, sea of flowers, beautiful detailed garden, wind, classic, spring, (detailed light), feather, nature, (sunlight), river, forest, (((floating palace))), ((the best building)), beautiful and delicate water, (painting), (sketch), (bloom), (shine)
参数: CFG 6, Euler
```

#### 12. 水下法（海底少女）
```text
正面: (((masterpiece))), (((best quality))), ((ultra-detailed)), ((underwater)), (illustration), (beautiful detailed water), ((coral)), open tuck, ((extremely delicate and beautiful girls)), dynamic angle, floating, (beautiful detailed eyes), (detailed light), (loli), floating hair, glowing eyes, pointy ears, (splash), underwater, ((fishes)), white hair, green right eye, iceblue left eye, leaves dress, feather, nature, (sunlight), (underwater forest), (painting), (bloom), (detailed glow), drenched, seaweed, fish, (((Tyndall effect))), face to face
参数: Steps 27, Euler a, CFG 7
```

### 二、星空/幻境系

#### 13. 幻之时（钟表/玻璃/折射）
```text
正面: ((illustration)), ((floating hair)), ((chromatic aberration)), ((caustic)), lens flare, dynamic angle, ((portrait)), (1 girl), ((solo)), cute face, ((hidden hands)), asymmetrical bangs, (beautiful detailed eyes), eye shadow, ((huge clocks)), ((glass strips)), (floating glass fragments), ((colorful refraction)), (beautiful detailed sky), ((dark intense shadows)), ((cinematic lighting)), ((overexposure)), (expressionless), blank stare, big top sleeves, ((frills)), hair_ornament, ribbons, bowties, buttons, (((small breast))), pleated skirt, ((sharp focus)), ((masterpiece)), (((best quality))), ((extremely detailed)), colorful, hdr
参数: cfg 4.5, euler_a, steps 28
```

#### 14. 星源法（星河宇宙）
```text
正面: best quality, Amazing, Beautiful golden eyes, finely detail, Depth of field, extremely detailed CG unity 8k wallpaper, masterpiece, (((Long dark blond hair))), ((red mediumhair)), (1 girl), (white stockings), (((((medium_breasts,))))), (hair ribbon), Exposing cleavage, ((Beautiful butterflies in detail)), (((halter dress))), huge ahoge, particle, (((solo))), (Background of details), standing, (Starry sky in beautiful detail), (((gloom (expression) depressed))), (Hazy fog), (((Very long hair))), {Fluttering hair}, {Thick hair}, {{{Gelatinous texture}}}, {profile}, (Ruins of beautiful details), (((Standing on the surface of the sea))), {Close-up of people}, {{{Smooth skin}}}, (((upper body))), (Smooth and radiant skin), (Smooth and radiant face), Perfect details, Beautifully gorgeous necklace, Authentic skin texture, {Cleavage}, {{{Authentic and detailed face}}}, (unexposed:1.5)
参数: Steps 50, Euler, CFG 4
```

#### 15. 星霞海（彩虹星海 loli）
```text
正面: ((extremely detailed CG)), ((8k_wallpaper)), (((masterpiece))), ((best quality)), watercolor_(medium), ((beautiful detailed starry sky)), cinmatic lighting, loli, princess, very long rainbow hair, side view, looking at viewer, full body, frills, (far from viewer), ((extremely detailed face)), ((an extremely delicate and beautiful girl)), ((extremely detailed cute anime face)), ((extremely detailed eyes)), (((extremely detailed body))), (ultra detailed), illustration, ((bare stomach)), ((bare shoulder)), small breast, ((sideboob)), ((((floating and rainbow hair)))), (((Iridescence and rainbow hair))), (((extremely detailed sailor dress))), ((((Iridescence and rainbow dress)))), (Iridescence and rainbow eyes), beautiful detailed hair, beautiful detailed dress, dramatic angle, expressionless, (big top sleeves), frills, blush, (ahoge)
参数: step28, scale5, k_euler_a, 832x512
```

#### 16. 星冰乐（冰晶翅膀+虹彩发）
```text
正面: (((masterpiece))), best quality, illustration, (beautiful detailed girl), beautiful detailed glow, detailed ice, beautiful detailed water, (beautiful detailed eyes), expressionless, beautiful detailed white gloves, (floating palaces:1.2), azure hair, disheveled hair, long bangs, hairs between eyes, (skyblue dress), black ribbon, white bowties, midriff, {{{half closed eyes}}}, big forhead, blank stare, flower, large top sleeves, (((ice crystal texture wings))), {{{{{{{{Iridescence and rainbow hair:2.5}}}}}}}}, {{{{{{detailed cute anime face}}}}}}, {{loli}}, {{{{{watercolor_(medium)}}}}, (((masterpiece)))
参数: 默认
```

#### 17. 月亮法（月下巫女）
```text
正面: (watercolor_medium), ((ukiyoe style)), ((((masterpiece)))), (((best quality))), (illustration), (1girl:1.5), (solo:1.5), ((an extremely delicate and beautiful)), ((little girl)), cute, ((hime_cut)), side blunt bangs, (ultramarine hair:1.2), hairs between eyes, ribbons, Bracelet, bare shoulders, ((japanese_clothes)), sakura, ((slit pupils)), ((miko)), (off_shoulder), ace, (Kagura Suzu), sword
参数: Steps 28, DDIM, CFG 11
```

### 三、机械/奇幻系

#### 18. 机凯种（机械少女）
```text
正面: {{masterpiece}}, {flat chest best quality}, {highres}, solo, flat_chest, a girl inside the church with white hair and blue pupil surrounded by {many} glowing {feathers} in cold face, detailed face, night with bright colorful lights with richly layered clouds and clouded moon in the detailed sky, {a lot of glowing particles}, high ponytail, mecha clothes, robot girl, cool movement, sliver bodysuit, {filigree}, delicate and (intricate) hair, ((sliver)) and (broken) body, blue streaked hair, full body, Depth of field, sitting on a {blue star}
参数: cfg12, euler_a, steps 28
```

#### 19. 机娘水（机械水翼）
```text
正面: (masterpiece), best quality, {full body}, ((1 girl)), ((beauty detailed eye)), {mecha, huge_filesize}, (bare shoulders), science fiction, highly detailed, illustration, extremely detailed CG unity wallpaper, submerge, cinematic lighting, dramatic angle, {{beautiful face}}, posing, caustics, fine water surface, Mechanical wing, Metal wings, Mecha wing, {mecha clothes}, robot girl, beautiful detailed face
参数: Steps 38, Euler a, CFG 12
```

#### 20. 龙机法（机甲+龙）
```text
正面: {{master piece}}, best quality, illustration, 1girl, small breast, beatiful detailed eyes, beatiful detailed cyberpunk city, flat_chest, beatiful detailed hair, wavy hair, beatiful detailed steet, mecha clothes, robot girl, cool movement, sliver bodysuit, {filigree}, dargon wings, colorful background, a dragon stands behind the girl, rainy days, {lightning effect}, beatiful detailed sliver dragon arnour, （cold face）
参数: ddim, steps 23, cfg 4.5
```

#### 21. 战姬法（战争少女）
```text
正面: {{{solo}}}, highres, {best quality}, {highly detailed}, beautiful detailed blue eyes, light blush, expressionless, white hair, hair fluttering in the wind, mechanical arm armor, mechanical body armor, clothes, riding motor, {bodysuit, ruins of city in war, fire, burning cars, burning buildings, air force fleet in the sky, dusk, bird see}
参数: Steps 50, Euler a, CFG 5
```

#### 22. 黄金法（熔金流体）
```text
正面: masterpiece, best quality, best quality, Amazing, beautiful detailed eyes, ((1girl)), finely detailed, Depth of field, extremely detailed CG unity 8k wallpaper, full body, (other Minato aqua), (((a girl wears Clothes with a silver texture))), ((Extremely gorgeous metal style)), ((Metal crown with ornate stripes)), ((((Various metals background)))), Sputtered molten iron, (floating hair), ((Hair like melted metal)), (((detailed face))), (((detailed eyes))), (((Clothes made of silver))), (((Clothes with gold lace))), ((full body)), ((((flowing gold and silver)))), (((((everything flowing and melt))))), (((((flowing iron))))), (((((flowing silver))))), ((((lace flowing and melt))))
参数: Steps 30, Euler, CFG 7
```

#### 23. 死灵法（骨架教堂2）
```text
正面: cinematic lighting, ((best quality)), ((single_human_girl)), ((((upper_body)))), ((extremely_detailed_eyes_and_face)), ink, (((bone))), (((ribs))), one girl, a young girl, upper body, rose, black hair, blue eyes, curly hair, greyscale, no shadow, simple background, bright skin, Cherry blossoms
参数: Steps 50, Euler a, CFG 12
```

#### 24. 水晶法（水晶质感）
```text
正面: (((crystals texture Hair))), {{{{{extremely detailed CG}}}}}, {{8k_wallpaper}}, {{{{Crystalline purple gemstone gloves}}}}, ((beautiful detailed Glass hair)), ((Glass shaped texture hand)), ((Crystallize texture body)), Gem body, Hands as clear as jewels, Crystallization of clothes, ((crystals texture skin)), sparkle, lens flare, light leaks, Broken glass, {{{{Detailed Glass shaped clothes}}}}, ((masterpiece)), (((best quality))), ((ultra-detailed)), ((illustration)), ((disheveled hair)), ((frills)), (1 girl), (solo), dynamic angle, big top sleeves, floating, beautiful detailed gemstone sky, gemstone sea, beautiful detailed eyes, overexposure, side blunt bangs, hairs between eyes, ribbons, bowties, buttons, bare shoulders, (((small breast))), pleated skirt, crystals texture flowers, ((Detailed crystallized clothing)), (gemstone of body), solo focus
参数: Steps 30, Euler, CFG 7
```

### 四、人物/风格系

#### 25. 圣光法（天使）
```text
正面: (((masterpiece))), (((best quality))), ((ultra-detailed)), (illustration), (detailed light), ((an extremely delicate and beautiful)), (beautiful detailed eyes), (sunlight), (angel), solo, young girls, dynamic angle, floating, bare_shoulders, looking_at_viewer, wings, arms_up, halo, Floating white silk, (Holy Light), just like silver stars imploding we absorb the light of day
参数: Steps 36, Euler a, CFG 7
```

#### 26. 雷男法（雷电法师）
```text
正面: A man with has short black hair, a round hat, no facial features, a high collar coat, Flashes of lightning from the hands, full body, (((masterpiece))), (((best quality))), ((ultra-detailed)), (illustration), (detailed light), ((Expressionless)), ((an extremely delicate and beautiful)), ((man)), ((lightning in hand)), Lightning surrounds men, (((Lightning chain))), Suspended crystal, with lightning inside the crystal, ((Suspended colorless crystal))
参数: Steps 60, Euler a, CFG 7.5
```

#### 27. 苇名法（月下武士/酒葫芦/樱花）
```text
正面: dramatic_shadow, ray_tracing, ((best quality)), (((beautiful_detailed_dark_midnight_sky))), ((((yellow_full_moon)))), (holding_wine_gourd), (((((surrounded_by_floating_sakura))))), dramatic_angle, (leaning_on_huge_stone), (((bare_shoulder))), ((((very_close_to_viewer)))), (((tispy))), (((sleepy))), ((far_from_viewer)), (((extremely_beautiful_detailed_anime_face_and_eyes))), ((((((1girl)))))), ((((open_hakama)))), ((samurai)), (ink), ((illustration)), depth of field, (((((beautiful_detailed_pampas_grass_field))))), watercolor, ((upper_body)), medium_breast, (bright_eyes), ((masterpiece)), ((messy_white_long_hair))
参数: cfg 6.5, 其余默认
```

#### 28. 自然法（花海水岸）
```text
正面: {{{masterpiece}}}, {{best quality, super fine illustration, beautiful and delicate water, The finest grass}}, ((beautiful eyes)), {very delicate light, perfect and delicate limbs}, {nature, painting, water spray}, {{fine luminescence, very fine 8K CG wallpaper}}, Lavender eyes, pink pupils, whole body, white hair, bright eyes, ((an extremely delicate and beautiful girl)), ((1 girl)), medium bust, dynamic angle, (white dress with gold decoration), (long hair flowing with the wind, beautiful hair ornaments, delicate wet skirt, nsfw, breeze, long bangs between eyes), wrinkled skirt, (staring blankly, lovely big eyes), messy_hair, payot, Lateral braid, (Tulle lace white skirt), Flowers and grass meadow, near the water edge, ((sunset, starry sky in a circle), randomly distributed clouds, (((river))), splashing water, falling petals
参数: 1280×720, cfg4, euler a, steps 30
```

#### 29. 森林法（精灵/阳光森林）
```text
正面: (((masterpiece))), (((best quality))), ((ultra-detailed)), (illustration), ((an extremely delicate and beautiful)), dynamic angle, floating, (beautiful detailed eyes), (detailed light), (1girl), loli, small_breasts, floating_hair, glowing eyes, pointy_ears, white hair, green eyes, halter dress, feather, leaves, nature, (sunlight), river, (forest), (painting), (sketch), (bloom)
参数: step40, scale7
```

#### 30. 蔷薇法（蔷薇少女/血迹）
```text
正面: (((masterpiece))), (((best quality))), ((ultra-detailed)), (illustration), ((an extremely delicate and beautiful)), beautiful detailed eyes, (detailed light), (beautiful deatailed shadow), 1girl, (loli), (small_breasts), floating_hair, glowing eyes, black hair, red eyes, sad, lolita, bare shoulders, white_dress, ((rose)), (vines), (blood), cage, bandage, red rope, ((sketch)), (painting)
参数: Steps 40, Euler a, CFG 5.5
```

#### 31. 泡泡法（泡泡星空少女）
```text
正面: (((masterpiece))), (((best quality))), ((ultra-detailed)), ((illustration)), ((an extremely delicate and beautiful)), dynamic angle, floating, (beautiful detailed eyes), (detailed light), (((ink))), depth of field, ((watercolor)), 1girl, small breasts, red hair, blue eyes, ((veil)), bare shoulders, navel, (starry sky), (desert), (floating sand flow), (((colorful bubble)))
参数: Steps 40, Euler a, CFG 5.5
```

#### 32. 冬雪法（白毛红瞳雪景）
```text
正面: (((masterpiece))), (((best quality))), ((ultra-detailed)), (illustration), beautiful detailed sky, night, stars, (1girl), ((an extremely delicate and beautiful girl)), red eyes, dramatic angle, small breasts, (((full body))), hood, cold face and white shirt, (((long white hair))), (red hair), (red plum blossom), ((winter)), (((snowflakes))), {{{{{{detailed cute anime face}}}}}}, cinmatic lighting, ((red and white flowers)), hairs between eyes, expressionless, young girl, (((Facing the lens))), (starry sky), ((Beautiful face)), ((full body)), (sitting), depth_of_field, ((colorful)), scenery, hair_flower, lantern, christmas, (starfall)
参数: Steps 50, DDIM, CFG 7
```

#### 33. 雪月法（雪月白发女仆）
```text
正面: hiten_1, (((masterpiece))), best quality, illustration, beautiful detailed glow, detailed ice, beautiful detailed water, red moon, snowflake, (beautiful detailed eyes), expressionless, beautiful detailed white gloves, (floating cloud:1.2), azure hair, disheveled hair, long bangs, hairs between eyes, dark dress, (dark magician girl:1.1), black kneehighs, black ribbon, white bowties, midriff, {{{half closed eyes}}}, big forhead, blank stare, flower, large top sleeves
参数: Steps 50, Euler a, CFG 5.5
```

#### 34. 火烧云（火焰战争）
```text
正面: a girl, Phoenix girl, fluffy hair, war, a hell on earth, Beautiful and detailed explosion, Cold machine, Fire in eyes, World War, burning, Metal texture, Exquisite cloth, Metal carving, volume, best quality, normal hands, Metal details, Metal scratch, Metal defects, {{masterpiece}}, best quality, official art, 4k, best quality, extremely detailed CG unity 8k, illustration, highres, masterpiece, contour deepening, Azur Lane, Girls' Front, Magical, Cloud Map Plan, contour deepening, long-focus, Depth of field, a cloudy sky, Black smoke, smoke of gunpowder, long-focus, Mature, resolute eyes, burning, burning sky, burning hair, Burn oneself in flames, fighting, Covered in blood, complex pattern, battleing, Flying flames, Flame whirlpool, Doomsday Scenes, float, Splashing blood, on the battlefield, Bloody scenes, Good looking flame, Exquisite Flame, Exquisite Blood, photorealistic, Watercolor, colourful
参数: Steps 50, Euler a, CFG 5.5
```

#### 35. 彩虹法（虹彩少女）
```text
正面: ((extremely detailed CG)), ((8k_wallpaper)), (((masterpiece))), ((best quality)), watercolor_(medium), ((beautiful detailed starry sky)), cinmatic lighting, loli, princess, very long rainbow hair, side view, looking at viewer, full body, frills, (far from viewer), ((extremely detailed face)), ((an extremely delicate and beautiful girl)), ((extremely detailed cute anime face)), ((extremely detailed eyes)), (((extremely detailed body))), (ultra detailed), illustration, ((bare stomach)), ((bare shoulder)), small breast, ((sideboob)), ((((floating and rainbow hair)))), (((Iridescence and rainbow hair))), (((extremely detailed sailor dress))), ((((Iridescence and rainbow dress)))), (Iridescence and rainbow eyes), beautiful detailed hair, beautiful detailed dress, dramatic angle, expressionless, (big top sleeves), frills, blush, (ahoge)
参数: step28, scale5, k_euler_a, 832x512
```

#### 36. 炼银术（银王座）
```text
正面: (((masterpiece))), best quality, illustration, (beautiful detailed girl), a girl, solo, bare shoulders, flat_chst, diamond and glaring eyes, beautiful detailed cold face, very long blue and sliver hair, floaing black feathers, wavy hair, black and white sleeves, gold and sliver fringes, a (blackhole) behind the girl, a silver triple crown inlaid with obsidian, (sit) on the black ((throne)), (depth) of (field)
参数: naifu 步骤23, 规模4.5, 采样ddim
```

#### 37. 唤龙术（龙女）
```text
正面: ((masterpiece)), (((best quality))), illustration, 1 girl, mature female, small breast, beautiful detailed eyes, long sleeves, hoodie, frills, extremely detailed CG unity 8k wallpaper, Loong, dragon background, loong background, game cg, depth of field, Cape hood
参数: Steps 40, Euler, CFG 7
```

#### 38. 血魔法（血月魔女）
```text
正面: (((masterpiece))), best quality, illustration, beautiful detailed glow, (beautiful detailed eyes), (dark magician girl:1.1), big forhead, flower, large top sleeves, Floating ashes, Beautiful and detailed explosion, red moon, fire, Fire cloud, Wings on fire, a cloudy sky, smoke of gunpowder, burning, black dress, (beautiful detailed eyes), expressionless, beautiful detailed white gloves, Dove of peace, (floating cloud:1.2), azure hair, disheveled hair, long bangs, hairs between eyes, black kneehighs, black ribbon, white bowties, midriff, {{{half closed eyes}}}
参数: Steps 50, Euler a, CFG 5.5
```

#### 39. 坠落法（天气之子坠落）
```text
正面: ((masterpiece)), (((best quality))), ((ultra-detailed)), ((((full body)))), (unhelpless), tear, crying, (((((falling from the sky))))), ((Weathering With You)), (((full body))), (illustration), (1 girl), ((falling)), tear, ((face towards the sky)), (hair flows upwards), ((illustration)), ((disheveled hair)), anime screeshot, ((frills)), (1 girl), big top sleeves, floating, beautiful detailed isky, beautiful detailed eyes, overexposure, expressionless, side blunt bangs, hairs between eyes, ribbons, bowties, buttons, bare shoulders, (((small breast))), detailed clothes, blank stare
参数: PLMS, steps 150, cfg 8
```

#### 40. 秘境法（仙境城堡）
```text
正面: (extremely detailed CG unity 8k wallpaper), (((masterpiece))), (((best quality))), ((ultra-detailed)), (best illustration), (best shadow), ((an extremely delicate and beautiful)), dynamic angle, floating, The detailed castle, (((the best building))), mist encircles the mountains, fairyland, dynamic angle, classic, (detailed light), feather, nature, (sunlight), river, forest, flowers, beautiful and delicate water, (painting), (sketch), (bloom), (shine)
参数: CFG 6, Euler
```

#### 41. 摄影法（极致写真）
```text
正面: extremely detailed CG unity 8k wallpaper, best quality, noon, beautiful detailed water, long black hair, beautiful detailed girl, serafuku, view straight on, eyeball, hair flower, close up
参数: 26step, cfg 6
```

#### 42. 摩登法（复古蒸汽艺术）
```text
正面: {{{{retro artstyle}}}}, {{masterpiece}}, best quality, illustration, 1 girl, mature female, small breast, beautiful detailed eyes, long sleeves, hoodie, frills, no shadow, simple background, bright skin, 1980s (style)
参数: Steps 30, Euler a, CFG 6.5
```

#### 43. 学院法（破碎教室/机械少女）
```text
正面: (((masterpiece))), best quality, illustration, (((1girl))), ((cute anime face)), (beautiful detailed girl), expressionless, cold attitude, red pupils, short hair, white hair, (((beautiful detailed eyes))), jacket, cracked floor, damaged classroom, Tables and chairs in disarray, The residual eaves DuanBi, beautiful sky, cumulus, mouldy, floating, wind, Dead end machine, (broken robot), (Mechanical girl)
参数: Steps 45, Euler a, CFG 5.5
```

#### 44. 浮世绘
```text
正面: (watercolor_medium), ((ukiyoe style)), ((((masterpiece)))), (((best quality))), (illustration), (1girl:1.5), (solo:1.5), ((an extremely delicate and beautiful)), ((little girl)), cute, ((hime_cut)), side blunt bangs, (ultramarine hair:1.2), hairs between eyes, ribbons, Bracelet, bare shoulders, ((japanese_clothes)), sakura, ((slit pupils)), ((miko)), (off_shoulder), ace, (Kagura Suzu), sword
参数: Steps 28, DDIM, CFG 11
```

#### 45. 绚丽术（水彩精绘）
```text
正面: (watercolor_medium), ((ukiyoe style)), ((((masterpiece)))), (((best quality))), (illustration), (1girl:1.5), (solo:1.5), ((an extremely delicate and beautiful)), ((little girl)), cute, ((hime_cut)), side blunt bangs, (ultramarine hair:1.2), hairs between eyes, ribbons, Bracelet, bare shoulders, ((japanese_clothes)), sakura, ((slit pupils)), ((miko)), (off_shoulder), ace, (Kagura Suzu), sword
参数: Steps 28, DDIM, CFG 11
```

#### 46. 星霞海-2（白发星海）
```text
正面: {best quality}, {{masterpiece}}, {highres}, extremely detailed CG, extremely detailed 8K wallpaper, extremely detailed character, {an extremely delicate and beautiful}, portrait, illustration, solo focus, straight-on, dramatic angle, depthoffield, {{cinematiclighting}}, outdoors, {{{character({{{a girl}}}, solo, loli, {{{{full body}}}}, standing, expressionless, [[[light smile]]], cute, beautiful detailed eyes, blue eyes, [long legs], {very_long_hair}, blonde hair, wavy_hair, [shiny hair], {{Gothic_Lolita}}, blue_white skirt, {{short skirt}}, black_Headdress, bowknot, {{{hair ornament}}}, [hair flower], stocking, [[Garter]], Lace, cross-laced footwear, ribbon-trimmed sleeves)}}}, [background(building architecture, {{gothic architecture}}, starry sky, outdoors, church, {castle}, [[fantasy]])]
参数: Steps 70, DDIM, CFG 12
```

### 五、深渊/暗黑系

#### 47. 暗锁法（深海/锁链/克苏鲁）
```text
正面: {{{{{masterpiece}}}}}, {{{{best quality}}}}, illustration, {{beautiful detailed girl}}, (((beautiful detailed lighting))), beautiful detailed eyes, (((((disheveled hair))))), {{{beautiful detailed dress}}}, midriff, {{female girl}}, ((off-shoulder jacket)), sailor dress, ((((darkside)))), {{{{{bust}}}}, {{{{{watercolor_(medium)}}}}}, wholeblack bloomer, wet clothes, wet skin, flowers, hollow eyes, hollow night, hollow knight, {{{{{chain}}}}}, dark soul, abyssal ship, deep dark, darkness, {{{small breast}}}, death garden, {{{{emotionless eyes}}}}, {{{cthulhu}}}, ((((extremely detailed dark clouds)))), {{{{{extremely detailed CG unity 8k wallpaper}}}}}, (((extremely detailed face))), (((jitome))), ((((dark_persona)))), {{ruins}}, {{{{{{beautiful deatailed shadow}}}}}}, {{{{chain storm}}}}}, {{{{chain ring}}}}
参数: step24, scale4.5, k_euler
```

#### 48. 望穿水（浮水魔法）
```text
正面: dream, (((extremely detailed CG unity 8k wallpaper))), {painting}, (((ink))), amazing, Depth of field, {{best quality}}, {{masterpiece}}, highres, dynamic angle, (illustration), cinematic lighting, {1girl}, ((wavy silver hair)), ((loli)), ((extremely_detailed_eyes_and_face)), (detailed flooding bare feet:1.5), translucent pink skirt, gemological hair, french braid, pointy ears, looking at viewer, {{translucent fluttering skirt}}, yellow hairpin, {{white dress with pink lace with yellow decoration}}, sleeves past wrists, ((sleeves past fingers)), walking_motion, strapless dress, ocean waves, wind, (((glistening light of waves))), {detailed sunset glow}, (floating flow), ((coral)), (Luminous), coast, {floating colorful bubbles}, beautiful detailed sky, {fluorescence}, detailed shadow, (conch), beautiful detailed water, drenched, starfish, meteor, rainbow, (seabirds), {glinting stars}, (glowworm), (splash), detailed cloud, shell, {fireworks}
参数: 512x768, DDIM, step 45, cfg 10, NAIFU
```

#### 49. 白骨法-2（骷髅裙）
```text
正面: cinematic lighting, ((best quality)), ((single_human_girl)), ((((upper_body)))), ((extremely_detailed_eyes_and_face)), ((church)), ((annoyed)), ((ink)), ((illustration)), depth of field, ((frown)), ((expression)), ((red_eyes)), ((((white_hair)))), ((extremely detailed)), ((watercolor)), ((anime face)), (skull_on_dress), (((yokozuwari))), ((detailed_skeleton_church)), (((beautiful_detailed_black_gothic_Empire_Waist_Dress))), (((dramatic_angle))), medium_breast, (8k_wallpaper), ((bright_eyes)), (looking_at_viewers), ((close_to_viewers)), ((masterpiece)), (((((messy_long_hair))))), ((((1girl)))), lens_flare, light_leaks
参数: CFG 6.5, 其他随意
```

#### 50. 森火法-2（火蝶教堂）
```text
正面: ((((ink)))), ((watercolor)), ((best quality)), (spirit), ((illustration)), (((1 girl))), (beautiful detailed eyes), world masterpiece theater, depth of field, (Burning forest), spark, anime face, Black gauze skirt, (red_hair), blue_eyes, focus_on_face, medium_breasts, (((((messy_long_hair))))), Bare shoulder, very_close_to_viewers, veil, light_leaks, Burning sky, navel, ((bustier)), flame, Red Gem Necklace, Rainbow in the sky, Flames burning around, A burning church, (((Fire butterflys))), (Flying sparks)
参数: Steps 30, Euler a, CFG 5.5
```

#### 51. 血魔法-2（血月魔女2）
```text
正面: (((masterpiece))), best quality, illustration, beautiful detailed glow, detailed ice, beautiful detailed water, red moon, (magic circle:1.2), (beautiful detailed eyes), expressionless, beautiful detailed white gloves, own hands clasped, (floating palaces:1.1), azure hair, disheveled hair, long bangs, hairs between eyes, dark dress, (dark magician girl:1.1), black kneehighs, black ribbon, white bowties, midriff, {{{half closed eyes}}}, big forhead, blank stare, flower, large top sleeves
参数: Steps 50, Euler a, CFG 6
```

#### 52. 龙骑士
```text
正面: (((masterpiece))), (((best quality))), illustration, 1 girl, mature female, small breast, beautiful detailed eyes, long sleeves, hoodie, frills, extremely detailed CG unity 8k wallpaper, Loong, dragon background, loong background, game cg, depth of field, Cape hood
参数: Steps 40, Euler, CFG 7
```

### 六、风景/背景系

#### 53. 城堡法（雾中山城）
```text
正面: (extremely detailed CG unity 8k wallpaper), (((masterpiece))), (((best quality))), ((ultra-detailed)), (best illustration), (best shadow), ((an extremely delicate and beautiful)), dynamic angle, floating, The detailed castle, (((the best building))), mist encircles the mountains, fairyland, dynamic angle, classic, (detailed light), feather, nature, (sunlight), river, forest, flowers, beautiful and delicate water, (painting), (sketch), (bloom), (shine)
参数: CFG 6, Euler
```

#### 54. 黄昏法（夕阳荒野）
```text
正面: cinematic lighting, ((best quality)), ((extremely_detailed_eyes_and_face)), ((((ink)))), ((illustration)), depth of field, ((extremely detailed)), ((watercolor)), ((anime face)), (((dramatic_angle))), medium_breast, (8k_wallpaper), ((bright_eyes)), (looking_at_viewers), (an detailed organdie dress), (((((very_close_to_viewers))))), ((sleepy)), ((masterpiece)), ((((((surrounded_by_heavy_floating_sand_flow_and_floating_sharp_stones)))))), (((((messy_long_hair))))), ((((veil)))), focus_on_face, (upper_body), (bare_shoulder), ((((1girl)))), (golden_bracelet), (long yarn), ((sunset)), lens_flare, light_leaks, ((detailed_beautiful_desert_with_cactus)), medium_wind, (detailed_beautiful_sky)
参数: CFG 5.5, euler_a, step 30
```

#### 55. 星霞海-3（星辰公主）
```text
正面: (extremely detailed CG unity 8k wallpaper), (((masterpiece))), (((best quality))), ((ultra-detailed)), (best illustration), (best shadow), ((an extremely delicate and beautiful)), dynamic angle, floating, solo, ((1girl)), {long wavy curly hair}, expressionless, ((white idol dress)), anglesailor dress, (detailed wet clothes), silk shawl, bikini, underboob, frills, cute anime face, blush, (beautiful detailed eyes), (detailed light), feather, nature, (sunlight), river, (forest), (((floating palace))), beautiful and delicate water, (painting), (sketch), (bloom), (shine)
参数: Steps 40-50, Euler, CFG 4-7
```

### 七、特殊/未分类

#### 56. 星冰乐-2（冰火魔女）
```text
正面: (((masterpiece))), best quality, illustration, (beautiful detailed girl), beautiful detailed glow, detailed ice, beautiful detailed water, red moon, (magic circle:1.2), (beautiful detailed eyes), expressionless, beautiful detailed white gloves, own hands clasped, (floating palaces:1.1), azure hair, disheveled hair, long bangs, hairs between eyes, dark dress, (dark magician girl:1.1), black kneehighs, black ribbon, white bowties, midriff, {{{half closed eyes}}}, big forhead, blank stare, flower, large top sleeves, (((ice crystal texture wings))), (((ice and fire melt)))
参数: Steps 39, Euler, CFG 4.5, 512x1024
```

#### 57. 星源法-2（星海女神）
```text
正面: masterpiece, {{{best quality}}}, (illustration), {{{extremely detailed CG unity 8k wallpaper}}}, game_cg, (({{1girl}})), {solo}, (beautiful detailed eyes), ((shine eyes)), goddess, fluffy hair, messy_hair, ribbons, hair_bow, {flowing hair}, (glossy hair), (Silky hair), ((white stockings)), (((gorgeous crystal armor))), cold smile, stare, cape, (((crystal wings))), ((grand feathers)), ((altocumulus)), (clear_sky), (snow mountain), ((flowery flowers)), {(flowery bubbles)}, {{cloud map plane}}, ({(crystal)}), crystal poppies, ({lacy}), ({{misty}}), (posing sketch), (Brilliant light), cinematic lighting, ((thick_coating)), (glass tint), (watercolor), (Ambient light), long_focus, (Colorful blisters), ukiyoe style
参数: Steps 45, Euler, CFG 6.5
```

#### 58. 刻刻帝（时钟/血月）
```text
正面: (((masterpiece))), best quality, illustration, (beautiful detailed girl), beautiful detailed glow, detailed ice, beautiful detailed water, red moon, snowflake, (beautiful detailed eyes), expressionless, beautiful detailed white gloves, (floating cloud:1.2), azure hair, disheveled hair, long bangs, hairs between eyes, dark dress, (dark magician girl:1.1), black kneehighs, black ribbon, white bowties, midriff, {{{half closed eyes}}}, big forhead, blank stare, flower, large top sleeves, (((clock))), (((red))), (((blood))), finely detail, Depth of field, Blood drop, Blood fog
参数: Steps 30, Euler, CFG 7
```

## 第一点五卷补充魔法（40+ 配方）

> 来源：《元素法典第一点五卷》（https://docs.qq.com/doc/DWGh4QnZBVlJYRkly）。以下为文末**文本形式**的完整配方，正文区魔法（万物熔炉、暗鸦法、花火法、星之彩、沉入星海、百溺法、辉煌阳光法、星鬓法、森罗法、星天使、黄金律、机凯姬改、人鱼法、末日、碎梦、幻碎梦、血法改、留影术、西幻术、星语术、金石法、飘花法、冰霜龙息）的 tag 为图片不可提取，仅保留名称作索引。

### 1.5-1 银河铁道（蒸汽火车/星空/侦探帽）
```text
正面: (solo), (((masterpiece))), (((best quality))), (bust), Amazing, beautiful detailed, extremely detailed wallpaper, (extremely detailed CG unity 8k wallpaper), (1girl), (loli), (super fine illustrations), (cute anime face), (Depth of field), (the galaxy), (blue jewel eyes), ((beautiful detailed face and eyes)), sparkling anime eyes, floating hair, gradient hair and eyes, (beautiful detailed Chestnut hair), Starry sky adorns hair, (night), (((night sky))), (((beautiful detailed night sky))), moon, (beautiful detailed crystals stars), (a great quantity of stars), (blighting stars), (full body), moonlight, bare shoulders, medium_breast, arms behind back, thigh, (leg loops), Sleeves covering hand, ((steam locomotive on water)), ((railway steam engine on water)), ((beautiful detailed steam locomotive)), (on beautiful detailed water), expressionless, blank stare, (detective), (Newsboy cap), (hair_ornament), (white shirt), (small dress), (browu coat), (brown frilled dress)
参数: CFG 8, STEP 40, 分辨率 1408*832, 模型 e6e8e1fc
```

### 1.5-2 银枪天马（黑暗骑士/圣光）
```text
正面: ((best quality)), ((masterpiece)), ((ultra-detailed)), extremely detailed CG unity 8k wallpaper, (illustration), ((detailed light)), ((angel wings)), solo, (an extremely delicate and beautiful), halo, horseback riding, knight, cavalry, war, fire, Knight of Darkness, Dark Souls, ((With a medieval helmet)), Long spear, holy-light
参数: Steps 50, Scale 12
```

### 1.5-3 机娘废墟（机械少女/战场）
```text
正面: (1robot girl), long white hair, solo, beautiful golden glowing eyes, (mechanical wing), disgust, ruins, debris, best quality, masterpiece, ultra-detailed, battlefield, fire, ((extremely_detailed_eyes_and_face)), cinematic lighting, finely detail, fighting_stance
负向: lowres, bad anatomy, bad hands, text, error, missing fngers, extra digt, fewer digits, cropped, wort quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet, poorly drawn asymmetric eyes, cropped, poorly drawn hands, poorly drawn face, mutation, deformed, worst quality, multiple breasts, (mutated hands and fingers:1.5), (long body :1.3), (mutation, poorly drawn :1.2), blurred
参数: Steps 40, DPM2 A, CFG 11, 896x704, Clip skip 2
```

### 1.5-4 黑鸦魔女（黑翼/黑雾/红月）
```text
正面: (((masterpiece))), best quality, extremely detailed CG unity 8k, illustration, contour deepening beautiful detailed glow, (beautiful detailed eyes), (1 girl:1.1), ((Bana)), large top sleeves, Floating black ashes, Beautiful and detailed black, red moon, ((The black clouds)), (black Wings), a black cloudy sky, burning, black dress, (beautiful detailed eyes), black expressionless, beautiful detailed white gloves, (crow), bat, (floating black cloud:1.5), white and black hair, disheveled hair, long bangs, hairs between eyes, black knee-highs, black ribbon, white bowties, midriff, {{{half closed eyes}}}, ((Black fog)), Red eyes, (black smoke), complex pattern, ((Black feathers floating in the air)), (((arms behind back)))
负向: (((ugly))), (((duplicate))), ((morbid)), ((mutilated)), (((tranny))), mutated hands, (((poorly drawn hands))), blurry, ((bad anatomy)), (((bad proportions))), extra limbs, cloned face, (((disfigured))), (((more than 2 nipples))), ((((missing arms)))), (((extra legs))), mutated hands, (((((fused fingers))))), (((((too many fingers))))), (((unclear eyes))), lowers, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet, text font ui, malformed hands, long neck, missing limb, (mutated hand and finger: 1.5), (long body: 1.3), (mutation poorly drawn: 1.2), disfigured, malformed mutated, multiple breasts, futa, yaoi, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), missing fingers, extra digit, fewer digits, bad feet
参数: Steps 50, Euler a, CFG 4.5, 1024x768, 模型 e6e8e1fc, Clip skip 2
```

### 1.5-5 阴阳熔炉（黑白道袍/流动墨色）
```text
正面: masterpiece, (best quality), Amazing, beautiful detailed eyes, ((((1girl)))), finely detailed, Depth of field, extremely detailed CG unity 8k wallpaper, (((((full body))))), (((cute animal face))), (((a girl wears Clothes Black and white Taoist robes))), ((Extremely gorgeous magic style)), ((((gold and silver lace)))), (((flowing lace))), (((flowing ((black)) and white background))), (((((gorgeous detailed eyes))))), (((((((gorgeous detail face))))))), ((floating hair)), (((Pick and dye black hair in white hair))), (((flowing transparent black))), (((flowing transparent white))), (((((ink))))), ((((small breast)))), (((extremely detailed gorgeous tiara))), (((black and white hair))), ((black hair stick)), ((white hair ornament)), ((gold gorgeous necklace)), ((flowing hair)), (((The picture fills the canvas))), ((The character is in the center of the frame)), (((flowing))), ((bright pupils)), ((((melt)))), (((((black and white melt)))))
负向: (((ugly))), (((duplicate))), ((morbid)), ((mutilated)), (((tranny))), mutated hands, (((poorly drawn hands))), blurry, ((bad anatomy)), (((bad proportions))), extra limbs, cloned face, (((disfigured))), (((more than 2 nipples))), ((((missing arms)))), (((extra legs))), mutated hands, (((((fused fingers))))), (((((too many fingers))))), (((unclear eyes))), lowers, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet, text font ui, malformed hands, long neck, missing limb, (mutated hand and finger: 1.5), (long body: 1.3), (mutation poorly drawn: 1.2), disfigured, malformed mutated, multiple breasts, futa, yaoi
参数: Steps 39, Euler, CFG 7
```

### 1.5-6 花火法（烟花/夏夜/浴衣）
```text
正面: ((extremely detailed CG unity 8k wallpaper)), (masterpiece), (best quality), (ultra-detailed), (best illustration), (best shadow), (an extremely delicate and beautiful), ((((1girl)))), dynamic angle, floating, finely detail, (bloom), (shine), glinting stars, ((((best detailed fireworks)))), ((((depth of field)))), (((hanabi))), Beautiful detailed girl, (((backlight))), extremely delicate and beautiful girls, ((summer long skirt)), (((solo))), best detailed hair, ((beautiful detailed water)), night sky, (((small breast))), beautiful detailed sky, beautiful detailed eyes, (((arms behind back))), long hair, (((dynamic angle))), long skirt
负向: Inverted mountain, low-quality, flowers, grass, distorted mountain, distorted light, low-quality light, low-quality mountain, low-quality illustration, low-quality background, nsfw, polar lowres, bad anatomy, bad hands, bad body, bad proportions, gross proportions, text, error, missing fingers, missing arms, missing legs, extra digit
参数: Steps 50, Euler a, CFG 5.5, 1024x768, 模型 e6e8e1fc, Clip skip 2
```

### 1.5-7 星眸少女（星星眼/泡泡/银河）
```text
正面: ((best quality)), ((masterpiece)), ((ultra-detailed)), (illustration), (detailed light), (an extremely delicate and beautiful), a girl, cute face, upper body, two legs, long dress, (beautiful detailed eyes), stars in the eyes, messy floating hair, colored inner hair, Starry sky adorns hair, (lots_of_big_colorful_Bubble), [pearl], [Galaxy], depth of field
负向: lowres, bad anatomy, text, bad face, error, extra digit, fewer digits, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, {blurry:1.1}, missing arms, missing legs, more than two legs, [[[small bubble]]]
参数: Steps 25, DDIM, CFG 5, 1024x640, 模型 e6e8e1fc, Clip skip 2
```

### 1.5-8 星眸少女-简版（星星眼核心）
```text
正面: {{best quality}}, {{masterpiece}}, {{ultra-detailed}}, {illustration}, {detailed light}, {an extremely delicate and beautiful}, a girl, {beautiful detailed eyes}, stars in the eyes, messy floating hair, colored inner hair, Starry sky adorns hair, depth of field
负向: lowres, bad anatomy, text, error, extra digit, fewer digits, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, {blurry:1.1}, missing arms
参数: Steps 25, DDIM, CFG 5, 1024x640, 模型 e6e8e1fc, Clip skip 2
```

### 1.5-9 百溺法（血水/湖面漂浮/漩涡）
```text
正面: (watercolor), ((extremely detailed CG unity 8k wallpaper)), (game cg), ((masterpiece)), ((best quality)), ((ultra-detailed)), (1 girl), (solo), (best illustration), (extremely detailed illustration), ((disheveled hair)), ((beautiful detailed lighting)), (from above), ((an extremely delicate and beautiful)), cinematic lighting, dynamic angle, detailed wet clothes, blank stare, overexplosure, floating, (beautiful detailed eyes), side blunt bangs, small breasts, black long straight, red eyes, aqua eyes, gradient eyes, black hair, very long hair, blunt bangs, ((blood)), white dress, frills, bowties, ((expressionless)), extremely beautiful detailed water, ((lying on the lake)), ((hairs curling in the water)), (bloodred water:1.5), (red background:1.3), swirl
负向: long body, long face, lowres, bad anatomy, bad hands, missing fingers, pubic hair, extra digit, fewer digits, cropped, worst quality, low quality, extra legs, extra arms, fused arms, fused legs, extra feet, fused feet, abnormal legs, abnormal shoulders, poorly drawn shoulders, blurry, misplaced arms, misplaced legs, misplaced hands, abnormal hands, watermark, username, signature, jpeg artifacts, multiple heads, abnormal face, twisted head
参数: Euler a, CFG 4.5-5.5, 768x512, Clip skip 2
```

### 1.5-10 星鬓法（星辰长发/星海）
```text
正面: masterpiece, best quality, illustration, stars in the eyes, dishevelled hair, Starry sky adorns hair, 1 girl, sparkling anime eyes, beautiful detailed eyes, beautiful detailed stars, blighting stars, emerging dark purple across with white hair, multicolored hair, beautiful detailed eyes, beautiful detailed sky, beautiful detailed water, cinematic lighting, dramatic angle
负向: lowres, bad anatomy, bad legs, bad hands, text, error, missing fngers, extra digt, fewer digits, cropped, wort quality, low quality, normal quality, jpeg, artifacts, signature, watermark, username, blurry, bad feet, artist name, bad anatomy, bad hands, bad body, bad proportions, worst quality, low quality, optical_illusion
参数: Steps 30, CFG 6, Euler a
```

### 1.5-11 森罗法（草原/栅栏/阳光少女）
```text
正面: {masterpiece}, {best quality}, {1girl}, Amazing, beautiful detailed eyes, solo, finely detail, Depth of field, extremely detailed CG, original, extremely detailed wallpaper, {{highly detailed skin}}, {{messy_hair}}, {small_breasts}, {{longuette}, {grassland}, {yellow eyes}, full body, incredibly_absurdres, {gold hair}, lace, floating hair, Large number of environments, the medieval, grace, A girl leaned her hands against the fence, ultra-detailed, illustration, birds, Altocumulus, 8kwallpaper, hair_hoop, long_hair, gem necklace, hair_ornament, prospect, water eyes, wind, breeze, god ray, lawn, Mountains and lakes in the distance, The skirt sways with the wind, The sun shines through the trees, A vast expanse of grassland, fence, Blue sky, bloom, smile, glow, The grass sways in the wind
负向: {lowres}, {{{{{{{{{{{blurry}}}}}}}}}}}, {{{{{{{{{bad hands}}}}}}}}}, {{{{{missing fingers}}}}, {{{{{{{{{{{{{extra digit}}}}}}}}}}}}}, fewer digits, small hands, error, multiple limbs, bad feet, cropped, worst quality, low quality, normal quality, jpeg artifacts, bad anatomy, long nails, {{{{interlocked fingers}}}}, milf, ugly, duplicate, morbid, mutilated, tranny, trans, trannsexual, mutation, deformed, long neck, bad anatomy, bad proportions, extra arms, extra legs, disfigured, more than 2 nipples, malformed, mutated, hermaphrodite, out of frame, extra limbs, missing arms, missing legs, poorly drawn hands, poorty drawn face, mutation, poorly drawn, long body, multiple breasts, cloned face, gross proportions, mutated hands, bad hands, bad feet, long neck, missing limb, malformed limbs, malformed hands, fused fingers, too many fingers, extra fingers, missing fingers, extra digit, fewer digits, mutated hands and fingers, lowres, text, error, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, text font ui, futa, yaoi
参数: CFG 7, Euler, Step40
```

### 1.5-12 飘花法（花丛/露肩/古典边框）
```text
正面: super fine illustration, masterpiece, best quality, {beautiful detailed eyes}, 1girl, finely detail, Depth of field, 4k wallpaper, bluesky, cumulus, wind, insanely detailed frills, extremely detailed lace, BLUE SKY, very long hair, Slightly open mouth, high ponytail, silver hair, small Breasts, cumulonimbus capillatus, slender waist, There are many scattered luminous petals, Hidden in the light yellow flowers, Depth of field, She bowed her head in frustration, Many flying drops of water, Upper body exposed, Many scattered leaves, branch, angle, contour deepening, cinematic angle, {{{Classic decorative border}}}
负向: 不   需   要
参数: Steps 50, DDIM, scale 8, 512x1024 / 1024x1024
```

### 1.5-13 圣光法-改（天使/光翼/白纱）
```text
正面: {{best quality}}, {{masterpiece}}, {{ultra-detailed}}, {illustration}, {detailed light}, {an extremely delicate and beautiful}, {beautiful detailed eyes}, {sunlight}, {{extremely light}}, {{extremely clothes}}, {{{Holy Light}}}, dynamic angle, a girl, {{angel}}, solo, {{{loli}}}, Light particle, very_long_hair, white_hair, yellow_eyes, {{glowing eyes}}, {{{expressionless}}}, [[light_smile]], [[[[white Tulle skirt]]]], {white silk}, looking_at_viewer, {{{{angel_wings}}}}, {{large_wings}}, multiple_wings, {angel_halo}, [[[starry sky]]], {{dusk_sky}}, {{Floating light spot}}, {{Lots of feathers}}
负向: lowres, bad anatomy, text, error, extra digit, fewer digits, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, missing arms, big breasts, head_wings, dutch angle, furrowed brow raised eyebrows, looking away, thin, petite, Skirt lift, {{smile}}
参数: Steps 42, Euler, CFG 7, 1024x576, 模型 e6e8e1fc, Clip skip 2
```

### 1.5-14 黄金律（金发金瞳金殿）
```text
正面: {{masterpiece}}, best quality, Amazing, {beautiful detailed eyes}, {1girl}, extremely detailed CG unity 8k wallpaper, highly detailed, official_art, highres, original, blonde hair, yellow eyes, white skin, slim legs, mature female, sunrise, golden sky, magnificent architecture, beautiful detailed sky, overexposure, detailed background, delicate gold metal decorations
负向: bad feet_hand_finger_leg_eye, missing fingers, worst low normal quality, bad face, blurry:1.1, Asymmetrical eyes, Simple background, mutation, poorly drawn, huge breasts, huge haunch, huge thighs, more than 2 nipples, huge calf, bad anatomy, liquid body, disfigured, malformed, mutated, anatomical nonsense, text font ui, error, malformed hands, long neck, blurred, lowers, lowres, bad proportions, bad shadow, uncoordinated body, unnatural body, text, ui, error, cropped, watermark, username, blurry, JPEG artifacts, signature, 3D, bad hairs, poorly drawn hairs, fused hairs, big muscles, ugly, bad face, fused face, poorly drawn face, cloned face, big face, long face, bad eyes, fused eyes poorly drawn eyes, extra eyes, malformed limbs
参数: Steps 51, Euler a, CFG 6, 1024x1024, 模型 925997e9
```

### 1.5-15 机凯姬改（紫发机械义肢）
```text
正面: masterpiece, best quality, illustration, beautiful detailed eyes, colorful background, mechanical prosthesis, mecha coverage, emerging dark purple across with white hair, pig tails, disheveled hair, fluorescent purple, cool movement, rose red eyes, beatiful detailed cyberpunk city, multicolored hair, beautiful detailed glow, 1 girl, expressionless, cold expression, insanity, long bangs, long hair, lace, dynamic composition, motion, ultra-detailed, incredibly detailed, a lot of details, amazing fine details and brush strokes, smooth, hd semirealistic anime cg concept art digital painting
负向: lowres, bad anatomy, bad legs, bad hands, text, error, missing fngers, extra digt, fewer digits, cropped, wort quality, low quality, normal quality, jpeg, artifacts, signature, watermark, username, blurry, bad feet, artist name, bad anatomy, bad hands, bad body, bad proportions, worst quality, low quality, optical_illusion
参数: Steps 25, CFG 4, euler a
```

### 1.5-16 人鱼法（美人鱼/鱼尾）
```text
正面: {long hair}, {revealing dress}, {elbow gloves}, {{{{beautiful mermaid}}}}, {smirk}, {nose blush}, stretch, Bare arms, Bare navel, (incredibly_absurdres), best quality, beautiful detailed eyes, blue_hair, (highly detailed beautiful fishtail:1.6), (((human hands))), (((masterpiece))), (blue_eyes), ((medium_breasts)), (the lower body is a fish:1.9) AND (no human thigh:1.2), seaweed, (full body), (white seashell), (curved and slender fish tail), (the lower body is bare:1.1), {beautiful tailfin}, ((underwater)), (illustration), detailed water, ((a extremely delicate and beautiful girl)), (underwater forest), ((sunlight)), ((fishes)), (floating), watercolor_(medium), ((an extremely delicate and beautiful)), ((coral)), floating hair, glowing eyes, (splash), (detailed glow), ((Tyndall effect)), (landscape), hair_ornament, (small whirlpool), ((The sensation of water flowing)), (detailed scales on a mermaid)
负向: lowres, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, (human thighs:1.5), hips, foot, the hand becomes a fishtail, thigh_gap, thighs, the lower body is human, (two legs:1.5), multiple breasts, (mutated hands and fingers:1.5), (long body :1.3), (mutation, poorly drawn :1.2), bad shadow, ugly, (extra legs:1.5), (too long tail:1.5), one hand with more than 5 fingers, one hand with less than 5 fingers, one hand with more than 5 digit, one hand with less than 5 digit
参数: Steps 80, Euler a, CFG 6
```

### 1.5-17 末日（血樱/屋顶/血雨）
```text
正面: full body, Blood Mist, background_Urban rooftop, 1 girl, despair, blood sakura, ((masterpiece)), (((best quality))), ((ultra-detailed)), ((illustration)), ((disheveled hair)), Blood Cherry Blossom, torn clothes, crying with eyes open, solo, Blood Rain, bandages, Gunpowder smoke, beautiful deatailed shadow, Splashing blood, dust, tyndall effect
负向: lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, missing fingers, bad hands, missing arms, long neck, Humpbacked
参数: Step50, CFG 14, 1408x960, 模型 e6e8e1fc, Eta 0.67, Clip skip 2
```

### 1.5-18 碎梦（机甲少女/太空港）
```text
正面: (masterpiece), black hair, red eyes, 1girl, solo, ((delicate face)), ((an extremely delicate and beautiful)), strange, Space opera, Space port, robot arm, elbow_gloves, night, glisten, stare, cyberpunk, ((((citylight)))), ((masterpiece)), (((best quality))), (beautiful detailed eyes), ((ultra-detailed)), ((illustration)), ((disheveled hair)), science fiction, bodysuit, Mechanical armor headdress, (bare shoulders)
负向: lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, missing fingers, bad hands, missing arms, long neck, Humpbacked, long neck
参数: Steps 48, LMS Karras, CFG 15, 1152x640, 模型 e6e8e1fc, Clip skip 2
```

### 1.5-19 幻碎梦（彩虹/玻璃/亚特兰蒂斯）
```text
正面: 8k Wallpaper, grand, (((masterpiece))), (((best quality))), ((ultra-detailed)), (illustration), ((an extremely delicate and beautiful)), dynamic angle, rainbow hair, detailed cute anime face, ((loli)), (((masterpiece))), an extremely delicate and beautiful girl, flower, cry, water, corrugated, flowers tire, broken glass, (broken screen), atlantis, transparent glass
负向: lowres, bad anatomy, bad hands, text, error, missing fingers, extra digt, fewer digits, cropped, wort quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet, nsfw, Deformed body, spectacles, Deformed face, blue face
参数: Steps 50, Euler, CFG 12, 1024x512, 模型 e6e8e1fc, Clip skip 2
```

### 1.5-20 血法改（血刀红发少女）
```text
正面: ((solo)), best quality, Amazing, 1girl, extremely detailed CG unity 8k wallpaper, masterpiece, (loli), (white hair), (((red streaked hair))), red eyes, (((full body))), (red hair), (((((Hold a red sword))))), (angry face), (beautiful detailed eyes), ((Blood drop)), ((Blood fog)), light shafts, soft focus, character focus, disheveled hair, long bangs, hairs between eyes, looking at viewer, lowing hair, ((Splashing blood)), Long hair, ((Bloodstain)), Fighting stance, {{{{{watercolor_(medium)}}}}, (((masterpiece))), ((white clock)), ((ultra-detailed)), ((Covered in blood)), flowing hair, Exquisite Flame, {{{{{{extremely beautiful detailed anime face}}}}}}, dynamic angle, floating, (shine), extremely delicate and beautiful girls, bright skin, (best illustration), (best shadow), finely detail, Depth of field (bloom), (painting), {very delicate light, perfect and delicate limbs}, beautiful detailed dress, Flying red petals, Holy lighting
负向: (mutated hands and fingers:1.5), (long body :1.3), (mutation, poorly drawn :1.2), liquid body, text font ui, long neck, uncoordinated body, fused ears, huge breasts, ((((ugly))))
参数: Steps 60, Euler a, CFG 7, 1600x768
```

### 1.5-21 留影术（黑白漫画/修道士）
```text
正面: 1male, solo, (Masterpiece), ((best quality)), beautifully painted, highly detailed, detailed clothes, detailed face, detailed eyes, {{intricate detail}}, detailed background, dramatic shadows, black and white, monochrome, {{comic}}, cross necklace, Cassock
负向: longbody, lowres, bad anatomy, bad hands, missing fingers, pubic hair, extra digit, fewer digits, cropped, worst quality, low quality, jpeg artifacts, signature, username, blurry, missing fingers, bad hands, missing arms, extra fingers, poorly drawn hands, poorly drawn face, malformed limbs, extra hands
参数: Steps 100, Euler a, CFG 10.5
```

### 1.5-22 西幻术（油画画风/彩虹/城堡晨雾）
```text
正面: (extremely detailed CG unity 8k wallpaper, masterpiece, best quality, ultra-detailed), (best illumination, best shadow, an extremely delicate and beautiful), classic, (impasto, photorealistic, painting, realistic, sketch, portrait), cinematic lighting, dynamic angle, floating, finely detail, (bloom), (shine), glinting stars, (1girl:1.75), (loli), ((an extremely delicate and beautiful girl)), ((extremely detailed cute anime face)), (((extremely detailed body))), (bare shoulder), small breast, ((sideboob)), Iridescence and rainbow sailor dress, (detailed wet clothes), (silk shawl:1.5), bikini (Iridescence and rainbow eyes), big top sleeves, frills, floating hair, Mist encircles the mountains, dawn, (The castle stands out against the sky), Flowery meadow, feather, nature, (sunlight), river, forest
负向: Inverted mountain, low-quality, low-quality illustration, low-quality background, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, Missing limbs, three arms, bad feet, text font ui, malformed hands, long neck, limb, Sleeveles, bad anatomy disfigured malformed mutated, (mutated hands and fingers :1.5), (long body :1.3), (mutation, poorly drawn :1.2), bad anatomy, disfigured, malformed, mutated, multiple breasts, futa, yaoi, three legs
参数: Euler a, CFG 7, step 30
```

### 1.5-23 星语术（星河/油画/星空长发）
```text
正面: ((masterpiece)), ((best quality)), ((illustration)), extremely detailed, style girl, long shot, small breast, light grey very_long_hair, scifi hair ornaments, beautiful detailed deep eyes, beautiful detailed sky, beautifuldetailed water, cinematic lighting, dramatic angle, (very long sleeves), frills, formal, close to viewer, (an extremely delicate and beautiful), best quality, highres, official art, extremely detailed CG unity 8k wallpaper, ((starry sky)), star river, array stars, Holy, noble, ((oil painting)), ((wallpaper 8k CG)), (realistic), Concept Art, vary blue and red and orange and pink hard light, intricate light, dynamic hair, haircut, dynamic fuzziness, beautiful and aesthetic, intricate light, manga and anime
负向: nsfw, owres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, missing fingers, bad hands, missing arms, long neck, Humpbacked
参数: Steps 50, Euler a, CFG 5-16, Clip skip 2
```

### 1.5-24 金石法（宝石/金笼/蓝宝石花边）
```text
正面: Hide hands, (Magic circle), Principal, ((Gem)), elegant, (holy), extremely detailed 8k wallpaper, (painting), (((ink))), (depth of field), ((best quality)), ((masterpiece)), (highres), (((ink))), (illustration), cinematic lighting, ((ultra detailed)), (watercolor), detailed shadow, (((1girl))), (detailed flooding feet), (((((long top sleeves past fingers))))), ((motion)), beautiful detailed fullbody, (leg up), (((sapphire frills))), (((yokozuwari in the golden cage))), gold cage, (birdcage), {{{very long dress cover feet}}}, (translucent fluttering dress with lace}, {{detailed skin}}, (((long Bright wavy hair))), Juliet_sleeve, (((hands hide in puffy sleeves))), ((bare shoulders)), flat_chst, ((Crystal shoes)), ((((arms behind back)))), (((extremely detailed cute anime face))), Jewelry decoration, ((expressionless)), (Iridescent Gem Headwear), (Beautiful detailed gemological eyes), ((melting silver and gold)), looking_at_viewer, {detailed bare foot}, Obsidian bracelet, gold arm ring, (Precious refraction), {splash}, {{optical phenomena}}, detailed glow, (lightroom), (shine), chains, reflective, Gemological ornaments, Cosmic background of nebula, ((silver thorns)), (huge golden clock core above), gear, falling petals, Window pane, beautiful water, Colored crystal, mirror, Silver frame, canopy, detailed Diamonds, (Columnar crystal), Latin Cross Budded, (Sputtered broken glass from inside to outside), (flow), dark
负向: lowres, highres, worst quality, low quality, normal quality, artbook, game_cg, duplicate, gross proportions, deformed, out of frame, 60s, 70s, 80s, 90s, 00s, ugly, morbid, mutation, death, kaijuu, mutation, no hunmans, monster girl, arthropod girl, arthropod limbs, tentacles, blood, size difference, sketch, blurry, blurry face, blurry background, blurry foreground, disfigured, extra, extra_arms, extra_ears, extra_breasts, extra_legs, extra_penises, extra_mouth, multiple_arms, multiple_legs, mutilated, tranny, trans, trannsexual, out of frame, poorly drawnhands, extra fingers, mutated hands, poorly drawn face, bad anatomy, bad proportions, extralimbs, more than 2 nipples, extra limbs, bad anatomy, malformed limbs, missing arms, miss finglegs, mutated hands, fused fingers, too many fingers, long neck, bad finglegs, cropped, bad feet, bad anatomy disfigured, malformed mutated, missing limb, malformed hands
参数: Step 随意（别太低）, Cfg 随意, DDIM
```

### 1.5-25 飘花法-2（花瓣/金眼白发）
```text
正面: ((ink)), (water color), bloom effect, ((best quality)), ((world masterpiece)), ((illustration)), (white_hair), (gold_eye), (((1girl))), (beautiful detailed girl), golden_eye, ((extremely_detailed_eyes_and_face)), long_hair, detailed, detailed_beautiful_grassland_with_petal, flower, butterfly, necklace, smile, petal, (silver_bracelet), (((surrounded_by_heavy_floating_petal_flow)))
负向: lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, bad feet, nude, skeleton_girl
参数: Steps 50, Euler a, CFG 4
```

### 1.5-26 冰霜龙息-上限版（蓝白龙娘/冰翼）
```text
正面: ((best quality)), ((masterpiece)), ((ultra-detailed)), (illustration), (detailed light), (an extremely delicate and beautiful), a girl, solo, (beautiful detailed eyes), blue dragon eyes, (((Vertical pupil))), two-tone hair:blue and white, shiny hair, colored inner hair, (blue Dragonwings), blue_hair ornament, ice adorns hair, [dragon horn], depth of field
负向: owres, bad anatomy, text, error, extra digit, fewer digits, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, (blurry:1.1), missing arms, two girls
参数: Steps 25, DDIM, CFG 5, 1280x448, 模型 e6e8e1fc, Clip skip 2
```

### 1.5-27 冰霜龙息-稳定版（蓝白龙娘/冰晶loli）
```text
正面: ((best quality)), ((masterpiece)), ((ultra-detailed)), extremely detailed CG, (illustration), ((detailed light)), (an extremely delicate and beautiful), a girl, solo, ((upper body,)), ((cute face)), expressionless, (beautiful detailed eyes), blue dragon eyes, (Vertical pupil:1.2), white hair, shiny hair, colored inner hair, (Dragonwings:1.4), [Armor_dress], blue wings, blue_hair ornament, ice adorns hair, [dragon horn], depth of field, [ice crystal], (snowflake), [loli], [[[[[Jokul]]]]]
负向: owres, bad anatomy, text, error, extra digit, fewer digits, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, (blurry:1.1), missing arms, two girls, feather, ((simple background)), squinting
参数: Steps 55, Euler, CFG 5, 1024x640, 模型 e6e8e1fc, Clip skip 2
```

## 第二卷补充魔法（风格专章+物象专章+经典专章）

> 来源：《元素法典 第二卷》（https://docs.qq.com/doc/DWEpNdERNbnBRZWNL）。第二卷共三章：风格专章（特殊画风/构图）、物象专章（风景/非人事物）、经典专章（经典高质量）。以下精选文本区完整配方；目录区魔法（白虎志、狡兽录、穷奇录、故障艺术、立体主义、嘻哈风、默剧法、漫画风格、彩墨法、繁浮法、半厚涂、古典肖像法、跑团法、太空兔、人像水墨法、断墨残楮、像素法、工程设计、世界文化、机魂法、失落之海、深海巨物恐惧症、萝卜法、灵铠法、星战法、巨星法、黑洞法、开席术、徽章法、积木法、美术场景法、水镜法、天堂台阶、中国龙、蒸汽朋克、军姬法、塔罗牌术、群像法Lite、古典系、圣宫法、向日葵法、人偶法、圣经篇、怨念芷、蜂女术、触手法、大威天龙、寂雨、彷徨、星际穿越、龙女幻想、国风少女、樱乐会、瓶中法、未名花、未名雨）的 tag 为图片，仅保留名称索引。完整 35 套提取数据见 `references/recipes_v2.json`。

### 2-1 赛博格少女（今宵万用公式，可塑性极强）
```text
正面: ((masterpiece)), best quality, highres, original, extremely detailed 8K wallpaper, world masterpiece theater, (an extremely delicate and beautiful cyborg girl), 1 cyborg girl, solo, assertive female, ((messy long hair)), dark red hair, ((beautiful detailed eyes)), dark dress, red scarf, torn clothes, arrogant smile, despair, (heroic fight:1.5), dynamic blur, detailed background, (cyberpunk:1.5), (((transformed body))), cloak, focus on face, depth of field, beautiful detailed shadow, dust, splashing blood, ((blood rain)), dynamic angle, light shafts, good lighting, tyndall effect, (Aestheticism Painting)
负向: (((ugly))), (((duplicate))), ((morbid)), ((mutilated)), (((tranny))), mutated hands, (((poorly drawn hands))), blurry, ((bad anatomy)), (((bad proportions))), extra limbs, cloned face, (((disfigured))), (((more than 2 nipples))), ((((missing arms)))), (((extra legs))), mutated hands, (((((fused fingers))))), (((((too many fingers))))), (((unclear eyes))), lowers, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet, text font ui, malformed hands, long neck, missing limb, (mutated hand and finger: 1.5), (long body: 1.3), (mutation poorly drawn: 1.2), disfigured, malformed mutated, multiple breasts, futa, yaoi, ((((bad face)))), unclear face
参数: Steps 28, Euler, CFG 13, 768x1280, 模型 e6e8e1fc
改造: cyborg girl→girl + cyberpunk→steampunk + blood rain→many metal decorations = 蒸汽朋克；cyborg→girl + cyberpunk→church + 去掉 transformed body + 加 many feathers = 黑暗教堂
```

### 2-2 彩虹少女（高饱和彩色泼墨）
```text
正面: (((masterpiece))), (((best quality))), ((ultra-detailed)), (illustration), (dynamic angle), ((floating)), (paint), ((disheveled hair)), (solo), (1girl), loli, ((small_breasts)), (((detailed anime face))), ((beautiful detailed face)), collar, bare shoulders, white hair, ((colorful hair)), ((streaked hair)), beautiful detailed eyes, (Gradient color eyes), (((colorful eyes))), (((colorful background))), (((high saturation))), (((surrounded by colorful splashes))), (((surrounded by colorful dot))), colorful bubble, ((shining))
负向: nsfw, nipples, (black skin), dark background, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, bad feet
参数: Steps 50, Euler a, CFG 6, 1280x512, 模型 e6e8e1fc, Eta 0.68, Clip skip 2, ENSD 31337
```

### 2-3 监狱少女（naifu/webui 双版本）
```text
naifu版: masterpiece, best quality, masterpiece, {best quality}, highly detailed, ultra-detailed, illustration, Depth of field, cold, solo, {{{Dark prison}}}, {{{1girl}}}, black short_hair, bob haircut, {{long_sleeves}}, off_shoulder, detailed eyes, {{Hematic red eyes}}, {{tareme}}, {{crazy}}, expressionless, {{prisoner's garb}}, Handcuffs, Chain, Hammer, miniskirt, {metal jewelry}, {{{heavy metal}}}, Foot cuffs, cross-laced_footwear, choker, {{Monster Energy}}, {Demon Array}, {{{666}}}, [Dry ice fog]
webui版: masterpiece, (best quality), highly detailed, ultra-detailed, illustration, Depth of field, (Dark prison:1.2), cold, solo, (1 girl), detailed eyes, (Hematic red eyes), (black short hair), bob haircut, (tareme), (crazy), expressionless, (prisoner's garb), (long_sleeves), off shoulder, miniskirt, (Monster Energy:1.2), (heavy metal:1.2), (metal jewelry), choker, cross-laced footwear, cuffs, wrist cuffs, (chain), hammer, (Demon Array), (666:1.2), Dry ice fog
参数: naifu steps 50 scale 4.2 | webui steps 50+ scale 4
```

### 2-4 德国军装（二战军服/战火）
```text
正面: (Gloomy dim yellow light), A blonde girl wears a German military uniform, (The girl wore a black German military uniform), ((The girl looked disgusted)), The girl was expressionless, (The girl was draped in a black cloak), ((((Flames burned behind the maiden)))), (There is battlefield behind the girl), (((Bloody))), (((beautiful detailed German military uniform))), ((German military uniform)), beautiful detailed girl, Perfect face, feet out of frame, ((Perfect body)), straight-on, ((solo)), red eyes, curly hair, ((backlight)), Girl on the center axis of the picture, small breasts, (The character is in the center of the frame), (extremely detailed CG unity 8k wallpaper, masterpiece, best quality, ultra-detailed), (best illumination, best shadow, an extremely delicate and beautiful), dynamic angle, floating, finely detail, (bloom), (shine), glinting stars, classic
参数: Steps 30, Euler, CFG 3.5, 768x1024, 模型 e6e8e1fc, Clip skip 2, ENSD 31337
```

### 2-5 林奈法（植物插画）
```text
纯植物: Botanical illustration, masterpiece, best quality, extremely detailed, 植物名
带人物（注意顺序）: watercolor, masterpiece, best quality, extremely detailed, 1girl, full body, beautiful detailed eyes, cute anime face, full body, beautiful detailed face, white hair, (Botanical illustration:1.5), white dress
参数: Steps 32, Euler a, CFG 11, 512x512
要点: 去掉 watercolor 加 sketch 花草线条更清晰；加 full body 权重更稳定出全身但脸崩率增加
```

### 2-6 群像法（gathering 多人物）
```text
正面: masterpiece, best quality, (girls), gathering, 其它自定义内容
要点: 复数形式 + gathering 确保群像；加 (boys) 可入男性；group photo 也可确保群像但绑定 full body
参数: Steps 65+, Sampler 随意, CFG 随意, 大宽图
高 Step 自带手部修复，可避免手指/脸部事故
```

### 2-7 中国神兽（白虎/狡/穷奇，国风水墨）
```text
起手: ((masterpiece)), best quality, ((illustration)), original, extremely detailed wallpaper,
国风: (((beijing opera))), (sketch), (wash painting), ((color splashing)), ((ink splashing)), ((((dyeing)))), ((Chinese painting)), ((colorful)) (beautiful and delicate mountain),
白虎: (solo), (Fantasy creatures), ((Chinese white tiger)), (solo;1.8), Black markings, (white tiger), ((solo)), beautiful and delicate golden eyes, Huge claws, Big and strong, Diabolical, Tyrannica,
狡: Stone figure, (solo), (Fantasy creatures), dog body, ((Chinese jiao)), (((Horns))), Horns, (golden dog body:1.3), (golden lion head), Leopard print, (solo), Canines, lion head, fly up to the cloudy regions, Big and strong, Diabolical, Tyrannica,
穷奇: ((a mythical ferocious animal)), {{The bull}}, {{long horns}}, {{With wings on its back}}, (Red and black wings,), (solo), mountain, Big and strong, Diabolical, Tyrannical
参数: Steps 40, Scale 5.5, k_euler_ancestral, 512x1024 (Euler 偏写实 / DDIM 偏意境)
```

### 2-8 故障艺术（Glitch Art）
```text
正面: {{cute anime face}}, (best quality), (ultra-detailed), (best illustration), (extremely delicate and beautiful}, {album cover}, album, album description, {error}, {{glitch lump} on face}, (glitch art:1.5), {Pixilation on face}, Double exposure, {Chromatic Aberration}, Light leaks, Noise and grain, Color degradation, Glitch lettering, design, 1 girl, art, abstract art, (flat_chest, short red hair, short wavy hair, floating black jacket, white school uniform, white beret, bowknot over white beret, floating black feathers:0.5), geometry, clear lines, squares, bright, limited palette
参数: NAI Diffusion Anime (Full) 模型（不能选 curated），steps 28, scale 11, ddim, portrait (w<h)
```

### 2-9 立体主义（毕加索）
```text
正面: Maidens of Avignon, colorful, flat_color, limited palette, {{by Picasso}}, {{cubism}}, {{a girl}}, pretty face, upper body, flat_chest, floating black jacket, white school uniform, white beret, bowknot over white beret
参数: Scale 10, steps 26（可复刻 seed 调高 scale 让少女变具体）
```

### 2-10 彩墨国风（花青/胭脂红/彩，水墨少女）
```text
正面: dramatic angle, (fluttered detailed ink splashs), (illustration), (((1 girl))), (long hair), (rain:0.6), (expressionless, hair ornament:1.4), there is an ancient palace beside the girl, chinese clothes, (focus on), color Ink wash painting, (ink splashing), color splashing, ((colorful)), [sketch], Masterpiece, best quality, beautifully painted, highly detailed, (denoising:0.7), [splash ink], yin yang
变体: 花青=花青水替换 + 瀑布；胭脂红=加 (Carmine hair ornament:1.4)；彩=colorful splashing
参数: CFG 10, DPM2 a Karras, Step 40, 512x1024（模型 e6e8e1fc / 925997e9 均可）
关键词: ink splashing(墨水飞溅), ink wash painting(水墨画), sketch(素描), splash ink(泼墨)
```

### 2-11 世界文化（壁画/剪纸/彩绘玻璃/铸币）
```text
中式壁画: (((best quality))), ((Dunhuang frescoes)), (Only murals), chinece_ancient, macro shot, longsleeve, (tradictional_chinese_painting), Shadow Play, Old Animation, three-dimensional, temple, (traditional Chinese painting), cloud, Painted on a rock wall, mural, cave, Characters step on the cloud, Tang painting, Rich rhyme, Buddhism, comic, chinese characters | sampling: ddim
埃及壁画: (((ancient egyptian mural))), story, Pharaoh | scale 12, ddim
教堂壁画: (((best quality))), ((fresco)), Christianity, dome, angel, (The Creation of Adam) | scale 4-10, ddim
街头涂鸦: (((best quality))), ((fresco)), street mural, (character graffiti), (Colourful), Cyberpunk | scale 6-8, ddim
剪纸窗花: ((art of paper-cut)), china, Red and white, PAPER-CUT, calligraphy, man and wife, (Flower, bird, insect and fish) | euler_a 或 ddim
彩绘玻璃: ｛Glass painting｝, (stained glass), God Light, colorful, story, 1girl | scale 12, ddim
铸币: Gold coin<>或silver coin<>, ｛Relief craft｝, Stereoscopic feeling, Grey background | scale 12, e_a
```

### 2-12 古典肖像法（classicism 画框）
```text
至简版: classicism, masterpiece, best quality, 人物描述, portrait, picture frame
厚重油画版: ((oil painting)), ((masterpiece)), ((best quality)), ((ultra-detailed)), (illustration), ((impasto)), highres, (beautiful detailed), classicism, Rembrandt lighting, brown background, detailed face, 人物描述, sitting on the chair, (portrait), picture frame
参数: Steps 20, Euler a, CFG 无所谓, 512x768 等肖像尺寸
要点: classicism 是灵魂；portrait + picture frame 防止人物走出画框
```

### 2-13 塔罗牌术（Alphonse Mucha 风格）
```text
正面: (((masterpiece))), ((the best quality, super fine illustrations, beautiful and delicate water)), Depth of field, fine 8K CG wallpapers, (delicate light), ((cinematic lighting)), (portrait), Portrait lens, (((Alphonse Mucha))), ((Fantasy style)), ((shine)), (((Tarot card))), (young girl), (((China_Cheongsam))), (delicate eyelash), ((cute anime face)), (extremely delicate and beautiful), (hair_flower), (Gem), (crystal), ((colored inner long hair)), (multicolored), (beautiful detailed face), (((detailed long hair))), floating long hair, gradient hair, (lace), (ribbon), ((crown)), (detailed cloth), ((Butterfly)), (detailed Butterfly), (multicolored Butterfly), (neon palette), ((detailed flowers)), ((multicolored flowers)), (flowers_Surrounded), (Butterfly_Surrounded), (((Flowers fill the screen))), ((Fill the screen))
参数: Steps 40, Euler, CFG 7, 448x896, 模型 e6e8e1fc, Batch 2, Eta 0.67, Clip skip 2, ENSD 31337
```

### 2-14 猫娘（琥珀青葉 春之猫，混色法）
```text
正面: original, (masterpiece), (illustration), (extremely fine and beautiful), perfect detailed, photorealistic, (beautiful and clear background:1.25), (depth of field:0.7), (1 cute girl with (cat ear and cat tail:1.2) stands in the garden:1.1), (cute:1.35), (detailed beautiful eyes:1.3), (beautiful face:1.3), casual, silver hair, silver ear, (blue hair:0.8), (blue ear:0.8), long hair, coat, short skirt, hair blowing with the wind, (blue eye:1.2), flowers, (little girl:0.65), butterflys flying around
参数: Hypernetwork anime_3, strength 0.5~0.6, CFG 4.5~5.5, step 30~50, 1024*768~1024*576, DDIM, CLIP skip 1, ENSD 17415
要点: 混色法 silver hair+blue hair 在 DDIM 下高概率银色但整体偏蓝；hires fix 处理 1024 宽低分辨率
```

### 2-15 狐娘（琥珀青葉 夏夜之狐）
```text
正面: original, (masterpiece), (illustration), (extremely fine and beautiful), (perfect details), (unity CG 8K wallpaper:1.05), (beautiful and clear background:1.25), (depth of field:0.7), (1 cute girl with (2 fox ear:0.9) and (fox tail on the back:1.2) stands aside the river:1.15), (cute:1.3), (detailed beautiful eyes:1.3), (beautiful face:1.3), silver hair, silver ear, (pink hair:0.7), (pink ear:0.7), long hair, (japanese kimomo:1.25), (hair blowing with the wind:1.1), (blue eye:1.1), (little girl:1.1), butterflys flying around, (moon light:0.6), tree, (summer), (night:1.2), (close-up:0.35), (gloves:0.8), solo
参数: Hypernetwork anime_3, strength 0.5~0.6, CFG 4~5, 1024x640 效果最好, ENSD 17415, CLIP skip 1(重要), hires fix 到 2048x1280
要点: 反咒特制防止 3+ 狐耳；(3 fox ears:1.7), (fox ear in middle), (hands) 进负向
```

### 2-16 像素法（Pixel Art）
```text
正面: ((pixel art)), masterpiece, best quality, cinematic lighting, soft lighting, (1girl:1.3), morning, red eyes, beautiful white hair, (TechWear:1.1), transparent raincoat, black gloves, Black coat, (with red ornaments:1.05), (with blue ornaments:1.03), looking to the side, flat chest, raining, beautiful detailed water, beautiful detailed sky, ruins
参数: Steps 50, Euler, CFG 7, 1280x832, 模型 e6e8e1fc, Clip skip 2
```

### 2-17 巨星法（巨大星球/月亮）
```text
正面: cola exists, planetarium, sky, fantasy, {{{giant Jupiter}}}, blue, {{{huge Jupiter}}}, {{{masterpiece}}}, {{the best quality, super fine illustrations, beautiful and delicate water}}, {{very delicate light}}, starfall, clean sky, night sky, night, depth of field, {{{Two moons}}}, Giants, Megaphobia, {{extremely detailed CG unity 8k wallpaper}}, {ultra-detailed}, {extremely delicate and beautiful}
参数: Steps 50, Euler, CFG 7.5, 1024x512, 模型 e6e8e1fc, Clip skip 2, ENSD 31337
```

### 2-18 黑洞法
```text
正面: (Very detailed CG unified 8k wallpaper), (masterpiece), (best quality), (Super detailed details), (best illustration), (extremely delicate and beautiful), (dynamic angle), (glow), classics, Realistic, ((very delicate light)), ((nature)), solo, (((Black hole))), ((Kagantua black hole)), astronomy, (bright and fine Black-Hole Accretion Disk:1.4), (黑洞视界:1.2), bright and fine (bipolar jet:1.3), ((prospect)), (Schwarzschild radius:1.2), chandrasekhar limit
参数: Sampling Steps 60, cfg 7, 960x768, 模型 e6e8e1fc, Eta 0.68, Clip skip 2, ENSD 31337
要点: Kagantua black hole 为主要 tag；「黑洞视界」用中文才能识别
```

### 2-19 瓶中法（水晶瓶少女）
```text
正面: (extremely detailed CG unity 8k wallpaper, masterpiece, best quality, ultra-detailed), (best illumination, best shadow, an extremely delicate and beautiful), dynamic angle, floating, finely detail, Depth of field (bloom), (shine), glinting stars, classic, (illustration), best starry sky, transparent, 1girl:1.75, long gray hair, detailed blue eyes, medium breasts, witch, (girl sitting inside a long crystal bottle), bottle with stopper, water in bottle, grass background, nature
参数: Steps 50, Euler a, CFG 11, 512x1024, 模型 925997e9, Clip skip 2
```

### 2-20 大威天龙（古僧/中国龙）
```text
正面: original, (masterpiece), (illustration), (extremely fine and beautiful), (extremely detailed:1.15), (perfect details), (unity CG 8K wallpaper:1.05), (beautiful and clear background:1.25), (depth of field:0.7), (A handsome Ancient Monk1.5), (detailed beautiful eyes:1.15), (detailed beautiful face:1.35), (bald:1.4), (Buddha's light shines back:0.9), (The plate sits in front of the temple1.25), (tower:1.1), (Red and yellow and cassock: 1.25), (golden and white eye:0.9), (Early in the morning), (close-up:0.35), treee, china, (mountain:0.9), (fantasy:0.85), (legendary Dragon King king:1.35), (Chinese dragon:1.25), (beautiful detailed glow), (fog:0.9), chinadre, traditional chinese painting, (Chinese wind:1.1)
参数: 模型 e6e8e1fc, CFG 4~5, 1280x640, Steps 30~50, DPM2 A Karras 或 DDIM
```

### 2-21 蒸汽朋克（飞空艇/维多利亚）
```text
正面: best light, Amazing, dream, ((((detailed Steampunk)))), ((Victorian era)), sunny, ((clear sky)), (depth of field), Hopeful, ((sketch)), ((((Jiburi)))), ((bright color)), (((flat color))), grand space, (((watercolor_(medium)))), (((ink))), (((masterpiece))), ((extremely detailed CG unity 8k wallpaper)), ((ultra-detailed)), (hometown), ((man)), ((chromatic aberration)), beautiful blue sky and white clouds, cinematic lighting, ((caustic)), ((((Floating airship above)))), ((many gentlemen)), ((Bird Mouth Gas Mask)), (Pocket watch), romanticism, (Science and Mysticism), ((Gentleman's high hat)), ((Leather riding boots)), (Leather coat), ((Windbreaker)), ((Motorcycle goggles)), (((Precision flight watch))), Mechanical arm, (((steam))), fantasy, (((gear))), (steam engine), Gothic architecture, wind, fog, Steam powered, (19th Century), machines, ((lever drive)), steel, rivet, (Heavy and slow), Grassland far away from the city, Utopia, The First Industrial Revolution, 90s, steam whistle, Canvas wing, ((Steam punk wings)), ((windmill)), landspace, (hang glider), (Canvas propeller), Hot Air Balloon, Balloon, (Waving Flag), rope, Flying splashes, Dutch windmill, Gothic architecture, Close up focus, (Medieval manor), background, scenecy, kikai, (vapour), Wooden parts, magic, street
参数: Step 40, cfg 4.5, ddim
```

### 2-22 中国龙（水墨祥云）
```text
正面: {master piece}}, (((best quality))), (((ultra_detailed))) grand movement, (illustration), cool movement, ((1 Orient dragon)), black background, beautiful and detailed squama, ((beautiful and detailed loong_horns)), beautiful and detailed dragon's head, beautiful and detailed loong_tail, feature, flames, lightning effect, rainy, (suspending), full_loong, coherent loong, (((beautiful_and_detailed_claw))), ((loong_with_4_claws)), overlook view, coordinate, ((slim and long)), ((slim claws)), black, half hidden in the cloud, (((wash_and_int))), Chinoiserie, Chinese_int, (((mount the cloud and ride the mist)))
参数: Steps 60, DDIM, CFG 11
```

### 2-23 水镜法（水面倒影）
```text
正面: (best illumination, best shadow, an extremely delicate and beautiful), ((only water)), Clear and turquoise sky, Water as smooth as a mirror, petal, There are clouds where water and sky connect, (Colorful clouds), depth of field, beautiful detailed sky, Cyan sky, beautiful detailed cloud, beautiful detailed water, reflection pool, (((extremely detailed CG unity 8k wallpaper, masterpiece, best quality, ultra-detailed))), dynamic angle, floating, finely detail, (bloom), (shine), glinting stars, feather, nature, (sunlight), fairyland
参数: Steps 50, Euler a, CFG 6.5, 1024x512, 模型 e6e8e1fc, Clip skip 2, ENSD 31337
要点: 可把云替换成其他物体让水镜反射；与横幅相性极佳
```

### 2-24 天堂台阶（悬空阶梯）
```text
出人物: (((There are Suspended staircase above the sky))), (((only suspended staircase))), (((Clouds surround the white suspended staircase))), The suspended staircase are snow-white, There are only suspended staircase in the sky, White feathers fluttered around the suspended staircase, (((Heaven, beautiful detailed sky))), beautiful detailed cumulonimbus, (((extremely detailed CG unity 8k wallpaper, masterpiece, best quality, ultra-detailed))), (best illumination, best shadow, an extremely delicate and beautiful), dynamic angle, floating, finely detail, (bloom), (shine), glinting stars, feather, nature, (sunlight), fairyland, extremely delicate and beautiful girls, full body, Cloud gap light
出景物: 同上但去掉人物 tag，加 (((White feathers fluttered around the suspended staircase)))
参数: Steps 50, Euler a, CFG 6.5, 1024x768, 模型 e6e8e1fc, Clip skip 2, ENSD 31337
```

### 2-25 星际穿越（太空舱少女）
```text
正面: ((masterpiece)), (((best quality))), ((ultra-detailed)), ((illustration)), ((disheveled hair)), space, spacecraft, (spacecraft_interior:2.0), border, floating, form behind, glowing, grey border, Science fiction, {{extremely detailed CG unity 8k wallpaper}}, super fine illustrations, the best quality, cockpit, holographic monitor, horizon, realistic, plane, 1girl, bangs, blue eyes, bodysuit, book, brown hair, cable, cockpit, computer, drawing tablet, earth (planet), floating, floating book, floating object, glasses, graphite (medium), grey bodysuit, hair over shoulder, juice box, laptop, long hair, looking to the side, planet, scenery, screen, semi-rimless eyewear, sitting, solo, space station, star, sunlight, sunrise, traditional media, kunder-rim eyewear, window, zero gravity, (aerial battle), (battle), (crossover), (dogfight), (backlight:1.5), middle
参数: Steps 64, DPM2 a Karras, CFG 12, 1216x704, 模型 925997e9, Variation seed strength 0.01
```

### 2-26 黄金叶（金线天使/金色丝线）
```text
正面: (((masterpiece))), (((crystals texture Hair))), (((((extremely detailed CG))))), ((8k_wallpaper)), (1 girls:1.5), big top sleeves, floating, beautiful detailed eyes, overexposure, side blunt bangs, buttons, bare shoulders, (loli), light shafts, soft focus, character focus, wings, (((Transparent wings))), [[((Wings made of golden lines, angel wing, gold halo around girl, many golden ribbon, Aureate headgear, gold magic circle in sky, light, black sky):1.3):((galaxy background, snowflakes, night sky, black pupils, starts sky background, stars behind girl, view on sky, standing):0.8)], [(Elegant hair, Long hair, The flying golden lines, Messy golden lines, halo, hairs between eyes, Small breasts, ribbons, bowties, red eyes, golden pupil, white hair, flowing hair, disheveled hair, lowing long hair):(Delicate arms and hands):0.8]
参数: Steps 150, Euler, CFG 7.5, 1216x576, 模型 e6e8e1fc, Clip skip 2, ENSD 31337
要点: 融合描绘 [A:B] 语法生成金线天使+星空背景；第一个彻底解决手和元素污染的魔法（500+ steps）
```

### 2-27 机甲法（萝卜法/魂系机甲）
```text
正面: masterpiece, best quality, ultra-detailed, Knight in Armor, Metal, extremely detailed HD wallpaper, realism, fluorescent, 8k, colorful background, cool movement, insanity, dynamic composition, motion, ultra-detailed, Cloak, incredibly detailed, a lot of details, amazing fine details and brush strokes, smooth, hd semirealistic anime cg concept art digital painting, volume, an extremely delicate and beautiful, dynamic angle, floating, painting, solo, full body, 1man, look up, Cloak, dark souls, two arms
参数: Steps 45, CFG 13
```

### 2-28 龙女幻想（汉服龙女）
```text
正面: (masterpiece), (best quality), (super delicate), (illustration), (extremely delicate and beautiful), (dynamic angle), white and black highlights, (legendary Dragon Queen:1.3), (1 girl), Hanfu, (complex details), (beautiful and delicate eyes), golden eyes, green pupils, delicate face, upper body, messy floating hair, messy hair, focus, perfect hands, (fantasy wind)
参数: Steps 30, DPM2 a, CFG 7, 1280x512, 模型 925997e9, Clip skip 2, ENSD 31337
```

### 2-29 寂雨（九龙城寨/雨巷）
```text
正面: (Kowloon Walled City), (((extremely detailed))), ((masterpiece)), (((best quality))), ((ultra-detailed)), ((illustration)), flowing, Telegraph Pole, solo, 1girl, cinematic lighting, vest, (Delicate face), (rain), (girl hold an umbrella), grey sky, lonely, (city), beautiful detailed eyes, detailed wet clothes, blank stare, dynamic angle, umbrella, expressionless, wet, alley, swirl
参数: scale 8-10, ddim
```

### 2-30 樱乐会（演唱会/应援棒）
```text
正面: ((masterpiece)), (((best quality))), ((ultra-detailed)), ((illustration)), A lot of waving glow sticks, Stage, Concert, (solo), 1 girl, ((singing)), headset, (leaning_forward:1.2), (arms_behind_back), ((extremely_detailed_eyes_and_face)), colorful, Tokyo Dome, ray tracing, (disheveled hair), cherry_blossoms, petals, Flying notes
参数: Steps 48, Euler, CFG 13, 1344x832, 模型 e6e8e1fc, Clip skip 2
```

### 2-31 军姬法（血火军人）
```text
正面: ((solo)), best quality, Amazing, 1girl, extremely detailed CG unity 8k wallpaper, masterpiece, (loli), (white hair), (((red streaked hair))), red eyes, (((full body))), (red hair), (((((Hold a red sword))))), (angry face), (beautiful detailed eyes), ((Blood drop)), ((Blood fog)), light shafts, soft focus, character focus, disheveled hair, long bangs, hairs between eyes, looking at viewer, lowing hair, ((Splashing blood)), Long hair, ((Bloodstain)), Fighting stance, {{{{{watercolor_(medium)}}}}}, (((masterpiece))), ((white clock)), ((ultra-detailed)), ((Covered in blood)), flowing hair, Exquisite Flame, {{{{{{extremely beautiful detailed anime face}}}}}}, dynamic angle, floating, (shine), extremely delicate and beautiful girls, bright skin, (best illustration), (best shadow), finely detail, Depth of field (bloom), (painting), {very delicate light, perfect and delicate limbs}, beautiful detailed dress, Flying red petals, Holy lighting
参数: Steps 60, Euler a, CFG 7, 1600x768
```

### 2-32 国风少女（白鹤道袍）
```text
正面: ((masterpiece)), ((best quality)), ((official art)), (extremely detailed CG unity 8k wallpaper), ((highly detailed)), ((illustration)), traditional chinese painting, ((Chinese wind)), ((a girl)), (single), staring, fairy, hair_ornament, earrings, jewelry, (very long hair), (messy_hair), bare shoulders, ribbon, hairs between eyes, beautiful detailed sky, full body, close-up, arms behind back, Taoist robe, thighs, aloft, mist-shrouded, chinadre, overexposure, [wet clothes], medium breast, solo, [doll], Bare thigh, incredibly_absurdres, intense angle, pleated dress, chinese style architecture, single hair bun, white_hair, red_eyes, sideways glance, cold attitude, eyeshadow, eyeliner, eyes visible through hair, no shoes, ribbon-trimmed sleeves, earrings, necklace, tiara, medium_breasts, sunlight, reflection light, ray tracing, loli, Phoenix crown and rosy robe, blush
参数: CFG Scale 5.5, Sampling Steps 60
```

### 2-33 丧尸少女（僵尸妹）
```text
正面: (((little girl, solo, Jiangshi girl, Chinese vampire, canines, 1girl, delicate beautiful face, Chinese Charms on the forehead)))
负向: nsfw, text font ui, error, blurred, bad shadow, JPEG artifacts, signature, 3D, 3D game, 3D game scene, 3D character, duplicate, blurry, strong girl, obesity, worst quality, low quality, normal quality, black-white, lowers, cropped, watermark, username, QR code, bar code, censored, mosaic, excrement, faeces, shit
参数: Steps 40, Euler, CFG 8, 512x512, 模型 925997e9, Clip skip 2
```

### 2-34 黄金船（分步描绘示范）
```text
正面: extremely detailed 8k wallpaper, (highly detailed:1.1), ((masterpiece:1.1)), [anime:Impasto:0.5], intricate, fantasy, (1ship), (ocean:1.2), [golden boat:golden boat with (green fire:1.2):0.1], clear sky, wind, beautiful sky, (nightsky), (galaxy), (huge blood moon in the background:1.05)
参数: Steps 150, DDIM, CFG 5, 1024x576, 模型 e6e8e1fc, Clip skip 2
要点: 分步法 [golden boat:golden boat with (green fire:1.2):0.1] 先生成船再生成绿火
```

### 2-35 未名花（花之少女）
```text
正面: beautiful detailed flower, beautiful detailed eyes, hyper detailed, flower, hyper quality, eyes, flower and hair is same color, beautifuly color, face, {{{{{her hair is becoming flower, flower, hair, flower, butterfly}}}}}, {{{{1girl}}}} kawaii, {{{high details, high quality}}}, {{{back light}}}, {{hair and clothes is flower}}, {{{upper body}}}, high quality, hair with body, webbed dress, upper body, flower leg, flower hands, body with flower, {{flower with clothes}}, dress with flower, light particles, black background, {{{{Hair with flower}}}}, small breast with flower, big hair with flower, {{floating hair with flower, floating}}, 1girl, small breast, marbling with hair and clothes, looking at viewer, {{original}}, {{arm down}}, {{paper cutting}}, black background, flower forground, {{hair with flower}}, {{{{{highres}}}}, hair with flower, hair with flower, hair, wavy hair, diffusion lighting, abstract, Butterfly with body, flower with hair, her hair is flower, big top sleeves, floating
参数: scale 3, steps 28, ddim
```

## 第二点五卷补充魔法（30 套，详见 references/v25-recipes.md）

> 来源：《元素法典 第二点五卷》（https://docs.qq.com/doc/DWHFOd2hDSFJaamFm）。本卷不设专章，聚焦精美画面，文本区含 50+ 套完整配方。**完整配方见 `references/v25-recipes.md`**，此处为索引：

| 配方 | 主题 | 亮点 |
|------|------|------|
| 2.5-1 | 下午茶 | 极简 tag，AI 对场景理解力示范 |
| 2.5-2 | 合成器浪潮 Synthwave | 复古未来、霓虹粉紫、limited palette |
| 2.5-3 | Lineart 实验室 | 线稿立绘、thick outline 关键 |
| 2.5-4 | 秋日晨光 | 自然叙事式长句构图 |
| 2.5-5 | 国风汉服 | 黑金汉服、武当山瀑布、1girl:2.5 |
| 2.5-6 | 和室红裙 | 京都庭院、红叶、Tyndall 效应 |
| 2.5-7 | 大正蒸汽朋克 | 日式女仆+怀表+蒸汽火车，step 120+ |
| 2.5-8 | 狼皇 | 传奇狼女皇国风铠甲，wolf 可换 |
| 2.5-9 | 港城少女 | 蓝发低双马尾、flat color 白主题 |
| 2.5-10 | 猫徽章 | 概念设计/矢量/octane render |
| 2.5-11 | Emoji 魔法 | 📜✏🎶🧙♀️ 直接用 emoji 出图 |
| 2.5-12 | 水下汉服 | 深海梦境、金饰汉服、antlers 鹿角 |
| 2.5-13 | 溶解裙 | 裙与海洋同色融合、liquid clothes |
| 2.5-14 | 武装释迦 | 佛陀+浮游兵器、Global Illumination |
| 2.5-15 | 桃花少女 | 月下桃花、泡脚、full moon |
| 2.5-16 | 游戏厅 | 街机霓虹、arcade、Pixel particles |
| 2.5-17 | 四神兽 | 地水火风兽耳精灵、Extremely gorgeous |
| 2.5-18 | 数字赛博 | 数据之眼、二进制、cyan theme |
| 2.5-19 | 踏水少女 | 月蓝天空、水面行走、reflective |
| 2.5-20 | 宇宙黑洞 | 斐波那契螺旋核心、Euler 采样 |
| 2.5-21 | 雷剑少女 | 闪电剑、黑龙王、Bottle bottom |
| 2.5-22 | 荧光蘑菇 | 夜间魔幻森林、Tyndall、Mucha |
| 2.5-23 | 四刻画 | 木刻/石刻/木壁/石壁国风 |
| 2.5-24 | 四核 | 怪核/梦核/伤核/池核/网核 liminal |
| 2.5-25 | 天使天城 | 云端城堡、白翼、2:1 长画幅 |
| 2.5-26 | 东方降魔 | 太极、符咒、神秘龙、黄纸 |
| 2.5-27 | 黑液少女 | black goo 泼墨、扁平化水墨 |
| 2.5-28 | 铅笔草稿 | sketch paper、partially colored |
| 2.5-29 | 双子镜 | 冰火双王、对称分屏、融合描绘 |
| 2.5-30 | 太空舱少女 | 宇航服、浮空要塞、夜天 |

## 使用指南（ComfyUI 工作流）

1. **选法**：根据想要的主题从配方库挑一个（如「星源法」出星空女神，「冬雪法」出白毛红瞳雪景）
2. **套前缀**：配方里没含 `masterpiece/best quality` 的，先加「通用起手式」
3. **调参数**：到工作流的 KSampler 节点设置对应的 Steps/Sampler/CFG
4. **人物定制**：把配方里的 `1girl/white hair/blue eyes` 等换成目标角色设定（如 Iris：`1girl, light blue hair, pale blue hair, maid...`）
5. **负向继承**：配方自带的负向词可合并到工作流负向节点

## 注意

- 配方来自 NAI 时代（e6e 模型为主），Animagine-XL 下**人物 tag 可平移使用，画风词微调**
- 括号语法 `()` WebUI/ComfyUI 通用；`{}` 大括号仅 NAIFU 官方有效（WebUI 会当文本）
- 部分配方含 `(1girl:1.5)` 显式权重——直接兼容
- 配方中 `,` 全角逗号建议统一为半角（ComfyUI 兼容更好）
- 第一卷魔法目录 58 种中，tag 以图片形式存在的（行 333 之后）无法提取文本，仅保留标题+作者+说明
- 第一点五卷正文区魔法（万物熔炉、暗鸦法、花火法、星之彩、沉入星海、百溺法等 22 种）的 tag 同样为图片不可提取，仅保留名称+作者+说明索引
- 第二卷目录区魔法（白虎志、故障艺术、嘻哈风、默剧法、漫画风格、世界文化、机魂法、深海巨物、蒸汽朋克、塔罗牌术等 55 种）tag 为图片，仅保留名称索引
- 第二点五卷目录区魔法（云海白鹤、下午茶、孔雀仙、潘多拉猫2.0 等）tag 为图片，仅保留名称索引

## 参考链接

- 第一卷原文：https://docs.qq.com/doc/DWHl3am5Zb05QbGVs（《元素法典——Novel AI 元素魔法全收录》第一卷）
- 第一点五卷原文：https://docs.qq.com/doc/DWGh4QnZBVlJYRkly（《元素法典第一点五卷》）
- 第二卷原文：https://docs.qq.com/doc/DWEpNdERNbnBRZWNL（《元素法典 第二卷》，风格/物象/经典三专章）
- 第二点五卷原文：https://docs.qq.com/doc/DWHFOd2hDSFJaamFm（《元素法典 第二点五卷》，无界限精选）
- 方法论：《元素同典》→ 见 `sd-prompt-methodology` skill
- 本机工作流：见 `comfyui-character-workflow` skill
