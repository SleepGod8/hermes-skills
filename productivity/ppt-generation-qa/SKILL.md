---
name: ppt-generation-qa
description: "Use when 生成/QA答辩PPT. pptxgenjs+PowerPoint COM+qwen-vl视觉验收。"
version: 1.0.0
tags: [pptx, presentation, ppt, qa, vision, windows]
platforms: [windows]
---

# PPT 生成 + 视觉 QA 闭环（Windows）

程序化生成 .pptx（pptxgenjs）+ PowerPoint COM 渲染 + qwen-vl-plus 视觉验收的完整流水线。单模态 LLM（DeepSeek）做内容与代码完全够用——视觉由外挂模型兜底（本机实测 14 页答辩 PPT 全流程跑通）。

## 触发条件

- 主人要求制作 PPT / 答辩 PPT / 演示文稿 / deck
- 需要把项目文档（README/架构/需求/评分标准）转成汇报演示

## 模型选择结论（与主人已对齐）

- 常规汇报型 PPT：DeepSeek 足够——瓶颈在内容逻辑与设计规范，不在模型智商
- 高难度（数据密集/深度归纳/答辩问答预测）：可切 gpt-5.6-sol（ASLNet provider，key 在 .env）
- 视觉验收永远用 qwen-vl-plus 外挂（DashScope，免费国内直连），不依赖主模型多模态
- 答辩 PPT 按评分标准倒推设计（评分项→专页），内容全部来自真实文档不编造数字

## 流水线

1. **侦察内容源**：读 README / 架构文档 / 需求文档 / 评分标准 / 负责域任务书，扩写 PPT 规格 → 主人审阅（v2 交互模式）
2. **pptxgenjs 生成**：`npm i pptxgenjs`；`defineLayout WIDE 13.3x7.5`；先设 layout 后加页；hex 颜色不带 `#`（`"FF0000"`）
3. **PowerPoint COM 渲染 PDF**：python win32com，`pres.SaveAs(pdf_path, 32)`（32=ppSaveAsPDF）
4. **PowerPoint COM 导出 PNG**：`slide.Export(out, "PNG", 1600, 900)` 逐页导出（比 PDF→图片工具链稳）
5. **qwen-vl-plus 逐页视觉 QA**：DashScope compatible-mode 直连，图片 base64 data URL（见坑清单）
6. 发现问题 → 改脚本 → 重新生成 → 重新渲染 → 重新 QA（循环，改后必须重跑渲染）

## 坑清单（本机实测）

- **read_file 误判 UTF-8 中文文件为 binary**（`"Binary file - cannot display"`）→ 用 Python `utf-8-sig` 读取，别用 read_file
- **PowerShell 脚本传中文路径乱码**（HRESULT 0x80070003）→ 一律用 python win32com 而不是 .ps1 调 COM
- **vision_analyze 对 qwen-vl（DashScope custom provider）报 image_url 格式错** → 直接 python/curl 调 `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`，图片 `data:image/png;base64,...`
- **pymupdf 不可靠**：execute_code 沙箱 import 不到、pip→3.13 与 python→3.12 错位 → 导出 PNG 直接用 PowerPoint COM `Slide.Export`，不依赖 PDF 工具链
- **skill 创建 description 必须 ≤60 字符**，否则被拒（写触发语放前面）
- 生成脚本放 workspace 后 `node gen_ppt.js` 输出到项目目录；文件名用中文没问题（COM 层 OK）

## 视觉 QA 提示词模板

```
这是答辩PPT第N页。检查：1.文字是否溢出卡片/重叠 2.表格是否错位 3.元素是否超出页面边界 4.信息是否拥挤无法阅读。无问题就说'无问题'。
```

逐页调用，页间 sleep 0.5s 防限流；返回含"无问题"即通过。

## 设计模板参考

- `references/defense-deck-outline.md` — 答辩 PPT 14 页结构模板（按评分标准倒推设计，可直接套用改内容）
