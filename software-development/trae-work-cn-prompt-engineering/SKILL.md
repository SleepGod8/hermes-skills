---
name: trae-work-cn-prompt-engineering
description: Use when the user asks Hermes to hand coding work to TRAE Work CN, Cursor, or another coding agent. Convert rough Chinese requirements into a clear, implementation-ready engineering prompt with scope, context, constraints, acceptance criteria, and verification steps before delegating.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [prompt-engineering, coding-agent, trae-work-cn, software-development, chinese]
    related_skills: [systematic-debugging, test-driven-development, codebase-review]
---

# TRAE Work CN Prompt Engineering

## Overview

This skill turns the user's natural-language coding request into a precise prompt for TRAE Work CN or a similar coding agent. The goal is not to make the prompt longer; it is to make it unambiguous enough that another agent can edit code with the right scope, style, and verification target.

Use current repository facts, files, logs, and prior user preferences when available. Do not invent project structure, APIs, credentials, or expected behavior. If a detail is retrievable from the workspace, inspect it. If it is not retrievable and materially changes implementation, ask the user or mark it as an assumption.

## When to Use

- The user asks to let TRAE Work CN code, fix, refactor, review, or implement something.
- The user gives a rough feature request and expects it to be converted into coding-agent instructions.
- The work is complex enough that a coding agent needs project context, target files, constraints, and tests.
- The user says “安排 TRAE”, “交给 TRAE”, “让 TRAE 写”, “帮我整理提示词”, or equivalent.

Do not use for:

- Tiny one-command questions that Hermes can answer directly.
- Requests where the user explicitly wants Hermes to implement in the current session instead of preparing a prompt.
- Pure brainstorming with no coding handoff.

## Source Principles

Follow widely accepted prompt-engineering patterns from current vendor docs and engineering practice:

| Principle | Coding-agent application |
| --- | --- |
| Clear instruction | State the exact task, target behavior, and what success looks like. |
| Context before task | Include project stack, relevant paths, current behavior, constraints, and known pitfalls. |
| Delimit inputs | Separate user request, repo context, requirements, and output format with headings. |
| Break complex work down | Ask TRAE to inspect first, then implement, then verify. |
| Provide examples when useful | Include UI copy, API shape, data examples, or before/after behavior only when they reduce ambiguity. |
| Specify output format | Require changed files, test results, and any manual verification notes. |
| Guard against overreach | Define files or modules in scope and explicitly forbid unrelated refactors. |
| Require verification | Name concrete commands, browser checks, API calls, or manual flows to run. |

## Workflow

1. **Classify the request.** Decide whether the job is feature work, bug fix, refactor, review, UI build, data/schema change, integration, or deployment. Completion criterion: the prompt has one primary task type and does not mix incompatible goals.

2. **Gather project context.** Inspect relevant files, app structure, package metadata, routes, schemas, tests, and existing patterns before writing the prompt when they are accessible. Completion criterion: every path or framework claim in the prompt is grounded in the workspace or explicitly labeled as an assumption.

3. **Normalize the user's requirement.** Convert vague wording into concrete expected behavior. Preserve the user's domain terms and Chinese business wording. Completion criterion: a developer can tell which behavior to add/change/remove without reinterpreting the original chat.

4. **Define scope boundaries.** Name target modules, allowed edits, forbidden unrelated changes, and migration/data-safety constraints. Completion criterion: TRAE knows what not to touch.

5. **Add implementation guidance.** Prefer existing project patterns over new abstractions. Include architectural notes only when they prevent a predictable mistake. Completion criterion: guidance is specific to this codebase, not generic advice.

6. **Add acceptance criteria.** Write checkable bullets covering user-visible behavior, edge cases, error states, and compatibility. Completion criterion: each criterion can be verified by running code, reading output, or exercising a UI flow.

7. **Add verification commands.** Include exact commands if known. For frontend work, require a real browser check or screenshot when appropriate. For backend work, require tests or API calls. Completion criterion: the prompt says how TRAE should prove the work is done.

8. **Request a concise handback.** Ask TRAE to return changed files, commands run, results, and unresolved issues. Completion criterion: Hermes can verify the result without guessing.

## Prompt Template

Use this structure by default. Remove irrelevant sections rather than filling them with boilerplate.

```markdown
你是 TRAE Work CN，请以资深代码工程师身份在当前项目中完成以下任务。

## 任务目标
<用 2-5 句清楚说明要实现/修复/重构什么，以及最终用户应该看到什么变化。>

## 用户原始需求
<保留主人原话或压缩后的中文需求，避免丢失业务表达。>

## 项目上下文
- 项目路径：<absolute path if known>
- 技术栈：<FastAPI/Vue/React/SQLite/MySQL/etc.>
- 相关文件：
  - `<path>`：<为什么相关>
- 当前行为：<已有行为/问题表现>
- 重要约束：<数据库、端口、兼容性、用户偏好、现有模式>

## 实现要求
1. <具体要求一>
2. <具体要求二>
3. <具体要求三>

## 范围限制
- 只修改与本任务直接相关的文件。
- 保持现有代码风格、命名和项目结构。
- 不要做无关重构、格式化全项目或删除现有功能。
- 如发现需求与现有架构冲突，先说明冲突并采用最小可行改动。

## 验收标准
- [ ] <可检查标准一>
- [ ] <可检查标准二>
- [ ] <错误场景/边界情况>
- [ ] <UI/API/数据持久化行为>

## 验证方式
请实际运行并反馈结果：
```bash
<test/build/run command>
```
如有前端页面，请启动服务并用浏览器验证关键流程；如无法运行，请说明阻塞原因和已完成的静态检查。

## 交付格式
完成后请返回：
1. 修改文件清单和每个文件的修改目的。
2. 已运行的命令及真实输出摘要。
3. 验收标准逐项结果。
4. 未解决问题、风险或需要主人确认的点。
```

## Task-Type Additions

### Bug Fix

Add these fields:

```markdown
## 问题复现
- 触发步骤：<steps>
- 实际结果：<actual>
- 期望结果：<expected>
- 相关报错/日志：<exact error if available>

## 修复要求
- 先定位根因，再做最小修复。
- 增加或更新能覆盖该问题的测试/验证步骤。
```

### UI / Frontend

Add these fields:

```markdown
## 视觉与交互要求
- 风格：<match existing dashboard/admin/game/etc.>
- 响应式：桌面和移动端都不能出现文字溢出、遮挡或布局跳动。
- 组件：优先复用现有组件/样式系统；图标使用项目已有图标库。
- 状态：覆盖 loading、empty、error、success、disabled 等必要状态。
```

For the user's known education-service admin projects, prefer quiet CRM/dashboard UI: dense but organized data, restrained colors, efficient navigation, no marketing hero page unless explicitly requested.

### Backend / API

Add these fields:

```markdown
## API/数据要求
- 路由/API：<endpoint and method if known>
- 请求/响应：<schema example if known>
- 数据库影响：<tables, constraints, migration/seed notes>
- 权限/校验：<auth, validation, error codes>
```

Require API verification with curl, pytest, or the project's existing test client when possible.

### Refactor

Add these fields:

```markdown
## 重构边界
- 外部行为必须保持不变。
- 重构目标是：<readability/duplication/performance/module boundary>
- 不改变公开 API、数据库结构或用户可见文案，除非上方明确要求。
```

### Code Review

Use review stance instead of implementation stance:

```markdown
请只审查，不修改代码。按严重程度输出问题，包含文件/行号、原因、影响和建议修复方式。优先关注 bug、回归风险、安全问题和缺失测试。
```

## Quality Bar

A good TRAE prompt is:

- **Specific:** it names behavior, files, constraints, and verification.
- **Grounded:** it uses real project facts, not guessed architecture.
- **Bounded:** it says what to avoid and what not to modify.
- **Executable:** TRAE can start coding without asking obvious follow-up questions.
- **Verifiable:** success is tied to commands, screenshots, API calls, or checklist items.
- **Concise:** no generic pep talk, no repeated “best practices,” no long theory.

## Common Pitfalls

1. **Passing the raw user request directly.** Rough requests often omit scope, context, and verification. Normalize them first.

2. **Inventing paths or stack details.** If the workspace has not been inspected, mark paths as “待 TRAE 确认” or inspect before writing.

3. **Overloading one prompt.** If the user asks for several unrelated features, split them into phases and tell TRAE to complete phase 1 first.

4. **Missing acceptance criteria.** A coding agent may stop after code changes without proving behavior. Always include checkable criteria.

5. **No handback format.** Without a required summary, Hermes cannot verify what TRAE changed.

6. **Allowing broad refactors.** For production-like projects, explicitly forbid unrelated rewrites and mass formatting.

7. **Forgetting user preferences.** Respect known preferences such as Chinese output, PyCharm workflow, preview pages before replacing existing pages, and code-first explanations.

## Verification Checklist

- [ ] User request has been converted into a clear `任务目标`.
- [ ] Relevant project facts are inspected or labeled as assumptions.
- [ ] Scope and non-goals are explicit.
- [ ] Implementation requirements are concrete and ordered.
- [ ] Acceptance criteria are checkable.
- [ ] Verification commands or manual checks are included.
- [ ] TRAE handback format asks for changed files, real command results, checklist status, and unresolved risks.
- [ ] Prompt is in Chinese unless the user requests otherwise.
