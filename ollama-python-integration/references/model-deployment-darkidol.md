# Ollama 模型部署实战记录

## darkidol 模型部署（2026-08-05）

### 模型信息
- **名称**: dagbs/darkidol-llama-3.1-8b-instruct-1.0-uncensored
- **大小**: 4.9 GB
- **参数**: 8B (Q4_K_M量化)
- **上下文**: 131072（推荐降低到512-1024）

### 部署步骤
```bash
# 1. 拉取模型（需要约5-7分钟）
ollama pull dagbs/darkidol-llama-3.1-8b-instruct-1.0-uncensored

# 2. 创建简短别名
ollama cp dagbs/darkidol-llama-3.1-8b-instruct-1.0-uncensored darkidol

# 3. 验证
ollama list
ollama ps
```

### OOM 问题解决
32GB内存机器需要降低 num_ctx：
```python
# 使用 num_ctx=512 避免 OOM
options = {"num_ctx": 512}
```

### 测试结果
- ✅ 普通对话：`你好` → `我是LUGUO`
- ✅ 故事生成：`讲一个关于机器人的短故事` → 正常输出
- ✅ 流式输出：工作正常

### 相关文件
- 测试脚本：`D:/PythonProject/test_darkidol.py`