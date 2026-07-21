# Windows FastAPI 环境常见问题

## 端口冲突

### 错误码速查

| WinError | 含义 |
|----------|------|
| 10013 | 端口被占用（以一种访问权限不允许的方式做了一个访问套接字的尝试） |
| 10048 | 地址已被使用（通常每个套接字地址只允许使用一次） |

### 排查步骤

```bash
# 查看谁占用了端口
netstat -ano | grep 8000 | grep LISTENING

# 输出示例：
# TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    16824
#                                                      ^^^^ PID

# 杀掉进程
taskkill -F -PID 16824
```

### 常见原因

1. **后台进程残留** — `uvicorn` 进程被杀后子进程（reloader 产生的 worker）没被清理干净
2. **重复启动** — 终端跑了一个 `python app/main.py`，Hermes 又在后台启动了一个
3. **IDE 残留** — 用 PyCharm/VSCode 调试过，进程还在

### 预防

- 启动前先确认端口空闲
- 用 `process(action='list')` 检查本会话的后台进程

### Ghost PID（TIME_WAIT 幽灵进程）

**现象：** `netstat -ano` 显示端口被占用，但 `taskkill -F -PID <pid>` 报「没有找到进程」。

**原因：** `uvicorn --reload` 的 reloader（父进程）被杀后，worker（子进程）仍在运行并持有端口。旧 worker 退出后端口进入 TIME_WAIT 状态（约 2 分钟），此时 PID 已不存在但端口未释放。

**诊断：**
```bash
netstat -ano | grep LISTENING | grep :8000
# → LISTENING    18920
taskkill -F -PID 18920
# → 错误: 没有找到进程 "18920"
```

**解决：**\n- 换端口绕过 TIME_WAIT：`uvicorn ... --port 8001`\n- 等 2 分钟让 TIME_WAIT 超时\n- Windows 重启可释放所有 TIME_WAIT 端口\n- 用 Python socket 验证端口是否真的不可用：\n```bash\npython -c \"import socket; s=socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(('127.0.0.1', 8000)); s.close(); print('port free')\"\n```\n  如果 Python 能绑定，说明 `netstat` 显示的是残留记录，实际可正常使用。\n\n**`python app/main.py` 的 reloader 残留：**
`app/main.py` 里的 `uvicorn.run(..., reload=True)` 会产生 reloader+worker 两个进程。仅杀父进程不杀子进程时，worker 继续持有端口。快速重启（停掉再起）时最容易触发。

## uvicorn reloader 子进程环境隔离

`uvicorn --reload` 会 spawn 一个子进程运行真正的 ASGI 应用。这意味着：

| 内容 | 父进程（reloader）| 子进程（worker）|
|------|:----:|:----:|
| 导入 app.main | ❌ 不导入 | ✅ 导入 |
| sys.path | 当前 python 的 | 继承父进程 |
| .env 加载 | 不在 main.py 里就不加载 | 同左 |
| os.environ 修改 | 不继承 | 不继承 |

**影响：**
- 如果在父进程里 `load_dotenv()`（比如在某个脚本里），子进程看不到
- `.env` 必须在子进程启动时加载（放在 `config.py` 或 `main.py` 的 `load_dotenv()`）
- `sys.path` 里 Hermes venv 排在前面，子进程可能用到错误版本的包

**解决方案：** `load_dotenv()` 放在 `app/config.py` 或 `app/database.py` 的模块级别。

## Hermes venv 与项目 conda venv 的路径冲突

当 Hermes 用 `PYTHONPATH=""` 启动子 shell 时，`sys.path` 顺序是：

```
1. Hermes venv  site-packages  (C:\Users\Windows\AppData\Local\hermes\...)
2. 项目 conda venv site-packages  (D:\anaconda\envs\wolin-sms\...)
```

**后果：** 用 conda python 的 pip 安装包时，如果 Hermes venv 也有同名包，pip 可能装到 Hermes venv 下充数，项目实际运行时找不到。

**解决方法：**
```bash
# 强制安装到 conda env
python -m pip install --target "D:/anaconda/envs/wolin-sms/Lib/site-packages" <package>

# 或使用 conda 安装
conda install -n wolin-sms <package>
```

**验证安装位置（而非版本）：**
```bash
python -c "import cryptography; print(cryptography.__file__)"
# 正确输出应在 D:\anaconda\envs\wolin-sms\... 下
# 错误输出在 C:\Users\...\hermes\... 下
```

## MySQL 连接问题

详见 `references/pitfalls.md` 陷阱 10（.env 未加载）和陷阱 11（cryptography 包缺失）。
