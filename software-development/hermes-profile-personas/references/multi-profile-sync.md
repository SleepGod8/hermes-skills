# 子档案 SOUL.md + config.yaml 同步模板

实战验证：4 次单档案新增模块 + 1 次跨档案 7 文件规则修改（2026-08，女仆家族 Hermes 档案系统）。

## 单档案新增模块（artemis/athena/hebe 等）

1. 先 patch 子档案 SOUL.md，用锚点插入（文件尾部固定锚点前，如 `## 茶会日常+野兽+疯狂口穴 🆕`）。

2. execute_code 同步 config.yaml：

```python
import shutil, yaml
from pathlib import Path

p = Path(r"C:\Users\80704\AppData\Local\hermes\profiles\athena\config.yaml")
shutil.copy2(p, p.with_suffix(".yaml.bak-<tag>"))                 # 1. 备份

c = yaml.safe_load(p.read_text(encoding="utf-8"))
sp = c["agent"]["system_prompt"]

anchor = "- 被主人打趣会罕见地别过脸：「……这是、数据整理。仅此而已。」\n\n## 事后报告"
assert anchor in sp, "anchor not found!"                           # 2. 锚点必须存在

new_block = '''- 被主人打趣会罕见地别过脸：「……这是、数据整理。仅此而已。」

## 新模块 🆕
- 设定内容...

## 事后报告'''                                                      # 3. 新模块插在锚点处

c["agent"]["system_prompt"] = sp.replace(anchor, new_block, 1)
p.write_text(
    yaml.dump(c, allow_unicode=True, default_flow_style=False, sort_keys=False),
    encoding="utf-8",
)

# 4. 读回验证
sp2 = yaml.safe_load(p.read_text(encoding="utf-8"))["agent"]["system_prompt"]
assert "新模块" in sp2
print("ok")
```

关键点：
- `allow_unicode=True`（中文/emoji 不转义）、`sort_keys=False`（保序）、`default_flow_style=False`（块格式）
- 锚点用 SOUL.md 与 config.yaml 中**都存在的同一段文本**，保证两边一致
- yaml 库加载后 emoji/中文引号都是正常字符，`str.replace` 直接匹配
- 备份名用带语义的后缀：`.bak-pre-m`（M属性）、`.bak-pen`（男根）、`.bak-ht`（后庭）

## 跨档案规则修改（一次改 7 处）

以「野兽模式男根规则」为例，枚举：

| 文件 | 内容 |
|---|---|
| default `SOUL.md` | 表格区 + Hermes/Iris 表 + 跨档案联动段（2~3 处替换点） |
| default `config.yaml` | `personalities.lewd-maid` 字符串内同样多处（同一串逐个 replace） |
| 每个子档案 `SOUL.md` | 各档案野兽模式段落 |
| 每个子档案 `config.yaml` | `agent.system_prompt` 对应段落 |

default config.yaml 的 `agent.system_prompt` 是基础版人格，可能不含目标串——先 `if "xxx" in sp` 判断再替换。

## 验证坑

- 检查关键词必须与实际写入文本一致：先 `grep -n "实际文本" file` 确认再写断言，否则误报 ❌
- 改完用「读回 yaml + grep」双重确认；备份文件保留到主人确认无误
