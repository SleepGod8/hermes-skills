---
name: local-llm-model-selection
description: Use when 用户问本地模型性能/选型/对比. 按显存预算+用途(无审查/RP/中文)从 HF 选模型.
version: 1.0.0
tags: [llm, local-model, vram, quantization, gguf, uncensored, roleplay, huggingface, model-selection]
---

# 本地 LLM 选型（Local LLM Model Selection）

当用户问「这个本地模型性能如何」「以我的配置还有什么更好的本地模型」「帮我选个能跑的模型」时使用。核心不是跑推理（那是 `llama-cpp` skill 的事），而是**在硬件预算内做选型决策**。

## 触发场景

- 用户给出一个模型名（如 DarkIdol）问本地性能/能不能跑
- 用户给出用途（言情/角色扮演/无审查/写作/看图/判断画风）问本地有什么更好选择
- 用户报显存/内存问该下哪个量化档
- 用户发图问画风但云端视觉模型被拦截，需要本地视觉模型替代

## 工作流

### Step 1: 先确定硬件约束（硬顶，别先谈模型）

```bash
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
```

8GB VRAM 档位的速查（本用户 RTX 4060 Laptop 8GB / 32GB RAM）：
- 7B Q4_K_M ≈ 4.7GB → 全 GPU，**40-60 tok/s**（甜点区）
- 8B Q4_K_M ≈ 4.9GB → 全 GPU，40-55 tok/s
- 9B (GLM-4) Q4 ≈ 5.5GB → 全 GPU，35-50 tok/s
- 14B Q4_K_M ≈ 9GB → **超显存**，靠 32GB RAM 部分 CPU offload → 15-25 tok/s
- Q8_0 8B ≈ 8.5GB → 超 8GB 显存，掉到 10-20 tok/s，不推荐
- 速度估算基准：4060 Laptop 带宽 ~256GB/s；8B Q4 全 GPU 约 40-55 tok/s

**视觉模型（VLM）档位**（需要额外 mmproj 投影器文件）：
- Qwen2.5-VL-7B Q4_K_M ≈ 4.5GB（mmproj-Q8_0 ≈ 0.6GB）→ 合计 ~5.1GB，全 GPU 可行
- Qwen2.5-VL-7B abliterated Q4_K_M ≈ 4.5GB → 去审查版，NSFW 图片无限制
- moondream2 ≈ 1.8GB → 极轻量但画风判断能力弱，仅做兜底
- 注意：VLM 比同参数量文本模型多占 ~0.5-1GB（mmproj 投影器），选显存预算时要多算进去

### Step 2: HF API 发现候选（headless，比浏览器快）

```bash
# 按关键词搜（URL-encode 中文/空格）
curl -s --max-time 25 "https://huggingface.co/api/models?search=abliterated&limit=8" | python -c "import sys,json; [print(m['id'],'| dl:',m.get('downloads',0)) for m in json.load(sys.stdin)]"
# 按作者搜全部模型（huihui-ai 是知名 abliteration 作者）
curl -s "https://huggingface.co/api/models?author=huihui-ai&limit=100" | python -c "..."
# 查某 repo 的 GGUF 文件清单
curl -s "https://huggingface.co/api/models/<repo>/tree/main?recursive=true" | python -c "..."
```

下载量（downloads）是热度代理指标，用于快速排序候选。

### Step 3: 核对模型卡（README），别信标题

```bash
curl -sL --max-time 30 "https://huggingface.co/<repo>/raw/main/README.md" | grep -iE "(uncens|nsfw|审查|censored|RP|roleplay|中文|romance|abliterat)"
```

必须验证的点：
- **是否真的去审查**：abliterated（消融拒绝方向）> 声称 uncensored 的微调 > 完全没提（多半有残留对齐）
- **中文支持是声明还是实测**：很多模型卡写支持 zh 但「only test en」——这是最大的坑（DarkIdol 就是如此）
- 基底模型是什么（决定中文能力上限：Qwen 系 > GLM 系 > Llama 系英文向）

### Step 4: 确认 GGUF 量化可用性

- mradermacher / bartowski / RichardErkhov / Lewdiculous 是常见 GGUF 量化作者
- **i1 / imatrix 加权版**同大小质量更好，优先
- Q4_K_M 是通用推荐档；Q5_K_M/Q6_K 质量优先；IQ4_XS 省显存给长上下文

### Step 5: 给推荐 + 用户确认后才下载

本用户偏好（实测两次）：**先调研选型、展示对比表格，等用户明确选「下哪个」才拉取 GB 级模型**。不要擅自开始下载。

推荐呈现格式：对比表格（模型 | 基底/特点 | 显存占用 | 速度预估 | 用途适配度）+ 一句「为什么这个最优」+ 升级路径。参考 `llm-benchmark-research` 的 🏆/⭐/⚠️ 标记风格。

## 无审查/RP 模型生态地图

详见 **[references/uncensored-rp-ecosystem.md](references/uncensored-rp-ecosystem.md)** — DarkIdol 家族、huihui-ai abliterated 栈、中文 RP 模型、选型启发式（含 2026-08 调研时的模型清单与下载量）。

核心启发式（中文言情/RP 场景）：
1. 中文能力看基底：Qwen2.5/3 系原生中文最强
2. 去审查首选 huihui-ai 的 abliterated 系列（社区公认）
3. RP 氛围靠 RP 微调层（如 Josiefied 版 Qwen2.5-7B-abliterated-v2 = 去审查 + 言情微调，8GB 甜点）
4. 英文向 RP 模型（DarkIdol/Lumimaid）中文文笔存疑，作为备选而非首选

## 本地 VLM 视觉模型（云端视觉被内容审计拦截时）

**2026-08 实测背景**：NSFW 图片会同时被 GLM-4.6v-flash（1301）、qwen-vl-plus（data_inspection_failed）、ASLNet（403）三家内容审计拦截，本地无审查 VLM 是唯一出路。

### 推荐选型（8GB 卡）

| 模型 | 大小 | 说明 |
|------|------|------|
| `mradermacher/Qwen2.5-VL-7B-Abliterated-Caption-it-GGUF` | Q4_K_M 4.4GB + mmproj-Q8_0 0.6GB | ⭐ 首选：去审查 + 专攻图像描述 + 支持中文 |
| `mradermacher/Qwen2.5-VL-7B-Instruct-abliterated-GGUF` | 同上 | 通用指令版去审查 |
| `qwen2.5vl:7b`（Ollama 官方库） | 6GB | 未去审查；Ollama 直拉国内极慢（实测 119-153 KB/s，14h+） |

### 下载与导入（mmproj 双文件结构）

VLM 的 GGUF 是**双文件**：主模型 `.gguf` + 视觉投影器 `mmproj-*.gguf`，两个都要下：

```bash
# hf-mirror 下载（国内直连）
curl -L -o model.Q4_K_M.gguf 'https://hf-mirror.com/<repo>/resolve/main/<model>.Q4_K_M.gguf'
curl -L -o mmproj-Q8_0.gguf 'https://hf-mirror.com/<repo>/resolve/main/<model>.mmproj-Q8_0.gguf'
```

Ollama 导入 VLM 需要同时指定主模型 + mmproj。Modelfile 用 `FROM` 指向本地 gguf，`ADAPTER` 挂载 mmproj。Ollama 新版语法也可用 `ollama create <name> --model gguf --mmproj mmproj`。国内 hf.co 直拉 Ollama VLM 极慢，建议走 hf-mirror 手动下载再导入。

### 运行验证

```bash
ollama ps  # 确认没有其他模型占显存
curl http://127.0.0.1:11434/api/chat -d @request.json  # 带图 base64 测试
```

显存注意：8GB 卡跑 7B VLM Q4 基本占满，darkidol 等文本模型要先退出。

## Pitfalls

- **Ollama 从 hf.co 直拉 GGUF 可能模板未识别（重大坑）**：`ollama pull hf.co/<repo>:Q4_K_M` 成功后，模型可能只输出 "safe"（中英文提示都只回一个词）。诊断：`ollama show <model>` 看 Capabilities 只有 **completion**（没有 chat）→ Ollama 没读到 GGUF 内嵌聊天模板，把输入当 raw completion 处理。修复：手动写 Modelfile 指定正确 TEMPLATE（Llama 3.1 用 `<|begin_of_text|><|start_header_id|>...`，Qwen 用 `<|im_start|>...`）+ `PARAMETER temperature 0.7`，然后 `ollama create <短名> -f Modelfile`（FROM 直接引用已拉的模型名，**不用重新下载**）。完整复现/修复见 [references/ollama-gguf-import.md](references/ollama-gguf-import.md)。
- **hf-mirror.com API 返回 308 重定向**：curl 不带 `-L` 会拿不到数据；备选是直接打 `huggingface.co/api/models`（本机直连可用）。README raw 拉取走 hf-mirror + `-L` 即可。
- **模型卡声明 ≠ 实测**：尤其「重新对齐中日韩但只测英文」这类话术，中文效果必须实测（下 Q4 跑一段中文提示词验证）。
- **Q8_0 看起来更准但超显存**：8GB 卡上 8B Q8_0 要 CPU offload，反而比 Q4_K_M 全 GPU 慢得多。
- **35B-A3B 这类 MoE 别推荐给 8GB 卡**：激活参数小但权重总量大（Q4 ≈ 20GB），offload 后速度不佳。
- **ASLNet 模型碰 NSFW 内容会 403 风控拦截**：涉及 NSFW/色情图片分析时，禁止用 ASLNet（gpt-5.x 系列）的视觉能力，必须走 GLM-4.6v-flash / qwen-vl 或本地 VLM。
- **像素统计推断画风是瞎猜**：当视觉 API 全部被内容审计拦截时，用 PIL+numpy 算饱和度/色数/边缘强度来推断画风（赛璐璐 vs 厚涂 vs 欧美风）是不可靠的——纯数值层面日系和欧美动漫风几乎无法区分。正确做法：坦诚告知用户看不到图，让用户描述画面特征后再判断，或者部署本地无审查 VLM（见「本地 VLM 视觉模型」章节）。
- **git-bash 下测速/计时坑**：`bc` 不存在（用 `awk "BEGIN{print ...}"` 算耗时）；curl `-o /dev/null` 会报 exit 23 写失败（写临时文件再测）。
- 模型迭代快，下载量/生态结论每几个月会变；以当次 HF 搜索为准，reference 文件当背景知识。

## 实测对比方法论（选型后验证）

拉下来之后别只看速度，按这套跑一遍再下结论（脚本可复用）：

1. **同一段提示词**跑两个模型（如一段中文言情场景 200-300 字），对比文风 + 字符/s。注意：**字符/s ≠ tok/s**——Qwen 系中文 tokenizer 高效（1 字≈1 token），Llama 系中文 token 更多，同 tok/s 下 Qwen 字符/s 更高。
2. **审查边界测试**：用直白暧昧/性张力提示词（如酒吧微醺互撩）验证「零审查」是否属实——拒绝 = 输出安全警告/空回答；通过 = 正常展开。这是选无审查模型的关键验收步骤。
3. 记录第一人称 vs 第三人称、直球 vs 细腻等文风差异，按用户口味推荐（本用户实测偏好见下）。

实测数据样本（2026-08，DarkIdol vs Josiefied，Q4_K_M，8GB 卡）见 [references/ollama-gguf-import.md](references/ollama-gguf-import.md) 末尾。

## 相关 skill

- `llama-cpp` — 跑 GGUF 推理、llama-server 命令、URL 式 discovery（本 skill 只管选型）
- `llm-benchmark-research` — 云模型基准对比（LiveBench 等），与本地硬件选型互补
- `local-llm-python` / `ollama-python-sdk` — 本地跑起来之后用 Ollama/llama.cpp Python 调用
