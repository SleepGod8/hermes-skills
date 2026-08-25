# DSH EAC 插件 CLI 安装（`dsh plugin` + pnpm）

## dsh CLI 路径

DSH EAC 桌面端**不在 PATH 里注册 `dsh` 命令**。CLI 内置在 EAC 目录：

```
E:\Deepseek Harness EAC\dsh-desktop\node_modules\.bin\dsh
```

调用方式（bash）：
```bash
DSH_BIN="E:/Deepseek Harness EAC/dsh-desktop/node_modules/.bin/dsh"
"$DSH_BIN" --version
```

或在 PowerShell 里（需 ExecutionPolicy Bypass）：
```powershell
powershell -ExecutionPolicy Bypass -Command "& 'E:\Deepseek Harness EAC\dsh-desktop\node_modules\.bin\dsh' --version"
```

## dsh plugin 命令

```bash
# 安装插件到 web-desktop profile
"$DSH_BIN" plugin --profile web add <package-name>

# 查看已安装插件
"$DSH_BIN" plugin --profile web list
```

**注意**：`dsh plugin` 实际转发给 pnpm。DSH 内置 pnpm（版本 ~11.22），位于：
```
E:\Deepseek Harness EAC\resources\npm\bin\npm-cli.js
```
但更推荐直接用 profile 目录的 pnpm。

## 三步注册新插件流程

### 1. 安装 npm 包到 profile

在 profile 目录下执行（pnpm 优先，npm 有 peer dep 冲突时用 pnpm）：

```bash
cd "$HOME/.dsh/profiles/web-desktop"

# 推荐 pnpm（peer dep 处理更好）
pnpm add <package-name>@<version>

# 备选 npm（可能有 peer dep 冲突）
npm install <package-name>@<version> --legacy-peer-deps
```

**已知坑**：npm 安装 DSH 插件时 `@deepseek-ai/*` peer dep 冲突频繁（`dsh-pet@0.1.8` 要求更新版本的核心包），pnpm 有 warning 但能成功安装。

### 2. 注册到 dsh.profile.bundles

编辑 `~/.dsh/profiles/web-desktop/package.json`，在 `dsh.profile.bundles` 数组末尾追加包名：

```json
"dsh": {
  "profile": {
    "bundles": [
      "...existing bundles...",
      "<package-name>"
    ]
  }
}
```

### 3. 插入 cordis.patch.yml

编辑 `~/.dsh/profiles/web-desktop/cordis.patch.yml`，在末尾追加：

```yaml
- insert:
    - id: <plugin-id>        # 用户自定义 ID
      name: '<package-name>' # npm 包名，必须与 node_modules/ 下一致
```

**注意**：部分插件自带 `cordis.patch.yml`（含 `dsh.bundle.patch` 配置），但 profile 的 `cordis.patch.yml` 仍需显式 insert 才能加载。插件自带的 patch 是 loader 层的补充，不是替代。

### 4. 重启 EAC 生效

插件只在启动时加载，安装/配置后必须重启 EAC。

## 验证

```bash
# 1. 包存在
ls "$HOME/.dsh/profiles/web-desktop/node_modules/<package-name>/package.json"

# 2. bundles 列表包含
cat "$HOME/.dsh/profiles/web-desktop/package.json" | python3 -c "
import json,sys; p=json.load(sys.stdin)
for b in p['dsh']['profile']['bundles']:
    if '<name>' in b.lower(): print('  ✅', b)
"

# 3. cordis.patch.yml 包含
grep "<plugin-id>" "$HOME/.dsh/profiles/web-desktop/cordis.patch.yml"
```

## 与 Hermes 技能体系的关系

| 安装方式 | 适用工具 | 技能格式 |
|---------|---------|---------|
| `npx skills add` | Hermes, Claude Code, Codex, OpenCode, Trae | Universal (`~/.agents/skills/`) |
| `dsh plugin add` / pnpm | DSH EAC | Cordis 插件 (`node_modules/` + `cordis.patch.yml`) |

DSH 的 Cordis 体系与 Hermes/Claude Code 的 universal 技能体系**不互通**。一个技能想两边都用，需要分别出 npm 包（`@xxx/dsh-plugin`）和 SKILL.md（universal 格式）。
