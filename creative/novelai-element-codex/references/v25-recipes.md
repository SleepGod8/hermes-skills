# 第二点五卷完整配方（从《元素法典 第二点五卷》文本区提取精选 30 套）

> 来源：https://docs.qq.com/doc/DWHFOd2hDSFJaamFm
> 完整 34 套提取数据见 `recipes_v25.json`

## 2.5-1 下午茶（极简tag）
正面: masterpiece, [(draft, (one girl:1.5))::0.5], [(at an afternoon tea party)], (medium shot:1.5), extremely detailed CG, [[beautiful detailed red eyes:0.5]::0.7], [[white and silver hair: 0.5]::0.7], [red hair:0.7], (luxurious hair ornament), floating hair, [[graceful full dress:0.5]::0.8], top_sleeves, [delicate hands:0.8]
负向: no person in the frame, (two heads), multiple girls, extra arms, character too close, headshot, close-up, deformed face, (two people:1.5), long body, bad anatomy, worst quality, water marks, extra fingers, (malformed hands:1.5), fused hands, nsfw, overhead perspective, rough hands, missing arms, misplaced hands
参数: Steps 51, Euler a 或 Euler, CFG 7, 1024x512

## 2.5-2 合成器浪潮（Synthwave）
正面: 1 synth wave style girl, extremely detailed CG, (masterpiece), (flat color:1.5), (best quality), (limited palette), pink fluorescent paint, noline art, silhouette, partially colored, (alternate color):1.4, dynamic angle, (pink, dark violet):1.3, dark violet shadow, (synth wave), (chromatic aberration), (((thick) outline)), pink outline, (solo focus), pink neon lights, perfect shadow, cowboy shot, blank stare, beret, bowknot on beret, flat chest, wearing an off-shoulder floating jacket, short wavy delicate hair, delicate face, bare shoulder, sitting on the top of the building, beautiful and delicate eyes, (1 girl):1.5, solo, from above, delicate background, streets with neon lights
负向: lowres, bad anatomy, bad hands, text, missing fingers, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, missing fingers, bad hands, missing arms, long neck
参数: NAI Diffusion Anime(full), steps 25, scale 10, ddim

## 2.5-3 Lineart 实验室
正面: Lineart, masterpiece, cool posing, (lab reaction systems:1.4), {experiment, lab, {{{chemistry laboratory}}}, delicate background, cool, {with a laboratory as background}}, best quality, a girl, solo: {papercut, thick outline: 2, short red hair, short wavy hair, floating lab-gown, flat chest, white school uniform, white beret, bowknot over white beret, outline}, masterpiece
负向: q-version, nsfw, lowres, bad anatomy, bad hands, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, symmetry
参数: NAI Diffusion Anime(full), steps 28, scale 11, ddim

## 2.5-4 秋日晨光
正面: original, (masterpiece), (illustration:1.2), (extremely fine and beautiful), (perfect details), (unity CG 8K wallpaper:1.05), (ray tracing), (beautiful and clear background:1.25), (depth of field:0.6), (1 (cute young girl:1.1) with (long hair:0.95) and tears in blue eyes, who is (crying:0.6), in forest with (river:1.2) under morning glow with sunrise in (autumn:0.5):1.15), (detailed beautiful eyes:1.2), (beautiful face:1.2), (hair blowing with the wind:1.1), (solo:1.3)
负向: lowres, bad anatomy, text, error, extra digits, fewer digits, cropped, (worst quality:1.2), (low quality:1.2), normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, (nsfw:1.3)
参数: 1024x512, CFG 5, DPM2 a Karras, Steps 35 | Hypernetwork 402c9025(anime_3) 0.5~0.6, ENSD 17415, Skip CLIP 1

## 2.5-5 国风汉服（黑金汉服/武当山）
正面: (((masterpiece))), best quality, ((illustration)), ((((beautiful detailed girl)))), (((extremely detailed CG 8k wallpaper))), ((official art)), (1girl:2.5), ((solo)), ((loli)), ((petite)), (((female focus on))), (macro shot:1.5), (focus on face), portrait of girl, The girl is in the center of the frame, (((Close-up of girl))), ((long black hair)), (very long hair), (floating hair), ((diamond and glaring eyes)), (((beautiful detailed cold face))), handsome, ((a cute and anime face)), beautiful eyes, (green eyes), bangs, bare shoulders, (((a girl wears clothes black and white hanfu))), small breasts, (super clothes detailed), ((white sleeves)), (((edged hanfu))), black ribbon, wide sleeves, looking_at_viewer, Perfect details, (((gold fringes))), (((arms behind back))), silk, ((sleeves past fingers)), ((standing)), (((Ancient palace background))), chinese place on the mountain, (((((chinese style architecture))))) behind the girl, depth of field, beautiful sky, ((beautiful cloud)), mountain, ((((waterfall)))) from the mountaintop, mist, beautiful and delicate water, ((beautiful detailed background)), ((((wudang)))), a girl in ((zhangjiajie)), dramatic angle, Chinese classical wooden tower, (Chinese ancient multistoried buildings), colorful, Pine, 1girl, handsome
负向: 通用负面 + none place, none girl
参数: Steps 40, DDIM, CFG 5.5

## 2.5-6 和室红裙（京都庭院）
正面: (super delicate), (illustration), (extremely delicate and beautiful), faux traditional media, perfect body, cowboy shot, (perspective), Kyoto Style, (sketch), (close-up), (a beautiful detailed girl in Washitsu:1.47), Washitsu, (solo:1.4), (HDbackground, Japanese courtyard:1.25), (Creek:0.55), wooden bridge, (cinematic lighting, beautiful detailed glow:1.0), (beautiful detailed pink eyes), ponytail, shiny platinum blonde hair, messy floating hair, ((black capelet)), red kimono, hair flower, hair ornament, hair over shoulder, japanese clothes, lace-trimmed kimono, pom pom hair ornament, tassel, wavy hair, glint, blue sky, (autumn:1.1), outdoors, (glowing particles:0.85), Maples in the distance, an epic scene, (Stone lantern, Bonsai:1.0), (White sand:0.85), (Rockery:0.8), (Japanese architecture:1.1), (contour deepening:1.1), (fluttered fallen leaves), (dappled sunlight on her:1.25), (Tyndall effect:1.1), (Cloud Retained background:1.1), (depth of field), highlight
负向: 通用负面 + pencil, Torii, 大胸系列
参数: CFG 8.5, e6e8e1fc, Eta 0.91, Clip skip 2 | 1280x768/1344x832 | DPM++ 2M/Karras → 35步；Euler a/ddim → 75步

## 2.5-7 大正蒸汽朋克（日式女仆）
正面: (extremely detailed CG unity 8k wallpaper), (masterpiece), (best quality), (ultra-detailed), (best illustration), (best shadow), (an extremely delicate and beautiful), dynamic angle, floating, finely detail, (bloom), (shine), glinting stars, classic, (painting), (sketch), Taisho steampunk, (steampunk:1.2), (1girl:1.7), (2020s), (cute face:1.3), anime face, ((solo)), beautiful detailed face, shiny hair, colorful clothes, (kimono), (Japanese maid), maid dress, maid headdress, hair flower, hair ornament, (Frill), Brass Pocket Watch, extremely delicate and beautiful girls, beautiful detailed eyes, cowboy shot, steam train, building architecture, (Japanese style architecture), (street:1.2)
负向: 通用负面 + from above, [naughty face:0.1], [open mouth:0.1]
参数: Steps 150, DDIM, CFG 5, 1024x640, e6e8e1fc, Clip skip 2 | step 120+

## 2.5-8 狼皇（传奇狼女皇）
正面: (masterpiece), (super delicate), (illustration), (extremely delicate and beautiful), (dynamic angle), black highlights, fluttered detailed ink splashs, (legendary wolf Empress:1.3), (1 girl), upper body, full moon, chinese armor, fairy, delicate face, (complex details), (beautiful and delicate eyes), golden eyes, Grey hair, messy floating hair, disheveled hair, focus, perfect hands, eyeshadow, red eyeliner, (fantasy style)
负向: 通用负面 + two head wolf, two girls
参数: Steps 40, DPM2 a Karras, CFG 6.5, 1280x640, e6e8e1fc, Clip skip 2

## 2.5-9 港城少女
正面: masterpiece, best quality, flat color, offical art, white theme, (ultra-detailed), (illustration), (an extremely delicate and beautiful harbour city), (an extremely delicate and beautiful girl with golden pupil), (+++++(blue hair)//), four ponytail, (long shot:1.3), (golden eyes:1.3), (++++++(low twintails:1.6)//), super fucking beautiful, ++++(very long sleeves)//
负向: 通用负面 + multiple people, animals, missing legs, huge person, optical_illusion
参数: Steps 23, Euler a/ddim, CFG 12, 1024x512, 925997e9, Eta 0.67, Clip skip 2

## 2.5-10 猫徽章（概念设计）
正面: concept art, a cat cloth emblem, electric current, circle shape, cyan color scheme, vector graphics, hyperrealism, octane render, high quality, illustration
负向: 通用负面 + peg artifacts
参数: Steps 50, Euler a, CFG 12, 512x512, 925997e9, Clip skip 2, ENSD 31337

## 2.5-11 Emoji 魔法
正面: ((📜)), ✏, 🎶, (🧙♀️), ✡, 🕯, ✨
负向: normal quality, highres, blurry_foreground, text, error, jpeg artifacts, signature, watermark, username
参数: Steps 40, DDIM, CFG 7, 1024x640, 925997e9, Clip skip 2, Eta 0.68, ENSD 31337

## 2.5-12 水下汉服（深海梦境）
正面: {{masterpiece}}, {best quality}, extremely detailed CG unity 8k wallpaper, highly detailed, extremely detailed, dramatic angle, {1girl:2}, {{solo}}, {full body:2}, {{{beautiful detailed eyes}}}, {{{beautiful detailed face}}}, {{{cute face}}}, {smile:1.3}, {black hair:5}, {{long hair}}, {{flowing hair:1.3}}, {{cone hair bun}}, {gorgeous hanfu:4}, {{black hanfu}}, {{hidden hand}}, Long sleeve, {{{sleeves past wrists}}}, {antlers:4}, {{gold hair stick}}, {{gold hair ornament}}, {{gold gorgeous necklace}}, {{gold lace}}, {{gold tassel}}, {{medium breast}}, {under water:2}, stream, {{wet}}, wet clothes, {{standing}}, ocean bottom, sea beds, beautiful and detailed bubbles, beautiful and detailed oceans, beautiful and detailed water, beautiful and detailed corals, gravels, {top-down light}, {dim light}, lighting, dream like benthos, transparent fish, Pearl, gemstone, seaweed, palace, {{ancient Chinese cityscape}}, {{ancient Chinese palace}}, {east Asian architecture:1.2}
负向: 通用负面 + {{{{:3}}}}, {{{3d}}}
参数: naifu, Step 28/50, Scale 5.5-7, DDIM/Euler a

## 2.5-13 溶解裙（海洋同色裙）
正面: depth of field, wave at the edge of dress, masterpiece, flat color, best quality, a girl, solo: {dress<wave>, {{dissolving dress}}, dress having the same color with ocean, dress floating into sea}, wave, ((colorful refraction)), ((beautiful detailed sky)), ((dark intense shadows)), ((cinematic lighting)), ((overexposure)), water on the dress, (water sea blue dress blending with sea), from side, (beautiful detailed girl), beautiful detailed glow, detailed lighting, detailed water, (beautiful detailed eyes), expressionless, standing in the ocean, detailed wet clothes, partially submerged, (long dress blending with ocean), (blue water long dress:1.5), (liquid clothes:1.2), a girl, solo, flat_chest, diamond and glaring eyes, black eyes, beautiful detailed cold face, short red hair, short wavy hair, water texture liquid clothes, backless dress, perfect light, white beret with a bowknot on it
负向: q_version, 通用负面 + symmetry, outline
参数: NAI官网, K_euler, steps 28, cfg 9

## 2.5-14 武装释迦（佛陀+浮游兵器）
正面: finely detail, Depth of field, (masterpiece), (((Extremely realistic))), ((extremely detailed CG unity 8k wallpaper)), best quality, high resolution illustration, Amazing, (detailed, clear and beautiful:1.4), intricate detail, (best illumination, best shadow, an extremely delicate and beautiful), Detailed beautiful and aesthetic, 1figure of Buddha, Gatling gun, electron, (many floating firearms:1.2), All kinds of weapons were floating around the statue, View from below, Global Illumination, auspicious cloud and golden cornfield, Nan Wusan, holy light, oppressive, Sharp Focus
负向: 通用负面 + vague, (simple background)
参数: Steps 39, Euler, CFG 8.5, 宽幅均可 | 出图率 60-70%

## 2.5-15 桃花少女（月下桃花）
正面: (best quality), (masterpiece), incredibly_absurdres, highly detailed, refined rendering, illustration, (highres), original, night_sky, (close_on:1.2), (close shot), (a girl:1.3) is (sitting on the tree) and soaking feet, [[light smile]], (baby_blue hair), very_long_hair, water inner hair, little double bun, (beautiful detailed eyes), (red eyes), floating ribbon, (peach blossom), flowers, (flower) tree, Petals on water, floating Petals, [[full moon]]
负向: 通用负面 + cross-eyed, (peach), wince
参数: Steps 30, DPM++ 2S a Karras, CFG 7, 896x896, e6e8e1fc, Eta 0.68, Clip skip 2, ENSD 31337

## 2.5-16 游戏厅（街机霓虹）
正面: ((masterpiece)), (((best quality))), ((illustration)), (depth of field:1.2), solo, dynamic angle, (1 girl:1.3), bangs, headphones, red eyes, white hair, (disheveled hair), Baseball cap, (jacket|hoodie), jeans, thigh strap, hands in pocket, cowboy shot, Moody Lighting, (arcade games:1.1), (Game Center:1.5), (Game Hall:1.1), (backlight:1.3), intricate detail, cyberpunk, slot machine, claw crane game machine, (crowd:1.1), (Pixel particles exploding:1.2)
负向: 通用负面
参数: Steps 150, DPM++ 2S a Karras, CFG 11, 1280x896, e6e8e1fc, Eta 0.67, Clip skip 2

## 2.5-17 四神兽（地水火风兽耳精灵）
地: {best quality}, {{masterpiece}}, Extremely gorgeous magic style, cave background, {legendary wolf empress}, fantasy, solo, {{detailed anime cat, {red tatoo}, stone accessory, anime eyes, anime style, cute, furry, mascot, Chibi, brown, {{wing}}, amber, golden headdress, body fur}}
水: {{masterpiece}}, {Extremely gorgeous magic style}, blue sea, blue sky, crystal orb, beautiful detailed water, beautiful detailed sky, fluttered detailed splashs, fantasy, highlights, solo, {{{detailed anime cat, anime eyes, anime style, detailed fox ears, cute, furry, mascot, Chibi, {dragon tail}, wings, white jewelry on head, blue skin}}}
火: {best quality}, {{masterpiece}}, (Extremely gorgeous magic style), magic, fire, burning ground, volocano background, fantasy, solo, {{{detailed anime dog, fox, wolf, dog, {yellow skin}, anime eyes, chinese accessory, anime style, cute, furry, chibi, mascot, body fur, gold accessory, {red pubic_tatoo}, red jewelry}}}
风: {best quality}, {{masterpiece}}, (Extremely gorgeous magic style), grassland, fantasy, solo, highlights, {legendary wolf}, {{{detailed anime cat, fox, wolf, dog, {{anime eyes}}, {{anime style}}, cute, furry, mascot, magic, Chibi, {{flower wing}}, jewelry, {light green skin}, floating magic ball}}}
负向: 通用负面 + Humpbacked
参数: NAIFU, steps 28, k_euler_ancestral, strength 0.69, noise 0.667, scale 12, 768x512

## 2.5-18 数字赛博（数据之眼）
正面: impasto, ((((1girl)))), Metaverse, original, ((an extremely delicate and beautiful)), (cyan theme), ((intricate detail)), ((((ultra-detailed))), ((illustration)), (((masterpiece))), ((extremely detailed CG unity 8k wallpaper)), highlight, sharpening, detailed face, ((Perfect details)), (binary numbers), Science fiction, sense of digital, cold light, ((data in the eyes)), ((data adorns hair)), 0 and 1 code, digitization, Running data, system screen, mathematical equation, young girl, (solo), (yubao)
负向: 通用负面 + flat color
参数: Steps 39, DDIM, CFG 9, 1024x640, 925997e9

## 2.5-19 踏水少女
正面: (masterpiece), (wallpaper), (best quality), (best illuminate, best shadow), (best illustration), dynamic angle, (+++a girl+++) is walking in front of a delicate and beautiful moon-blue sky, solo, from side, (Backlight), mid shot, (the beautiful and delicate girl:1.3), beautiful bare back, (detailed face:1.2), (long floating hair:1.2), (beautiful long dress:1.2), floating dress, the girl (walking) on surface of the water, Beautiful and delicate violet light water surface, reflective water surface, High saturation blue clouds and (stars sky) in the background, cold color
负向: 通用负面 + three arms, three legs, huge breasts
参数: Steps 50, Euler a, CFG 7, 1024x576, e6e8e1fc, Clip skip 2, ENSD 31337

## 2.5-20 宇宙黑洞（斐波那契螺旋）
正面: (masterpiece):1.2, ((best quality)):1.2, {{ultra-detailed}}, {{8k wallpaper}}, lifelike, Fibonacci spiral, wide-angle, {{extremely detailed background description}}, Depth of field, {best quality}, {highly detailed}, {{revolve round Stellar black hole:1.15}}, {{Schwarzschild radius:1.35}}, {{Black-Hole Accretion Disk:1.4}}, ((({{quasar}}, {windstorm}, {{The distant Milky Way}}, {{supernova star}}, {star cluster}, {nebula}, {star river}):0.8):((light with beautiful details), {shine}, {Stars surround}, depth, ether,):0.9), Fisheye lens
负向: 通用负面
参数: step > 80, 模型 e6e, Euler（DDIM 笔触重），1024x512 最佳, CFG 5.5 强烈推荐（别拉高）
要点: Fibonacci spiral 为稳定核心

## 2.5-21 雷剑少女（黑龙王）
正面: [(white background:1.4)::5], original, (illustration:1.1), (best quality), (masterpiece:1.1), (extremely detailed CG unity 8k wallpaper:1.1), (colorful:0.9), (imid shot:0.95), (full body:1.25), Dynamic angle, (solo:1.2), [Bottle bottom], ((1 younger (cute) girl:1.35) with Lolita, (The legendary sword of lightning:1.25):1.2), (detailed beautiful eyes:1.15), (beautiful face:1.15), (glowing blue eyes:1.25////), Silver ((pink)) gradient (disheveled:0.8) hair////, (+perfect hand+:1.21), Air bangs, Explosive lightning, (perfect sword:1.21), (((+++Lightning and Sword Interweave///))), expressionless, (Bottle bottom:0.8), (Purple flame around the wings behind the girl), (The Black Dragon King is behind the girl)
负向: 通用负面 + (bad sword:1.4), three legs, fused leg
参数: Steps 30, DDIM, CFG 5, 1024x1024, 925997e9, Clip skip 2, ENSD 17415 | 开高清修复更佳

## 2.5-22 荧光蘑菇（夜间魔幻森林）
正面: 1girl, alone, single, solo, only one, one character, (((Personage as the main perspective))), (((character in the middle))), ((masterpiece)), ((best quality)), (ultra-detailed), (illustration), clear-cut margin, alphonse mucha, extremely detailed CG unity 8k wallpaper, ((an extremely delicate and beautiful)), (dynamic angle), An enchanted forest at night illuminated by glowing mushrooms, ((Tyndall effect)), (Fluorescent mushroom forests background), 1girl, (arms behind back), (beautiful detailed eyes), cute pink eyes, golden pupil, detailed face, upper body, white dress, messy floating pink hair, disheveled hair, focus, (beautiful water), river, flying butterfly, sunlight, shine, chiaroscuro, ray_tracing, (painting), [[[[[[8 k artistic photography]]]]]]
负向: 通用负面 + futa, futanari, yaoi, three legs, ((two girls))
参数: Steps 60, DDIM, CFG 4.5, 960x640, e6e8e1fc, Clip skip 2, ENSD 31337

## 2.5-23 四刻画（木刻/石刻/木壁/石壁国风）
木刻画: (wooden gorgeous chinese borders:1.55), (best quality, extremely detailed CG unity 8k wallpaper, ultra-detailed), (best illumination, best shadow, an extremely delicate and beautiful), (ink:1.2), (graphite:0.75), (ink wash painting:1.05), (1 girl:1.15), solo, (the character is in the center of the frame:1.1), medium full shot, hanfu, taoist robes, celestial being uniform, very long hair, (a small (black:1.25) ornament), beautiful detailed eyes, black eyes, (tai chi:1.05), (yin yang:1.05), ba gua, (the bottom of the bottle background:0.85), (girl surrounded by floating ink water flow:1.1), (swirl:0.01), studio lighting, medium breasts, (cyan cloudy:1.15), (stratocumulus_stratiformis:1.1), (cirrus spissatus:1.1), (white lotus:1.1), (detailed lines:0.85), UHD
石刻画: 同木刻但 (stone gorgeous chinese borders:1.55), (detailed lines:0.55)
木壁画: (detailed lines:0.85), (wooden gorgeous chinese card borders:1.55), 4k, 同木刻 + (tai chi diagram:1.25), chaos
石壁画: (detailed lines:0.85), (stone gorgeous chinese borders:1.55), UHD, movie poster, splash art, studio lighting, 同木刻
负向: 通用负面 + large breasts
参数: clip 1（clip 2=挂画）, 768x1152/1152x768, e6e8e1fc, DPM2 a Karras, CFG 5.5-7, Steps 30
要点: 云纹 = cloudy + stratocumulus_stratiformis；可删 the bottom of the bottle background 概率出圈

## 2.5-24 四核（怪核/梦核/伤核/池核/网核）
怪核: photographic, realistic, liminal space, backrooms, weirdcore, one line of advertising words | DDIM CFG 7 512x512
梦核: liminal space, a candyhouse, dreamcore, clouds | DDIM CFG 7 512x512
梦核2: room, in the 1980s, there are a lot of clouds outside the window, overexposure
伤核: photographic, realistic, a big white humanoid doll is standing aside an old bed, a pink and yellow bedroom, liminal space, [(dim light, blood stains):0.8] | DDIM CFG 11 768x512
池核: masterpiece, detailed, poolcore, liminal space, dream pools, the pool is so clean that you can see the tiles and steps under it, underwater shot, photographic, flowing water, a black hole under the water, hyper-realism, CG, detailed shadow, overexposure, film texture | Euler a CFG 10 512x512
网核: masterpiece, highly detailed, windows_xp_screen_cap, video_game_website_page AND an_email_page AND windows_xp_start_menu, message_box AND old_school_memes, noise | DDIM/Euler a CFG 12 1024x640
要点: 伤核/池核需定制负向（防人/防手/防自然物）

## 2.5-25 天使天城（云端城堡）
正面: (ultra-detailed), (best shadow), classic, (cinematic lighting), dynamic angle, (finely detail), (best masterpiece:1.6), (extremely detailed CG unity 8k wallpaper:1.45), extremely detailed illustration, [3d], (((solo))), (((An extremely delicated and beautiful) girl is spreading her (beautiful wings) and ((flying in the sky)))), (((She has an extremely detailed and beautiful cute anime face), extremely detailed body)), long white hair, bare shoulders, floating hair and detailed mouth, The girl is wearing (white hair ribbon) with black edge, (white translucent (silk) hood), white robe with (gold pattern), white boots with black pattern, detailed white stockings, (The background is very detailed), ((((There are many castles in the background)))), (The castles are ((on the clouds))), (Clouds surround the base of the castles), (Many birds fly in the sky), ((((There are many gorgeous colorful (hues)) at the top of the planting), and there are some (detailed) feathers falling in the sky), (((((The background is the sky at dawn))))), (The light of dawn blooms gloriously), The painting depicts a scene with many well-defined clouds have beautiful light and shadow
负向: 长负面（防缺人/防小/防嘴/防金城堡/防衣褶等）
参数: Steps 50-350, 低步数 ddim 高步数 ddim/euler a, CFG 7, e6e8e1fc, Clip skip 2, size 2:1 | 尽量 1408x704+

## 2.5-26 东方降魔（太极/符咒龙）
正面: ((illustration)), ((floating hair)), ((extremely_detailed_eyes_and_face)), ((chromatic aberration)), ((caustic)), lens flare, dynamic angle, ((portrait)), (1 girl), ((solo)), ((cute face)), ((hidden hands)), asymmetrical bangs, eye shadow, ((Giant Tai Chi)), ((colorful refraction)), (beautiful detailed sky), ((dark intense shadows)), ((cinematic lighting)), ((overexposure)), (expressionless), blank stare, big top sleeves, ((frills)), (((small breast))), pleated skirt, ((sharp focus)), ((masterpiece)), (((best quality))), ((extremely detailed)), colorful, hdr, (((cheongsam))), (((Exquisite Chinese sword))), ((Scattered runes)), (((magnificent ancient pagoda))), Architectural community, Fluttering long hair, (((Mysterious Dragon))), gentle wind, (((Yellow paper all over the sky))), ((Spells written on paper)), (Yellow paper all over the sky), ((Antique glasses)), Dragon pattern, ((A solemn atmosphere)), (beautiful and delicate eyes), ((Black and white dress pattern)), (Yellow glass light column), ((mysterious)), ((Chinese architecture))
负向: 通用负面 + Humpbacked
参数: Steps 50, Scale 5.5, Euler, 512x1024

## 2.5-27 黑液少女（black goo 泼墨）
正面: masterpiece, wallpaper, (highly detailed), [street, wall:(1girl), (solo), pale skin, [black eyes|red eyes], (hollow eyes), black hair, long hair, (liquid hair:1.2), floating hair, bangs, expressionless, (black goo:1.4), (white dress:1.2), (white skirt), white, intricated filigree, (stained clothes:1.2):0.25], (black goo:1.4), (black dripping), (black splashing:0.85), (tentacles:0.85), shiny, [:face focus, upper body, (cowboy shot), lateral view, dutch angle, dynamic:0.25], [white background|black goo], volumetric lighting, (high contrast:0.85), (limited palette:0.65)
负向: 通用负面
参数: Steps 30, DPM++ 2S a, CFG 12, 960x640, e6e8e1fc, Eta 0.68, Clip skip 2, ENSD 31337
要点: 无 ink 也能泼出扁平化水墨；black goo 多次描述必要

## 2.5-28 铅笔草稿（sketch paper 天使）
正面: masterpiece, best quality, floating, beautiful detailed eyes, (angel), blush, (back), floating hair, (sketch paper:1.1), (pencils), graphite, drawing board, partially colored, spot color
负向: 长负面（防多种怪物/草图/模糊等）
参数: Steps 50, Euler a, CFG 11, 768x768

## 2.5-29 双子镜（冰火双王对称分屏）
正面: (extremely CG, best quality), (best illumination, best shadow), 8k wallpaper, (2King look at each other), (beautiful and detailed girl) with (beautiful and detailed face) with (blue long hair) with (blue eyes) with (flower necklace) with ([white:0.8|blue|golden] long sleeves lace layered long dress) with (black waistband) with (full body) with (flower:1.2)+(pretty blue ice:1.25)+(blue Ice crystals texture the wings:1.3) inside (floating palace:1.3), (half decorational vertical border in the middle), (Symmetry split theme and screen:1.4), (beautiful and detailed girl) with (beautiful and detailed face) with (red long hair:1.35) with (red eyes) with (flower necklace) with (([red|black|silver:3.0] long sleeves lace layered long dress)) with (black waistband) with (full body) with (flower:1.35)+(pretty red fire:1.32)+(red Wings covered in flame:1.4) inside (floating palace:1.3), [[delicate fingers and hands:0.5]::0.85]
负向: (Mutant hand:1.3), (mutated fingers:1.5), (Mutant legs:1.3), (mutation, poorly drawn :1.2), liquid body, text font ui, long neck, (uncoordinated body:1.3), fused ears, (ugly:1.5), (huge breasts:1.5), the extra finger, the missing finger, long finger, masterpiece
参数: Steps 150, DPM++ 2S a Karras, CFG 4.7, 1408x768, 925997e9, Eta 0.667, Clip skip 2

## 2.5-30 太空舱少女（宇航服）
正面: (((masterpiece, best quality, an extremely delicate and beautiful, illustration))), (from side, medium long shot), ((a cute_detailed_girl in spacesuit, beautiful_detailed_face in aerospace_helmet)), (((upper body))), (disheveled hair:0.3), (((clouds:0.3), multiple_luna, (floating_fortress technology machinery), night sky background)), (cyberpunk_aerospace_helmet)
负向: 通用负面
参数: Steps 30, DDIM, CFG 7, 1024x576, e6e8e1fc
