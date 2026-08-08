# 《元素法典》文本配方库（recipes.json 的数据镜像）
# 从腾讯文档 textPool 提取的 62 套配方，JSON 格式，供程序化调用
# 字段：id, positive, negative, params
# 完整 JSON 在 E:/ai1/comfyui_workflow/recipes.json（62 条）
# 本文件是说明文档，实际数据请读取 recipes.json 或 skill 内 recipes.json

# 快速用法（Python）：
# import json
# with open('E:/ai1/comfyui_workflow/recipes.json', encoding='utf-8') as f:
#     recipes = json.load(f)
# # 按关键词筛选（如 ice）：
# hits = [r for r in recipes if 'ice' in r['positive'].lower()]

# 配方类别速查（手动归类，非官方）：
# 水/冰/自然：1 水魔法, 2 冰魔法, 7 森林冰, 8 冰火法, 9 森火法, 11 水森法, 12 水下法, 28 自然法, 29 森林法, 30 蔷薇法
# 星空/幻境：4 星空法, 13 幻之时, 14 星源法, 15 星霞海, 16 星冰乐, 17 月亮法, 31 泡泡法, 35 彩虹法, 55 星霞海-3, 57 星源法-2
# 机械/奇幻：18 机凯种, 19 机娘水, 20 龙机法, 21 战姬法, 22 黄金法, 23 死灵法, 24 水晶法, 52 龙骑士
# 人物/风格：25 圣光法, 26 雷男法, 27 苇名法, 32 冬雪法, 33 雪月法, 34 火烧云, 36 炼银术, 37 唤龙术, 38 血魔法, 39 坠落法, 40 秘境法, 41 摄影法, 42 摩登法, 43 学院法, 44 浮世绘, 45 绚丽术, 46 星霞海-2
# 深渊/暗黑：47 暗锁法, 48 望穿水, 49 白骨法-2, 50 森火法-2, 51 血魔法-2
# 风景/背景：53 城堡法, 54 黄昏法
# 特殊：56 星冰乐-2, 58 刻刻帝
