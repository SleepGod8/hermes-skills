---
name: sillytavern-rp-frontend
description: Use when SillyTavern酒馆安装配置,接Ollama本地模型,建角色卡。
---

# SillyTavern（酒馆）RP 前端：安装、配置、接本地模型

## 触发条件

- 用户提到 SillyTavern / 酒馆 / 角色扮演前端 / 角色卡 / 群聊 RP
- 需要把本地 Ollama 模型（darkidol、josiefied 等）接进 RP 场景
- 用户想建角色卡、世界书、多角色群聊

## 是什么

- 开源 Web 聊天前端（Node + express），**不含模型**
- 后端可接 Ollama/本地 GGUF，或云端 API（OpenAI、Claude、DeepSeek）
- 核心功能：**角色卡**（Character Card：名字/性格/背景/说话风格/示例对话）、**世界书**（Lorebook 触发式世界观）、**群聊**（多角色互聊）、预设（采样参数一键切换）
- 中文社区叫「酒馆」；模型卡挂 sillytavern 标签的模型（DarkIdol 等）就是为它训练的

## Windows 安装流程（本机已验证 2026-08，RTX 4060 + E 盘）

1. **环境检查**：`node --version`（≥18，本机用 Hermes 自带 runtime v22）、`git --version`
2. **装 E 盘独立文件夹**（用户偏好不装 C 盘）：
   ```bash
   mkdir -p /e/SillyTavern && cd /e/SillyTavern
   git -c http.proxy= -c https.proxy= clone --depth 1 https://github.com/SillyTavern/SillyTavern.git .
   ```
   （国内网络：`-c http.proxy= -c https.proxy=` 绕代理直连 GitHub）
3. **npm 换国内镜像再装依赖**（实测 25s 装完 667 包）：
   ```bash
   npm config set registry https://registry.npmmirror.com
   npm install --no-audit --no-fund
   ```
4. **改端口**：首次启动自动从 `default/config.yaml` 复制生成 `config.yaml`；默认 port 8000 常被占用（见 Pitfalls），改成 8001
5. **启动**：`node server.js`，浏览器访问 http://127.0.0.1:8001
6. **启动脚本**：写 `启动酒馆.bat` 给用户双击用（模板见 `templates/start_sillytavern.bat`）

## Pitfalls（全部实测踩过）

- **8000 端口冲突**：`curl http://127.0.0.1:8000` 返回 `{"detail":"Not Found"}` + `server: uvicorn` → 被其他 FastAPI/Dify 服务占用。ST 启动报 "Address already in use / Another SillyTavern instance" → 改 config.yaml 的 `port:`。**先诊断端口再归因启动失败**。
- **git-bash 后台启动失败**：background=true 跑 `node server.js` 报 "bash: no job control in this shell / stdin is not a tty" exit 1，但前台能正常跑。解法：background=true **+ pty=true**；或直接前台长驻跑。
- **残留孤儿进程**：前台跑超时被 kill 后，node 子进程可能继续存活占端口，导致下次启动报 "already in use"。诊断：
  ```bash
  netstat -ano | grep ":8001"          # 找 LISTENING PID
  powershell -Command "Get-Process -Id <pid> | Select Id,ProcessName,Path"
  ```
- **tasklist //FI 在 git-bash 下参数转换失败**（乱码报错），用 powershell Get-Process 代替。
- **bat 中文乱码**：启动脚本加 `chcp 65001 >nul`。

## 接 Ollama 本地模型（UI 30 秒）

1. 打开 http://127.0.0.1:8001
2. 右上角 ⚙️ → API 连接
3. API 选 **Ollama**，服务器 URL `http://127.0.0.1:11434`
4. 模型下拉选 `darkidol` / `goekdenizguelmez/JOSIEFIED-Qwen2.5` 等
5. 点连接，即可和角色对话

## 进阶玩法（用户场景）

- **角色卡**：女仆家族人格可做成角色卡（人格/说话风格/背景故事），每女仆一张卡，一键切换
- **群聊模式**：多角色卡放同一房间互聊（配合 group-chat 类场景）
- **世界书**：给 RP 场景建世界观/地点/NPC 触发设定
- 本地零审查模型接入后：不烧 API、无限量、私密

## 关联

- Ollama 从 hf.co 拉 GGUF 的模板坑（只输出 safe）→ skill: `ollama-hf-gguf-import`
- 本地模型对比测试通用脚本 → `ollama-hf-gguf-import` 的 `scripts/compare_models.sh`
- 本地零审查言情/RP 模型选型（已装/候选/下载速度实测）→ `references/local-rp-models.md`
