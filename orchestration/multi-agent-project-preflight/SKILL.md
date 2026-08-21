---
name: multi-agent-project-preflight
description: "多 Agent 团队项目开工前的文档分析：读取需求/架构/骨架仓库，提取约束与边界（DRI 矩阵/冻结契约），做契约 vs 实际 DDL 字段级缺口分析，产出 Agent 可执行任务书 + 数据缺口清单 + 致架构组对齐提案。Invoke when user 提供项目骨架/需求文档要求分析、整理任务书、列数据缺口、写对齐提案，或准备多人/多 Agent 团队开发。"
version: 1.0.0
tags: [multi-agent, project-analysis, gap-analysis, task-book, contract, ddl]
metadata:
  hermes:
    tags: [multi-agent, project-analysis, gap-analysis, task-book, contract, ddl]
    category: orchestration
---

# 多 Agent 团队项目开工预检

## 触发条件
- 用户提供项目骨架仓库 + 需求文档，要求"读取文档、明确约束边界、不动代码"
- 需要为某角色产出 Agent 可执行任务书（喂给 OpenCode/Claude Code/Hermes 写代码用）
- 需要找"没考虑到的盲点"、列数据缺口、写对齐提案

## 工作流（实测验证的顺序）

### Step -1: 材料证据预处理（按需）

若输入包含用户明确指定的图片/PDF/扫描文档，先调用 `persona-distillation` 的本地只读流程，生成 `ocr-report-v1` JSON/Markdown 报告和证据分级。报告只作为预检输入，不等同于冻结契约；低置信度、敏感字段、冲突和待确认项必须进入数据缺口/对齐提案，主人确认后才能写入工程宪法或任务书。

### Step 0: 建立项目工程宪法

工程宪法建立或确认后，根据任务复杂度从 `multi-agent-protocol/templates/agents/` 初始化项目根目录 `.agents/` 控制面。标准/重型任务至少创建 `project-brief.md`、`task-board.yaml`、`module-ownership.yaml`、`decisions.md`、`validation-log.md`、`risk-register.md`、`handoff.md`；所有 Agent 以这些文件作为跨会话执行状态来源。（多 Agent 开工前置）
- 在任何派工前，先加载 `project-constitution-authoring`。
- `default` 或 `Athena` 负责读取需求/架构/骨架仓库，产出或更新项目级 `PROJECT_CONSTITUTION.md` / `AGENTS.md` / `DEVELOPMENT_GUIDE.md`。
- 工程宪法必须明确：技术栈、禁止项、架构边界、代码风格、测试命令、Git/PR、需批准操作、Agent 执行协议、Done Definition、待确认事项。
- 后续 `Hypnos` 设计、`Athena` 派工、开发位实现、`Eos` 验收时，都必须先读取并遵守该宪法；若任务需求与宪法冲突，先列冲突并请求裁决，不得擅自覆盖。
- 文档优先级固定为：项目工程宪法/AGENTS > 冻结契约/ADR/schema/CI > Agent 任务书 > `.agents/` 本轮状态 > 聊天临时说明。
- 工程宪法建立后，若需要给具体开发位分活，加载 `agent-task-book-authoring` 生成域/模块任务书，再由 `Athena` 根据任务书和文件所有权派工。
- 若用户只给了单份规范文档（如 FocusFlow 风格 `agent_example.md`），先把它整理成工程宪法，再进入 Step 1。

### Step 1: 侦察目录结构
```bash
find . -maxdepth 2 -not -path './.git/*' -not -path './.venv/*' | head -80
ls -la README.md AGENTS.md PROJECT_CONSTITUTION.md DEVELOPMENT_GUIDE.md .env.example pyproject.toml requirements.txt
```
找：README / **AGENTS.md**（多 agent 总章程）/ PROJECT_CONSTITUTION.md / DEVELOPMENT_GUIDE.md / docs/00-README（文档索引）/ docs/02-roles/*（角色页+DRI）/ docs/01-architecture/*（冻结契约）/ sql/（实际 DDL）。

### Step 2: 读文档顺序（按依赖）
README → AGENTS.md → docs/00-README.md → docs/02-roles/00（DRI 矩阵）+ 目标角色页 → 冻结契约（接口/事件/Tool/DDL）→ 故障治理 → 门禁规范 → .env.example / pyproject.toml。
**同时读代码现状**（app/ 下已有文件）——文档和代码经常不一致，必须双向核对。

### Step 3: 交叉验证（高价值产出 = 找冲突）
- **文档 vs 代码**：基类命名（本 session 发现文档写 AgentBase、代码用 BaseAgent）、文件头"维护人" vs DRI 矩阵归属
- **规则/需求字段 vs 实际 DDL**：`grep -iE "CREATE TABLE" sql/create_tables.sql` 拿表清单，`sed -n '/CREATE TABLE .../,/ENGINE/p'` 拿字段，逐条比对规则需要的数据字段
- **接口入参 vs 规则需要的数据**：monitor 接口 5 字段 vs 20 条规则需要对手方/年龄/开户时间——往往是最大缺口
- 分工变化要主动指出：用户以为负责 X+Y，最新文档 DRI 只给 X——先确认再写任务书

### Step 4: 产出三件套（用户认可的模式）
1. **任务书**（给 Agent 执行）：负责内容(DRI 写/读/协作方) / 任务需求(原子任务+Done 条件) / 技术栈 / 核心规则完整参数 / 代码做法(每个文件现状+实现要点) / 接入骨架(抽象方法) / 边界(不越界清单) / 红线 / 验收清单 / 参考索引+待确认项
2. **数据缺口清单**：逐规则字段需求×现状×缺口，分 P0(必须加字段)/P1(名单 mock)/P2(口径确认)，末尾给"建议对齐方案"
3. **对齐提案**：N 项对齐事项，每项"现状/影响/建议/决策点"，**决策汇总表用"建议默认值 + 不采纳的后果"格式**——决策者 3 分钟读完，只需说同意/改

### Step 5: 确认闭环
把待确认事项逐条给用户拍板（clarify 给选项），确认后**写回任务书定稿**，清除所有"待确认"标记。

## 关键模式
- **量化证据**："现有数据只能支撑 20 条规则中 5 条"比"有缺口"有力得多
- **建议默认值+后果**让架构组不用从零想
- 产出文件放**项目根目录**（agent 一进仓库就看到），用 `RISK-*`/`DOMAIN-*` 前缀，与 AGENTS.md 并列
- 用户说"不动代码" = 全程只读侦察，绝不改任何文件

## 坑
- 上传的 HTML 需求文档：用 Python 正则提取纯文本（去 script/style、标题换行、压缩空行）再 `grep -n "^### "` 看章节地图，按行区间 read_file；别直接读一堆标签
- read_file 大文件会被截断——**所有规则参数必须回到权威源逐条核对**（本 session 曾因截断写错 3 条规则参数进任务书，靠补读后半段才发现）
- 占位文件（TODO/NotImplementedError）不要当成已实现——要标注"现状=占位，待填充"
- 规则引擎类实现：确定性代码优先，LLM 只做生成/分类，不做数值判断（金额/权限/阈值）
- 冻结契约"只准加不准改"——提加字段可行，提改字段要双签

## 参考文件
- `references/decision-proposal-format.md` —— 对齐提案的"建议默认值+不采纳后果"决策表模板
