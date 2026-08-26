# DSH EAC 插件安装（`dsh plugin` CLI 用法与坑）

适用于给 EAC 的 `web-desktop` profile 新增插件（npm 包 / GitHub 仓库）。

## EAC 的 dsh CLI 位置

EAC 是 Electron 桌面端，**`dsh` 不在系统 PATH**，也没有全局安装。内置 CLI：

```
E:\Deepseek Harness EAC\dsh-desktop\node_modules\.bin\dsh
```

PowerShell 里裸敲 `dsh` 会报「无法将 dsh 项识别为 cmdlet」——正常，因为没进 PATH。

## ⚠️ 关键坑：`--profile web` ≠ EAC 实际用的 profile

**`dsh plugin --profile web add ...` 会装到 `~/.dsh/profiles/web/`，但 EAC 实际加载的是 `web-desktop`！**

- 证据：`E:\Deepseek Harness EAC\resources\app\main.js` 有 `const DESKTOP_PROFILE = 'web-desktop'`，桌面端从此默认运行独立 profile `web-desktop`。
- `web` 是旧的共享 profile，EAC 不用它。
- **结论：必须 `dsh plugin --profile web-desktop add <pkg>`**，否则装错地方、EAC 不加载。

装错后：别留在 `web`，用 `--profile web-desktop` 重新装到正确位置即可（不会覆盖已有）。

## 安装三步（缺一不可）

`dsh plugin add` 只完成 **1 和 2**，**第 3 步 cordis.patch.yml 必须手动补**：

1. **node_modules 里有包**
   `~/.dsh/profiles/web-desktop/node_modules/<pkg>/`（含 package.json、lib/、cordis.patch.yml 等）

2. **package.json → `dsh.profile.bundles` 注册**（`dsh plugin add` 会自动加）

3. **cordis.patch.yml 插入启用行**（`dsh plugin add` 不自动加，需手动）：
   从插件自带的 `node_modules/<pkg>/cordis.patch.yml` 复制其 insert 块到 profile 的 `cordis.patch.yml` 末尾：
   ```yaml
   - insert:
       - id: <插件id>
         name: '<包名>'
   ```
   每个插件一个 insert 块，重复安装不重复插。

## 安装来源写法

| 来源 | 命令 | 示例 |
|------|------|------|
| npm 包 | `add <包名>` | `dsh plugin --profile web-desktop add @wxkingstar/specfusion-dsh` |
| GitHub 仓库 | `add github:<owner>/<repo>` | `add github:9livewolf/dsh-think-bounce-pet` |

GitHub 仓库方式 `dsh plugin add` 会用 pnpm 拉取 github 依赖，同样只注册 bundle，仍需手动补 cordis.patch.yml。

## 验证清单

```
1. ls node_modules/<pkg>/package.json        → 存在
2. cat package.json | grep '<pkg>' in bundles → 已在 dsh.profile.bundles
3. grep -A2 '<id>' cordis.patch.yml          → 已插入启用行
```

重启 EAC 后生效。验证生效：界面出现插件功能 / `~/.dsh/profiles/web-desktop/cordis.patch.yml` 该行存在。

## 常见失败

- 用 npm（非 pnpm）在 profile 目录 `npm install <pkg>` → ERESOLVE peer 冲突炸裂。**DSH profile 必须用 pnpm**（`dsh plugin` 内部就是 pnpm）。
- 用 `--profile web` 装 → EAC 不加载，查 main.js 的 DESKTOP_PROFILE 确认实际 profile。
- 只装没补 cordis.patch.yml → bundle 在但插件不激活。

## 配套参考

- 插件的手动更新/回滚流程见 `manual-plugin-update.md`。
