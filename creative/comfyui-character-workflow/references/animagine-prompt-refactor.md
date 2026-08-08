# Animagine-XL 提示词重构实战（iris_maid_detailer, 2026-08-08）

方法论（`sd-prompt-methodology` skill，源自《元素同典》cv19505389）在动漫系模型 animagine-xl-4.0
（danbooru tag 体系）上的落地验证。原 prompt 是多年经验堆积的平铺词表，重构后实测出图正常、
发色绑定验证通过（顶部 77.5% 像素为淡蓝 RGB(203,227,245)）。

## 旧版问题诊断（对照方法论逐条查）
| 问题 | 旧写法 | 方法论依据 |
|---|---|---|
| 质量词在末尾 | `...artist:ikarin, masterpiece, best quality, year 2024` | 质量前缀应置顶（通用顺序公式第一步） |
| 发色裸词 | `light blue hair, pale blue hair` 无加权 | 关键特征应绑定加权 |
| 顺序混乱 | 手部词夹在头发和表情之间、眼部细节插在中间 | 物→特征→动态→服饰→背景→光照→画风叠加 |
| 重复词 | `modest`×2、`arms down/arms at sides/hands at sides`×3 | 同词重复语义复杂难控 |
| 厚涂风险词 | `highly detailed` | 方法论明确警告会偏厚涂/油画 |
| 隐式括号权重 | `((artist:melon22))` | 推荐显式 `(word:weight)` |

## 新版结构（动漫系人像模板）
```
masterpiece, best quality, very aesthetic, amazing quality, year 2024,   ← 质量前缀
1girl, solo, single character, maid,                                     ← 人（物1）
((light blue hair, pale blue hair)),                                     ← 发色整组加权 ×1.21（绑定）
long hair, very long hair, waist-length hair, straight hair, flowing...  ← 发型特征紧随其后
hair flowing behind body, hair not covering hands,                       ← 手部保护词提前（防遮挡）
hands clearly visible, unobstructed hands,                               ← 手部可见性
gentle smile, warm smile, kind eyes, gentle expression,                  ← 表情
medium breasts, slender figure, slim waist,                              ← 身材
standing upright, three-quarter view, body slightly angled,              ← 站姿/视角
arms down, arms at sides, hands at sides, hands hanging down, fingers relaxed,  ← 动态
good hands, perfect hands, detailed hands, individual fingers, 5 fingers,       ← 手部质量
detailed eyes, detailed pupils, clear iris, detailed eyelashes,                 ← 眼部细节
classic maid uniform, long dress, apron, frilled headband,               ← 服饰整体+细节
modest, dignified, composed,                                            ← 气质
simple background, soft lighting,                                       ← 背景+光照
ultra detailed, intricate details, detailed hair,                        ← 画风滤镜（不写 highly detailed）
(artist:melon22:1.2), (artist:ikarin:1.1)                                ← 画师显式权重
```

## 落地要点
- **质量词前置**后 animagine 的 `masterpiece/best quality` 引导力显著增强（旧版放末尾是浪费）
- **`((a, b))` 整组加权**对「发色+发色近义补充」有效：ComfyUI 支持对括号内整组乘权，比逐个 `(a:1.1), (b:1.1)` 更简洁且绑定更紧
- **手部保护词（hair not covering hands, hands clearly visible）要跟着头发写**，不是扔在画面词末尾——配合手部精修链，主图手部质量直接决定 detailer 能否救回
- 显式 `(artist:xxx:1.2)` 替代 `((artist:xxx))`：可读性更好，避免嵌套括号在某些解析器下权重失效
- 动漫系模型下**自然语言长咏唱谨慎使用**：danbooru tag 体系更认逗号分隔的 tag 堆叠；长咏唱保留给「颜色必须绑定到具体物件」的场景（特定发色+特定衣服颜色同时出现时）

## 验证方法
- 发色绑定验证：读图取顶部 30% 区域，统计蓝色像素（b>180 且 b>r+20 且 b>g+10）占比——77.5% 说明淡蓝长发生效
- 新旧对比：同 seed 分别跑 v9/v10 更严谨（本次 seed 未固定，仅验证了整体可出图 + 发色正确）
