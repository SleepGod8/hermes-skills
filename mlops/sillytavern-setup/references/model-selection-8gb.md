# 8GB 显存本地零审查中文言情/RP 模型选择（2026-08 实测）

硬件：RTX 4060 Laptop 8GB VRAM + 32GB RAM + Windows。目标：本地零审查写中文言情/角色扮演。

## 实测主角：DarkIdol vs Josiefied

| 维度 | DarkIdol-Llama-3.1-8B-1.2 | Josiefied-Qwen2.5-7B-abliterated-v2 |
|------|---------------------------|-------------------------------------|
| 基底 | Llama 3.1 8B（英文原生） | Qwen2.5 7B（中文原生） |
| 特化 | **RP 角色扮演特化**（数据全是 RP 集） | 通用无审查助手（abliterated + 进一步去审查微调） |
| 去审查 | 单层 abliteration | 双层（更彻底） |
| 中文 | 声明支持但只实测英文，实测有轻微翻译腔 | 原生流畅，用词考究 |
| 言情风格 | 第一人称「我」、暗黑阴郁、直球快节奏、动作推进快 | 第三人称、起名（林晓依）、细腻温暖、温水煮青蛙 |
| 速度 | 20-34 字符/s | 24-34 字符/s |
| 许可 | Llama 3.1 社区许可 | Apache 2.0（最宽松） |
| Ollama 官方库 | ❌ 无（需 hf.co 或手动 GGUF，有模板坑） | ✅ 官方库一键 pull |
| 大小(Q4_K_M) | 4.9 GB | 4.7 GB |

**结论**：言情重度依赖中文细腻度 → Josiefied 更稳；DarkIdol 的戏精感/第一人称代入是特色。两个都零审查实测通过（酒吧性张力场景都敢写，无拒绝）。

## 其它候选（调研未全测）

- `Qwen2.5-14B-Instruct-abliterated-v2`（huihui-ai / RichardErkhov GGUF）— 中文质量上限，Q4 ~9GB 略超 8GB 显存，需少量 CPU offload（15-25 tok/s）
- `glm-4-9b-chat-abliterated`（bartowski GGUF）— 中文原生对话自然，~5.5GB 全 GPU
- `collective-v0.1-chinese-roleplay-8b` — 中文 RP 特化带角色卡，但模型卡未声明去审查（风险项）
- `Lumimaid-v0.2-8B` — 英文 RP 热门，中文弱
- huihui-ai 是 abliteration 社区最活跃作者，Qwen 系全覆盖

## 检索技巧

- HuggingFace API：`https://huggingface.co/api/models?search=<kw>&limit=N` 直接 JSON 搜（hf-mirror 的 API 会 308 重定向，直连 HF 更稳）
- 模型卡：`https://huggingface.co/<repo>/raw/main/README.md`（国内用 hf-mirror.com 前缀）
- 查 GGUF 文件列表：`/api/models/<repo>/tree/main`
- 下载速度实测（本机 2026-08）：HF 官方 CDN 直连 6.8 MB/s > 代理 12450 6.1 MB/s > hf-mirror 5.7 MB/s；Ollama 多线程分块下载可达 29 MB/s —— 不要盲目开代理
