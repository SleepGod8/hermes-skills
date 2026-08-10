---
name: dev-environment-inventory
description: 项目开发前的本机依赖盘点：系统化探测 Windows 机器已装/未装的运行时、容器服务与 Python/npm 包，回答"完成该项目所需但本机尚未安装的依赖项"。Use when 用户要求列出依赖清单/环境检查/本机有没有装 X/项目可行性盘点。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [environment, dependency, inventory, recon, windows]
    related_skills: [project-requirements-analysis, multi-agent-protocol, windows-admin-installs]
---

# 开发环境依赖盘点（Dev Environment Inventory）

Use when the user asks:
- “列出完成该项目所需但本机尚未安装的依赖项”
- 环境检查 / 依赖盘点 / “本机有没有装 X”
- 项目研究分析报告（只分析不开发）里的「已具备 vs 未安装」清单

## 核心原则

- **实测为准**：所有结论来自真实命令输出，不靠记忆——记忆可能属于另一台电脑（本用户两台电脑跑 Hermes，`D:\PythonProject`/`wolin` 环境是另一台机的记忆，本机可能不存在）。
- 区分三类能力：**本机服务**（MySQL 等独立进程）vs **Docker 容器**（docker ps 可见）vs **API/云端能力**（有 key 即算已具备，无需安装）。
- 输出格式：✅ 已具备 / ❌ 未安装（🔴必须 🟠高 🟡可选）/ ⚠️ 数据源·模型缺口，每项带验证命令或安装建议。

## 探测清单（Windows + git-bash，可一次批量跑）

1. **语言运行时**：`python --version`、`node --version`、`npm --version`、`git --version`
2. **conda 环境**：`conda env list` —— 注意记忆里的 env（如 wolin）可能不在本机
3. **Docker 容器**：`docker --version && docker ps --format '{{.Names}} {{.Status}}'` —— 容器即服务（Redis/Milvus/MinIO/Neo4j 常以容器形态存在，不算“未安装”）
4. **端口与本地服务**：`netstat -ano | grep LISTENING | grep -E ':(3306|6379|9000|19530|11434|8001)'`
5. **识别未知端口服务**：用 Python socket 读握手 banner 拿版本号（见下）
6. **CLI 缺失 ≠ 服务缺失**：`redis-cli --version` / `mysql --version` 报 not found 不代表服务端没跑——先查端口
7. **Python 包**：`python -m pip list | grep -iE 'fastapi|uvicorn|pymysql|langchain|pymilvus|redis|openai|dashscope|akshare|jieba|sqlalchemy|pandas|httpx'` —— 注意区分系统 python 与 conda base 的包
8. **本地模型**：`ollama list` —— 区分 embedding 模型（bge-m3）与对话模型（缺对话模型 = 需 ollama pull 或走 API）
9. **API key 盘点**：DeepSeek / DashScope / ZhipuGLM / Agnes-AI 等已有 key 的能力算“已具备（API 层）”

## 关键技巧

- **socket banner 探测服务版本**（MySQL 握手包前几字节即版本号）：
  ```bash
  python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',3306)); print(s.recv(100)[:60]); s.close()"
  # 输出含 b'...\n9.7.0\x00...' → MySQL 9.7.0
  ```
- **netstat PID 反查进程归属**：`tasklist //FI "PID eq <pid>"` —— 判断该端口是容器（docker 内部 PID）还是本机独立服务。
- **需求文档可能缓存在本地**：飞书导入的 42 篇「AI项目603」知识库在 `C:\Users\80704\AppData\Local\hermes\workspace\feishu_import\markdown\`，用户说“读取需求文档”时先查这里 + Desktop/Downloads 的 `*需求*`，再问用户。

## 输出格式

- 依赖清单三栏表：✅ 已具备（含验证命令）/ ❌ 未安装（分级 + 安装命令建议）/ ⚠️ 数据源·模型缺口
- 若项目文档指定技术栈（如 FastAPI），对照文档逐项核对，不只查“常见包”
- 结尾给结论：项目可行性与最大缺口（本实例最大缺口 = 后端 Python 依赖 + 前端全新工程 + 金融数据源）

## Support Files

- `references/ai-advisor-project.md` — AI投顾 Agent 项目完整盘点实例（2026-08-10）：文档位置、MVP 范围、本机环境实测、依赖缺口、数据库基线、12–16 周阶段、多 agent 分工映射。
