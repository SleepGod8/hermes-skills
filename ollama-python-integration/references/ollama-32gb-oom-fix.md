# Ollama 32GB 内存限制与 num_ctx 调优

## 问题
8B 模型（如 darkidol、qwen2.5:7b）默认 `num_ctx=131072`，需要约 17GB KV cache 内存。
在 32GB 总内存的机器上，可用内存通常只有 ~16GB，导致 OOM：

```
Error: 500 Internal Server Error: llama-server reported out-of-memory
ggml_backend_cpu_buffer_type_alloc_buffer: failed to allocate buffer of size 17179869184
```

## 解决方案

降低 `num_ctx` 来减少内存占用：

| num_ctx | 内存需求 | 适用场景 |
|---------|---------|---------|
| 512     | ~3.5GB  | 32GB 内存机器（最低） |
| 1024    | ~4.5GB  | 32GB 内存机器（推荐） |
| 4096    | ~8GB    | 64GB 内存机器 |
| 131072  | ~17GB   | 64GB+ 内存机器 |

## 代码示例

```python
import requests

def chat_with_ollama(prompt, num_ctx=512):
    """使用低 num_ctx 避免 OOM"""
    url = "http://localhost:11434/api/chat"
    data = {
        "model": "darkidol",
        "messages": [{"role": "user", "content": prompt}],
        "options": {"num_ctx": num_ctx}
    }
    r = requests.post(url, json=data, stream=True, timeout=120)
    # 处理流式响应...
```

## 验证方法

```bash
# 检查可用内存
wmic OS get FreePhysicalMemory,TotalVisibleMemorySize

# 检查当前运行模型
ollama ps
```

## 注意事项

1. **num_ctx 降低的影响**：上下文窗口变小，长对话可能截断。但对于简单问答足够。
2. **模型加载大小不变**：模型本身 ~5GB 不变，只是 KV cache 变小。
3. **32GB 内存最佳配置**：qwen2.5:7b (4.7GB) + num_ctx=1024 是最佳平衡点。
4. **模型加载**：8B模型下载需要约5-7分钟（取决于网速）。