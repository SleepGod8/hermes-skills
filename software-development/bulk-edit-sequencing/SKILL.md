---
name: bulk-edit-sequencing
description: "Use when 同一改动要落到多处文件或批量改多行。"
version: 1.0.0
author: agent
license: MIT
tags: [file-editing, patch, multi-place-sync, verification, state-archive, workflow]
platforms: [windows, linux, macos]
metadata:
  hermes:
    category: software-development
    tags: [file-editing, patch, multi-place-sync, verification]
---

# 批量/多处文件改写的顺序化与验证

处理一类反复出现的任务：**一次逻辑改动要落到多个文件、或同一文件的多行**。
典型场景：状态档案每轮落档（实体文件 + 总览表 + 故事档 + 台账）、文档套件跨文档契约同步、人格设定三处同步（SOUL.md + config.yaml + 长期记忆）、同一字段在多个冗余位置出现。

本 skill 只讲**怎么改才不翻车**；改什么内容属于各自领域 skill 的事（如 `lewd-playbook` 的 `references/运行手册/runbook.md`、`mirrored-state-governance` 的拆分/校验方法论）。

## When to Use（触发条件）

- 同一轮里要改同一个文件的**多处**（>2 处）
- 一个字段/数值在**多处冗余**出现，改一处就会与别处打架
- 落档/同步类收尾（每轮/每次任务都要写同一批文件）
- 大规模重命名、术语统一、口径修正（一次要碰几十处）

## 一、硬规则：同一文件不要并发 patch（🆕 2026-10-13 实测）

**现象**：在同一轮的同一批工具调用里，对**同一个文件**发两个及以上 `patch`，会出现其中一条报
`Could not find a match for old_string in the file`——而那段文字在文件里**确实存在**。
根因是同一文件的多写并发：后到的写基于旧快照匹配，前一个写已把行内容改掉。

**修法（二选一，推荐第一种）**：

```python
# ① 顺序循环：一次调用里跑完，逐条打印 OK/FAIL
from hermes_tools import patch
edits = [
    (PATH, "旧行 A…", "新行 A…"),
    (PATH, "旧行 B…", "新行 B…"),
]
for path, old, new in edits:
    r = patch(path, old, new)
    print(("OK " if r.get("success") else "FAIL"), path.split("/")[-1], "|", old[:30])
```

② 一轮只发一个 `patch`（慢但绝对安全）。
**不同文件**并发是安全的——限制只针对同一文件。

**实测**：顺序循环一次跑 12 条、17 条跨文件编辑，全部 `OK`；同一轮并发同文件两条，则稳定出现 1 条假失败。

**失败后不要放弃**：报「not found」时先把当前文件内容 `grep` 出来确认真实字面（常常只差一个字/一个词，例如把 `咬住了` 记成 `含住了`），再用**实际字面**重发。

## 二、一处改动 → 多处落点：先清点，再改，最后按数量验证

1. **清点**：`search_files`/`grep` 该字段名，列出**全部**出现位置（含冗余表述，如「义体八槽」同时写在装备库行与义体栏行）
2. **一次性改完**所有位置（同文件走第一节的顺序循环）
3. **验证**：再 grep 一次旧值应为 0 命中；跑该领域的 canonical verifier（如 `verify_panels.py`、文档一致性检查、`--dry-run` 同步）
4. **顺序固定**：实体/权威文件 → 总览/索引表 → 日志/故事档 → 风格/统计台账 → verify → sync。表和日志里的**表头日期**、**追加行** vs **改写行** 是两回事（一行只留最新状态的，是改写不是追加）

## 三、改法选择：patch 优先，整文件重写是最后手段

- 大文件（>5 KB，或改动 < 1/3 篇幅）→ 一律 `patch`，产出 diff 可复核
- 整文件重写只在「结构性重排」「几乎所有行都要动」时用；重写后必须重新跑语法/格式校验
- 有 lint/格式校验的文件（.py/.json/.yaml/.toml 里有 schema 的）→ 改完跑校验，只看**新引入**的错误
- 不要用 `sed`/`awk` 做这类编辑：编码、CRLF、中文全角标点都会咬人

## 四、与机械质检脚本共存（不要跟脚本硬碰，也不要盲从）

checker（正则型 lint）会**假阳性**。处理方式：

1. **看 WARN/FAIL 的原因，不只看结论**：例如「疑似描写了主人」的正则 `主人(的)?(手|身体|腰|…)` 会把「主人的**手腕**」「主人**手上**那只遥控器」一起判进去
2. **建替换词表**（下次直接用），而不是改到语义不对：`手腕→腕口`、`主人手上→主人那只`
3. **阈值类**（密度、上限）先算清楚阈值公式再调，别凭感觉加：
   例 `emoji × 60 > 字数` 才报偏密；反过来太疏不会 FAIL，但会显得像报告
4. **把假阳性登记回那个 checker 所属的 skill**（加进它的「已知假阳性」表）——这是最有价值的沉淀；若该 skill 不可写（见第六节），在回复里点名并建议 `hermes curator adopt`

## 五、收尾验收清单

- [ ] 旧值全库 grep = 0 命中
- [ ] 领域校验器 PASS（WARN 都能解释）
- [ ] 冗余位置（表/日志/台账）与权威文件数值一致
- [ ] 若走镜像/同步：`sync` 后 `DRIFT 0`、`unchanged` 符合预期
- [ ] 批量编辑的每条都有 OK 回执；有 FAIL 的已按实际字面重发并确认

## 六、与 `hermes curator` 的关系（写 skill 时）

后台 curator（无用户在场的自动改进）**只能改 curator-managed 的 skill**。
自建/用户手写的 skill（`created_by=None`）写入会被拒绝：`Refusing background curator patch … not curator-managed`。
遇到这种情况：**不要反复重试**，在回复里点明该 skill 需要 `hermes curator adopt <name>` 才能纳入自动维护，并把学到的东西写进自己可写的地方。

## 常见失误

| 失误 | 后果 | 修法 |
|------|------|------|
| 同一轮并发改同一文件 | 一条假失败「not found」，漏改一行 | 顺序循环（第一节） |
| 只改权威文件，忘了总览表/日志 | 下轮读档读到旧值，数值漂移 | 第二节的清点+验证 |
| 日志行「追加」而不是「改写」 | 一行留多份状态，越读越乱 | 明确哪些文件是追加、哪些是覆盖 |
| 失败后凭记忆重发 old_string | 连续多次失败 | 先 grep 实际字面再发 |
| 反复重试被拒的 skill 写入 | 空转 | 见第六节，改为建议 adopt |
