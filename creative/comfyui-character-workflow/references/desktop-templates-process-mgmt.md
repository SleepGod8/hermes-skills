# ComfyUI Desktop 模板库安装 + 进程管理（2026-08 实测）

## 1. 「模板太少 / Browse Templates 几乎是空的」的诊断与修复

### 诊断（关键一步）

ComfyUI Desktop 的模板库由 pip 包提供，缩略图媒体包和核心数据包是**分开**的。
先查后端状态里两个字段：

```bash
curl -s http://127.0.0.1:8188/system_stats | python -c "import sys,json; d=json.load(sys.stdin); s=d['system']; print('installed:', s.get('installed_templates_version'), '| required:', s.get('required_templates_version'))"
```

- `installed_templates_version: null`（而 required 有值）→ **核心模板数据包没装**，模板库几乎为空。症状完全吻合。
- 缩略图包（`comfyui_workflow_templates_media_*`）装了不代表数据包装了，两者独立。

### 修复

装到 **`.venv`**（Desktop 真实运行环境，不是 standalone-env）：

```bash
VENV="E:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/Scripts/python.exe"
PYTHONPATH="" "$VENV" -m pip install comfyui-workflow-templates
```

- 主包带依赖：`-core` / `-json` / `-media-api` / `-media-video` / `-media-image` / `-media-other` / `-media-assets-01`，会自动一起装。
- 装完模板 JSON 在 `.venv/Lib/site-packages/comfyui_workflow_templates_json/templates/`（约 500+ 个 `.json`）。
- **必须重启 Desktop** 才生效：杀进程 → 重启 GUI（见 §3）。

### ⚠️ Desktop 会自动更新并「校准」包版本

重启 Desktop 时它会自动执行 git 更新后端（实测 0.27.0 → 0.31.0）并**重新安装依赖到它自己锁定的版本**——我手动装的 0.11.37 被它换成 0.11.34。这没关系：模板包装上了就行。**重启后要重新验证** installed == required 才放心。

### 验证

```bash
curl -s http://127.0.0.1:8188/system_stats | python -c "import sys,json; d=json.load(sys.stdin); s=d['system']; print(s.get('installed_templates_version'), '==', s.get('required_templates_version'))"
# 数量
find "E:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/Lib/site-packages/comfyui_workflow_templates_json/templates" -name "*.json" | wc -l
```

UI 使用：Workflow → Browse Templates（浏览模板）。

## 2. 模板/社区工作流补充渠道

- 官方模板库本质是 GitHub `Comfy-Org/ComfyUI-Workflows-Templates`，桌面版通过 pip 包分发。
- 社区模板：comfyworkflows.com / Civitai 下载 `.json` 直接拖进画布；缺节点用
  `comfy node install-deps --workflow=xxx.json` 自动补齐。

## 3. Windows git-bash 下杀/启 Comfy Desktop 的正确姿势

多个方法实测（git-bash / MSYS 环境）：

| 方法 | 结果 |
|---|---|
| `taskkill //F //IM "Comfy Desktop.exe"` | ❌ MSYS 把 `//F` 转义坏，报无效参数 |
| `cmd //c "taskkill ..."` | ❌ 转义后进了交互式 cmd，没执行 |
| `python -c "import subprocess; subprocess.run(['taskkill','/F','/IM','Comfy Desktop.exe','/T'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)"` | ✅ 能杀（用 DEVNULL 避免中文编码解码崩） |
| PowerShell `Stop-Process -Name 'Comfy Desktop' -Force` | ✅ 最干净，推荐 |

启动 GUI：

| 方法 | 结果 |
|---|---|
| `./Comfy\ Desktop.exe &`（bash 后台） | ❌ 秒退（Electron 单实例/无窗口会话），进程不驻留 |
| PowerShell `Start-Process -FilePath ...` | ❌ 实测没起来（进程没出现） |
| PowerShell `explorer.exe 'E:\ComfyUI\Comfy Desktop\Comfy Desktop.exe'` | ✅ 可靠，走资源管理器拉起，进程驻留 |

杀完等 3-5 秒（netstat 确认 8188 释放），再用 explorer.exe 拉起，然后轮询
`curl http://127.0.0.1:8188/system_stats` 直到就绪（首次可能先跑更新，最久 1-2 分钟）。

## 4. Desktop 日志位置

- 应用/更新日志：`%APPDATA%\Comfy Desktop\logs\app.log`（看自动更新、依赖安装过程）
- 后端启动日志：`E:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\user\comfyui.log`
- 旧版位置 `%APPDATA%\ComfyUI\logs\main.log`（Electron 主进程，窗口关闭即退出提示）
