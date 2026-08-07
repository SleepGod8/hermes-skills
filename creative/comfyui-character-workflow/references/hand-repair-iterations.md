# Athena 女仆手部精修迭代记录（2026-08）

Workflow: `E:\ai1\comfyui_workflow\athena_maid_detailer_api.json`
模型: animagine-xl-4.0, 1024×1536, 双手交叠身前姿势。原始问题：手部"时不时异常"（手指粘连/蹼指/数量错）。

## 单张修复迭代（v2 系列）—— 目标"修好一张"
| 版本 | 关键改动 | 结果 |
|---|---|---|
| v2 | 手叠手高权重 `((one hand resting on the other hand))`, denoise 0.5, cycle 2 | ❌ 手指粘连模糊 |
| v2.1 | denoise 0.7, dilation 30, guide 512, 手部提示词去掉姿势词 | ❌ 机械义体手（金属质感/分段指节/手腕管道） |
| v2.2 | denoise 0.58, 提示词加 soft skin/natural skin, 负向加 mechanical/robotic/claw | ✅ 恢复自然皮肤, 但左手指根蹼状粘连 |
| v2.3 | denoise 0.62, cycle 3, dilation 20, crop 3.2, guide 640; 正负提示词攻防完整 | ✅ 7.5/10 自然皮肤无粘连（单张成功） |

## 稳定性迭代（v3 系列）—— 目标"不再时不时异常"
| 版本 | 关键改动 | 结果 |
|---|---|---|
| v3.0 | 加 Hires fix(768→1024 denoise 0.35) + dpmpp_2m + "hands slightly apart" | ❌ 构图漂移, 手跑左下角, 幻视金色物件, detailer 没救回 |
| v3.1 | 回退提示词, 保留 dpmpp_2m | ❌ 手部位置仍漂移(搭腰/握物), 左手粘连 |
| v3.2 | 完全恢复 v2.3 配置(euler_ancestral 40 steps), 批量 6 seed | ⚠️ 成功率 50% (3/6), 失败全在画面左侧手并指 |
| v3.3 | 三 pass 交叉检测: v9c主力(0.65)→v8s补漏(0.6)→脸(0.45)→v8s收尾(0.5); bbox_threshold 0.25 | ✅ 成功率 75% (3/4), 最好 7 分; 失败 1 张手垂到底部边缘漏检 |

## 垂放姿势迭代（v4 系列, 主人指定 2026-08-07）
| 版本 | 关键改动 | 结果 |
|---|---|---|
| v4.0 | 主 prompt 改 `arms down, arms relaxed at sides, hands at sides, hands hanging down naturally`; **负向删掉 arms/hands at sides、hanging down 等压制词**; 保留三 pass | ✅ 75% (3/4), seed 42 达 **8/10**（比交叠的 7 分更好）; 失败 seed 13579 是手垂到 y0.87 底部被漏检 → 可加 `hands near waist level` 或加大 dilation |

## Iris 画像验证（2026-08-07, workflow: iris_maid_detailer_api.json）
- 角色配方: lavender hair(薰衣草紫长发, 整体 8.5-9/10 完美还原) + gentle smile + medium breasts + 双手垂放
- seed 42: 整体 8.5-9/10, 但**前伸的手(画面左侧)特写畸形 2/10**（荧光色+多指）, 垂放的手 7/10 → 印证\"姿势越简单手越稳\"
- ⚠️ bbox_threshold 0.25 误检爆炸: Iris 布局检测到 5~11 个 segment（围裙花边/蕾丝误检）, 单张 **85 分钟**（20+ 次 30 步采样）; 提速 = threshold 0.35 + cycle 3→2 / 2→1（~35 分钟, 质量几乎不降）

### Iris v3 简化构图（最终成功, 2026-08-07）
前 4 张（v1 旧参数 seed42/2024 + v2 提速 seed42/777）手部全失败——紫发飘散覆盖手部区域，检测器分不清手和发丝，detailer 修不动。成功改动：
| 改动 | 内容 |
|---|---|
| 主正向头发收束 | 加 `hair flowing behind body, hair swept back behind shoulders, hair not covering hands, hands clearly visible, unobstructed hands` |
| 手detailer正向 | 头部加 `hands not covered by hair, unobstructed hands, clear hands` |
| 手detailer负向 | 头部加 `hair over hands, hair covering hands, hair wrapped around hands, hair in front of hands` |
| 侧身构图 | 让一只手入镜(轻放裙摆)、另一只手不入镜，避开双手难题 |

结果：seed 42 右手 8/10(左手被裙摆遮挡 2/10) → seed 777 失败 → **seed 2024 左手 8/10、右手未入镜、整体 9/10** ✅。提速收益：误检减少后 seed 42 仅 200s。
经验：**构图里大色块/发丝/装饰物覆盖手部区域 = 检测器误检 + 修复无效**；prompt 层"把干扰物从手部区域挪走"比调 detailer 参数更根本。

## 验证过的最优参数（v2.3）
- 主采样: **euler_ancestral + normal, 40 steps, cfg 7**（构图稳定性关键; dpmpp_2m 会漂移构图）
- 手部 FaceDetailer: denoise 0.62, cycle 3, bbox_threshold 0.3, bbox_dilation 20, bbox_crop_factor 3.2, guide_size 640, max_size 896, sam_threshold 0.8, feather 10, dpmpp_2m/karras, steps 30
- 主提示词手势: `hands gently resting in front of waist, natural hand pose`（避免高权重交叠词）
- 手部正向: good hands, perfect hands, 5 fingers, individual fingers, fingers spread apart, separated finger bases, soft skin, natural skin texture, normal hand proportions
  （**避免 slender/elegant/detailed finger joints → 机械感**）
- 手部负向: 坏手全套 + webbed fingers, finger webbing, connected fingers, fused finger bases + mechanical hands, robotic hands, metallic hands, claw hands, elongated fingers

## 失败模式与假设
- 失败 3 张全是画面左侧手并指 → 疑似 hand_yolov8s 漏检左侧手（手小+围裙低对比度），FaceDetailer 未检测即跳过 → v3.3 双检测器交叉覆盖
- 手部检测模型: `bbox/hand_yolov8s.pt` 与 `bbox/hand_yolov9c.pt` 都在本地（v9c 51MB, 8月6日装）
- 手部 LoRA 路线: Civitai 直连/代理均失败（国内网络 + Civitai 现在要 API key）; 需要时走 hf-mirror 找替代源

## 工具链坑
- POST /prompt 用 Python urllib（curl -d @file 在 git-bash 报 "No prompt provided"）
- `LatentUpscaleBy` 参数名是 `upscale_method`（非 method）
- 批量等待 >5 分钟用 terminal background 轮询（execute_code 只有 5 分钟上限）
- vision 检查: 先整图定位手（x/y 比例），裁剪后转 ~800px JPEG 避免 400 too-large; 辅助 vision 偶尔 404（glm-4.6v-flash not found）→ 重试
