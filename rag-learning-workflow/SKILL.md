---
name: rag-learning-workflow
description: Use when learning RAG. Guide doc loading and retrieval.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [rag, vector-database, milvus, embedding, retrieval]
    related_skills: [local-llm-python, jupyter-live-kernel]
---

# RAG 学习工作流

## Overview

提供完整的RAG（检索增强生成）学习路径指导，涵盖从文档加载、文本切片、向量嵌入、语义检索到完整RAG系统的实现。基于D:\w1_d3目录的教学代码，帮助学习者理解和实践RAG核心技术。

## When to Use

- 用户询问RAG相关概念或实现
- 用户需要学习向量数据库（Milvus）的使用
- 用户需要了解文本切片策略（chunking）
- 用户需要实现语义检索或混合检索
- 用户需要构建完整的RAG系统

## 核心知识体系

### 1. RAG基础概念

RAG = Retrieval Augmented Generation（检索增强生成）

```
公式：AI应用开发能力 = 软件工程系统能力 × LLM系统能力

RAG流程：文档向量化 → 向量检索 → 大模型拼接上下文回答
```

**离线链路**：文档解析 → 数据清洗 → 文本切分 → Embedding → 向量存储 → 索引构建

**在线链路**：问题理解 → 知识检索 → 候选重排 → 上下文构建 → 大模型生成 → 来源引用

### 2. 文档加载（04_load_documents.py）

支持格式：`.txt`（UTF-8/GBK）和 `.pdf`（按页拆分）

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Document:
    title: str          # 文档标题（文件名或页码）
    source: str         # 文件来源路径
    content: str        # 正文内容
    metadata: dict      # 元数据（file_type, page, encoding等）
```

### 3. 文本切片策略（05_chunking_strategies.py）

| 策略 | 函数 | 特点 |
|------|------|------|
| 固定字符 | `fixed_char_chunks(text, 120)` | 简单快速，可能切断语义 |
| 段落 | `paragraph_chunks(text)` | 保持段落完整性 |
| 句子 | `sentence_chunks(text)` | 细粒度，保持句子完整 |
| 滑动窗口 | `sliding_window_chunks(text, 140, 40)` | 重叠保留上下文 |
| 递归切片 | `recursive_chunks(text, 180, 30)` | 优先语义完整 |

### 4. Embedding生成（06_embedding_ollama.py）

```bash
ollama pull bge-m3
ollama pull nomic-embed-text
```

```python
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"

def embed_texts(texts: list[str], model: str) -> list[list[float]]:
    response = requests.post(OLLAMA_EMBED_URL, json={"model": model, "input": texts})
    return response.json()["embeddings"]
```

### 5. 检索方法（07_retrieval_methods.py）

| 方法 | 说明 |
|------|------|
| 向量检索 | 余弦相似度Top-K |
| 关键词检索 | BM25/词频统计 |
| 混合检索 | RRF融合多路结果 |
| Rerank | 对候选结果重排 |

### 6. Milvus向量数据库（01-03.py）

```python
from pymilvus import MilvusClient, DataType
client = MilvusClient(uri="http://localhost:19530", db="claz604")
```

### 7. 完整RAG流程（99.py）

离线：文档切分 → Embedding → 存储向量
在线：检索相关文档 → 构建Prompt → 大模型生成

## 执行流程

1. **环境检查**：确认Milvus和Ollama运行
2. **选择学习路径**：根据用户目标选择模块
3. **实践指导**：提供可运行代码示例
4. **知识总结**：输出核心结论

## 常见问题

**Q: 切片策略如何选择？**
- 文档结构清晰 → 段落切片
- 需要精确匹配 → 句子切片
- 平衡语义和长度 → 递归切片（推荐）

**Q: 向量维度如何选择？**
- bge-m3: 1024维
- nomic-embed-text: 768维

**Q: 检索结果不准确怎么办？**
1. 检查切片策略
2. 尝试混合检索
3. 添加Rerank
4. 优化Prompt

## Verification Checklist

- [ ] 理解RAG基本流程
- [ ] 掌握至少3种切片策略
- [ ] 能使用Ollama生成Embedding
- [ ] 能实现向量检索
- [ ] 理解RRF融合原理
- [ ] 能搭建完整RAG系统

## 参考资源

- Milvus: https://milvus.io/docs
- Ollama: https://ollama.com/library
- BAAI/bge-m3: https://github.com/FlagOpen/FlagEmbedding