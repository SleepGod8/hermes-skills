# Windows DSH Agent 切换失败：EPERM rename

## 适用症状

日志形如：

```text
切换新版本失败: EPERM: operation not permitted, rename
<userData>\\agent -> <userData>\\agent-old-<timestamp>
```

这说明 npm 安装/staging 已经完成，失败发生在生产 overlay 切换阶段；不要把它继续归因于 registry 或下载。

## 根因模型

Windows 不能重命名仍被 Node 进程加载的 `agent` 目录。只等待 updater 持有的 `serverProc` 不够：Electron 的 renderer recovery、guarded boot 或重启逻辑可能在停止旧服务后重新拉起新的 `dsh web`，形成竞态。日志中若出现：

```text
startServer 重入：先终结旧进程再启动
启动 ...\\agent\\node_modules\\@deepseek-ai\\dsh\\lib\\bin.js
```

应优先怀疑恢复流程重新获取了目录锁。

## 安全修复模式

1. 更新前保存当前 `serverProc`，调用有界的 `killTreeAndWait`，不要只调用异步 `killTree`。
2. 在 `updater.applyUpdate()` 之前暂时阻止/绕过自动恢复，避免服务异常退出触发 `startAndShowGuarded()`。
3. 不能仅依赖 `serverProc` 句柄；在 Windows 上按命令行精确扫描包含当前 `userData\\agent` 且为 dsh Node 入口的进程。
4. 只对匹配的 PID 使用 `taskkill /PID <pid> /T /F`，等待文件锁释放；禁止无条件结束所有 `node.exe`。
5. 再执行 `agent -> agent-old-*`、`agent-staging -> agent` 的切换。失败时保留生产 agent，清理 staging，并尝试恢复服务。
6. 切换成功后再启动新版服务做健康验证，确认版本与 Web UI，再清理 `agent-previous`。

## 诊断与验收

- 先读 `%APPDATA%\\Deepseek Harness EAC\\logs\\desktop.log` 尾部，确认失败阶段和前后是否有 recovery/startServer 重入。
- `wmic process get ProcessId,CommandLine /format:list` 可用于按完整命令行匹配；注意 WMIC CSV 输出字段可能被截断，优先使用 list 格式逐记录解析 `CommandLine=` 与 `ProcessId=`。
- 更新前后验证：生产 `agent/package.json`、`agent-staging` 是否存在、目标 Node 进程是否仍加载生产 agent。
- 修改 `main.js`/`updater.js` 后必须用随应用提供的 Node 执行 `node --check`，并加载 updater 模块做最小 smoke test。
- 失败后的提示路径可能缺少反斜杠或目录名异常；以实际 `%APPDATA%\\Deepseek Harness EAC\\logs` 文件为准。

## 重要边界

不要直接删除生产 `agent`、`.dsh`、会话或配置；不要只提高 npm watchdog 阈值来处理 rename EPERM。前者是数据破坏风险，后者针对的是不同阶段的问题。
