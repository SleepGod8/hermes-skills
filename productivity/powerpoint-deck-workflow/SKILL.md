---
name: powerpoint-deck-workflow
description: "Use when 主人要答辩/汇报PPT。pptxgenjs生成→COM导出→qwen-vl视觉QA闭环。"
version: 1.0.0
author: Hermes Agent (learned from session 2026-08)
tags: [pptx, powerpoint, presentation, 答辩, windows, com, qa]
platforms: [windows]
metadata:
  hermes:
    tags: [pptx, powerpoint, presentation, 答辩, windows, com, qa]
    category: productivity
---

# PowerPoint 答辩/汇报 PPT 生成工作流（Windows）

在 Windows 上从零生成高质量 .pptx 的完整闭环：**读文档 → 设计规格 → pptxgenjs 生成 → PowerPoint COM 导出 → qwen-vl 视觉 QA → 修复循环**。实战验证于 smart-wealth 答辩 PPT（15 页，2026-08）。

## 触发条件

- 主人要求制作答辩 PPT / 汇报 PPT / 演示文稿（.pptx）
- 需要从项目文档生成结构化演示
- 生成后需要视觉质量检查与迭代

## 环境要点（本机已具备）

- Node.js（v22）可用；`npm install pptxgenjs` 安装生成库
- **无需 LibreOffice/poppler**——本机装有 Microsoft Office，用 pywin32 调 PowerPoint COM 导出
- 视觉 QA 用 DashScope qwen-vl-plus（key 在 `~/.hermes/.env` 的 DASHSCOPE_API_KEY）
- Python 有 pywin32；pymupdf 的 pip/python 可能环境错位，**优先用 PowerPoint COM 直接导 PNG，不依赖 PDF 工具链**

## 标准工作流

### Phase 1：读文档 + 设计规格（交互模式 v2）

答辩 PPT 必须**从评分标准倒推设计**，不是介绍系统：
1. 深读项目文档（README/架构/需求/评分标准/负责人 DRI 文档），抓真实数字（阈值、规则数、表数），**不编造**
2. 按评分权重分配页面（权重高的模块专页讲）
3. 加分项/答辩讲点单独成页
4. 页面数 ≈ 答辩分钟数 × 2~3（5 分钟 ≈ 12-15 页）
5. 输出页面规划表给主人审阅 → 确认后才生成

### Phase 2：pptxgenjs 生成

- `LAYOUT_WIDE` = 13.3" × 7.5"
- 颜色：hex **不带 `#`**（`color: "0A1628"`），透明度用 `transparency: 0-100`
- 金融/科技风配色：深蓝背景 `0A1628` + 金色点缀 `C9A227`，微软雅黑
- 卡片式布局 + 表格 + 分层图（本技能自带 `scripts/ppt_qa.py` 做 QA）

### Phase 3：PowerPoint COM 导出（PDF + 逐页 PNG）

```python
import win32com.client
ppt = win32com.client.Dispatch("PowerPoint.Application")
pres = ppt.Presentations.Open(pptx_path, True, False, False)  # ReadOnly, Untitled, NoWindow
pres.SaveAs(pdf_path, 32)                  # 32 = ppSaveAsPDF
for i in range(1, pres.Slides.Count + 1):
    pres.Slides(i).Export(out_png, "PNG", 1600, 900)
pres.Close(); ppt.Quit()
```

### Phase 4：qwen-vl 视觉 QA（14-15 页逐页）

- 直接调 DashScope OpenAI 兼容端点（compatible-mode/v1/chat/completions），图片转 base64 data URL
- 每页问：文字溢出/重叠？表格错位？越界？拥挤？无问题就报"无问题"
- 对改动页做细节追问（逐字读出某段文字验证未截断）
- 工具脚本：`scripts/ppt_qa.py`（传入图片目录，逐页出报告）

### Phase 5：修复循环

改 `gen_ppt.js` → `node gen_ppt.js` → 重新导出 PNG → 重新 QA → 同步 PDF。**每次改动必须重跑导出**，PDF/PNG 不会自动反映脚本修改。

## 坑清单（全部实战踩过）

1. **卡片行溢出截断**：一行 5 个卡片却沿用 4 个卡片的间距算法 → 最后一个卡片超出右边界被截断。修复：`drawChain` 按行计算卡片宽度+间距并**居中**（`startX = (13.3 - totalW)/2`），各行独立参数。
2. **页码全局替换误伤**：`t.replace("addFooter(s, 13)", "addFooter(s, 14)")` 会替换多处 → 页码错乱。修复：用**上下文锚点**定位（如"记忆不是交易权威源"之后的那一个 footer），改完用 `re.findall` 校验页码序列为 1..N 且 addSlide 数 == addFooter 数。
3. **UTF-8 BOM 文件被 read_file 误判为二进制**：项目 md 带 BOM 时 read_file 返回 `is_binary: true`。修复：用 Python `open(path, encoding="utf-8-sig")` 读取。
4. **PowerShell .ps1 中文路径乱码失败**：`Presentations.Open("E:\项目\...")` 报 DirectoryNotFoundException。修复：改用 Python pywin32（UTF-8 原生支持中文路径），不要写 .ps1。
5. **pip/python 环境错位**：`pip show pymupdf` 有但 `import fitz` 失败（pip→3.13，python→3.12）。修复：不依赖 PyMuPDF，直接用 PowerPoint COM 导 PNG。
6. **答辩页信息密度**：每页一个主标题 + 一张图/表 + 一句核心结论，杜绝大段文字；主人钦定内容（评分标准、DRI 文档）逐字核对。

## 答辩加分技巧

- **问答预测反哺 PPT**：生成 PPT 后，用强模型（GPT 系）做「评委预计提问 + 参考回答」预测，把暴露的防守点（规格边界重叠、置信度来源、幂等性、事件补偿）提前补进 PPT——这是 6 处调整的实战来源。
- **演示红线用例**：故意让 C1 客户申购 R5 被拒、重复提交只执行一次，失败用例比成功页面更能证明系统可控。
- **trace_id 贯穿**：用一条完整业务链（如大额转账 9 步）串起跨 Agent 协作，比逐个 Agent 介绍更有说服力。

## 相关文件

- `scripts/ppt_qa.py` — qwen-vl 逐页视觉 QA 工具（传图片目录 + 页数范围）
- 与 bundled `powerpoint` 技能互补：本技能管 Windows 全流程落地（COM 导出 + QA 闭环），`powerpoint` 管 pptxgenjs API 细节
