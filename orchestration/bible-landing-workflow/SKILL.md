---
name: bible-landing-workflow
description: "Bible落盘机械流程：W0总编执行圣经版本更新的标准操作序列、陷阱与验证方法。"
version: 1.0.0
author: Hermes Agent
tags: [novel, workshop, bible, workflow, orchestration]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [novel, workshop, bible, workflow]
    category: orchestration
---

# Bible 落盘机械流程（Bible Landing Workflow）

> 适用：W0 总编在主人拍板新设定后，将内容写入 bible.md 并同步 state 文件的标准操作。
> 与 novel-workshop-protocol（总协议）配合使用；本技能专管机械操作层。

## 一、触发条件

- 主人明确说「落盘」「写入 bible」「确认入库」等指令。
- 多轮讨论后主人拍板一批设定，W0 需批量执行。
- bible 版本号需要递增。

## 二、标准操作序列（按序执行）

### Step 1: 备份

```bash
cp bible.md backups/bible-v{CURRENT}-before-v{NEXT}.md
```

- 备份文件名格式：`bible-v{当前版本}-before-v{新版本}.md`
- 必须在任何修改前执行。

### Step 2: 读取当前 bible 结构

用 `search_files` 和 `read_file` 确认：
- 版本号头（L1）
- §0 版本记录末尾行
- §1 各小节目标插入位置
- §2 待补清单末尾
- §4 当前状态末尾
- §5 插槽总表目标行

### Step 3: 按依赖序执行 patch

**顺序不可乱**（后插入的内容不影响前文行号，反序会导致偏移累积）：

```text
① bible 标题版本号（L1）
② §0 版本记录——新增 v{NEXT} 行（在最旧行后插入）
③ §1 正文——先扩写已有节，再新增节（扩写不改变行结构，新增在节末）
④ §2 待补清单——在现有条目后追加
⑤ §4 当前状态——在现有状态后追加/替换
⑥ §5 插槽总表——更新目标插槽状态
```

**§1 内部顺序**：如果本次落盘涉及多个子节（如 §1.5⑦ 扩写 + §1.5⑧ 新增 + §1.7 更新），先扩写再新增，避免新增内容的 patch 因扩写偏移而找不到目标。

### Step 4: 更新 state 文件

**tasks.yaml**（全量重写）：
- `bible_version` 字段更新为新版本号
- `updated` 日期更新
- 新增任务条目（status=archived, 含 evidence 引用）

**decision-impact.yaml**（增量追加）：
- 新增决策条目，含 decision_id / source / summary / direct_impacts / review_required / unaffected / affected_tasks / regression_status
- review_required 必须包含从旧决策继承的约束（如防膨胀锁从 v2.7.0 继承到 v2.8.0）

### Step 5: 读回验证

**⚠️ 关键陷阱：patch 后 offset 偏移**

patch 操作会插入/删除行，导致之前记录的行号**全部偏移**。如果用 `read_file(path, offset=N)` 做验证，读到的**不是你刚写的内容**。

**正确做法**：
- 用 `search_files(pattern=关键词, path=bible.md)` 做**内容搜索验证**
- 每个落盘点位至少检查一个**唯一关键词**是否出现
- 验证清单基于**内容特征**，不基于行号

**验证清单模板**（按本次落盘内容勾选）：

| # | 检查项 | 方法 | 关键词 |
|---|--------|------|--------|
| 1 | 版本号头 | search | `v{NEXT}` |
| 2 | §0 版本记录 | search | `v{NEXT}` + 变更摘要关键词 |
| 3 | §1 各新增/扩写内容 | search | 每块至少 1 个唯一术语 |
| 4 | §2 新增条目 | search | 待补条目关键词 |
| 5 | §4 状态同步 | search | `v{NEXT} 落档 ✅` |
| 6 | §5 插槽更新 | search | 插槽编号 + 状态关键词 |
| 7 | 备份文件存在 | terminal `ls` | 文件路径 |
| 8 | tasks.yaml 版本一致 | read | `bible_version: v{NEXT}` |
| 9 | decision-impact.yaml 新条目 | terminal `grep -c` | decision_id |
| 10 | 关键术语出现次数 | terminal `grep -c` | 核心设定术语（≥3 次） |

## 三、常见陷阱

| 陷阱 | 后果 | 规避 |
|------|------|------|
| patch 顺序反了 | 后续 patch 找不到目标字符串 | 严格按 §0→§1→§2→§4→§5 顺序 |
| §1 内先新增再扩写 | 新增的 patch 偏移找不到扩写目标 | 先扩写已有节，再新增节 |
| 用 offset 验证 | 读到旧内容，误报通过 | 用 search_files 内容搜索 |
| 版本号冲突 | 覆盖旧版本记录 | 落盘前确认下个版本号未被占用 |
| tasks.yaml 只追加不更新 version | 版本号不一致 | 全量重写 tasks.yaml |
| review_required 遗漏继承约束 | 新决策缺少旧约束 | 从受影响的旧决策继承 review_required |

## 四、决策影响分析（decision-impact.yaml）条目格式

```yaml
- decision_id: {UNIQUE-ID-YYYYMMDD}
  source: SleepGod 群聊指令（按 W0 建议口径落档）
  summary: 一句话描述决策内容
  direct_impacts:
    - bible.md §0 版本记录
    - bible.md §1.X 具体小节
    - bible.md §2 待补充素材清单
    - bible.md §4 当前状态
    - bible.md §5 插槽总表
    - state/tasks.yaml
  review_required:
    - 从旧决策继承的约束（如适用）
    - 新增的写作约束
  unaffected:
    - 不受影响的硬约束列表
  affected_tasks:
    - TASK-ID
  regression_status: pending
```

## 五、与 novel-workshop-protocol 的关系

- `novel-workshop-protocol` 定义**做什么**（岗位职责、流程阶段、状态标签）。
- `bible-landing-workflow` 定义**怎么做**（机械操作序列、patch 顺序、验证方法、陷阱）。
- 两者互补：workshop protocol 里的 §5.5/§5.6 引用本技能作为操作手册。
