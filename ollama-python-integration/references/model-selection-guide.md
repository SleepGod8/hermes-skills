# Ollama 模型选择指南

## CPU 推理性能速查

同一模型在不同硬件上的推理速度差异巨大：

| 模型 | 笔记本 CPU 2GHz | 桌面 CPU 3.5GHz | RTX 3060 (12GB) | RTX 4090 |
|------|----------------|----------------|-----------------|---------|
| qwen2.5:3b (2GB) | 15~25 t/s | 30~40 t/s | 80~120 t/s | 150+ t/s |
| qwen2.5:7b (4.7GB) | 5~12 t/s | 15~25 t/s | 50~80 t/s | 100+ t/s |
| qwen2.5:14b (9GB) | 2~5 t/s | 8~15 t/s | 25~45 t/s | 60+ t/s |
| glm-4.7-flash (19GB) | 1~3 t/s | 5~10 t/s | 15~30 t/s | 40+ t/s |

> t/s = tokens per second（每秒生成的 token 数），低于 5 t/s 会明显感觉卡顿

## Ollama 推荐模型清单

### 中文最强

| 模型 | `ollama pull` 命令 | 大小 | 备注 |
|------|-------------------|------|------|
| 通义千问 7B | `ollama pull qwen2.5:7b` | 4.7GB | ⭐ 首选，中文能力最强 |
| 通义千问 3B | `ollama pull qwen2.5:3b` | ~2GB | 更快，适合低配 |
| 通义千问 14B | `ollama pull qwen2.5:14b` | ~9GB | 更强但需更高配置 |
| 通义千问 32B | `ollama pull qwen2.5:32b` | ~19GB | 桌面高配适用 |
| 智谱 GLM4 | `ollama pull glm4:9b` | ~5.5GB | 清华智谱出品 |
| 智谱 GLM4-Flash | `ollama pull glm-4.7-flash` | 19GB | 30B MoE 架构 |

### 英文/通用

| 模型 | 命令 | 大小 | 备注 |
|------|------|------|------|
| LLaMA 3.2 (3B) | `ollama pull llama3.2:3b` | ~2GB | Meta 最新小模型 |
| LLaMA 3.1 (8B) | `ollama pull llama3.1:8b` | ~4.7GB | 通用能力强 |
| Gemma 2 (9B) | `ollama pull gemma2:9b` | ~5.5GB | Google 出品 |
| Mistral (7B) | `ollama pull mistral:7b` | ~4.1GB | 效率高 |
| Phi-3 Mini (3.8B) | `ollama pull phi3:mini` | ~2.3GB | 微软高效模型 |

## Windows Ollama 路径参考

```bash
# Ollama 安装路径
%LOCALAPPDATA%\Programs\Ollama\
# Git Bash 下需用完整路径
/c/Users/Windows/AppData/Local/Programs/Ollama/ollama.exe

# 常用命令
ollama.exe pull 模型名    # 下载模型
ollama.exe list           # 查看已下载
ollama.exe run 模型名     # 运行并对话
ollama.exe rm 模型名      # 删除模型
```

## 诊断命令速查

```bash
# 查看 Ollama 运行状态
curl http://localhost:11434/api/tags | python -m json.tool

# 查看运行中的进程
ollama.exe ps

# 测试生成速度（简单 prompt）
time ollama.exe run qwen2.5:7b "你好"
```
