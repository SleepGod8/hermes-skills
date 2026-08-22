# DSH EAC 插件手动更新与回滚

适用于 DSH EAC 的 `web-desktop` profile。先识别安装来源，再选择更新方式；不要默认把普通 `web` profile 当成 EAC。

## 路径与来源判定

- EAC profile：`%USERPROFILE%\.dsh\profiles\web-desktop\`
- 插件目录：`web-desktop\node_modules\<package>`
- 启用清单：`web-desktop\cordis.patch.yml`
- `package.json`/lockfile 中的普通依赖：优先使用 `dsh plugin --profile web-desktop update <package>`
- `link:` / junction：更新其源仓库后重启，不要覆盖链接目录
- GitHub 手工复制：采用“备份 → `-new` 临时目录 → 校验 → 原子换名 → 启动验收”
- EAC 自带并在启动时同步的 companion plugin：先检查 `resources/app/assets/plugins/` 与 `COMPANION_PLUGINS`；直接改 profile 副本可能在下次启动被覆盖

## GitHub 手工插件更新

1. 完全退出 EAC（窗口和托盘），确认没有加载目标插件的 DSH Node 进程。
2. 将仓库 clone/pull 到独立源码目录，例如 `E:\Hermes workspace\external\<repo>`。
3. 核对上游 `package.json` 的 `name`、`version`、`main`，并记录 commit SHA。
4. 将现有插件复制到 `%APPDATA%\Deepseek Harness EAC\backups\plugins\<name>-<timestamp>-v<old>`。
5. 把新版（排除 `.git`）复制到同级 `<name>-new`，不要直接边下载边覆盖正式目录。
6. 校验 `-new/package.json` 后，将旧目录换名为 `-old-<timestamp>`，再把 `-new` 换成正式名称。
7. 确认 `cordis.patch.yml` 中只有一个对应 `id/name` 启用项；已有配置时不要重复插入。
8. 用 EAC 内置 Node 执行：
   - `node.exe --check <plugin>/lib/index.js`
   - 对 ESM 插件用动态 `import(file:///...)` 验证模块能加载及关键导出存在
9. 检查插件声明的 assets 全部存在，再启动 EAC 做界面、交互、接口和日志验收。
10. 验收成功后可删除临时 `-old-*`；正式 backups 保留用于回滚。

## 回滚

完全退出 EAC，移走新版目录，将备份复制回原插件路径；保留原 `cordis.patch.yml` 启用行。若插件导致整棵插件树无法启动，可暂时给该行加 `disabled: true`，启动恢复后再调查。

## 验证要点

- 安装目录中的实际版本等于目标版本，而不是只相信 `git pull` 输出。
- `cordis.patch.yml` 的 profile 必须是 `web-desktop`。
- 语法通过不等于可用：必须动态加载模块并启动 EAC 实际验收。
- 不删除用户凭据、profile 配置、localStorage 或会话数据。
