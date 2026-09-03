# 案例：Unity 存档 UDD702 parts 数组丢 `{`（2026-09-03）

## 场景
用户提供两份存档：`save.plain.json`（游戏可读）与 `save.plain (1).json`（游戏读不了），
问坏档哪里写错。

## 关键发现链
1. **两份文件 Python `json.loads` 都报错**：
   - 好档报 line 3257：`"__type" : "string""ach_story_memento"`（相邻字符串无逗号）
   - 坏档报 line 2224：`Expecting ',' delimiter`（更早）
2. **可疑模式统计两份完全一致**：`"__type" : "string""` 相邻怪癖 938 处、带逗号 1 处
   → 该怪癖是序列化器固有格式，游戏容忍，**不是病因**。
3. **括号配平扫描**（决定性证据）：
   - 好档：0 未闭合 ✅
   - 坏档：`line 2226: mismatch opened [@2223 closed }` ❌
4. **diff（CRLF 归一化后）**：差异全是语义改动（RankUp 数值 0→7、新增装备 parts），
   混杂一处结构损坏。

## 病灶
坏档第二件 `UDD702` 记忆体（MemoryUnitData, Assembly-CSharp）的 `parts` 数组：

```
"parts" : [          ← 2223 行，数组已开
        "id" : 0,    ← 2224 行，本该先有 { ！丢了
        "key" : "UDD702_S1"
    },{
```

好档/坏档第一件 UDD702 的正常写法是 `"parts" : [` 后先 `{` 再 `"id" : 0`。
→ 存档修改工具加装备/加部件时漏写数组首元素的 `{`，导致 `[` 被 `}` 错误关闭。

## 修复
在坏档 2224 行前插入一行 `\t\t\t{`（对齐同款对象正常缩进），存为新文件。

## 验证
- 括号扫描修复版 → 0 未闭合 ✅
- strict parse 修复版 → 断点推进到 line 3350（同类怪癖处，与好档 3257 同性质）
  → 证明除缺 `{` 外无其他结构伤 ✅
- 交付 `save.plain_fixed.json` 让用户替换测试

## 复用要点
- 结构伤定位用括号扫描，不要信 strict json.loads 的第一报错（会被容忍怪癖误导）
- 修复 .json 用 Python 脚本，`patch`/`write_file` 工具的 JSON 校验会拒绝非严格 JSON 文件
- 读取用 `encoding='utf-8-sig'`（兼容 BOM）+ `newline=''`；写回保持原行尾
