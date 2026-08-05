# ComfyUI Desktop 自动更新崩溃循环修复

实战验证（2026-08）：Desktop v1.0.28 反复「自动更新后自动关闭」，根因定位 + 修复全流程。

## 症状

- ComfyUI Desktop 启动后几秒内自动关闭，反复循环
- 用户描述：「一直显示自动更新后自动关闭」
- app.log 每次启动都停在 `[cloud-capacity] init` 就退出
- 现象通常在：手动杀过后端 main.py 进程 / 自动更新下载后出现

## 根因（按概率排序）

1. **主因：pending 更新装不上** — settings.json 里有
   `"pendingDownloadedUpdateVersion": "1.0.35"`，Desktop 每次启动都尝试应用
   已下载但无法安装的更新 → 失败 → 退出 → 重启 → 循环。
2. 手动杀 ComfyUI 后端进程（python main.py）会加剧 Desktop 的状态混乱。
3. ComfyUI-Manager 联网刷新节点缓存超时（cdn.jsdelivr.net 被墙）会产生
   Traceback，但**无害**，不影响出图。

## 诊断步骤

```bash
# 1. 服务状态
curl -s http://127.0.0.1:8188/system_stats        # 挂了则无输出

# 2. Desktop 进程（正常应有 5+ 个 Comfy Desktop.exe：主进程/gpu/renderer/network）
tasklist | grep -i "Comfy Desktop"

# 3. 日志（关键！看启动停在哪一步）
tail -20 "$APPDATA/Comfy Desktop/logs/app.log"

# 4. 找 pending 更新（核心证据）
grep -i pending "$APPDATA/Comfy Desktop/settings.json"
```

## 修复流程

### 步骤 1：清除 pending 更新标记

```bash
# 编辑 $APPDATA/Comfy Desktop/settings.json
# 删除这一行（或置空）：
#   "pendingDownloadedUpdateVersion": "1.0.35"
# 注意：JSON 删除键时确保逗号正确，建议用 python 重写整个文件：
python -c "
import json, pathlib
p = pathlib.Path.home() / 'AppData/Roaming/Comfy Desktop/settings.json'
d = json.loads(p.read_text(encoding='utf-8'))
d.pop('pendingDownloadedUpdateVersion', None)
p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding='utf-8')
print('cleared')
"
```

⚠️ **不要用 patch 工具改 JSON 键** — 删行时容易留下重复键/尾逗号，
直接跑坏 JSON。用 python json 库整体重写最安全。

### 步骤 2：重新启动 Desktop

```bash
"/e/ComfyUI/Comfy Desktop/Comfy Desktop.exe"   # 路径以实际安装位置为准
```

验证：`tasklist | grep -i "Comfy Desktop"` 出现 5+ 进程且持续存活。

### 步骤 3：若 Desktop 不自动拉起后端

Desktop GUI 可能停在主页等待操作。两种选择：
- 在 Desktop GUI 里点启动按钮
- 或命令行手动拉起（推荐，可控）：

```bash
cd <ComfyUI 安装目录>/ComfyUI  # 如 E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI
PYTHONPATH="" ./.venv/Scripts/python.exe -s main.py \
  --feature-flag show_signin_button=true \
  --feature-flag enable_telemetry=true \
  --enable-manager \
  --extra-model-paths-config "C:\Users\<user>\AppData\Roaming\Comfy Desktop\shared_model_paths.yaml" \
  --input-directory "E:/Comfy-Desktop/ComfyUI-Shared/input" \
  --output-directory "E:/Comfy-Desktop/ComfyUI-Shared/output"
```

⚠️ 路径用**正斜杠**（`E:/...`），反斜杠会被 bash 转义成乱拼接路径
（实测产生 `Comfy-DesktopComfyUI-Sharedoutput` 这种畸形目录）。

## 关键环境事实（避免误操作）

- **ComfyUI 真实运行环境是 `.venv`**（`<安装目录>/ComfyUI/.venv`），
  torch 2.10.0+cu130 CUDA 正常
- **standalone-env 是备用环境**（`<安装目录>/ComfyUI/standalone-env`）——
  不要往里面 pip 装东西，会污染它的 torch 成 CPU 版（不影响 .venv 主环境，
  但会留下脏环境）
- 判断哪个 python 是真后端：
  `wmic process where "name='python.exe'" get ProcessId,CommandLine | grep main.py`

## 无害的 Traceback（可忽略）

- ComfyUI-Manager 刷新缓存：`InvalidChannel: cdn.jsdelivr.net`（被墙，无害）
- 手动 kill 后端时的 `asyncio CancelledError / TimeoutError`（进程终止日志）

## 验证清单

- [ ] `curl 127.0.0.1:8188/system_stats` 返回 JSON
- [ ] Desktop 进程 5+ 个且持续存活
- [ ] `netstat -ano | grep 8188` 有 LISTENING
- [ ] 队列空闲：`curl 127.0.0.1:8188/queue`
