---
name: pptx-render-qa-windows
description: "Use when 生成PPT后需渲染与视觉QA。pptxgenjs→PowerPoint COM→qwen-vl检查。"
version: 1.0.0
author: Hermes Agent (learned from session 2026-08)
tags: [pptx, powerpoint, render, qa, windows, vision, qwen-vl]
platforms: [windows]
metadata:
  hermes:
    tags: [pptx, powerpoint, render, qa, windows, vision, qwen-vl]
    category: productivity
---

# PPTX 渲染与视觉 QA 工作流（Windows）

> 定位：与 bundled `powerpoint` 技能互补。`powerpoint` 管生成（pptxgenjs 脚本），本技能管**渲染验证闭环**：生成后必须渲染成图、逐页视觉检查、确认无溢出/重叠/越界再交付。

## 触发条件

- 用 pptxgenjs / python-pptx 生成了 .pptx，需要验证排版质量
- 用户要求「渲染看看」「检查排版」「QA」
- 答辩/汇报类 PPT 交付前必做

## 流水线（4 步闭环）

```text
① 生成 .pptx（pptxgenjs，见 bundled powerpoint 技能）
② PowerPoint COM 转 PDF（可选交付物）+ 导出每页 PNG
③ qwen-vl-plus 直连 API 逐页视觉检查（溢出/重叠/越界/拥挤）
④ 发现问题 → 改生成脚本 → 重新生成 → 重跑 ②③（必须重新渲染！）
```

## ② 渲染：PowerPoint COM（pywin32）

```python
import win32com.client, os
ppt = win32com.client.Dispatch("PowerPoint.Application")
pres = ppt.Presentations.Open(pptx_path, True, False, False)
pres.SaveAs(pdf_path, 32)              # 32 = ppSaveAsPDF
for i in range(1, pres.Slides.Count + 1):
    pres.Slides(i).Export(os.path.join(out_dir, f"slide-{i:02d}.png"), "PNG", 1600, 900)
pres.Close()
ppt.Quit()
```

## ③ 视觉 QA：qwen-vl-plus 直连 DashScope（不是 vision_analyze！）

**关键坑**：`vision_analyze` 走主模型/DashScope custom provider 时可能报 `400 unknown variant image_url`。可靠路径是**直连 DashScope OpenAI 兼容端点**，图片转 base64 用 `data:image/png;base64,` 前缀：

```python
import base64, json, urllib.request
# key 从 ~/AppData/Local/hermes/.env 的 DASHSCOPE_API_KEY 读取
b64 = base64.b64encode(open(img_path, "rb").read()).decode()
payload = {
    "model": "qwen-vl-plus",
    "messages": [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        {"type": "text", "text": "这是答辩PPT第N页。检查：1.文字是否溢出卡片/重叠 2.表格是否错位 3.元素是否超出页面边界 4.信息是否拥挤。无问题就说'无问题'。"},
    ]}],
}
# POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
# 注意：逐页调用间 sleep 0.5s 避免限流；全量页检查约 40-50s
```

判断技巧：qwen-vl 若输出长段「无问题」描述而非简短回答，用 flag = "无问题" in content 判定；⚠️ 标记的页再单独追问细节（如「逐字读出底部红框文字」）确认是否真有问题——qwen-vl 有误报倾向，不当最终验收，重要页用二次追问交叉验证。

## 坑清单（全部实测）

1. **PowerShell .ps1 调 COM 中文路径必炸**：脚本里含中文路径（如 `E:\项目\...`）编码变乱码 → `0x80070003 DirectoryNotFoundException`。**用 Python pywin32 代替 PowerShell**，Python 源码 UTF-8 无此问题。
2. **pip 与 python 环境错位**：本机 `pip → python3.13` 但运行时 `python = 3.12`，`pip install pymupdf` 装到了错误的解释器，`import fitz` 失败。PDF→图**不要依赖 pymupdf**，直接用 PowerPoint `slide.Export(..., "PNG", w, h)` 一步到位，零额外依赖。
3. **`execute_code` 沙箱无项目包**：execute_code 用的解释器可能没有 pywin32/pymupdf，但 terminal 的 python 有。COM 操作放 execute_code 可用（pywin32 在沙箱里成功过），但装包后 import 的验证放 terminal。
4. **保存文件名用 .pptx 全路径**；PPT 打开时 ReadOnly=True, WithWindow=False 避免弹窗。
5. **PPT 页数变化后页码核对**：插入/删除页后，用正则把所有 `addFooter(s, N)` 按出现顺序列出来核对 1..N；**不要用全局 replace 改页码**（会误伤多处），要按页面上下文锚点精准替换（如「在『记忆不是交易权威源』之后的第一个 addFooter」）。
6. **PowerPoint COM 首次运行慢**（约 7-9s 打开+导出 14 页），属正常；`presentations.Open` 参数 `(path, ReadOnly, Untitled, WithWindow)` 缺一不可。

## 交付物

- .pptx 主交付 + .pdf 预览版（SaveAs 32 同步生成）
- 视觉 QA 记录：逐页 ✅/⚠️ + 重点页二次追问结果
- 渲染图片留在 `workspace/ppt_qa/` 供主人查看

## 答辩 PPT 设计模式

评分标准倒推页面设计 → 生成 → 问答预测（强模型）→ 按预测反向补防守点。完整模式见 `references/defense-ppt-pattern.md`。

## 相关

- 生成语法/设计规范（hex 不带 #、LAYOUT_WIDE 尺寸、模板编辑）：bundled `powerpoint`
- 视觉模型配 Key：DashScope（.env `DASHSCOPE_API_KEY`）
- 渲染脚本：`scripts/pptx_render_qa.py`
