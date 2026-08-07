---
name: hermes-config-migration
description: "跨电脑 Hermes 配置迁移：打包(本机→新机)与还原合并(新机接收包→合并进已有环境)。覆盖用户铁律(先过问)、档案级 skills 合并、MCP 路径适配、平台 enabled 检查、cp -r 目录 bug、hermes profile show 验证。Use when 用户要把另一台电脑的 Hermes 配置/档案/技能迁移到本机，或把本机配置打包带走。"
version: 1.0.0
author: agent
license: MIT
tags: [hermes, migration, profiles, multi-machine, merge, config]
platforms: [windows]
---

# Hermes 配置迁移（打包 + 还原合并）

跨电脑迁移 Hermes 全套配置（config/SOUL/env/memories/skills/plugins/cron/profiles）。两个方向：

- **打包方向**（本机 → 新机）：`tar -czf` 归档核心配置（不含 state.db 的轻量方案 A / 含历史的方案 B），详见 `hermes-skills-sync/references/full-config-migration.md`（受保护技能，内容仍可参考）。
- **还原合并方向**（新机接收包 → 合并进已有环境）：本文重点。目标机**已有 Hermes 配置**时如何安全合并，2026-08-07 实测（本机 5 档案 + 包 6 档案 → 6 档案）。

## 触发条件

- 用户提供 `hermes-multiagent-config.tar.gz` 之类迁移包，要求"解压合并到 %LOCALAPPDATA%\hermes"、"6 个档案 + 人设/技能/记忆/协作机制"
- 用户提供 rar/zip 的 skill/文档导出包，要求"按 Hermes 档案配置分别导入"（如 multi-agent-export.rar 按 6 档案分开装 skill）
- 用户要求把本机 Hermes 打包搬到另一台电脑
- 用户要求**统一多个档案中同名技能的命名/路径/结构**（同机规范化，2026-08-07 实测：六档案 multi-agent-protocol 目录/文件名/岗位文件/共享档案 MD5 全统一）
- 用户要求**新写一个全档案共享的技能/协议并同步到所有女仆档案**（2026-08-07 实测：group-chat-autonomous-chat 同步 9 档案 + 根级）
- 关键词：迁移、合并、hermes profile show、另一台电脑的配置、统一命名、统一路径、同步到所有档案

## ⚠️ 档案列表会变（2026-08-07 实测）

**不要按记忆里的旧档案列表硬编码**。本机女仆档案已从 6 个变为 9 个：
`aphrodite/ares/artemis/athena/dionysus/eos/hebe/hypnos/nemesis`（iris 已迁移为 hypnos，
另有 3 个新增：aphrodite 冷感魅魔 / ares 假小子 / dionysus 微醺直球）。用户可能在其他会话
里用 Studio 或 CLI 增删档案（迁移痕迹如 `config.yaml.bak-iris-migrate`）。**同步/遍历前
先 `ls $HERMES_HOME/profiles/` 确认实际档案名**，用实际列表循环，不要写死。

## 用户铁律（先过问，不可跳过）

目标机已有配置/档案时：**合并优先，绝不覆盖原配置**；涉及修改原配置和档案的**先向用户过问**（逐项差异清单 + clarify 选执行范围）。纯新增项（本机不存在的档案/技能/插件）可直接做。用户明确追加"同名档案的 skills 也要合并"时，合并 = 只补缺失、不覆盖同名。

## 迁移包结构

根级 `config.yaml` / `SOUL.md` / `.env` + `memories/` + `skills/` + `plugins/` + `cron/` + `hooks/` + `profiles/<名>/{config.yaml,SOUL.md,.env,memories,skills}`。
注意 `.env` 是隐藏文件，`ls` 默认不显示，用 `ls -a` 确认。

## RAR/zip skill 导出包导入（按档案分开装 skill 的场景）

用户给 `*.rar`/`*.zip`，里面按档案目录分装 skill 文件（如 `multi-agent-export/{artemis,athena,eos,hebe,iris,nemesis}/`，各档案下可能是标准 skill 结构 `SKILL.md + references/`，也可能是散文件 `01-xxx.md`）。导入目标 = `profiles/<档案>/skills/<分类>/<skill名>/`。

### 解压（本机 7-Zip 在 D:\7-Zip）

- 7-Zip 路径：**`D:\7-Zip\7z.exe`**（本机实测位置，不在 C:\Program Files；用正斜杠 `"D:/7-Zip/7z.exe"` 调用）
- **7z.exe 不认 MSYS 路径**（`/c/Users/...` 报 "系统找不到指定的路径"），必须传 Windows 原生路径 `C:\Users\...`
- 解压前先 `7z l <包>` 列内容看结构；`7z x -y <包>` 解压
- 中文文件名解压后正常显示（Rar5 存 UTF-8，列表乱码只是终端显示问题）

### 差异分析（MD5 全量比对，不用 sed）

散文件包常常只是导出快照——**本机同名 skill 可能已同步过且 MD5 完全一致**。先逐档案比对包内文件 vs 本机 `skills/<分类>/<skill名>/` 的全部文件 MD5：

- 全部一致 → 该档案已同步，跳过不动（本次 artemis/athena/eos/hebe/nemesis 全是这种情况）
- 本地缺失 → 纯新增，直接 `mkdir -p` + `cp`（含 references/），导入后**再 MD5 复核**
- 同名不同 MD5 → 不覆盖，按用户铁律过问

**MD5 比对用 Python**（`scripts/md5-diff.py <包目录> <本机skill目录>`，输出 OK/DIFF/MISSING/EXTRA）：`sed` 处理含反斜杠的 Windows 路径会报 `Invalid back reference`（本会话实测踩坑）；`md5sum` 逐文件在 shell 里做路径拼接也易出错。

### 清理陷阱（rm -rf busy）

`rm -rf <目录>` 报 `Device or resource busy`：**bash 会话当前工作目录还停在被删目录里**（之前 cd 进去过）。先 `cd` 到别处（如 workspace）再删即可。cmd 的 `rmdir /s /q` 同样被锁，不是权限问题。

## 多档案技能结构归一化（统一命名/路径/内容）

用户要求"优化 6 个档案的同类技能，统一文件命名、路径"时（2026-08-07 实测：multi-agent-protocol 六档案归一化）。目标形态：目录名、references 文件名、frontmatter name、SKILL.md 内部引用全部一致，共享档案 MD5 六档案字节级一致。

### 归一化流程

1. **盘点现状**：Python `os.walk` 列出每档案技能树 + 每文件 MD5/大小，输出差异矩阵（目录名不同？文件名大小写不同？岗位文件命名几套风格？哪些档案缺独立协议文件？）。
2. **定规范**：目录统一 `skills/<分类>/<技能名>/`；岗位文件统一 `soul-0N-<岗位>.md`（如 soul-01-project-lead / soul-02-recon-architect / soul-06-test-review）；协议主文件统一小写（如 `multi-agent-protocol.md`）；独立岗位技能（如 `agent-5-feature-developer/`）并入 references/。
3. **定权威版**：共享档案以内容最全/最权威的档案为基准（如 athena/eos），其他档案对齐。
4. **文件操作 + 引用同步一起做**：重命名后必须同步改——各档案 SKILL.md 内部引用、`skill_view(name='...')`、路径登记表、team-sync 的 DIRS 映射、verify 脚本 BASE 路径。改完做**全量残留扫描**（旧文件名/旧路径/源机用户名）。
5. **frontmatter name 与目录名对齐**：目录改名后 SKILL.md frontmatter 的 `name:` 必须同步改（hebe: multi-agent-collab-protocol → multi-agent-protocol），否则该 skill 不被识别。
6. **验证**：`scripts/verify-profile-skill.py <技能名>`（跨档案盘点 + 共享 MD5 一致性 + 旧名残留扫描，一键 PASS/FAIL） + `hermes profile show` 各档案 Skills 数正常。

### Windows 文件系统坑（归一化必踩）

- **大小写重命名是 no-op**：Windows 文件系统大小写不敏感，`os.rename('MULTI-AGENT-PROTOCOL.md', 'multi-agent-protocol.md')` **静默成功但文件名不变**（`os.path.isfile` 对两个名字都返回 True，误判"已存在/已改名"）。纯大小写改名必须两步：先 rename 到临时名（`_tmp_xxx`），再 rename 到目标名。
- **CRLF/LF 导致 MD5 漂移**：Python `open(..., encoding='utf-8')` 读文本再写回会转换行符（universal newlines），同一内容 MD5 会变。共享档案要字节级一致必须**二进制读写**（`rb`/`wb` 原样复制），否则六档案 MD5 对不齐。
- **单反斜杠 vs 双反斜杠混淆**：文件里实际是单反斜杠 `C:\Users\...`，但 `repr()`/终端显示为双反斜杠；用 raw string `r"C:\Users\..."`（单反斜杠）匹配才成功。且 `C:\Users` 是 `C:\\Users` 的子串，肉眼检查会假阳性——拿不准就读原始字节确认。
- **⚠️ 删"重复目录"前先看父目录内容**：iris 的 `skills/autonomous-ai-agents/multi-agent-protocol` 是重复副本，但父目录 `autonomous-ai-agents/` 下还有 13 个正常技能（claude-code/codex/opencode 等）。`shutil.rmtree(父目录)` 会**连坐误删**正常技能。只删精确目标目录；若已误删，同技能在其他档案都有副本（如 artemis），`shutil.copytree` 恢复 + MD5 校验。
- **MSYS 删目录 busy**：bash cwd 停在被删目录内时 `rm -rf`/`cmd rmdir` 报 Device or resource busy——先 `cd` 出去再删。

## 新写全档案共享技能/协议（同步到所有女仆档案）

用户要求"写一个 X 协议/技能并同步到所有档案"时（2026-08-07 实测：群聊自主沟通协议
`group-chat-autonomous-chat` 同步 9 档案 + 根级）：

1. **先问清用途范围，别自作主张**：用户要「群聊自主沟通协议」时只写**日常聊天**场景，
   **绝不混入多 Agent 协作开发内容**（A1-A6 接力链、[STATUS]/[HANDOFF] 格式、契约冻结、合流发布）。
   首次起草混入开发协议被用户明确纠正：「这份协议只是用于群聊聊天，不涉及多agent协作开发」。
   开发协作另走 `multi-agent-protocol.md`。拿不准时用 clarify 确认「聊天 vs 开发」定位。
2. **组装 SKILL.md**：YAML frontmatter（name 小写连字符 + description 含 Use when 触发词）+ 正文。
   正文用自然语言规则表（优先级 P0-P4、接力轮次上限、防刷屏纪律、冷场兜底、主人边界），
   不套开发消息格式；触发词按各档案人设写（Aphrodite↔穿搭魅力、Ares↔体力、Athena↔推理、
   Hypnos↔困、Nemesis↔毒舌）。
3. **同步目标 = 所有女仆档案 + 根级**：`profiles/<名>/skills/<分类>/<技能名>/SKILL.md` 逐个写 +
   根级 `skills/<分类>/<技能名>/SKILL.md`（default 档案也参与群聊）。**先 `ls profiles/` 拿实际
   档案列表**（见上节档案会变），不要用记忆里的旧列表。
4. **CRLF + MD5 全一致**：内容用 `\r\n`（`content.replace('\n','\r\n')`），写完 `hashlib.md5(open(p,'rb'))`
   校验全部档案 MD5 一致。
5. **验证**：`hermes profile show <各档案>` Skills 数增加 + 抽查 SKILL.md frontmatter 可读。

## 合并前差异分析（必做）

1. 包完整性：`gzip -t <tar.gz>`
2. 包 vs 本机对比：
   - 顶层：`tar -tzf <pkg> | awk -F/ 'NF>=2{print $1"/"$2}' | sort -u` vs `ls $HERMES_HOME`
   - 技能差异：`comm -23 <(包 skills 列表) <(本机 skills 列表)`（包有本机无 = 可新增）
   - 同名文件比大小：**包内档案 SOUL.md 远小于本机**（如包 1.6KB vs 本机 10KB）= 基础版 vs 深化迭代版 → 绝不覆盖
3. 逐项清单按三组分类汇报：🟢 纯新增（建议直接做）/ 🔴 不覆盖（本机权威版）/ 🟡 可选择性合并（.env key、moa、记忆信息——逐项让用户拍板）

## 合并执行（纯新增原则）

### 档案级 skills 合并（只补缺失，不覆盖同名）

```bash
for p in artemis athena eos hebe nemesis; do
  missing=$(comm -23 <(ls pkg/profiles/$p/skills/ | sort) <(ls $HERMES_HOME/profiles/$p/skills/ | sort))
  for s in $missing; do
    cp -r pkg/profiles/$p/skills/$s $HERMES_HOME/profiles/$p/skills/ && echo "$p: +$s ✓"
  done
done
```

- **symlink 技能跳过**：tar 解压时报 `Cannot create symlink to '/c/Users/<源机用户>/...'` 的技能目录是损坏链接（源机路径），复制过来无效——本机根级可能有可用版本，直接跳过并记录。
- 新档案（本机无）的 skills 直接全量复制。

### 路径适配（必须！否则新档案启动报错）

迁移包 config 的 `mcp_servers` 常指向**源机路径**（`C:\Users\Windows\...`、`D:\Program Files\Hermes Studio\...`），本机无效。
**参考本机已有档案的 mcp_servers**（即本机有效路径），替换迁移档案对应块：
- `command`: `C:\Users\<本机用户>\.hermes-web-ui\desktop-runtime\hermes\<ver>\win-x64\node\node.exe`
- `args[0]`: `<Hermes Studio 安装盘>:\Hermes Studio\resources\webui\bin\hermes-studio-mcp.mjs <toolset>`
- env 的 `HERMES_WEB_UI_HOME` / `HERMES_WEBUI_STATE_DIR` 改本机路径；`HERMES_WEB_UI_PROFILE` 保持档案名

用**字符串替换**（YAML 里是转义路径 `C:\\Users\\Windows\\...`）最稳，避免 yaml round-trip 改格式：
```python
s = s.replace(r'C:\Users\Windows\.hermes-web-ui', r'C:\Users\<本机用户>\.hermes-web-ui')
s = s.replace(r'D:\Program Files\Hermes Studio', r'E:\Hermes Studio')
```

### 平台 enabled 检查（新档案风险）

迁移档案自带源机平台的凭据（QQ/Telegram 的 .env key）+ `enabled: true`。若本机经验是某平台不稳（如 QQ 拖死网关），把新档案 `platforms.<平台>.enabled` 改为 false。**YAML 是嵌套结构**，正则要匹配缩进：
```python
s = re.sub(r'(  qqbot:\n    enabled:) true', r'\1 false', s)
```
先 `grep -n -A3 "qqbot" config.yaml` 看实际格式，避免误改 toolsets 段同名键（`toolsets: qqbot:` 与 `platforms: qqbot:` 是两处）。

### cp -r 目录复制 bug（MSYS）

`cp -r <src-dir> <已有目标目录>/` 可能把**目录内容散到目标根**（orca-status 的 plugin.yaml/__init__.py 直接进 plugins/ 根，而非 plugins/orca-status/）。复制后**必须 find 验证目录结构**，发现散落时修复：
```bash
mkdir -p <目标>/<目录名> && mv <目标>/<散落文件> <目标>/<目录名>/
```

## 验证

`hermes profile show <名>` 逐个验证全部档案：Model / Skills 数 / Gateway / .env / SOUL.md 均在。新档案 Gateway 显示 `stopped` 属正常（首次使用才启动）。`hermes profile show` 需要档案名参数，没有"列出全部"子命令。

## 敏感处理

- .env 对比只显示 key 名（`grep -oE "^[A-Z_]+=" .env | sort` + `comm`），**不显示值**。
- 源机 .env 里的平台凭据（QQ/TELEGRAM）默认不导入本机（本机有意禁用）。
- 迁移包 config 的 custom_providers 硬编码 key 是源机的（全局有效可保留），但 moa 引用的模型（如 anthropic/claude-opus-4.8）若本机无对应 key 则导入后不可用——先核对再导。

## 实测清单（2026-08-07 本机 5→6 档案，源机用户名 Windows）

| 项 | 结果 |
|----|------|
| 新增 profiles/iris（SOUL+config+.env+memories+36 skills） | ✓ |
| 根级新技能 3 个（comfyui-rtx4060-8gb-workflow / high-reliability-coding-workflow / skill-authoring-quality-workflow） | ✓ |
| plugins/orca-status（修复 cp 散落 bug） | ✓ |
| 档案级 skills：artemis 32 / athena 32 / eos 36 / hebe 32 / nemesis 35（+17，跳过损坏 symlink computer-use） | ✓ |
| iris config：MCP 路径替换 + qqbot 禁用 | ✓ |
| 原配置保护：根 SOUL/config/memories/cron/5 档案全部未动 | ✓ |
| `hermes profile show` 6 档案全绿 | ✓ |
| RAR skill 导出包 multi-agent-export.rar（2026-08-07）：7z 在 D:\7-Zip 解压 → MD5 比对发现 artemis/athena/eos/hebe/nemesis 已同步，仅 iris 缺 multi-agent-protocol → 导入 SKILL.md+references×4，show iris Skills 136 验证 | ✓ |
