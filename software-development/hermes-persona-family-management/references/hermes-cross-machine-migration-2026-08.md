# Hermes 多档案跨机迁移合并（另一台电脑 → 本机）

实测 2026-08-07：把另一台电脑（用户名 `Windows`）的完整 Hermes 配置包迁移到本机并**合并**（不覆盖本机原配置）。迁移包约 32.5MB / 4999 文件，含根配置 + 6 个档案 + 全套技能/记忆/插件/cron。

## 迁移包结构

```
hermes-multiagent-config.tar.gz
├── config.yaml  SOUL.md  .env        # 根级（另一台电脑的版本）
├── memories/    MEMORY.md USER.md    # 另一台电脑的记忆
├── skills/                           # 根级技能（~38 个目录）
├── plugins/  cron/  hooks/           # 扩展组件
└── profiles/<name>/                  # 每档案: config.yaml + SOUL.md + .env + memories/ + skills/
```

包已剔除 state.db（会话历史）、缓存、日志。注意：**包内 `computer-use` 技能是损坏 symlink**（指向 `/c/Users/Windows/.agents/skills/computer-use`，本机无此路径），解压报 `Cannot create symlink`，跳过即可（本机根级有可用版）。

## 第一步：差异对比（决定合并策略）

1. **顶层结构对比**：`tar -tzf | awk -F/ 'NF>=2{print $1"/"$2}' | sort -u` vs `ls ~/AppData/Local/hermes/`；先看本机 profiles 有哪些、包里有哪些（本例：本机 5 个无 iris，包 6 个多 iris）。
2. **关键文件大小对比**（大小悬殊 = 内容悬殊）：
   - 根 SOUL.md：本机 13.5KB（Hermes×Iris v9.4 权威版）vs 包 529B 基础版 → **保护本机**
   - 根 config.yaml：本机 68KB/23 种人格 vs 包 9.7KB/15 种 → **保护本机**；包 MCP 路径全是 `C:\Users\Windows\...`，本机无效
   - 各档案 SOUL.md/config.yaml：本机 10-19KB（0807 迭代版）vs 包 1.3-1.7KB 基础版 → **保护本机**
3. **.env key 对比**（不显示值，只看 key 名）：
   ```bash
   grep -oE "^[A-Z_]+=" .env | sort > pkg_keys.txt
   grep -oE "^[A-Z_]+=" "$LOCALAPPDATA/hermes/.env" | sort > local_keys.txt
   comm -23 pkg_keys.txt local_keys.txt   # 包有本机无
   comm -13 pkg_keys.txt local_keys.txt   # 本机有包无
   ```
   选择性补充时注意：Telegram/QQ 相关 key 若本机记忆明确禁用 → 跳过（避免误启用拖死 gateway）。
4. **skills 差异**：`ls` 对比目录；同名目录用 `find <dir> -type f | wc -l` 对比文件数（文件数不同 = 需要文件级合并）。
5. **cron 对比**：`python -c "import json; ..."` 读 jobs.json 的 name/script/enabled——本机已有 job 绝不覆盖。

## 第二步：合并策略分级

| 级别 | 内容 | 做法 |
|------|------|------|
| 🟢 纯新增 | 包有本机无的档案、技能目录、插件 | 直接复制 |
| 🔴 保护本机 | 根 SOUL/config/memories、本机已有档案的 SOUL/config、cron、同名技能 | 一律不动（本机是权威/最新版） |
| 🟡 选择性 | .env 补充 key、moa 配置、包记忆信息 | 先过问主人（用 clarify 给组合选项） |

**用户明确要求**：涉及修改本机原配置和档案必须先过问。默认执行最保守方案（只做纯新增），C 组等主人拍板。

## 第三步：档案级 skills 合并（目录级）

只补缺失技能目录，不覆盖已有：
```bash
missing=$(comm -23 <(ls profiles/$p/skills/ | sort) <(ls "$LOCALAPPDATA/hermes/profiles/$p/skills/" | sort))
for s in $missing; do cp -r "profiles/$p/skills/$s" "$LOCALAPPDATA/hermes/profiles/$p/skills/"; done
```

## 第四步：同名技能文件级合并（文件级）

只补包内 unique 文件，绝不覆盖本机已有。用 Python（bash 的 `/tmp` 在 Python 里不存在，先 `cygpath -w /tmp/...` 取 Windows 路径）：
```python
for root, dirs, files in os.walk(pkg_skill):
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules', '.venv')]
    for f in files:
        dst = os.path.join(local_dir, rel, f)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)   # 只补缺失
```

## 第五步：新档案路径/平台适配

包内档案 config.yaml 有另一台电脑的路径引用，直接复制会导致启动报错：
1. **MCP servers**：`command`/`args`/`env` 里的 `C:\Users\Windows\...` → 本机 `C:\Users\<本机用户>\...`；`D:\Program Files\Hermes Studio` → 本机安装路径（本例 `E:\Hermes Studio`）。参考本机已有档案（如 artemis）的 mcp_servers 段照抄路径，只改 `HERMES_WEB_UI_PROFILE` 为档案名。
2. **平台启用**：按本机经验禁用不稳定平台。⚠️ **platforms 是嵌套结构**（`qqbot:\n    enabled: true`），正则要匹配嵌套：`re.sub(r'(  qqbot:\n    enabled:) true', r'\1 false', s)`——只改 platforms 段，别误伤 toolsets 段（那里也有 `qqbot:`）。
3. **.env 是隐藏文件**：`ls` 不显示，验证用 `ls -a` 或 `wc -c`。

## 坑清单

- **cp -r 复制插件目录会散落文件**：`cp -r plugins/orca-status 目标/plugins/` 实测把 `plugin.yaml`/`__init__.py` 散到 plugins/ 根下而不是 `plugins/orca-status/` 子目录 → 复制后必须 `find 目标 -maxdepth 2` 验证，发现散落就 `mkdir -p` + `mv` 修复。
- **symlink 技能跳过**：`computer-use` 是损坏 symlink，`find -type f | wc -l` 为 0，跳过并说明（本机根级有可用版）。
- **验证 hermes profile show**：6 个档案全绿（Profile/Model/Skills/SOUL.md/.env/Gateway）；新档案 Gateway stopped 是正常的（首次使用自动启动）。
- **群聊多 agent 能力评估**（迁移后常问"能不能群聊协作"）：
  - Studio 群聊功能存在性：`grep -o "创建房间\|添加智能体\|群聊\|邀请码" <Studio>/resources/webui/dist/client/assets/js/zh-*.js`
  - 群聊 Agent = Profile 列表（6 档案直接可添加）+ 编程工具（Codex/Claude Code，`which` 检查）
  - Codex 配置在 `~/.codex/`（auth.json+config.toml）但可执行文件可能缺失 → 需重装 `npm install -g @openai/codex`
