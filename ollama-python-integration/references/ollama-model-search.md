# Ollama 模型搜索与安装指南

## 在 Ollama 库中搜索模型

### 方法1：Web搜索
访问 https://ollama.com/search?q=关键词

示例搜索结果：
- `kingzeus/llama-3.1-8b-darkidol` - 角色扮演/偶像制造
- `dagbs/darkidol-llama-3.1-8b-instruct-1.0-uncensored` - 8.5GB
- `crown/darkidol` - 1.5GB

### 方法2：命令行（模型不存在时）
```bash
ollama pull kingzeus/llama-3.1-8b-darkidol
ollama pull dagbs/darkidol-llama-3.1-8b-instruct-1.0-uncensored
```

如果报错 `file does not exist`，说明该标签不存在，尝试：
```bash
# 不指定标签，拉取latest
ollama pull 用户名/模型名

# 或尝试其他标签
ollama pull 用户名/模型名:q4_K_M
```

## 创建模型别名

安装后创建简短别名方便使用：

```bash
# 方法1：cp命令
ollama cp dagbs/darkidol-llama-3.1-8b-instruct-1.0-uncensored darkidol

# 方法2：创建Modelfile
ollama create darkidol -f << 'EOF'
FROM dagbs/darkidol-llama-3.1-8b-instruct-1.0-uncensored
EOF
```

验证：
```bash
ollama list  # 查看已安装的模型和别名
```

## 常用模型别名

| 别名 | 完整名 | 大小 | 说明 |
|------|--------|------|------|
| `darkidol` | dagbs/darkidol-llama-3.1-8b-instruct | 4.9GB | 角色扮演 |
| `qwen2.5` | qwen2.5:7b | 4.7GB | 通用中文 |
| `glm` | glm-4.7-flash:latest | 19GB | 智谱GLM |

## 下载进度监控

```bash
# 查看下载状态
ollama ps  # 正在运行的模型

# 检查模型文件
ls -la ~/.ollama/models/blobs/ | grep partial
```

## 网络问题处理

如果下载速度慢或超时：

```bash
# 设置代理（如果有）
export HTTPS_PROXY=http://127.0.0.1:12450
export HTTP_PROXY=http://127.0.0.1:12450

# 重新尝试
ollama pull 模型名
```
