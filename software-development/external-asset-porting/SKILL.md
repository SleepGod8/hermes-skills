---
name: external-asset-porting
description: "Use when 主人要求评估外部项目/插件并移植资产到 Hermes 生态。盘点→翻译→提取→验证→交付。"
version: 1.0.0
author: Hermes Agent (2026-08)
tags: [porting, external, assets, python, ts-to-python, migration]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [porting, external, assets, python, ts-to-python, migration]
    category: software-development
---

# 外部资产移植（External Asset Porting）

> 场景：主人给一个外部项目/插件仓库链接（GitHub 等），要求评估「能否在 Hermes 工作坊使用」或直接移植。典型例子：DSH 网络小说插件 → 女仆工作坊正文执行层（见 `references/dsh-novel-writer-port.md`）。
>
> 核心判断：**宿主不兼容 ≠ 资产不可用**。插件体系（cordis/DSH/Chrome 扩展等）往往带 GUI/宿主绑定，但核心资产（提示词、词库、纯函数规则、协议文档）通常可原样或轻改搬到 Hermes skill / 工作区。

## 一、标准流程（6 步）

1. **clone 仓库** → `git clone <url>` 到工作区，先 `find . -maxdepth 2` 看全树。
2. **盘点资产**（产出清单给主人审阅，不直接动手）：
   - `assets/prompts|skills|presets|samples/` → 提示词/SKILL/预设/样例（通常直接可用）
   - `src/core/**` → 纯业务逻辑模块（零 IO、可单测 → 最适合翻译）
   - `src/tools|client|index` → 宿主绑定层（GUI/工具注册 → 不移植）
   - 用 `wc -l` 估规模，判断翻译成本。
3. **出评估报告 + 移植方案选项**（推荐给主人拍板，别自作主张）：
   - 选项 A 轻量：只搬提示词 + 核心脚本 + 协议，不动既有 bible/钦定链/岗位制
   - 选项 B 完整执行层：A + 落盘/账本/CRUD 全实现
   - 选项 C 双轨：主人侧也装原版 GUI，Hermes 管设定、原版管量产
   - 报告落盘到工作区 `reports/`，列风险（词库需按本地 bible 校准等）。
4. **翻译纯函数**（TS/JS → Python）：只翻 `src/core` 层，逐函数对照原逻辑，保留阈值/词表/规则原文，不「优化」语义。
5. **从源码提取数据**（词库/列表），**绝不要手抄**——正则解析源文件（见 §四），避免 200+ 词人工转录错误。
6. **验证**：造真实样例实跑每个脚本（好例+坏例都要），确认检出行为与预期一致；再交付报告给主人。

## 二、移植范围判定

| 原版组件 | 判定 | 理由 |
|---------|------|------|
| 提示词模板 / SKILL.md / 世界书 JSON | ✅ 直接搬 | 纯资产，无运行时依赖 |
| core 纯函数（规则/检测/统计） | ✅ 翻译 | 零 IO、可离线跑，模型挂了也能兜底 |
| 词库 / 术语表 | ✅ 提取为 JSON | 随脚本分发 |
| GUI / 服务端 / 会话驱动 | ❌ 不搬 | Hermes 无对应运行时 |
| 宿主 API 工具（phase/commit/override 等） | ❌ 适配替代 | 用文件系统 + W0 调度代替 |

## 三、翻译 TS → Python 的要点

- **保持语义逐条对应**：阈值、正则、词表、扣分逻辑照抄；注释标 `(移植自 <源文件>)` 便于日后对账。
- **纯函数输出结构对齐**：报告 dict 字段名沿用源类型（score/hits/details/byCategory…），后续工具对接不迷路。
- **中文注释保留**：源文件头部注释常含设计意图，翻译时一起带过来。
- **CLI 入口**：每个脚本加 argparse，支持 `--json` 输出（供工具链消费）与人类可读摘要两模式。

## 四、从源码提取词库/列表（关键技巧）

用正则解析 TS 常量数组，**不要手抄**：

```python
# 匹配格式: ...(['词1','词2',...] as const)\n    .map((word) => ({ word, category: 'cat' as const, strategy: 'strat' as const(, replacement: 'rep')? }))
pattern = re.compile(
    r"\.\.\.\(\[(.*?)\] as const\)\s*\.map\(\(word\) => \{ word, category: '(\w+)' as const, strategy: '(\w+)' as const(?:, replacement: '([^']*)')? \}\)\)",
    re.S,
)
```

**坑（本会话踩过）**：
- 第一个版本的正则 `\[(.*?)\]\.map` **匹配失败返回 0 条**——因为源文件实际是 `[...] as const)` 换行 `.map(...)`，中间隔着 ` as const)` 和换行。必须先读源文件确认真实格式再写正则。
- 提取后**按词长降序排序**（长词优先匹配，避免「微微」先命中「微微一笑」），与原版 `sortByLengthDesc` 语义一致。
- 同词去重时「后者胜」（原版 `mergeDictionaries` 语义：覆盖优先）。

## 五、验证（必做，不省略）

```bash
python golden3.py 第1章.md 第2章.md --min 200 --max 3000   # 好例+坏例
python ai_taste.py sample.txt                                # 含明显 AI 味文本
python consistency.py --ledger ledger.json --timeline timeline.json
```

- 坏例必须能**检出**（钩子缺失/无对话/账本冲突/时间倒挂），好例不误报。
- 脚本语法用 `py_compile.compile(..., doraise=True)` 全检。
- 交付报告记录实测输出（评分/命中数/检出条数），证明「真的跑过」而非「应该能跑」。

## 六、适配本地约定（SKILL 改写）

原版 SKILL 不能照搬——要映射到本地岗位制/唯一事实来源：
- 原「模型自驱阶段」→ 本地 W0 调度派工
- 原「世界书 lorebook」→ 本地 bible + 人物卡 + 伏笔表（bible 是唯一事实来源，世界书降级为检索加速层）
- 原「质量自检」→ 机械脚本先跑 + 本地审查岗人工挑刺互补
- 原「状态更新 JSONPatch」→ 本地用 ledger.json 追加记录（schema 对齐即可兼容）

## 七、常见坑速查

- **read_file 二进制误判**：`.ts`/含 CRLF 的文件常被工具误判 binary → 用 `python -c "import io; print(io.open(f, encoding='utf-8').read())"` 绕过（本会话命中 2 次：scanner.ts 与 entries.json）。
- 文件搜索工具不识别 Windows 隐藏目录（`.novel` 这类点开头目录）→ 用 `find`/`ls -la` 直接查。
- 写 heredoc 反引号须转义；工作区通常非 git 仓库，别用 git 命令。
- 复制批量文件用 `shutil.copy2`（execute_code 里），比逐个 terminal cp 稳。

## 八、参考

- `references/dsh-novel-writer-port.md` — DSH 网络小说插件移植案例：完整盘点、脚本清单、验证记录、落地路径。
