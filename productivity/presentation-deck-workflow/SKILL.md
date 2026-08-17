---
name: presentation-deck-workflow
description: "Use when 主人要做PPT/答辩/汇报deck或问哪个模型做PPT好。深读文档→评分映射→规格→生成→视觉QA。"
version: 1.0.0
tags: [presentation, pptx, deck, defense, workflow, single-modal]
platforms: [linux, macos, windows]
---

# 演示文稿（PPT / 答辩 / 汇报）交付工作流

## 触发条件

- 用户要求制作 PPT / 答辩 PPT / 项目汇报 / deck / 幻灯片
- 用户问「哪个模型做 PPT 好」「单模态能不能做 PPT」「DeepSeek 适合做 PPT 吗」
- 用户提供项目目录要求产出介绍/答辩演示

## 模型选择判断（先回答，再干活）

**两种 AI 做 PPT 的方式必须分清：**

| 方式 | 原理 | 单模态 LLM（DeepSeek） |
|---|---|---|
| 图像生成式 | LLM 直接「画」整页幻灯片 | ❌ 不适合（纯文本模型无图像能力） |
| 代码生成式 | LLM 写 pptxgenjs/python-pptx 生成 .pptx | ✅ 完全适合（本质是写代码任务） |

**单模态 + 外挂视觉 QA = 质量达标**：
- 视觉验证用 qwen-vl-plus（DashScope custom，免费国内直连，主人已配）逐页看渲染图挑毛病
- 多模态 LLM（GPT-4o 类）优势是「开箱即用」——原生能看图自改，但配置好的单模态+外挂视觉差距通常 <10%
- 决定性因素排序：**内容逻辑 > 设计规范执行 > 视觉验证闭环 > 模型智商**——换模型提升有限，瓶颈不在模型
- GPT 类强模型只在「答辩问答预测/讲稿润色」阶段值得临时切（对抗性推理），PPT 主体不必
- 模型切换用 `/model` 会话内切（见 hermes-model-switching）

## 工作流（遵循交互模式 v2：口语需求→规格→主人审阅→执行）

1. **深读项目文档**：README / 架构总览 / 需求文档 / 评分标准 / 负责人 DRI 文档
2. **提取评分与约束**：答辩时长、模块权重、加分项、扣分红线 → **倒推页面设计**（权重高的模块专页讲）
3. **输出 PPT 规格**（页面规划 + 配色 + 每页核心内容 + 内容来源声明）→ 主人审阅确认
4. **生成**：按 powerpoint skill（pptxgenjs）写脚本生成 .pptx
5. **渲染 QA 闭环**（本机 Windows 实测两种路径）：
   - **路径 A（推荐，本机验证过）**：PowerPoint COM 渲染，不依赖 LibreOffice/poppler。用 `scripts/ppt_com_render.py`（pywin32 + win32com.client）：`Presentations.Open(path, True, False, False)` → `SaveAs(pdf, 32)` 转 PDF → `slide.Export(png, "PNG", 1600, 900)` 逐页出图。PowerPoint 在 `C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE`。
   - **路径 B**：LibreOffice 转 PDF → pdftoppm 转图片（仅当路径 A 不可用时）
   - 图片出来后用 qwen-vl-plus 逐页检查（溢出/重叠/配色），见下「视觉 QA」。
6. **交付** + 可选：答辩问答预测（此时可临时切强模型）

## 答辩 PPT 要点

- 时长约束决定页数：5 分钟 PPT ≈ 12-14 页，每页一个核心观点，页脚统一页码+项目名
- 页面按评分标准映射（P1-P5 权重表 → 每个高权重模块一页）
- 加分项（架构深度/创新功能/RAG 效果等）单独提炼成讲点，不淹没在正文
- 所有数字/规则必须来自真实文档原文（如「20 条规则、8 意图、申购>1万二次确认」），**绝不编造**
- 每页信息量：主标题 + 一张图/表 + 一句核心结论，杜绝大段文字

## 视觉 QA（qwen-vl-plus 直调法，实测）

- ⚠️ **`vision_analyze` 工具对 DashScope custom provider 会报错**：`unknown variant image_url, expected text`（400）。不要用它做 PPT 视觉 QA。
- **正确做法**：urllib 直调 DashScope OpenAI 兼容端点 `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`，模型 `qwen-vl-plus`，key 从 `~/AppData/Local/hermes/.env` 的 `DASHSCOPE_API_KEY` 读。图片转 base64 后以 `data:image/png;base64,...` 放 `image_url` 字段。逐页提问「文字是否溢出卡片/重叠、表格是否错位、是否越界、是否拥挤」，返回含「无问题」即通过。轮询间隔 0.5s 防限流。
- 视觉模型结果只做**粗筛**（溢出/重叠/越界），关键页（封面/数据密集页）再自己抽查一遍确认设计质感。

## 坑（实测）

1. **read_file 会把 UTF-8 BOM 中文 md 误判为 binary**（返回空）。改用 execute_code + `utf-8-sig`/`utf-16`/`gbk` 兜底读。README.md 常是 utf-8-sig。
2. pptxgenjs 细节（layout 默认 10"×5.625"、hex 不带 #）见 bundled `powerpoint` skill，照它的 gotchas 写。
3. 视觉 QA 必须重新渲染：改 .pptx 后 → 重新转 PDF/PNG → 再检查，四步全重跑，否则看的还是旧图。
4. skill 描述 ≤60 字符（系统提示预算），超长创建被拒。
5. 答辩/汇报场景模型建议先给选项（A DeepSeek 全流程 / B DeepSeek+GPT 精修 / C 全程 GPT），默认推荐 A + 答辩前 B 补问答预测。
6. **PowerShell 调 COM 转 PDF 中文路径会乱码失败**（HRESULT 0x80070003 DirectoryNotFound）。别写 .ps1 调 COM，用 Python pywin32（`win32com.client.Dispatch("PowerPoint.Application")`），中文路径无问题。
7. **pip 与 python 环境错位**：本机 `pip → python3.13` 但 `python → 3.12`（hermes venv）。pip 装的包（如 pymupdf）在 `python` 里 import 不到。要么用 `python -m pip`，要么直接用 PowerPoint COM 出 PNG（连 PDF 工具链都不用）。
8. **PPT 生成后一定要跑视觉 QA**：pptxgenjs 坐标越界是"写入但不报错"，只有渲染成图才能发现。14 页全查一遍约 50s（qwen-vl 逐页）。

## 参考样例

- `references/smart-wealth-defense-2026-08.md` — 首个实战样例：答辩 PPT 规格 v1（页面规划/配色/评分映射）
- `scripts/ppt_com_render.py` — PowerPoint COM 渲染脚本（pptx→PDF + 逐页 PNG），本机验证过，直接跑
- `scripts/qa_vision.py` — qwen-vl-plus 逐页视觉 QA（如存在）；否则照「视觉 QA」章节 urllib 直调即可
