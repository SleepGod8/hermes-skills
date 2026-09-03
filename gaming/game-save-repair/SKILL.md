---
name: game-save-repair
description: Use when 游戏存档读不了或 JSON-like 数据文件解析失败，需对比好档坏档定位结构错误。
---

# 游戏存档 / 非严格 JSON 数据文件修复

## 触发场景
- 用户给两份存档（或数据文件），一份游戏能读一份读不了，问「哪里写坏了」
- 任何「程序不认但看着像 JSON」的文件报错排查（Unity/Assembly-CSharp 序列化、`__type` 类型标注的存档等）

## 核心认知（先记住，别走弯路）
1. **游戏能读的「好档」也经常不是严格 JSON。** 程序自写序列化器会产出格式怪癖（例：`"__type" : "string""ach_x"` —— 相邻字符串**无逗号**，938 处），Python `json.loads` 会在这类文件上直接报错。**严格解析失败 ≠ 文件坏了。**
2. **判据是「好档坏档的差异」，不是「能否通过 json.loads」。** 怪癖若两份文件里数量相同 → 游戏容忍，不是病因。真正的病因是**结构性括号损坏**（丢 `{`、多 `}`、错配）。
3. 序列化存档可能含重复对象（同一 unit 出现两次、一处被改坏），对照时按对象找，别被整行 diff 带偏。

## 诊断流程
1. **括号配平扫描两份文件**（决定性一步）：`python scripts/scan_brackets.py 好档 坏档`
   - 好档配平 0 未闭合 + 坏档报错 → 坏档确有结构伤，报错行即病灶
   - 扫描实现要点：逐字符、忽略字符串内内容（处理 `\"` 转义）、括号入栈、报首个错配/未闭合
2. **strict json.loads 两份各跑一次**，记录首个报错的行/列/char 位置。注意断点性质：
   - 好档断在怪癖处（如 3257 行缺逗号）→ 正常
   - 坏档断在更早的结构错处（如 2224 行）→ 结构伤就在这
3. **统计可疑模式在两份的数量**，确认哪些是共有怪癖（不是病因）：
   `re.findall(r'"__type" : "string""', data)` 数数对比
4. **diff 看语义差异**：`diff <(tr -d '\r' < 好档) <(tr -d '\r' < 坏档)`（Windows CRLF 先归一化），区分改档内容（RankUp 等数值改动）与结构损坏
5. **定位病灶上下文**：打印报错行 ±10 行 raw repr（注意 `\r`、`\t`），与好档**同对象**区域对照，确认缺的是 `{` / `}` 还是逗号。缺逗号类 → 游戏多半容忍；缺括号类 → 必死
6. **修复**：复制坏档为新文件，用 **Python 脚本按行插入**缺失字符（对齐同款对象正常写法的缩进）。**不要用 patch/write_file 工具直接改 .json** —— 工具内置 JSON 语法校验，文件本身非严格 JSON 会被拒（报 "candidate content fails .json syntax validation"）
7. **验证**：
   - 括号扫描修复版 → 0 未闭合
   - strict parse 修复版 → 断点应推进到与好档**同类**怪癖处（证明无其他结构伤）
   - 交付修复文件路径，提醒用户替换原档测试

## Pitfalls
- `patch`/`write_file` 对 `.json` 跑 JSON 校验；目标文件本身不合严格 JSON 时**连修复后的内容也会被拒** → 一律用脚本改
- Windows 文件是 CRLF：读用 `encoding='utf-8-sig'` + `newline=''`，写回保持原行尾；diff 前先 `tr -d '\r'`
- 行内嵌转义/引号多时别用 `python -c`（引号地狱），写成 .py 文件执行
- 坏档常见来源：存档修改工具改了数值/加了装备，却漏了括号 → 结构伤往往在**被新增/复制的那段对象**里
- `isTampered`/`checksum` 字段是存档自校验；修复括号后若游戏仍拒读，可能需同步修 checksum（本次未遇，属延伸风险）

## 验证命令速查
```bash
# 括号配平扫描
python scripts/scan_brackets.py save_ok.json save_bad.json
# strict parse 断点
python -c "import json; json.loads(open('f','r',encoding='utf-8-sig').read())"
# CRLF 归一化 diff
diff <(tr -d '\r' < save_ok.json) <(tr -d '\r' < save_bad.json)
```

## 参考
- references/unity-save-2026-09.md — 实际案例：Unity MemoryUnitData 存档 UDD702 parts 数组丢 `{` 的完整排查记录
