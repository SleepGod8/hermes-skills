# 多 Agent QQ 群聊桥接

通过 QQ Bot + OpenCode 在 QQ 群实现两个 AI Agent（Hermes + OpenCode）互相对话。

## 架构

```
         QQ 群
           |
    ┌──────┴──────┐
    │   QQ Bot    │
    │  (Hermes)   │
    └──────┬──────┘
           │ 消息转发
    ┌──────┴──────┐
    │  OpenCode   │
    │  (第二Agent) │
    └─────────────┘
```

## 前置条件

1. QQ Bot 已连接（`app_id` + `client_secret` 已配置）
2. OpenCode CLI 已安装并认证（DeepSeek API Key）
3. QQ 群已创建，Bot 已拉入群

## QQ Bot 群聊配置

在 `config.yaml` 中开启群聊：

```yaml
platforms:
  qqbot:
    enabled: true
    dm_policy: open
    group_policy: open  # ← 关键：开启群聊
```

配置后需重启 Gateway 生效（`hermes gateway restart`，不能在 Gateway 内执行）。

## 桥接脚本

位置：`scripts/multi_agent_bridge.py`

### 使用命令

| 命令 | 效果 |
|---|---|
| 直接说话 | Hermes 回复 |
| `/oc <消息>` | 转发给 OpenCode，贴回回复 |
| `/talk <轮数>` | Hermes + OpenCode 多轮对话 |
| `/status` | 查看消息状态 |

### 关键实现细节

**Windows subprocess 调用 OpenCode**：

```python
# ❌ 错误：直接调用 opencode（POSIX shell 脚本）
subprocess.run(["opencode", "run", msg])

# ✅ 正确：使用 .cmd 启动器 + shell=True
OPENCODE_BIN = str(Path.home() / "AppData/Local/hermes/node/opencode.cmd")
cmd = f'"{OPENCODE_BIN}" run "{message}" --continue --model deepseek/deepseek-chat'
subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
```

**PATH 设置**：需要在调用前将 node 目录加入 PATH：
```python
node_dir = str(Path.home() / "AppData" / "Local" / "hermes" / "node")
os.environ["PATH"] = node_dir + os.pathsep + os.environ.get("PATH", "")
```

## 陷阱

- Gateway 内不能执行 `hermes gateway restart`（会自杀），需从外部 shell 操作
- QQ Bot 的 opencode 在 `~/AppData/Local/hermes/node/opencode.cmd`，不是全局 PATH 中的
- 群聊消息类型是 group 而非 C2C，日志中会显示不同的事件类型
