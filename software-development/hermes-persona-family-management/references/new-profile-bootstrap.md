# 新档案建档 + 年龄排序批量同步（2026-08 Hypnos 实测）

## 1. 从零建档（profiles/hypnos/ 案例）

```python
import os, yaml

HOME = r'C:\Users\80704\AppData\Local\hermes'
HYPNOS_DIR = os.path.join(HOME, 'profiles', 'hypnos')
os.makedirs(HYPNOS_DIR, exist_ok=True)

# SOUL.md：人格 + 年龄定位 + 🔞色情设定 + 共通机制10条 + 家族玩法 + 姐姐联动
soul = """...完整文本..."""

# CRLF 写 SOUL.md（与家族一致）
with open(os.path.join(HYPNOS_DIR, 'SOUL.md'), 'w', encoding='utf-8', newline='') as f:
    f.write(soul.replace('\n', '\r\n'))

# config.yaml 不手写：复制 artemis 骨架，只换 system_prompt
src_cfg = os.path.join(HOME, 'profiles', 'artemis', 'config.yaml')
dst_cfg = os.path.join(HYPNOS_DIR, 'config.yaml')
cfg = yaml.safe_load(open(src_cfg, encoding='utf-8'))
cfg['agent']['system_prompt'] = soul
with open(dst_cfg, 'w', encoding='utf-8') as f:
    yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

# 验证：读回 system_prompt，检查专属玩法 + 共通10条 + 年龄定位 各关键子串，逐项 OK/MISS
sp = yaml.safe_load(open(dst_cfg, encoding='utf-8'))['agent']['system_prompt']
```

## 2. 年龄排序批量同步（7 档案）

### 先扫描（找出哪些文件有排序行、什么格式）

```python
KEY = 'Athena > Hermes×Iris'
# 遍历 default SOUL + 各档案 SOUL/config；config 用 yaml 库取 system_prompt
# （default config 取 agent.personalities.lewd-maid）
# 输出 count + 排序行样例
```

扫描结果（本案例）：
- default SOUL：count=1，加粗行 `**Athena > … > Eos**` + 表格
- athena/artemis/hebe/nemesis SOUL + config：count=1，普通行 `- 女仆家族年龄排序：…`
- eos SOUL：count=1（+ 定位行「排行第六」）
- eos config / iris SOUL+config / default config：count=0 → 跳过

### 批量替换

```python
SORT_OLD = 'Athena > Hermes×Iris > Hebe > Artemis > Nemesis > Eos'
SORT_NEW = 'Athena > Hermes×Iris > Hebe > Artemis > Nemesis > Hypnos（18） > Eos（16）'

# SOUL 文件：读（newline='' 保留 CRLF）→ count==1 才 replace → 写回
# config 文件：shutil.copy2 备份 .bak-age-sync → yaml 库 → sp.replace(LF 变体) → yaml.dump 写回
# default SOUL 额外：表格插新行
#   '| 6 | Eos | …' → '| 6 | Hypnos | …\r\n| 7 | Eos | …'
# eos SOUL 额外：定位行 '- 本档案定位：…（排行第六）' → '（排行第七）'
```

### 验证陷阱（本案例实际踩到）

- hypnos 自身排序行用了加粗 `> **Hypnos（18）** > Eos（16）`，普通版 `SORT_NEW` 匹配不到 → 验证输出 `FAIL hypnos config`（误报）
- 用加粗版子串再验证一次 → True。**验证字符串必须与实际写入格式一致**
- 全部断言：新排序 count>=1 且旧排序 count==0 才算过

## 3. 用户决策流（本案例）

draft 展示 → clarify(年龄定位：用户答「18岁，只比eos大」) → clarify(建档+方向：用户选「建档案+共通机制」) → 建档 → clarify(同步范围：用户选「同步全部7档案」)。新档案需新开会话（/new）才生效。
