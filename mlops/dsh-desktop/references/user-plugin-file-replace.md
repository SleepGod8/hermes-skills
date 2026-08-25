# DSH EAC 非内置用户插件：从 GitHub release 简易更新

适用于非内置、非 link/junction 的普通用户插件（如通过 `dsh plugin add` 或
市场安装的皮肤类插件 `dsh-client-liang-intensity-skin`）。此方法与
`manual-plugin-update.md` 的「完整构建流程」相比更轻量：不需要完全退出 EAC、
不需要建 `-new` 临时目录做原子换名，直接逐文件覆盖即可。

## 核心判断

- **companion 内置插件** → 走覆盖层方式（见 `builtin-plugin-update.md` + `scripts/update-builtin-plugins.js`）
- **非内置用户插件** → 用本文的简易文件替换

## 何时用 GitHub release 而非 npm

先查 npm 是否有新版本：
```bash
node -p "require('~/.dsh/profiles/web-desktop/node_modules/<pkg>/package.json').version"  # 当前
npm view <pkg> version   # npm latest（可能停在旧版）
```

若 GitHub 发了新版但 npm 未更新（实测 `dsh-client-liang-intensity-skin`：
npm 停在 0.1.6，GitHub release v0.1.7），则从 GitHub 下载。

## 从 GitHub release 更新（实测 2026-08-25）

```bash
# 1. 查最新 release tag
curl -s "https://api.github.com/repos/<owner>/<repo>/releases/latest" | \
  node -e "d=JSON.parse(require('fs').readFileSync(0));console.log(d.tag_name)"

# 2. 下载 tarball（tag 可能带 v 前缀）并解压
curl -sL -o /tmp/v.tar.gz "https://github.com/<owner>/<repo>/archive/refs/tags/<tag>.tar.gz"
tar -xzf /tmp/v.tar.gz -C /tmp
# 解压目录名格式：<repo>-<tag>/（如 dsh-liang-skin-0.1.7/）

# 3. 备份旧版
cp -r <plugin_dir> <plugin_dir>.bak-<old_ver>

# 4. 逐文件覆盖核心文件（按新版 package.json "files" 字段）：
#    assets/, cordis.patch.yml, lib/, src/, package.json, README.md
# 排除：.git, .gitignore, package-lock.json, docs/, scripts/（开发工具）

# 5. 验证实际版本（不要只信 tar 输出）
node -p "require('<plugin_dir>/package.json').version"   # 应显示新版本

# 6. 清理备份和 staging
rm -rf <plugin_dir>.bak-<old_ver> /tmp/v.tar.gz /tmp/<repo>-<tag>
```

注意：若 tarball 内文件全在 `files` 白名单里（如 dsh-liang-skin），逐文件复制
足够；若新版有构建步骤（`npm run build` 生成 bundle），则改用
`manual-plugin-update.md` 的完整构建流程。

## EAC 守护进程与运行时覆盖

- **EAC 有守护进程**：强杀（`Stop-Process -Force`）后会自动重启，PID 立即变化
  （实测 4 个新 PID 出现）。需要停服替换时，杀完立即操作文件，不用等守护重启。
- **Electron 不锁 node_modules 运行时文件**：非 companion 插件可直接在 EAC
  运行时覆盖文件（实测 dsh-liang-skin 更新成功），重启 EAC 加载新代码。
  无需杀进程即可完成替换。
