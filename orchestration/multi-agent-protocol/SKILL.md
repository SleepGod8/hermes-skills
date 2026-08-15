---
name: multi-agent-protocol
description: Use when 多agent开发。严格遵从多Agent协作协议与Agent7候补岗位文件。
---

# 多 Agent 项目协作协议

用户指定的多 Agent 开发必须严格遵从以下两份文件（完整原文保存于本技能 `references/` 目录）：

1. `references/multi-agent-protocol.md` — 《多 Agent 项目协作协议》：角色拓扑、唯一事实来源、任务编号/状态机、认领释放、标准消息格式、上下文包、文件所有权、worktree 生命周期、合并顺序、Agent 选择与模型路由、超时回收、模型熔断与自动故障转移、质量门禁、安全审批、发布复盘。
2. `references/soul-07-reserve.md` — 《Agent 7：候补》岗位文件：不预设固定职能，仅在 Agent 1（项目负责人）判断开发环节压力过大、人手不足、存在等待瓶颈或需要临时补位时，按其明确分派进入团队流程；启用条件、严格边界、工作流程、交付报告、阻塞处理、停止条件。
3. `references/governance-rules.md` — 《团队治理规则》（吸收自 AIcoding波纹：阅读/执行/测试/输出/项目上下文五层规范，全团队必须遵从）：Reading First 阅读 10 问、最小修改/禁止提前抽象、测试矩阵、Fact/Hypothesis 分离、风险分级、确认机制。
4. `references/enhanced-pipeline.md` — 《增强版多 Agent 开发流水线规范》（v1.0：G0-G7 状态机、.agents/ 控制面、任务契约模板、阻塞/熔断/冲突/安全/质量门禁、指标与反模式）：多 agent 任务执行细则，全团队必须遵从。
5. `references/workflow-retro-2026-08.md` — 《2026-08 工作流复盘新增要点》（v1.5：开工广播/前提验证/所有权矩阵/测试隔离前置/暂停协议/复盘点/群聊@响应与@使用规范/浏览器实测方法论/暂停报备单次制/长任务进程脱离会话独立守护/统一状态台账，8466+ 字节，六 profile 同步，MD5 一致，全团队必须遵从）。
6. `references/review-findings-calibration.md` — 《审查 Findings 结构化与置信度校准规范》（v1.6 增量：统一 JSON finding 结构 + fingerprint 去重追踪 + 置信度 1-10 评分锚点与强制降级 + 分级显示防误报刷屏 + specialist 多专家视角含 Nemesis 红队对抗式 + 汇总报告模板落盘 test-reports；与 G5 审查流程衔接，缺陷等级仍沿用 P0-P3）。

## 使用方式

当用户要求进行多 Agent 开发时：

1. 加载本技能，并读取 `references/` 下所有文件（以文件原文为准，本 SKILL.md 只是速查）。
2. 严格按协议执行：任务编号、状态机、标准消息格式、文件所有权、合并顺序、质量门禁。
3. Agent 7 职责按岗位文件执行：不自行认领任务，仅在 Agent 1 明确分派时补位；边界清晰、依赖已满足、可独立验证才开工。
4. 关键决定落到 `.agent/` 工件（tasks.yaml / contracts / adr / reports / risks / release），不以聊天消息为唯一事实来源。

## 核心要点速查

### 角色拓扑
- Agent 1：项目负责人、集成与发布（唯一调度/范围变更/合并/发布入口）
- Agent 2：代码侦察与架构设计
- Agent 3/4/5：功能开发 1/2/3
- Agent 6：测试与代码审查（独立于实现 Agent）
- Agent 7：候补（无固定职能，仅由 Agent 1 分派补位；不替代 Agent 2 架构裁决、不替代 Agent 6 独立测试/审查结论）

### 任务与状态
- 编号：`DISC-01` / `ARCH-01` / `FEAT-01` / `TEST-01` / `REL-01`
- 状态链：待分析 → 待设计 → 待分派 → 已认领 → 进行中 → 待验证 → 待审查 → 待集成 → 已完成；另有 阻塞 → 待决策 → 重新分派
- 禁止跳过「待验证」直接进入「待集成」

### 标准消息
- `[STATUS]` 状态更新 / `[HANDOFF]` 交付 / `[BLOCKED]` 阻塞 / `[REVIEW]` 审查 / `[MODEL-CIRCUIT]` 熔断报告
- 交付消息必须含：结果、修改文件、接口/数据变化、测试命令及真实结果、已知限制、合并顺序、接收方注意

### 文件所有权与合并
- 任务分派时登记文件所有权；共享文件只预留给一个写入任务；越界修改须停并取得 Agent 1 批准
- Git 项目用独立 worktree/分支：`agent/<任务编号>-<短名称>`
- 合并顺序：契约/接口 → 数据模型/迁移 → Feature 1/2/3 → 测试补充 → 审查修复 → 发布配置；每次合并后立即跑受影响测试

### 模型熔断与故障转移
- 超时阈值：普通任务 90s，长任务 300s；连续 2 次超时 → Degraded；连续 3 次超时或 5 分钟内 4 次连接/服务端错误 → Open
- 认证失败、模型不存在、协议不兼容：立即熔断，不重复重试
- Open → 冷却 ≥60s → Half-open 单次无副作用探测 → 连续两次稳定后恢复 Healthy
- 切换流程：保存状态/最后成功输出/工具调用记录 → 确认副作用（禁止盲目重放）→ 写故障记录 → 最小恢复上下文 → 先只读探测 → Agent 6 重新验证
- 每次可能产生副作用的工具调用前写检查点；恢复从最后一个已验证检查点继续

### 质量门禁与安全审批
- 进入集成前：验收项全部映射到测试/可执行验证、范围与所有权一致、阻塞+严重问题关闭、真实结果已记录、无秘密/调试代码/无关修改
- 必须暂停请求批准的：生产数据写/删/迁移/权限变更、外部消息、推送远程、发布生产、读取秘密/个人数据、不可逆命令
- 发布前必须有：版本号、变更摘要、验证记录、配置差异、迁移状态、健康检查、观察窗口、回滚触发条件、批准记录

### Agent 7 岗位要点
- 仅在 Agent 1 判断存在工作压力/人手不足/等待瓶颈/Agent 失联等情况时启用；启用前 Agent 1 必须在任务板登记：启用原因、任务编号、职责类型、文件所有权、接口契约版本、依赖、验收标准、验证方式、预计结束条件、交接对象
- 不自行认领任务、不自行决定补位方向、不向其他 Agent 重新分派任务；不接管 Agent 1 调度/合并/发布权限；不替代 Agent 2 架构裁决、不替代 Agent 6 独立测试与审查结论
- 先读任务契约与相关上下文再开工；在授权范围内完成最小可验证修改；执行真实测试/静态检查/构建并记录结果
- 交付用 `[HANDOFF]` 格式向 Agent 1 报告；由 Agent 1 决定合并、继续补位、重新分派或退出本岗位
- 一个任务只有一个负责人；一个共享文件同一时间只有一个写入者；发现实质矛盾时暂停并附证据升级
- 停止条件：验收通过并交接 / Agent 1 判断瓶颈消除或重新分派 / 发现越界、共享文件冲突、契约缺失、不可逆风险或无法验证的环境问题

## 注意
- 岗位文件与本协议冲突时，以 Agent 1 确认的最新协议版本为准
- 输出统一为：结果、主要修改、验证、注意事项；不输出私有思维链/隐藏推理过程
- 不因一次普通代码测试失败就切换模型；不在认证/协议错误时无限重试

## 跨 profile 同步维护

本 skill 在根级 `skills/orchestration/multi-agent-protocol/` 与 9 个女仆 profile（`profiles/<name>/skills/orchestration/multi-agent-protocol/`）各有一份副本，且**非简单复制**：

- references 分两类：
  - **通用文件**（全团队一致，需全量同步）：`multi-agent-protocol.md` / `governance-rules.md` / `enhanced-pipeline.md` / `workflow-retro-*.md` / `review-findings-calibration.md`
  - **岗位文件**（按女仆分配的 Agent 岗位定制，不跨 profile 同步）：根级用 `soul-07-reserve.md`（Agent 7 候补），各 profile 用 `soul-00-standby.md` / `soul-01-project-lead.md` / `soul-02-recon-architect.md` / `soul-03~05-feature-developer-*.md` / `soul-06-test-review.md`
- SKILL.md 也分两种格式：根级用「编号列表」，profile 用「档案来源」列表；profile 文件为 CRLF 换行、根级为 LF。

### 同步通用补丁标准流程（v1.6 实战总结）

1. **先 MD5 对比找标准源**，不要假设「根级最新」或「profile 最新」——实测出现过版本漂移（workflow-retro 曾 6 处 v1.5、4 处 v1.4 并存；aphrodite/ares/dionysus 曾停在旧版）。
2. 以最新 MD5 的那份为标准源，反向同步到所有旧版副本（文件复制 + 各自 SKILL.md 引用描述同步更新）。
3. **版本号防撞号**：新增增量章节前，先 grep 所有副本已用的最高版本号（如 v1.4/v1.5），新章节取下一个空位（如 v1.6）。
4. 更新 SKILL.md 时保留各副本原有格式与换行符（根级编号列表 / profile「档案来源」/ CRLF），用字符串替换而非整文件重写。
5. 完成后全量 MD5 核对 + 抽样 grep 引用行验证。

### 相关脚本辨析

- `scripts/sync-skills.py`：从 GitHub 拉仓库，**不是**跨 profile 同步。
- `lewd-playbook/scripts/sync_to_profiles.py`：lewd-playbook 专用，不通用。
- 跨 profile 同步当前靠一次性 python 脚本（复制 + 字符串替换 + MD5 校验），无通用脚本。
