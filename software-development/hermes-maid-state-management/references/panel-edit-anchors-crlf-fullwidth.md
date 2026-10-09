# 面板编辑三坑：换行符 / 全角标点 / 维护脚本（2026-10-10 实战）

> 本文是 `references/panel-patch-pitfalls.md`（备注追加实操坑）的续篇，专讲**锚点静默 MISS** 的三种非内容性根因。
> 触发场景：改人设、结算落盘、批量改数值时，明明内容没写错，`patch` 却「成功但没改」/「找不到」。

---

## 1. 多行锚点在 CRLF 文件上「静默 MISS」⚠️

同一 `面板存档/` 目录里**行尾不统一**：`maids/<名>.md` 可能是 **CRLF**（`\r\n`），而 `references/` 下的手册多是**纯 LF**。

用 `\n` 写的**多行** old_string 去替换一个 CRLF 文件 → **不报错、内容却没变**（工具返回的 success 是假象）。

**做法（写个 `edit()` 包一层）**：

```python
def edit(p, pairs):
    raw = Path(p).read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    t = raw.replace("\r\n", "\n")
    for old, new, label in pairs:
        if old in t: t = t.replace(old, new, 1); print("✔", label)
        else:        print("✘ MISS:", label)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t.replace("\n", nl))
```

- **诊断信号**：同一批里**多行锚点 MISS、换单行锚点就成功** ⇒ 基本就是 CRLF 作祟，**不要**怀疑内容写错（别去改内容）。

---

## 2. `panel_maintain.py` 会吃掉「备注标题」后的空行 ⚠️

归档脚本（`panel_maintain.py --apply`）**重写**面板文件后，标题与首条之间的空行被抹掉：

```
## 最近备注（按日期倒序，保留最新 6 条）
                                  ← 这个空行被吃掉
- 备注追加…
```

于是「标题 + 空行 + 首条」这种多行锚点**静默 MISS**。

- **做法**：跑完维护脚本后**重新读文件**再取锚点；或一律**锚定唯一单行前缀**（如 `- 备注追加<日期>：`）然后把新条目插在它上方，不依赖任何多行块。
- 实测：Athena 备注 `10/10-2` 就这么 MISS 了一次，改成单行前缀锚点后一次成功。

---

## 3. 全角 `｜`(U+FF5C) ≠ 半角 `|` ⚠️

这些中文档案里，列表/单元格分隔大量用**全角** `｜`（U+FF5C）、**全角**括号 `（）`，不是半角 `|`、`()`。

- 锚点 MISS 时**优先核对是不是全角**；从文件里**原样复制**字符，别手打（肉眼几乎分不出）。
- 实测：`maids/hebe.md` 的专属机制行用全角 `｜` 开头，用半角 `|` 写的锚点直接 MISS。

---

## 4.（连带）人格 / 配置镜像也是副本

改女仆**人设**时，根 `config.yaml` 的 `agent.personalities.<名>`（**旧快照**）与子档案 `config.yaml` 可能仍写着旧值——实测：`profiles/hebe/SOUL.md` 已是「**四姐**」，根 `config.yaml` 却仍写「**三姐**」，两处打架。

- 权威源 = `profiles/<名>/SOUL.md` ＋ skill `lewd-playbook`。
- 镜像要么**同步**、要么在块首加一行「⚠️ 旧快照，以 X 为准」。
- 改 `config.yaml` 前**先备份**（`shutil.copy2` 到 `config.yaml.bak-pre-<事项>-<ts>`）；改完 `yaml.safe_load` 读回验证能解析且新值在、旧值不在。

---

## 一句话总结

编辑这些档案，**命中失败 = 先怀疑「行尾 / 全角 / 维护脚本」三者之一**，再怀疑内容：归一化行尾 + 用唯一单行锚点，多数 MISS 当场消失。
