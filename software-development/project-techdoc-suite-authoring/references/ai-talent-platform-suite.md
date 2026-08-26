# AI 人才平台文档套件 — 模板复刻参考

## 项目背景

AI 数字化人才智能平台（ai-talent-platform）：面向招人公司/人力公司/外包公司，
JD生成→简历匹配→AI初面→人工复试→入职问答，2026-08 冻结 v1.2。

## 文档结构速查

```
docs/
├── REQUIREMENTS.md       # 需求权威源，FR编号体系（FR-x.y），分期计划
├── 01-architecture.md    # 六层架构、组件拓扑、技术选型答辩要点
├── 02-api-design.md      # 统一响应/错误码/幂等矩阵/全接口+JSON示例
├── 03-test-cases.md      # 编号规则TC-{模块}-{F/N}-{序号}，按模块分节
├── 04-overview-design.md # 模块划分/依赖/ADR/状态机/事件全集
├── 05-database-design.md # DDL冻结表（18+2张）、Milvus向量、Redis key
├── 06-detail-design.md   # Pydantic Schema/核心算法伪代码
DEVELOPMENT_GUIDE.md     # Agent分工、阶段门禁、编码规范
```

## 格式规范（复刻时沿用）

- 头部元数据表：项目/版本/状态/生效时间/维护者/适用范围
- 修订记录表：版本|日期|变更|批准
- DDL 表格：字段|类型|约束|说明（四列）
- API 表格：统一响应结构（code/message/data）+ 错误码映射表
- 测试编号：TC-{模块}-{F/N}-{序号}（F=功能，N=异常）
- FR 编号：FR-{模块}.{序号}，连续无空洞
- 事件流：append-only（INSERT only，禁止 UPDATE/DELETE）
- 幂等：三状态 processing/succeeded/failed + INSERT原子获取 + 5分钟lease

## 已验证的工程规范（模板复刻时直接套用）

1. **双码错误约定**：每个错误 = HTTP状态码 + 业务码（如 422↔42200），前端用code
2. **幂等矩阵**：每个写接口标注幂等性/Header约定
3. **RBAC五角色模型**：admin/hr/interviewer/candidate/employee（按项目调整）
4. **状态机显式分支**：不允许"多重箭头歧义"
5. **DB租户隔离锚点**：company_id过滤链，禁止裸WHERE
6. **MySQL+Milvus+Redis三件套**：主数据/向量/缓存职责分离

## 实战复刻样例

**AI 求职护航助手**（ai-career-assist, 2026-08）：
- 参照本套件为"求职者侧"场景从零改编
- 概念映射：JD生成→职业测评，候选人→求职者，HR→顾问，offer→谈薪
- 保留全部格式规范，替换业务术语与功能点
- 8份文档共1874行，全套v1.0一次性生成
