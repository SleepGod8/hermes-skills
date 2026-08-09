# multi-agent-protocol 协议 skill 家族：布局、岗位映射与新增岗位流程

> 团队协议以 skill 形式存在于每个档案的 skills 目录（9 档案 + 根级）。本文件记录其布局、
> 岗位-档案映射、新增 Agent 岗位的完整流程与踩坑点。被要求「新增 Agent N」「同步协议」「调整岗位」时先读本文件。

## 存放布局（每个档案一份 skill）

```
skills/orchestration/multi-agent-protocol/                     # 根级 = default(Hermes×Iris)
profiles/<名>/skills/orchestration/multi-agent-protocol/       # 其他 9 个档案
├── SKILL.md                        # 速查版（各档案略有差异：角色拓扑 + 本岗位要点）
└── references/
    ├── multi-agent-protocol.md     # 协议全文（9 档案 MD5 一致）
    ├── governance-rules.md         # 团队治理规则（MD5 一致）
    ├── enhanced-pipeline.md        # 增强流水线规范（MD5 一致）
    ├── workflow-retro-2026-08.md   # 复盘要点（MD5 一致）
    └── soul-0N-<岗位>.md           # 各档案自己的岗位文件（命名规范 soul-0N-<岗位>）
```

共享 4 件套 MD5（2026-08 实测，用于同步校验）：
- multi-agent-protocol.md = `b0894587e3ae346bdad2f4ea1083279e`
- governance-rules.md     = `04c404e734d7c54e81b777ba0447cf0a`
- enhanced-pipeline.md    = `56254cf363df314d4f9d4359d640ec02`
- workflow-retro-2026-08.md = `1e993cd41b46d68b8723989de656c121`

## 岗位-档案映射（v1 现状，2026-08）

| Agent | 岗位 | 档案 | 岗位文件 |
|-------|------|------|----------|
| 1 | 项目负责人 | athena | soul-01-project-lead.md |
| 2 | 侦察与架构 | hypnos | soul-02-recon-architect.md |
| 3 | 功能开发 1 | hebe | soul-03-feature-developer-1.md |
| 4 | 功能开发 2 | artemis | soul-04-feature-developer-2.md |
| 5 | 功能开发 3 | nemesis | soul-05-feature-developer-3.md |
| 6 | 测试与审查 | eos | soul-06-test-review.md |
| 7 | 候补（无固定职能，仅 Agent 1 分派补位） | default(Hermes×Iris) | soul-07-reserve.md |
| 预备役 | standby | aphrodite / ares / dionysus | soul-00-standby.md |

## 新增一个 Agent 岗位的流程（Agent 7 已验证）

1. 岗位职责文档 → 保存为目标档案的 `references/soul-0N-<岗位>.md`。
2. 从任一已有档案复制 4 个共享协议文件到目标 skill 的 `references/`，并 `md5sum` 校验一致。
3. 写 SKILL.md（参考 eos/Agent 6 速查版模板：文件清单 → 使用方式 → 核心要点速查 → 角色拓扑 → 任务/状态 → 标准消息 → 文件所有权/合并 → 模型熔断 → 质量门禁 → 本岗位要点 → 注意）。
4. 把 `Agent N：<岗位>（…）` 行插入**全部 9 个档案 + 根级** SKILL.md 的角色拓扑（团队级变更必须全同步；athena SKILL.md 第 140 行有明文规则：技能/协议/规则/模板固化类任务必须全团队同步）。
5. grep 验证每个档案都含新 Agent 行。
6. 更新 memory 记录新岗位映射。

## 坑

- **cross-profile soft guard**：patch/write_file 跨档案会报 `Cross-profile write blocked by soft guard`，团队级同步须加 `cross_profile=true` 重试（用户在团队级变更场景下默认授权全量同步）。
- **athena 格式特殊**：角色拓扑用加粗列表 `- **Agent N**：…`；其余档案多为 `text` 代码块（`Agent N：…` 无加粗）。grep `"Agent N：候补"` 匹配不到 athena，要用 `grep -n "Agent N"`。
- **各档案 SKILL.md 格式不统一**：aphrodite/ares/dionysus/hypnos/nemesis 是完整协议版（角色拓扑在 `## 角色拓扑` 代码块），hebe/artemis/eos 是速查版，athena 特制版。插入角色拓扑行前先 `sed -n` 看上下文，按原格式插入。
- 岗位文件与本协议冲突时，以 Agent 1（athena）确认的最新协议版本为准。
- 用 write_file 直接建 skill 的文件后，skill 记录 created_by=None，后台 curator 会拒绝后续 write_file/patch（`Refusing background curator write_file`）——需要 curator 可维护的正式 skill 时用 skill_manage(action='create') 建，或接受该 skill 不可被自动维护。
