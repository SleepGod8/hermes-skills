---
name: pyinstaller-windows-packaging
description: "Use when 打包 Python 为 Windows 免装 exe：uv 重建、GBK 修复、密钥清扫、交付验证。"
version: 1.0.0
author: Hermes & Iris (learned from session 2026-08)
tags: [pyinstaller, windows, packaging, exe, security, key-scrub]
platforms: [windows]
---

# PyInstaller Windows 打包 + 安全交付

把 Python 项目打成 Windows 免装 exe（双击即用）的完整工作流，含两大杀手级坑（conda Python 不适配、GBK 控制台 emoji 崩溃）与交付前密钥清扫红线。

## 触发条件

- 用户要求「打包成 exe 发给别人」「免装 Python 双击即用」的交付形态
- 任何需要把含 API key / 内部配置的 Python 项目打包分发的场景
- 用户问「交付包会不会泄露我的 key」

## 核心决策

| 环节 | 正确做法 | 错误做法 |
|---|---|---|
| Python 环境 | **uv 建干净 venv + 官方 CPython**（实测 3.12.11，`uv venv --python 3.12.11`） | conda Python 3.13 → PyInstaller 报 ffi.dll 缺失/DLL 警告 |
| 打包命令 | PyInstaller 6.x，`--onefile` + `--add-data static` 内置静态资源 | 依赖外部 static 目录 → 别人机器上页面 404 |
| 隐式导入 | 显式 `--hidden-import` 补 uvicorn 等（FastAPI 项目必查） | 依赖 PyInstaller 自动分析 → 运行时 ImportError |
| 控制台 | 无控制台模式（`--noconsole`）时 stdout 为 GBK | 入口 print 含 emoji/中文 → 必崩 |
| 密钥 | 交付包必须零真实密钥（三重扫描） | 环境变量兜底把 key 写进 config.json → 泄露 |

## 标准流程

### 1. 干净环境重建（跳过 conda）

```bash
uv venv --python 3.12.11 .venv-pack          # 官方 CPython，非 conda
uv pip install --python .venv-pack/Scripts/python.exe -r requirements.txt pyinstaller
```

> conda 的 Python 3.13 实测不适配 PyInstaller（ffi.dll 缺失）。uv 拉官方 CPython 3.12.11 后零 DLL 警告。

### 2. GBK 编码崩溃修复（必做，Windows 无控制台模式）

症状：exe 双击闪退 / 一启动就崩；源码里 print 带 emoji 或中文。

修复（main.py 入口最顶部）：

```python
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
```

同时把 print 里的 emoji / 中文替换成 ASCII 安全写法（如 `[OK]` 代替 ✅）。修复后**必须同步项目源 + 重新打包**，两处保持一致。

### 3. 打包

```bash
.venv-pack/Scripts/pyinstaller.exe --noconfirm --onefile --noconsole \
  --name AppName \
  --add-data "static;static" \
  --hidden-import uvicorn.logging --hidden-import uvicorn.loops.auto --hidden-import uvicorn.protocols.http.auto \
  main.py
```

### 4. 全链路实测（打包后必须真跑）

1. 启动 exe，确认进程存活（`tasklist | findstr AppName`）
2. 确认监听端口（8010 被占 → 自动改 8011 属预期行为）
3. 逐个端点 curl：全部 200（注意 size=0 可能是 /tmp 路径映射问题，非应用缺陷，用 urllib 直接解析确认内容真实返回）
4. 真实 API 闭环：`/setup` 填 base_url + api_key → 落盘 config.json → 真实请求成功
5. 功能端点（如 /api/analyze）对真实外部服务调用成功

### 5. 密钥清扫（交付红线，三重扫描）

**为什么会有 key 进包**：config.py 的 `prefer_env=True` 环境变量兜底逻辑，测试时 exe 目录无 config.json → 环境变量 key 被读入并落盘 dist/config.json。

扫描命令（对 exe 二进制、zip 整包、包内文本分别扫）：

```bash
# 1) exe 二进制字符串扫描
grep -a -c "sk-真实key前缀" App.exe            # 期望 0
# 2) zip 整包（含压缩流）
zipgrep -c "sk-真实key前缀" app.zip            # 期望 0
# 3) 包内文本文件
grep -c "api.agnes-ai.cn" README.md            # 期望 0
```

**必扫特征清单**：每个真实 key 的前缀（如 `sk-Zd4…`）、base_url 域名、模型名。README 里的示例也要改中性占位符（`your-api-key` / `https://api.example.com`），因为「示例里出现真实域名」也算不干净。

**清理动作**：
- `dist/` 下 config.json（环境变量兜底产物）必须删，exe 目录只留 exe
- 源码 config.py 默认值必须全空串（DEFAULT_CONFIG 无硬编码 key）
- 运行时残留 `.ai_cache`/`.gh_cache`/`__pycache__` 不进交付包
- 工作目录 config.json 若含测试真实 key，只留本机，不进任何交付物

### 6. 交付 zip 构建与最终验证

- zip 内容：exe + README（使用说明：双击即用、默认端口、占用自动切换、/setup 填自己的 key）
- 验证：zip 内 exe 哈希 == dist exe 哈希（`sha256sum` 对比）；zip 内所有文件过一遍密钥特征扫描
- README 提「模型名示例」也可能被扫到，一并换中性占位符

## 验证清单（全部通过才算完成）

- [ ] exe 启动进程存活，端口监听正常，全部端点 200
- [ ] 真实 API 闭环成功（/setup 配置 + 实际调用）
- [ ] exe 二进制 4 组特征（真实 key ×N + 域名）全 0 命中
- [ ] zip 整包扫描 0 命中，包内文本无真实域名/模型名
- [ ] exe 哈希两处一致（dist 与 zip 内）
- [ ] dist 目录无 config.json / 运行时残留

## 踩坑

- **conda Python 3.13 → PyInstaller 必炸**：ffi.dll 缺失或大量 DLL 警告。直接用 uv 拉官方 CPython 3.12.x。
- **GBK 控制台 + emoji print = 必崩**：`--noconsole` 模式下 stdout 是 GBK，emoji 编码失败抛异常直接退出。入口重配 UTF-8 是标准解法，修复后重打包再实测。
- **环境变量兜底会把真实 key 写进 dist/config.json**：config.py 的加载顺序是 config.json 缺失/损坏时 `prefer_env=True` 读环境变量。测试时 exe 目录没 config.json → key 落盘。交付前必须删 + 扫描。
- **`/setup` 落盘 vs 环境变量兜底**：config.json 存在时以落盘配置为准（实测 agnes-2.0-flash 生效）；缺失时才走兜底（gpt-5.4）。测试时别把兜底行为当缺陷。
- **Windows curl 直连某些域名需 `--ssl-no-revoke`**（CRYPT_E_REVOCATION_OFFLINE）；应用侧 httpx 走 certifi 校验不受影响，不用改应用。
- **size=0 别慌**：PyInstaller onefile 的 /tmp 路径映射问题可能导致 curl 看到 size=0，直接解析响应体/urllib 确认真实内容，非应用缺陷。
- **README 示例文本也要扫**：示例 URL/模型名/示例 key 都可能被扫描命中，统一用中性占位符。
