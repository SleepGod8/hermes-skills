# 结构化 LLM 输出的「软质量」自动化验证

适用场景：批量生成结构化产物（JD、候选人画像、评分报告、面试题），**Schema 校验通过但语义自洽性差**——
例如技能要求与岗位职责矛盾、level 与年限不匹配、评分依据与结论相反。

这类追问是 AI 岗面试的高频深水区，考的是"你知不知道 Schema 只是第一层"。以下是可以直接口述/落地的框架。

---

## 0. 一句话立场

**不是规则 vs 评估 Agent 的二选一，而是分层：规则做高精度低成本闸门，模型做语义覆盖，两层取并集，人工只处理低置信度那一小部分。**

（与本项目 M7 合规扫描同构：规则词库 + LLM 语义审查，任一层命中即报告，不以单层漏过为由放行。）

## 1. 四层验证链

| 层 | 手段 | 保证什么 | 特性 |
|---|---|---|---|
| 契约层 | Pydantic / JSON Schema、枚举、必填、权重和=1.0 归一化 | 字段与类型正确 | 确定性，但**不保证语义** |
| 确定性规则层 | 可结构化的关系断言 | 硬矛盾 | 高精度、零成本、可 pytest 回归 |
| 语义评估层 | 独立评审 Agent（Rubric 化输出） | 隐含矛盾 | 高召回、非确定性、要压方差 |
| 回归与指标层 | 正负样本集 + 人工兜底 | 改动不回退 | 唯一能自证"变好了"的东西 |

## 2. 规则层：把关系变成断言（可直接写 pytest）

关键前提：**技能要用受控词表（闭集）**，例如岗位能力模型库的 `skill_tree_json`，不要让模型自由抽词。

1. **职责 ⊇ 技能**：`responsibilities` 中识别出的技术实体必须落在 `hard_requirements.skills`；职责写"Vue 前端开发"而技能全是 Java → 硬矛盾。
2. **技能 ∩ 岗位能力模型 ≠ ∅**：`skills` 与 `job_category` 对应的 skill_tree 必须交集非空。
3. **level × years 单调**：`junior+8年`、`senior+1年` → 拒绝。
4. **权重与硬性要求自洽**：`evaluation_criteria.education_weight` 显著大于 0，但 `hard_requirements.education` 为空 → 告警。
5. **加分项与硬性要求互斥**：同一技能同时出现在 `bonus_points` 与必需 `skills` → 逻辑冲突。
6. **软素质与岗位性质匹配**：软素质模板（`soft_requirements_json`）与岗位类别不匹配 → 告警不拦截。

实现要点：
- 技术实体词表外映射失败时**只告警不拦截**（避免误报，参照 M7 误报率 ≤15% 的口径）；
- 同义词表 + embedding 最近邻 + 阈值做词表映射；
- 断言失败信息必须**定位到字段**，才能反哺 Prompt 修补。

## 3. 语义评估层：独立评审 Agent

- **必须与生成解耦**：不同 Prompt、独立调用、只看结构化产物本身，不看生成时的推理过程；否则是自我确认偏差。更彻底可换模型/换角色（成本换独立性）。
- 输出结构化矛盾对，走同一个 `LLMClient.complete(prompt, schema, temperature=0.2, max_retries=3)`：

```python
class ConsistencyIssue(BaseModel):
    dimension: Literal["duty_skill", "level_years", "soft_fit", "actionability", "weight"]
    severity: Literal["high", "medium", "low"]
    conflicting_fields: list[str]   # 冲突涉及的结构化字段
    snippet: str                     # 命中的原文
    suggestion: str                  # 定向修改建议

class ConsistencyReport(BaseModel):
    consistency_score: float         # 0-100
    issues: list[ConsistencyIssue]
    schema_version: str = "1.0"
```

- 自洽性维度建议固定为：职责-技能一致、级别-年限一致、软素质-岗位性质、可执行性（能不能直接拿去筛人）、权重合理性。

## 4. 压制非确定性（复用 M3 初面评分的已验证做法）

- `temperature = 0.2` 低温；
- 同一产物采样 3–5 次，取**中位数**为主结论，记录同维度**极差 max-min**；
- 极差超阈值 → 标 `low_confidence` 转人工，**不硬判死**；
- 依据文本取与中位一致的那次；不一致时拼接差异说明。

## 5. 分流与回炉

```
score 高        → 直接放行
score 中        → 进人工复核队列
score 低 / high 级 issue → 带 issues 清单做定向 revision，最多 2 轮
2 轮仍不过      → 标 blocked，转人工（不无限重试）
```

revision 只改冲突字段，不整份重生成——省 token 也避免引入新矛盾。

## 6. 批量生产与回归指标

- 入任务队列 + 幂等键（本项目 `idempotency_requests` 那套），同版本产物不重复评审；
- 每条产物的判定结果落库，可按批次聚合，坏例定位到片段；
- 评测集：**正例（人工确认自洽）+ 负例（人工注入矛盾：改技能、改年限、错配职责）**，算 precision / recall；
- 监控三项：自洽通过率、人工接管率、Prompt/模型变更后的回归差异。

## 7. 必须说清的边界（面试防穿透）

本项目 M1 JD 生成的一期验收**只有**：Schema 通过率 ≥99%、核心字段非空率 100%、人工可读性抽样（10 份 JD / 5 人评审 ≥4/5）。
即：软质量当时只有人工抽样一道，上述自动化是**演进设计**，不是已跑出数字的实测结果；阈值（采样次数、极差 1.0 档、权重）为示例参数，需用真实 JD 集标定。

主动交代这个边界比装作已实现更能加分——它证明你分得清"设计文档 / 验收目标 / 实测结果"。
