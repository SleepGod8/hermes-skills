# EAC 内置插件更新引擎（设置 → 插件 → 更新）

适用 Deepseek Harness EAC v4.4+（用户本机 `E:\Deepseek Harness EAC`，app 4.4.1）。
EAC 把社区插件作为「内置 companion plugin」随应用分发
（`resources/app/assets/plugins/<dir>`），并通过 `plugin-updater.js` 提供上游更新
（npm / GitHub）。自动更新默认关闭（settings.pluginAutoUpdate 默认 false），仅提示；
需在 GUI 或手动流程里更新。更新后需重启服务生效。

## 更新源注册表（main.js PLUGIN_UPDATE_SOURCES，V4.3+）

只有登记了的插件才参与更新检测（EAC 独占插件如 dsh-balance/dsh-terminal 不登记；
zat-market 自带 selfupdate 不登记）：

- tool-vision → dsh-tool-vision
- soul-md → dsh-soul-md
- tdai-memory → dsh-tdai-memory
- dsh-pet → dsh-pet
- better-sidebar → dsh-better-sidebar
- dsh-navbar → @vlln/dsh-navbar
- mobile-fix → dsh-web-mobile-fix
- offpeak → dsh-offpeak
- dsh-market-plugin → @sanqi-normal/dsh-webui-market-plugin
- dsh-session-manager → dsh-session-manager
- dsh-undo → github:lire1131/dsh-undo-savepoint（npm 未发布，走 codeload tarball）

内置插件同名单的 npm 包与 profile 副本同名：插件同时存在于
`resources/app/assets/plugins/<dir>`（资产副本）和
`~/.dsh/profiles/web-desktop/node_modules/<pkg>`（profile 副本，每次启动从资产/覆盖层同步）。

## 检测与更新流程（plugin-updater.js）

1. **checkPluginUpdates**：current 版本优先读 profile 副本
   （`~/.dsh/profiles/web-desktop/node_modules/<pkg>/package.json`），回退资产副本；
   latest 用 `npm view <pkg> version`（镜像链 npmmirror → npmjs）；10 分钟内存 TTL +
   24h 落盘节流（settings.pluginUpdateCheckedAt）。
2. **applyBuiltinPluginUpdate**：
   - guard 保护快照（失败即中止，保证可回滚）
   - npm install 到 staging `%APPDATA%\Deepseek Harness EAC\plugin-update-staging\`
     （`--save-exact --omit=dev --ignore-scripts`，绝不执行第三方安装脚本）
   - **engines.dsh 门槛**：新包声明的最低 dsh 内核 > 当前内核 → 拒绝（多数插件不声明）
   - 合并进覆盖层：以资产副本为底（保留 EAC 附加文件，如 dsh-webui-market 的
     `data/` 离线目录快照）+ npm 包覆盖；旧覆盖层改名 `.bak-<ts>`
   - copyPluginPackage 尽力拷入 profile（服务运行中撞文件锁时保留覆盖层，下次启动同步）
   - 返回 restartRequired → **重启 EAC 生效**
3. **IPC**：`dsh:plugin-updates`（清单）、`dsh:plugin-update`（单个更新）、
   `dsh:plugin-auto-update`（开关）。GUI 路径：设置 → 插件 → 更新 标签。

## 手动验证是否有更新（无需开 GUI，已实测 2026-08）

```bash
cd ~/.dsh/profiles/web-desktop
for p in "@sanqi-normal/dsh-webui-market-plugin" dsh-better-sidebar dsh-pet dsh-session-manager dsh-soul-md; do
  echo "$p installed=$(node -p "require('./node_modules/$p/package.json').version") latest=$(npm view $p version)"
done
```

实测版本对照：market-plugin 0.1.2→0.5.5、better-sidebar 0.12.2→0.16.1、
pet 0.1.3→0.1.8、session-manager 0.1.0→0.1.2、soul-md 0.2.8→0.5.9。

engines 检查：新版本通常只声明 node 要求（如 market-plugin 0.5.5 要求
`node ^22.19.0 || >=24.0.0`）；EAC 内置 node v24.18.1
（`resources/app/resources/node/node.exe`）达标。engines.dsh 才拦 dsh 内核版本。

## GUI 自动化驱动 EAC（cua-driver 不可用时的替代）

cua-driver 安装脚本依赖 raw.githubusercontent.com，国内网络会卡死
（`hermes computer-use doctor` 超时）。改用 pyautogui 驱动（本会话已验证到
设置 → 插件页）：

- **pip 装在 py 3.13，但 `python` 命令解析到 3.12**：必须 `py -3.13` 运行
  （pyautogui/pygetwindow/pywin32 装在 3.13）；`python - <<EOF` 会报 ModuleNotFoundError
- EAC 窗口可能最小化到 (-32000,-32000)：用
  `ctypes.windll.user32.ShowWindow(hwnd, 9)` (SW_RESTORE) + `SetForegroundWindow(hwnd)` 恢复，
  等 1.5-2s 再截图
- **vision_analyze 给绝对坐标不可靠**（曾给出超出裁剪范围的坐标）：先裁剪小区域 +
  PIL LANCZOS 放大 3 倍再问相对位置；每次点击后必须截图回读验证（注意 pip 与 python
  解释器不一致时 `python` 路径可能不同）
- 点击路径：左下角「设置」齿轮（约窗口 x+45, y+h-55）→ 左侧「插件」菜单项
  → 顶部「更新」标签 → 逐个插件点「更新」→ 重启 EAC 生效
- 本会话在「更新」标签点击前因工具调用上限中断，**最终更新动作未完成**——
  后续会话继续时先截图确认「更新」标签坐标再点击

## 相关文件

- `manual-plugin-update.md` — GitHub 手工插件更新/回滚（web-desktop profile 视角）
- 更新日志：main.js 顶部 changelog 节；UI 文案在
  `resources/app/node_modules/@deepseek-ai/dsh-web-frontend/dist/assets/*.js`
