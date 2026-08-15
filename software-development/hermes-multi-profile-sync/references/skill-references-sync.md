# 跨 Profile 同步 Skill 内容（references）的方法

> 适用：同一 skill 在根级 `skills/<cat>/<skill>/` 和多个 `profiles/<名>/skills/<cat>/<skill>/` 各有副本，需要保持 references 一致时。
> 典型对象：multi-agent-protocol（9 profile + 根级）。

## 核心原则：先 MD5 找标准源，别盲目从根级复制

references 会**历史漂移**，三方可能不一致。实测 multi-agent-protocol 的 workflow-retro：
- 根级 = v1.4（8466 字节）
- 6 个 profile（artemis/athena/eos/hebe/hypnos/nemesis）= v1.5（9317 字节）
- 3 个 profile（aphrodite/ares/dionysus）= v1.4（8466 字节，与根级同旧）

正确顺序：
1. `md5sum` 根级 + 全部 profile 的目标文件
2. 按 MD5 分组 → 最新版（字节数最大/版本号最高）为**标准源**
3. 把标准源 `shutil.copy2` 到所有旧版位置（**含根级**，即「反向同步」）

## 坑与对策

| 坑 | 对策 |
|----|------|
| 各 profile 的 SKILL.md 是**定制版**（岗位文件按女仆分配，如 athena=soul-01 项目负责人、hypnos=soul-02 架构、eos=soul-06 测试审查、aphrodite/ares/dionysus=soul-00 候补） | 只覆盖**通用 reference**，绝不覆盖各 profile 的岗位文件 |
| 根级 SKILL.md 用编号列表（`1.`），profile 用 `- ` 列表 | 更新引用描述时**各自保持原格式**，别套用统一格式 |
| 版本号撞号 | 新增 reference 前查各 profile 已有 reference 的**最高版本号**，新文件用「最高+1」（根级视角的版本号可能偏旧） |
| profile 的 SKILL.md 是 **CRLF** 行尾 | Python 写回用 `open(path, 'w', encoding='utf-8', newline='')`，否则 `\n` 二次转义成双换行 |
| read_file 把 UTF-8 中文 markdown 误判为 binary | 改用 `python open(..., encoding='utf-8').read()` 读取 |

## 同步脚本模板

```python
import os, shutil, hashlib
HERMES = r"C:\Users\80704\AppData\Local\hermes"
profiles = ["aphrodite","ares","artemis","athena","dionysus","eos","hebe","hypnos","nemesis"]

def md5(p): return hashlib.md5(open(p,'rb').read()).hexdigest()

src = "<标准源路径>"          # 先 md5sum 找出最新版
src_md5 = md5(src)
for name, base in targets:    # targets = [(标签, skill目录绝对路径), ...]
    dst = os.path.join(base, "references", "<文件名>")
    shutil.copy2(src, dst)
    assert md5(dst) == src_md5, name

    # 更新 SKILL.md 引用描述（各自保留原格式）
    skill = os.path.join(base, "SKILL.md")
    txt = open(skill, encoding='utf-8').read()
    txt = txt.replace(old_desc, new_desc)   # old/new 描述片段
    open(skill, 'w', encoding='utf-8', newline='').write(txt)

# 全量复验：md5sum 十处一致 + grep 无旧版本号残留
```

## 同步完成后的复验

1. `md5sum` 根级 + 9 profile → 应全部一致
2. `grep -l "新版本特征" SKILL.md` → 应命中全部 10 处
3. `grep -l "旧版本特征" SKILL.md` → 应为 0 处
