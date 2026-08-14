---
name: sillytavern-setup
description: Use when 安装/配置 SillyTavern 酒馆或接入 Ollama 本地模型。
---

# SillyTavern（酒馆）安装与 Ollama 连接

## 触发条件

- 用户要求安装/启动 SillyTavern（酒馆）
- 需要在酒馆里接入本地 Ollama 模型（darkidol、josiefied 等 RP/言情模型）
- 酒馆连不上模型、API 面板找不到 Ollama 选项

## 环境要求（Windows）

- Node.js 18+（Hermes 自带 runtime 可用，v22 实测 OK）
- git（国内 clone 用 `-c http.proxy= -c https.proxy=` 绕代理直连 GitHub）

## 安装流程（用户偏好 E 盘独立文件夹，如 E:\SillyTavern）

1. **建目录 + clone**：
```bash
mkdir -p /e/SillyTavern && cd /e/SillyTavern
git -c http.proxy= -c https.proxy= clone --depth 1 https://github.com/SillyTavern/SillyTavern.git .
```
2. **换 npm 源 + 装依赖**（国内不换源很慢）：
```bash
npm config set registry https://registry.npmmirror.com
npm install --no-audit --no-fund   # 实测 25s 装完 667 包
```
3. **端口冲突检查**（关键坑）：默认 `port: 8000` **常被其他服务占用**（本机 Dify/uvicorn 占了 8000）。启动前先 `netstat -ano | grep -E ":8000"` 查占用；被占则改 `config.yaml` 的 `port:` 为 8001 或其它空闲端口。
4. **启动**：后台模式**必须 pty=true**（无 pty 时 node server.js 报 `bash: no job control in this shell` / `stdin is not a tty` 并 exit 1）。
5. **验证**：`curl http://127.0.0.1:<port>/` 应返回 SillyTavern HTML（`<title>SillyTavern</title>`）。

## Ollama 连接（SillyTavern 1.18 中文 UI）

⚠️ **核心坑：Ollama 不在「聊天补全」分类下，在「文本补全」里！** 新版 ST 的 `main_api` 下拉只有：文本补全/聊天补全/NovelAI/AI Horde/KoboldAI。

1. 底部菜单栏「**API 连接**」打开面板
2. API 类型（`main_api`）选「**文本补全**」
3. 子下拉 `textgen_type` 选「**Ollama**」
4. 填 `ollama_api_url_text` = `http://127.0.0.1:11434`（注意：不是 5000 的 oobabooga 默认值）
5. 点「**连接**」按钮 —— ⚠️ 页面上有 4 个「连接」按钮，只有**可见的那个**（`offsetParent !== null`，通常 index 2）才是当前面板的
6. 连接成功后 `ollama_model` 下拉自动加载本地模型列表

详细 UI 元素 ID 和排查见 `references/ollama-connection-ui.md`。

## 用户启动脚本（E:\SillyTavern\启动酒馆.bat）

```bat
@echo off
chcp 65001 >nul
title SillyTavern (端口 8001)
cd /d E:\SillyTavern
echo 浏览器访问: http://127.0.0.1:8001
node server.js
pause
```

## 创建角色卡（Chara Card V2）—— 重要！

⚠️ **ST 只扫描 characters 目录里的 .png 文件**！纯 .json 角色卡放目录会被静默忽略（`src/endpoints/characters.js` 的 `/all` 路由只 `filter(file => file.endsWith('.png'))`）。
⚠️ **PNG 的 chara tEXt 块必须是 base64 编码的 JSON**，明文 JSON 解析失败会被静默跳过（`src/character-card-parser.js` 里 `Buffer.from(text, 'base64')`）。

流程：
1. 写 JSON 角色卡（spec: `chara_card_v2`；data: name/description/personality/scenario/first_mes/mes_example/creator_notes/system_prompt/alternate_greetings/tags）
2. `python scripts/make_char_card.py input.json output.png [avatar.png]`（用 PIL `PngInfo` 写 base64 的 chara 块；无 avatar 参数时生成占位图）
3. 放到 `data/default-user/characters/`
4. 刷新页面（角色列表每次从服务端重新读目录）
5. 立绘：make_char_card.py 第三参数传角色图即可嵌入 PNG

JSON 模板见 `templates/character-card-v2.json`。

## 服务端配置固化（settings.json）

ST 会把 API 连接配置写进 `data/default-user/settings.json`（**服务端文件**，换浏览器/重启自动加载）：
- `main_api = "textgenerationwebui"`
- `textgenerationwebui_settings.type = "ollama"`
- `textgenerationwebui_settings.ollama_model = "darkidol:latest"`
- `textgenerationwebui_settings.server_urls.ollama = "http://127.0.0.1:11434"`

所以配过一次后**不用每次重配**；唯一手动步骤是每次打开页面点一次「连接」（连接状态本身不持久化，ST 设计如此）。重启后显示「未连接到 API」是正常的，配置在就行。

## 8GB 显存 RP 模型选择

本机 RTX 4060 Laptop 8GB 的零审查中文言情/RP 模型对比（DarkIdol vs Josiefied vs 其它候选）见 `references/model-selection-8gb.md`。

## Pitfalls

- **API 端点 curl 直接调返回 403**（会话/CSRF 保护）：验证角色列表、导入角色必须走浏览器端（browser_console 里 fetch 或点 UI）；curl 只能做健康检查（GET `/` 返回 200 HTML）
- **角色卡文件名字符**：文件名用 ASCII（`HermesxIris.png`），JSON 内 `name` 字段可以用 × 等特殊字符
- **角色卡改了不显示** → 确认是 .png + chara 块 base64；必要时重启服务重新扫描
- **改 settings.json 前先停 ST**（运行中会被自动保存覆盖）
- **端口 8000 被占**（本机 Dify uvicorn 等）→ 改 8001，否则报 `Address ... already in use. Another SillyTavern instance may already be running`
- **残留 node 进程占端口**：`netstat -ano | grep :<port>` 找 LISTENING 的 PID，用 `powershell -Command "Get-Process -Id <pid>"` 确认进程名；kill 后再启
- **后台启动 node server.js 无 pty 必失败** → terminal(background=true, pty=true)
- **npm 默认源慢** → 先换 npmmirror
- **git clone GitHub 被墙/慢** → `-c http.proxy= -c https.proxy=` 绕代理直连
- 修改 config.yaml 后要重启 ST 才生效
- 从 hf.co 直拉 GGUF 的模板坑（模型只输出 safe）见 skill `ollama-hf-gguf-import`
