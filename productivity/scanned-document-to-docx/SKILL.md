---
name: scanned-document-to-docx
description: Use when 扫描件/照片要复刻成同版式 Word（含去印章）。
---

# 扫描件/照片 → 同版式 Word 文档复刻

把一张证明/合同/表单的照片或扫描件，还原成**内容与格式一致、可编辑**的 .docx（常见附带要求：去掉印章/水印/签名）。

## 触发条件
- 「基于图片的内容，生成一份内容、格式相同的 word 文档」
- 「照着这张证明/合同/表单做个 word」
- 「不需要印章的内容」「去掉那个红章」
- 附带条件：输入是 jpg/png 扫描件或手机拍照，产物必须是可编辑 Word 而不是图片

## 铁律
1. **先定位源图**。这类请求里图片常常根本没进上下文（CLI/Studio 未注入附件）。用户说「基于图片」而你看不到图 → 立刻按 `references/locating-source-images.md` 去磁盘找，不要反问用户重发。
2. **小字必须双通道确认**。中文小字（公司名、姓名、身份证号）被红章压住时，一次视觉读取极易误读（本次 8 倍放大后仍把「成谷」看成「凌荟」）。必须用第二个 OCR 模型独立复核。
3. **不许口头声称「格式一致」**。必须先渲染成图，与原图做逐行像素比对（band y 坐标 + 左右边界 + 行宽），偏差 > 半个字就调参重跑，1–3 轮收敛。
4. **印章不进文档**。永远不要往 docx 插图片；交付前用 zipfile 确认 `word/media` 为空、无 `w:drawing`/`w:pict`。

## 工作流（按顺序，勿跳步）

| 步 | 动作 | 工具 |
|----|------|------|
| 0 | 定位源图（WeChat / Codex 会话 / Temp 目录） | `references/locating-source-images.md` |
| 1 | 转录：本地视觉读 + 第二 OCR 模型复核关键字段 | 下方「双通道转录」 |
| 2 | 像素级测量版式（行 band / 缩进 / 行距 / 下划线 / 页边距） | `scripts/measure_doc_layout.py` |
| 3 | 生成 docx | `templates/reconstruct_docx.py` 起手改 |
| 4 | 本机 Word 渲染成图（docx→PDF→PNG，宽度对齐原图） | `scripts/render_docx_win.py` |
| 5 | 逐行比对 + 调参重跑 | 下方「比对与调参」 |
| 6 | 回读校验 + 交付 | 下方「验证」「交付」 |

## 双通道转录（关键字段）
- 通道 A：自己看（`vision_analyze`，必要时 `region=` 放大；红章遮挡时先做通道分离再看）。
- 通道 B：第二个 OCR 模型，直接用 Hermes 现有配置里的 key 调 API（不要新配 provider）：
  - key 在 `~/AppData/Local/hermes/.env` 与 `config.yaml`（如 `DASHSCOPE_API_KEY`、ZhipuGLM key）。
  - `qwen-vl-plus`（DashScope compatible-mode）对中文小字最稳，**图片走 base64 data URL**；裁 2–3 块不同区域问同一问题，结果一致才落笔。
  - GLM-4.6v-flash 免费池常 429 → 带退避重试；连续 429 就换 qwen-vl-plus，别在这上面耗时间。
- 身份证号等数字逐位核对（本次 `360428199904295317` 由 OCR + 像素分组双重确认）。

## 测量 → Word 参数的换算（A4 扫描件，图宽 W px）
- 归一：`1px = 21cm/W`；A4 全宽时 `1pt = 2.15px`、`1cm ≈ 60.95px`（W=1280）
- **字号**：中文一字宽 = 1em = 字号。取一行纯汉字（标点按整字算），`字号pt = 行宽px / 字数 / 2.15`。例：30.1px → 14pt（四号）
- **行距**：相邻行 ink 顶 y 差 ≈ 行距。用「固定值」`WD_LINE_SPACING.EXACTLY` + `Pt(px/2.15)`；别用倍数行距（随字号浮动，对不上）。例：67px → 31.4pt
- **段首缩进**：段首行起点 − 同段续行起点；2 字符 = 2×字号。原文档可能「左缩进 + 首行缩进」混用 → 按测量值分别设 `left_indent` / `first_line_indent`
- **页边距**：文字块最小左沿 → 左边距；页面右沿 − 最大右沿 → 右边距。扫描件常有整体平移/裁切：**以文字块宽度为准、边距取对称值更接近原文档**（本次实测左 3.36/右 2.82，但整页右移 17px，取对称 3.1cm 更合理）
- **段间距**：某行 ink 顶差 > 行距的部分就是 `space_after`（本次「特此证明。」段后 ≈70pt）
- **下划线填空**：行内 `≥12px 连续黑像素` 的横 run = 下划线。重建用 `run(text, underline=True)`，前后各加空格补足空白宽度（数值字段半角空格、姓名/职位全角空格，按实测宽度选）
- **落款**：右对齐 + `right_indent`（= 正文右沿 − 落款右沿）；落款两行行距可能大于正文

## 文字还原注意
- **Word 自动加「中文与西文间距」**：汉字与数字/字母之间看起来有空隙是正常的、原图也有。不要为此给数字换字体或加字距——会把整行宽度和折行带偏。
- 中文文档半角冒号 `:` 与全角 `：` 常混用（本次「注:」「包括但不限于:」半角，括号内「身份证号：」全角）。可按行宽反推：半角冒号比整字少约 0.5 字。
- 勾选框用 `☐` / `☑`（Word 回退到符号字体），别用 Wingdings 字符（不可读、难编辑）。
- 换行位置：**优先自然折行**。只有自然折行怎么调都对不上时才插手动换行符——硬换行毁掉可编辑性。

## 比对与调参（第 5 步）
对原图与渲染图跑同一个 band 分析（`scripts/measure_doc_layout.py`），逐行对齐比较：
- y 坐标容差 ~5px；行宽容差 ~1%；**行数必须一致**
- 某行 ink 宽差 ≈ 1 个字 → 折行点漂了一位：微调页边距（±0.05cm）或缩进，**不要动字号**
- 整块纵向偏移 → 调标题/首段的 `space_after`
- 已知「假差异」不要修：扫描件笔画被阈值加粗，ink 高度比渲染大 3–6px（不是字号问题）；扫描件整页平移 10–20px（不是边距问题）

## 数字/像素处理
- 颜色分离：`lum = 0.299R+0.587G+0.114B`，`redness = R-(G+B)/2`
  - 黑字掩码：`lum < 170~190 且 redness < 25~35`
  - 红章掩码：`redness > 22~25`（其余置白）→ 黑字/印文可分别放大读
- 下划线检测：行 ink band 内找 `连续 ≥12px` 的横向 run
- 行/字符分组：行内列投影，按 gap 分组成字符，可确定字段宽度与位置

## 验证（交付前必须做完）
1. 用第二 OCR 模型转录音**渲染图**全文，与原图转录逐字比对（数字逐位）
2. band 表对照（y、左沿、右沿、行宽）
3. `python-docx` 回读：段落数、每段对齐/缩进/行距/段后、每个 run 的字号与 `underline`
4. `zipfile` 打开 docx：`word/media` 为空、无 `w:drawing`/`w:pict`（确认没把印章带进去）

## 环境（首次使用可能要补）
- `python -m pip install python-docx pymupdf`（Hermes 自带 python 里未必有）
- 渲染需要 `pywin32` + 本机 Microsoft Word（`C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE`）；无 Word 才退回 LibreOffice（`soffice --headless --convert-to pdf`）

## 交付
- 给 Windows 绝对路径的 Markdown 链接（尖括号包住，避免盘符冒号被解析），例如 `<E:/Hermes workspace/离职证明.docx>`
- 附一张渲染预览 PNG 让用户直接肉眼验收
- 明确说明：印章/水印按要求未包含，文字全部可编辑

## 支持文件
- `references/locating-source-images.md` — 用户说「基于图片」但上下文无图时，去哪些磁盘位置找
- `references/worked-example-离职证明.md` — 完整案例的测量数值、参数表与比对结果（可对照复用）
- `scripts/measure_doc_layout.py` — 扫描件版式测量（行 band、下划线、缩进、页边距）
- `scripts/render_docx_win.py` — Word COM 渲染 docx→PDF→PNG（宽度对齐原图，供像素比对）
- `templates/reconstruct_docx.py` — python-docx 复刻模板（CJK 字体/固定行距/首行缩进/下划线填空/右对齐落款）
