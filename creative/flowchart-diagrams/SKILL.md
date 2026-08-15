---
name: flowchart-diagrams
description: "Use when 用户要流程图/工作流/泳道图. 生成 dark HTML+SVG 泳道/流程图."
version: 1.0.0
author: agent
license: MIT
tags: [diagram, flowchart, swimlane, svg, html, workflow, process]
platforms: [windows, macos, linux]
---

# Flowchart / Swimlane Diagrams (HTML + inline SVG)

Generate process / workflow / swimlane flowcharts as **standalone dark-theme HTML with inline SVG** — no build step, no libs, opens in any browser, prints cleanly for hand-copying.

## When to use

- 用户要「流程图 / 工作流 / 泳道图 / 角色分工图 / 流程设计 / 全链路示意」
- 需要区分多个角色主体（业务/产品/工程/AI 等）并展示 8~12 阶段的串行流程
- 需要标注「自动化 vs 必须人工判断」边界、反馈闭环

**与 architecture-diagram 的区别**：architecture-diagram 画 infra/组件框（前后端/DB/云服务，组件+连线）；本 skill 画**流程泳道图**（阶段列 × 角色行，带门禁和闭环）。用户要的是"流程怎么走、谁负责哪段、哪里要人拍板"时，用本 skill。

## Layout pattern（泳道图）

- **横向 = 阶段列**（S1..Sn，时间推进）；**纵向 = 角色泳道**（责任主体）。
- 常用 4 泳道：`业务客户 / 产品负责人 / 工程岗位(人类) / AI·Agent`。
- **角色配色（语义色）**：业务=sky `#38bdf8`、产品=amber `#fbbf24`、人类工程=cyan `#22d3ee`、AI=emerald `#34d399`。
- **人工判断门**：玫瑰色 `#fb7185` 虚线箭头 + `⚑人工判断` 标记——人类必须拍板的环节（需求确认/架构审核/Review/测试验收/部署审批/修复确认）。
- **反馈闭环**：玫瑰虚线 path——修复回流（问题修复→编码）、迭代闭环（持续迭代→需求理解）。

## Key technique（写 SVG 的要点）

- 纯 inline SVG 包在 `<div class=canvas>` 里，`overflow-x:auto` + `svg{min-width:...}`，宽图可横向滚动。
- 节点 = `<rect rx="7">` + 两行 `<text>`（角色名 bold + 动作小字），宽约 138px。
- 箭头用 `<defs><marker>` 定义三种：主流程=emerald 实线、交接=slate 细线、门禁/闭环=rose 虚线。
- 阶段表头：`S# + 名称 + 自动化徽标`（高自动=绿 / 半自动·人X=amber）。
- 图下方放 3 张「summary cards」（自动化边界 / 人工判断清单 / 闭环机制），让图自解释。

## Pitfalls

- **节点文字 ≤12 字/行**，否则溢出 138px 框；动作说明放第二行小字。
- **中文用 sans 字体栈**（`"PingFang SC","Microsoft YaHei",sans-serif`），别用 monospace，中文会糊。
- **浅色底打印/手绘更清晰**，深色底屏幕观感更好——用户要「打印手绘对照」时换浅色。
- **校验渲染**：browser 打开后查 console 无报错 + `document.querySelectorAll('svg rect').length > 0`（元素真的渲染了）。
- 坐标手工算容易错位：阶段列用固定 pitch（如 149px）+ 统一 node 宽（138px），先算好 stage center 数组再写节点。

## Template

- `templates/swimlane-flowchart.html` — 已验证可渲染的泳道图骨架（4 泳道 × 完整结构：marker 三种箭头、grid 背景、泳道色带、1 个示例阶段节点、图例 + summary cards）。复制后按 `<!-- repeat for S2..Sn -->` 扩阶段、改节点文案。
