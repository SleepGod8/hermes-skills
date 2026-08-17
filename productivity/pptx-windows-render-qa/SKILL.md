---
name: pptx-windows-render-qa
description: "Use when Windows上做PPT。pptxgenjs→PowerPoint COM→qwen-vl看排版"
version: 1.0.0
author: Hermes Agent (2026-08 实测)
tags: [powerpoint, pptx, windows, com, qa, rendering]
platforms: [windows]
metadata:
  hermes:
    tags: [powerpoint, pptx, windows, com, qa, rendering]
    category: productivity
---

# Windows PPT 生成与渲染 QA（实测工作流）

在 Windows 本机（无 LibreOffice/poppler，装有 Microsoft Office）生成答辩/汇报 PPT 并做视觉 QA 的完整闭环。2026-08 实测（智能财富管家答辩 PPT，15 页全通过）。

## 一、生成（pptxgenjs）

```bash
npm install pptxgenjs   # 一次性
node gen_ppt.js         # 脚本用 pptxgenjs 生成 .pptx
```

关键点：
- `LAYOUT_WIDE` = 13.3" × 7.5"，坐标超界不会被 clamp，直接画在页面外 → 布局函数要按卡片数自适应宽度并居中（多卡片行尤其注意右边界截断）
- 颜色 hex 不带 `#`、不带 alpha（pptxgenjs 会损坏文件）
- 中文用 `fontFace: "Microsoft YaHei"`

## 二、渲染导出（PowerPoint COM，替代 LibreOffice）

本机无 LibreOffice/poppler，但有 Office 16（`C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE`）→ 用 pywin32 COM：

```python
import win32com.client, os
ppt = win32com.client.Dispatch("PowerPoint.Application")
pres = ppt.Presentations.Open(pptx_path, True, False, False)  # 只读、无窗口
pres.SaveAs(pdf_path, 32)              # 32 = ppSaveAsPDF
for i in range(1, pres.Slides.Count + 1):
    pres.Slides(i).Export(png_path, "PNG", 1600, 900)  # 逐页 PNG
pres.Close(); ppt.Quit()
```

⚠️ 坑：
- **不要用 PowerShell .ps1 脚本传中文路径**（乱码 + 0x80070003）。用 Python COM（pywin32），中文路径 OK
- 每次改脚本后要重新生成 → 重新导出 PNG（PPTX 是快照，PDF 不会自动更新）
- 依赖：`pip install pywin32`（本机已装）

## 三、视觉 QA（qwen-vl-plus 直连）

`vision_analyze` 工具走主模型（DeepSeek 单模态不支持图）会报 image_url 400 → 改直连 DashScope：

```python
# .env 读 DASHSCOPE_API_KEY
# POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
# model: qwen-vl-plus, messages: [{image_url: data:image/png;base64,...}, {text: 检查问题}]
```

检查 prompt 要点：文字是否溢出卡片/重叠、表格是否错位、元素是否超页边界、信息是否拥挤。
qwen-vl 有时把「无问题」描述得很长而没出现「无问题」字样 → 判断用关键词兜底（看具体内容，不全靠 flag）。
关键页（改动页/复杂流程图）要额外追问细节（逐字读出某区域内容），不能只信一次检查。

## 四、交付

- 交付 .pptx + .pdf 双份（PDF 用于预览）
- PDF 用 COM SaveAs(32) 同步生成，改 PPT 后必须重新生成

## 相关技能

- `powerpoint`（bundled，pptxgenjs API/设计规范；本 skill 补 Windows 渲染 QA 差异）
- 看图用 qwen-vl：见记忆「看图方案」
