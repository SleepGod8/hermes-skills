# DSH npm Agent 更新排查

## 先区分两条更新链路

- 桌面端更新：日志含 `[client-update]`，下载 `Deepseek-Harness-EAC-Setup-x64.exe`。
- Agent 更新：日志含 `[update] npm install`，在 `agent-staging` 安装 `@deepseek-ai/dsh@<version>`。

Agent 更新失败时，当前生产 `agent` 应继续保留；不要先删除 `.dsh`、生产 agent 或整套客户端。

## 诊断顺序

1. 优先读取 `%APPDATA%\\Deepseek Harness EAC\\logs\\desktop.log` 和 `logs\\update.log`；弹窗路径可能显示错误或拼接异常。
2. 记录目标版本、完整 npm 命令、registry、退出码和失败阶段。`npm view` 成功只证明元数据可读，不证明依赖 tarball 下载/解包成功。
3. 分别测试 registry 根地址和包元数据。若都返回 HTTP 200 而 UI 报“下载停滞”，优先怀疑依赖 tarball、npm 解包/写盘、进程竞争或更新器 watchdog，不要只重复切换镜像。
4. “下载停滞（150 秒无进展）”是更新器 watchdog 的判定，不等于 registry 不可达。
5. DSH 完全退出后，使用 DSH 自带 Node/npm，在与生产目录分离的临时目录复现目标版本，并保留 `--loglevel=info` 或更详细日志。手动临时安装成功后，才可判断问题偏向 UI 更新器、主进程 watchdog 或并发竞争。
6. 检查多实例/残留 `node.exe` 及 `JUNCTION_FOREIGN` 共享模块告警（例如 `cosmokit`、`schemastery`）。只结束确认属于 DSH 的进程树，不要盲目杀掉所有 `node.exe`。
7. 只有在临时安装成功并完成备份后，才设计 staging 替换；不要直接覆盖生产 agent。

## 报告最低字段

```text
desktop_version:
agent_current:
agent_target:
registry_attempts:
npm_exit_code:
log_paths:
reproduction_result:
production_state:
```

未实际复现成功时，不要声称某个绕过方案有效。