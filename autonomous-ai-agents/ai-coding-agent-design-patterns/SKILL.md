---
name: ai-coding-agent-design-patterns
description: Use when 问外部 AI agent 项目有何可借鉴。拆解设计模式并落地。
version: 1.0.0
tags: [ai-coding-agent, design-patterns, gstack, orchestration]
metadata:
  hermes:
    tags: [ai-coding-agent, design-patterns, gstack, orchestration]
    category: autonomous-ai-agents
---

# AI 编程 Agent 设计模式参考

> 定位：拆解外部 AI 编程 agent 项目（Claude Code 生态、gstack、OpenClaw 等）的设计模式，评估可借鉴性并落地到 Hermes 多智能体体系。

## 触发条件

- 用户问「gstack / OpenClaw / 某 AI agent 项目有什么可借鉴」
- 用户要求「参考 X 项目做 Y」或「把 X 的设计搬过来」
- 需要从外部 agent 项目提炼审查 / 编排 / 模型适配等机制

## 借鉴方法论（3 步）

1. **拆本质，不套表象**：先读源码看清机制的真正作用（例：model-overlays 的本质是「模型行为怪癖 + 补偿指令」，不是「格式适配」——只看目录名会误判）。
2. **映射到现有体系**：问「这个机制在我们已有的协议里对应哪个环节、有没有已覆盖的部分」，避免重复造轮子（例：gstack 的结构化 findings 映射到 review-findings-calibration.md）。
3. **评估优先级**：按「是否命中用户真实痛点 / 是否与现有机制互补 / 落地成本」排序，优先做「最后一公里」增量而非整套搬运。

## 关键原则（借鉴时必守）

1. **人格特质 ≠ 职能岗位**：毒舌、冷静等人格语气只用于日常，不能作为分配职能的依据。审查/测试职能要求独立性，归独立审查岗。
2. **审查独立于实现**：审查者不能审查自己参与实现的代码，否则对抗价值作废。
3. **借鉴 = 增量补强，不是整套替换**：落地时映射到现有版本号（如 review-findings-calibration.md 的 v1.6→v1.7→v1.8），保留原有缺陷等级（P0-P3）等约定。

## 已拆解项目

| 项目 | 详情 |
|------|------|
| garrytan/gstack | 见 `references/gstack-design-analysis.md`——23 工具 4 层结构、8 大设计模式、已借鉴/未借鉴映射、关键教训 |

## 参考

- `references/gstack-design-analysis.md` — gstack 完整设计拆解（工具清单、设计模式本质、借鉴映射、model-overlays/review-army 真相）
