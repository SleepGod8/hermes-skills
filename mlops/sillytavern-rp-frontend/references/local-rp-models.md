# 本地零审查言情/RP 模型选型（RTX 4060 Laptop 8GB VRAM, 32GB RAM）

用户场景：中文言情/暧昧 RP、零审查、本地离线、不烧 API。8GB 显存甜点区 = 7-9B Q4_K_M 全 GPU。

## 已安装并实测（2026-08，Ollama）

| 模型 | 基底 | 性格/文风 | 实测 |
|------|------|----------|------|
| `darkidol` | Llama 3.1 8B uncensored（abliteration + RP 数据集微调） | 直球、暗黑系、第一人称「我」视角、动作推进快 | 零审查 ✅；20-34 字符/s；需 Modelfile 手写 Llama 3.1 模板否则只输出 "safe"（见 ollama-hf-gguf-import） |
| `goekdenizguelmez/JOSIEFIED-Qwen2.5` | Qwen2.5-7B abliterated + 进一步去审查微调 | 细腻温暖、第三人称叙事、心理描写丰富、中文更顺 | 零审查 ✅；24-34 字符/s；Ollama 官方库直拉无模板问题 |

选型速记：**DarkIdol = 英文脑 + 戏精魂；Josiefied = 中文脑 + 更敢的老实人**。言情重度依赖中文细腻度 → Josiefied 更稳；要沉浸式第一人称暗黑感 → DarkIdol。

## 候选升级路径（未安装）

- **Qwen2.5-14B-Instruct-abliterated-v2**：中文质量上限，Q4 ~9GB 略超显存 → CPU offload，15-25 tok/s（32GB RAM 撑得住）
- **glm-4-9b-chat-abliterated**：GLM 中文原生 + 去审查，~5.5GB 全 GPU
- **collective-v0.1-chinese-roleplay-8b**：中文 RP 特化（带角色卡系统），但模型卡未提去审查 → 有残留安全对齐风险
- **Lumimaid-v0.2-8B**：SillyTavern 热门，但英文向中文弱
- huihui-ai 系 GGUF 需去 huihui-ai 或 mradermacher 仓库找量化版

## 国内下载速度（实测）

- HF 官方 CDN 直连可快（Cloudflare 边缘节点，实测 6.8 MB/s），**不要盲目开代理**（绕路反而慢 6.1 MB/s）
- Ollama 多线程 pull 更快（实测 29 MB/s）
- hf-mirror.com 作稳定备选（单线程 ~5.7 MB/s）
