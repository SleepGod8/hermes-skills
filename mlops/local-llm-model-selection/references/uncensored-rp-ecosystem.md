# 无审查/RP 本地模型生态地图（2026-08 调研快照）

> 调研背景：用户 RTX 4060 Laptop 8GB VRAM / 32GB RAM，需求=本地零审查写中文言情/RP。
> 下载量数据是 2026-08 时点快照，会过期——复用此文件时以当次 HF 搜索为准。

## DarkIdol 家族（Llama 3.1 8B 无审查 RP）

| Repo | 说明 |
|------|------|
| `aifeifei798/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored` | 原版（1.2 最新）。abliteration 去审查；RP/dark-RP/写作；训练数据 ChaoticNeutrals/Gryphe/meseca/Lumimaid；128K ctx |
| `mradermacher/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored-GGUF` | 标准静态量化 Q2_K~f16（Q4_K_M 4.92GB） |
| `mradermacher/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored-i1-GGUF` | **imatrix 加权版，优先选它** |
| `LWDCLS/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored-GGUF-IQ-Imatrix-Request` | Lewdiculous IQ-imatrix |
| `DavidAU/Llama-3.1-DeepSeek-8B-DarkIdol-Instruct-1.2-Uncensored-GGUF` | **DeepSeek R1 蒸馏推理 + DarkIdol 无审查合并版**，带 think 标签，任意温度可推理 |

⚠️ DarkIdol 模型卡：声明「重新对齐中日韩」但 **only test en**——中文效果未实测，是最大悬念。

## huihui-ai abliterated 栈（社区公认最强去审查作者）

| Repo | 基底/特点 |
|------|----------|
| `huihui-ai/Qwen2.5-7B-Instruct-abliterated-v2` (5.2K dl) | Qwen2.5-7B 去审查，中文 7B 档最强 |
| `huihui-ai/Qwen2.5-14B-Instruct-abliterated-v2` | 14B 中文更强；GGUF 见 `RichardErkhov/huihui-ai_-_Qwen2.5-14B-Instruct-abliterated-v2-gguf` (11.5K dl) / `maicog` Q4_K_M |
| `Goekdeniz-Guelmez/Josiefied-Qwen2.5-7B-Instruct-abliterated-v2` | ⭐ **abliterated + RP/言情微调**（Josiefied），中文言情甜点；GGUF: `mradermacher/Josiefied-...-i1-GGUF` |
| `huihui-ai/Huihui-Qwen3-14B-abliterated-v2` | Qwen3 14B 去审查 |
| `huihui-ai/Huihui-Qwen3.6-35B-A3B-abliterated` | MoE 35B-A3B——**8GB 卡不推荐**（权重 Q4≈20GB，offload 慢） |
| `huihui-ai/DeepSeek-R1-Distill-Qwen-14B-abliterated-v2` | 推理向 + 去审查；言情偏理性，非首选 |
| `huihui-ai/Huihui-Qwythos-9B-Claude-Mythos-5-1M-abliterated` | 9B Claude-Mythos 风格，1M ctx |

## GLM 系（中文原生）

- `byroneverson/glm-4-9b-chat-abliterated` / `bartowski/glm-4-9b-chat-abliterated-GGUF` (1.7K dl) — GLM-4-9B 中文原生 + 去审查，Q4≈5.5GB 全 GPU
- `huihui-ai/Huihui-GLM-5.2-abliterated-GGUF` (24K dl) — GLM-5.2（尺寸需确认，可能超 8GB 甜点）

## 中文 RP 特化（注意审查状态）

| Repo | 说明 | 风险 |
|------|------|------|
| `Collective-Ai/collective-v0.1-chinese-roleplay-8b` | 中文 RP 特化，结构化角色卡（姓名/性别/年龄/性格/关系/背景）| ⚠️ 模型卡未提去审查，可能有残留对齐 |
| `senseable/WestLake-7B-v2` | 中文通用创意写作，非 RP 特化 | 非无审查定位 |
| `maywell/Qwen2-7B-Multilingual-RP` | Qwen2 多语言 RP | 2 代基底，中文一般 |

## 英文向 RP（中文弱，备选）

- `NeverSleep/Llama-3-Lumimaid-8B-v0.1-GGUF` / `Lewdiculous/Lumimaid-v0.2-8B-GGUF-IQ-Imatrix` — SillyTavern 热门，轻度审查，中文文笔弱

## 选型启发式（中文言情/RP → 8GB 卡）

1. **中文能力看基底**：Qwen2.5/3 系 > GLM 系 > Llama 系（英文向）
2. **去审查看作者**：huihui-ai abliterated 系列社区公认；abliterated（消融拒绝方向）比「声称 uncensored 的微调」更可靠
3. **RP 氛围靠微调层**：abliterated 基底上叠 RP 微调（Josiefied 版 Qwen2.5-7B）≈ 最优组合
4. 推荐排序（2026-08）：
   - 首选 `Josiefied-Qwen2.5-7B-Instruct-abliterated-v2`（Q4_K_M ~4.7GB，40-60 tok/s）
   - 质量上限 `Qwen2.5-14B-Instruct-abliterated-v2`（Q4 ~9GB 部分 offload，15-25 tok/s）
   - 对话向 `glm-4-9b-chat-abliterated`（Q4 ~5.5GB 全 GPU，35-50 tok/s）
   - DarkIdol/Lumimaid 英文向作备选
5. ✅ 已实测（2026-08）：DarkIdol 与 Josiefied 都通过审查边界测试（敢写性张力），文风差异见 [ollama-gguf-import.md](ollama-gguf-import.md) 第三节；**DarkIdol 需先修 Ollama 模板坑**（见该文件第一节），Josiefied 官方库直拉即用

## 网络注意（本机）

- `huggingface.co/api/models` 直连可用（无需代理）
- `hf-mirror.com` API 返回 308，curl 需 `-L`；README raw 用 hf-mirror + `-L` 拉取
