# -*- coding: utf-8 -*-
"""复刻扫描件的 python-docx 起手模板：改 CONTENT 与页边距/字号即可。

要点：
  * 中文字体必须同时设 w:ascii / w:hAnsi / w:eastAsia，否则 Word 中文回退字体；
  * 行距用「固定值」(EXACTLY) 才能与扫描件逐行对齐，倍数行距随字号浮动对不上；
  * 下划线填空 = 带 underline 的 run，前后用半角/全角空格补足空白宽度；
  * 落款右对齐用 right_indent 控制右沿位置。
"""
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

# ==== 按实测填这里 ====
OUT = r"E:/Hermes workspace/output/重建文档.docx"
CJK_FONT = "SimSun"        # 宋体
BODY_SIZE = 14             # 四号 = 14pt（实测字宽 30.1px @1280px 宽）
TITLE_SIZE = 22            # 二号 = 22pt
BODY_LINE_PT = 31.4        # 固定行距 = 相邻行顶差 67px / 2.15
INDENT_2CH = Pt(BODY_SIZE * 2)
# 正文段落: [(文本, 是否下划线), ...]
CONTENT = [
    ("兹证明", False), ("　游鑫　", True), ("（身份证号：…）自", False),
    (" 2023 ", True), ("年", False), (" 07 ", True), ("月", False),
    (" 03 ", True), ("日至", False), (" 2026 ", True), ("年", False),
    (" 08 ", True), ("月", False), (" 14 ", True),
    ("日期间在我公司任职", False), ("　AI应用开发工程师　", True),
    ("岗位，现已于", False), (" 2026 ", True), ("年", False),
    (" 08 ", True), ("月", False), (" 14 ", True),
    ("日与我公司解除劳动关系，其离职后　　□需要/☑不需要履行竞业限制义务。", False),
]
FOOTER = [("公司名称", 4), ("2026年08月14日", 0)]   # (文本, 段后pt)


def set_run(run, size=BODY_SIZE, bold=False, underline=False, font=CJK_FONT):
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = rpr.makeelement(qn("w:rFonts"), {})
        rpr.insert(0, rf)
    rf.set(qn("w:ascii"), font)
    rf.set(qn("w:hAnsi"), font)
    rf.set(qn("w:eastAsia"), CJK_FONT)     # 中文必须单独指定
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.underline = underline


def body_para(doc, parts, first_indent=INDENT_2CH, left_indent=None,
              space_after=0, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_pt=BODY_LINE_PT):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY   # 固定行距，勿用倍数
    pf.line_spacing = Pt(line_pt)
    if left_indent is not None:
        pf.left_indent = left_indent
    if first_indent is not None:
        pf.first_line_indent = first_indent
    for text, ul in parts:
        set_run(p.add_run(text), underline=ul)
    return p


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.2)
sec.left_margin = sec.right_margin = Cm(3.1)

normal = doc.styles["Normal"]
normal.font.name = CJK_FONT
normal.font.size = Pt(BODY_SIZE)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), CJK_FONT)

t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.paragraph_format.space_after = Pt(27)          # 与首行间距按实测调
t.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
t.paragraph_format.line_spacing = Pt(30)
set_run(t.add_run("文档标题"), size=TITLE_SIZE, bold=True)

body_para(doc, CONTENT, left_indent=Cm(0.36), first_indent=Cm(0.54))
body_para(doc, [("注:其他段落…", False)])
body_para(doc, [("本证明自盖章之日起生效，复印件及涂改无效。", False)])
body_para(doc, [("特此证明。", False)], space_after=70)

for text, after in FOOTER:                       # 落款：右对齐 + 右缩进
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.right_indent = Cm(0.76)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    p.paragraph_format.line_spacing = Pt(BODY_LINE_PT)
    set_run(p.add_run(text))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)
print(OUT)
