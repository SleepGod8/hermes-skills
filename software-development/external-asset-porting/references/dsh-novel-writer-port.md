# DSH 网络小说插件移植案例（2026-08-19）

> 来源仓库：`github.com/akira399/dsh-novel-writer`（DeepSeek Harness 插件 v0.1.7）
> 结论：插件体系（DSH host 工具注册 + React GUI + agent 预设）不能直接在 Hermes 安装（iOS App 装不进 Android），但核心资产全部可移植。
> 主人拍板「A 轻量移植」→ 落地 `E:\Hermes workspace\.novel\execution-layer\`。

## 一、资产盘点（初评）

| 资产 | 位置 | 规模 | 判定 |
|------|------|------|------|
| 提示词模板 | `assets/prompts/*.md` | 62 个（creation14/diagnose7/polish13/style8/writing8/lorebook5/guide7）| ✅ 原样复制 |
| 创作工作流 SKILL | `assets/skills/novel-writing-workflow/SKILL.md` | 45 行 | ✅ 改写适配 |
| 黄金三章诊断 | `src/core/diagnose/rules.ts` | 213 行 | ✅ 翻译 Python |
| AI 味词库 | `src/core/polish/dict.ts` | 234 词（49+69+48+47+21）| ✅ 正则提取 JSON |
| AI 味扫描器 | `src/core/polish/scanner.ts` | 91 行 | ✅ 翻译 Python |
| 一致性检测 | `src/core/consistency/detect.ts` | 129 行 | ✅ 翻译 Python |
| 字数统计 | `src/core/stats/wordcount.ts` | 依赖模块 | ✅ 并入 golden3 |
| 世界书样例 | `assets/samples/demo-book/lorebook/` | 3 JSON | ✅ 复制（SillyTavern 原生）|
| GUI/服务端/工具层 | `src/client|tools|index` | — | ❌ 不移植 |

## 二、落地结构

```
.novel/execution-layer/
├── SKILL.md                  # novel-execution-layer：九阶段门禁+两段式写章+质检→Eos审查闭环
├── prompts/                  # 62 个提示词模板 + _dsh-skill-original.md（原版存档）
├── scripts/
│   ├── golden3.py            # 黄金三章 6 维评分（字数/对话占比/章末钩子/开场钩子/设定灌输/冲突词）
│   ├── ai_taste.py           # AI 味扫描（词库匹配→命中明细+密度评分，每千字×10 上限 100）
│   ├── consistency.py        # 账本冲突/时间线倒挂/世界书沉淀建议
│   └── ai_taste_dict.json    # 234 词，5 类，策略 rewrite154/delete44/replace36
└── lorebook-sample/          # SillyTavern 原生 JSON（可导入酒馆 8001）
```

## 三、验证记录（实测）

- `golden3.py`：好例+坏例 → 6 维评分 92/100，rule-hook/rule-opening error 正确检出。
- `ai_taste.py`：AI 味文本 73 CJK 字 → 19 处命中全检出、评分 100/100、长词优先正确（「眼底闪过一丝」先于「闪过」）。
- `consistency.py`：账本 7 条 → 冲突 3 条（数值单调上升=info 正确、非数值覆盖=warning）、时间倒挂 1 条、无法解析 1 条、沉淀建议 3 条全检出。
- 三脚本 `py_compile` 全绿；总交付 133.6 KB。

## 四、踩过的坑

1. **read_file 二进制误判**：`scanner.ts` 与 `entries.json` 均被工具判 binary → 用 `python -c "import io; print(io.open(f, encoding='utf-8').read())"` 读。
2. **词库正则第一版失败**：`\[(.*?)\]\.map` 返回 0 条——源格式是 `...([...] as const)` 换行 `.map(...)`。修正为匹配 `as const\)\s*\.map` 才成功。
3. **README 误判**：README.md 也被判 binary（含特殊字节）→ python 只读解析。
4. 工作区非 git 仓库；`.novel` 隐藏目录文件搜索工具不识别 → 用 `find`/`ls -la`。

## 五、适配映射（原版 → 工作坊）

| 原版 | 工作坊 |
|------|--------|
| 模型自驱九阶段 | W0 调度派工 |
| novel_* 工具（phase/commit/override）| 文件系统 + W0 派工 |
| 世界书 lorebook | bible v2.5.1 + 人物卡 + 伏笔表（F01-F29）|
| JSONPatch 状态更新 | ledger.json 追加记录（同 schema）|
| 质量自检 | 3 脚本机械质检 → Eos（W5）人工审查 |

## 六、后续可选（未做，等主人）

- 注册 `execution-layer/` 为正式 Hermes skill（主人未拍板）。
- 世界书样例导入酒馆 8001 测试。
- 词库追加项目级覆盖词（同词后者胜，与原版 mergeDictionaries 语义一致）。

## 七、相关文件

- 初评报告：`.novel/reports/dsh-novel-writer-assets-review-v1.md`
- 交付说明：`.novel/reports/execution-layer-delivery-v1.md`
