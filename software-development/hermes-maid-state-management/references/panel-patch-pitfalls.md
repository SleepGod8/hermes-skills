# panel-records.md 备注追加实操坑（2026-08-23 实战总结）

> 本次连续 4-5 次 patch 失败后总结的规律。适用场景：给 `lewd-playbook/references/面板存档/panel-records.md` 各女仆「备注追加」行追加结算记录。

## 核心规律

| 女仆 | 备注追加行结尾格式 |
|------|-------------------|
| Hermes / Iris / Athena | 以 `）` 或 `））` 收尾（多数有括号） |
| Dionysus / Artemis / Nemesis / Hypnos | **无右括号**，EXP/部位片段后直接换行 |

⚠️ **不要猜结尾**。每次追加前：

1. `search_files` 定位该女仆的 EXP 片段（如 `EXP 150→170`）
2. `read_file` 看该行**实际末尾 200-300 字符**，确认有无右括号、是否粘连下一区块标题
3. 用**短唯一单行锚点**（只取 EXP/部位片段，如 `EXP 150→170，男根 0/6→0/7`）做 old_string

## 三个翻车点

1. **多行 old_string 在超长备注行上失败**：备注追加行极长（1000+ 字符），带 `\n\n- 专属机制：…` 等尾部上下文的 old_string 模糊匹配经常匹配不到——**改用短单行锚点**。
2. **结尾括号猜错**：Dionysus/Artemis/Nemesis/Hypnos 无 `）`，按 Hermes 格式猜会直接找不到。先读再改。
3. **通用头行跨女仆重复**：如 `- 已解锁：茶会侍奉、口交、吞精、深喉、诱惑姿态` 在 Hermes/Iris 等多段重复（patch 报「Found 3 matches」）；`- 服装：…` 也重复——**必须带前一行（服装/等级行）做上下文**才唯一。

## 结构稳定可直接精确替换的部分

- ⚡ 快速一览表行（`| 女仆 | **Lv.X** | **称号** | N/上限 |`）
- 详细 EXP 行（`- 等级：… ｜ EXP **N/上限**`）
- 📊 部位统计行（`- 📊 部位统计（8/14起）：…`）

这三类格式稳定，锚点唯一，放心替换。**备注追加是唯一高风险点**。

## 推荐流程（一次成功的追加）

```
1. search_files(pattern=EXP片段, path=panel-records.md)   # 定位行号
2. read_file(path, offset=行号-1, limit=3)                # 看实际结尾
3. execute_code 批量 patch：
   - 一览表行、EXP 行、部位统计行：直接精确替换
   - 备注追加：短单行锚点（EXP/部位片段，按读到的真实结尾决定是否带括号）
4. python sync_to_profiles.py
```

## 相关

- 换行符：文件为标准 CRLF（`\r\n`），用 `open(path, encoding='utf-8', newline='')` 读写保留原字节
- 区块标题粘连（`...）## 女仆名`）：定位用 `text.find('## 女仆名')` 不用行锚正则
- 全局 replace 有误改风险：先锁定女仆区块再段内 replace，改完读回验证等级行+部位统计行
