# Ollama 导入 GGUF：模板坑 + 下载速度 + 实测数据（2026-08）

## 一、Ollama 从 hf.co 直拉 GGUF 的模板坑（重要）

### 现象
```bash
ollama pull hf.co/mradermacher/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored-GGUF:Q4_K_M
# 成功。但 ollama run 之后，中英文提示都只输出 "safe"（单次生成就结束）
```

### 诊断
```bash
ollama show hf.co/mradermacher/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored-GGUF:Q4_K_M
```
看到 `Capabilities: completion`（**没有 chat**）→ Ollama 没识别 GGUF 内嵌聊天模板，把 chat 输入按 raw completion 拼接，模型无从理解格式，给出退化输出（"safe"）。`temperature 0`（默认）加剧了问题。

### 修复（不用重新下载）
写 Modelfile，FROM 直接引用**已拉下来的模型名**（Ollama 复用 blob 层，秒建）：

```
FROM hf.co/mradermacher/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored-GGUF:Q4_K_M

TEMPLATE """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{{ if .System }}{{ .System }}<|eot_id|>{{ end }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

PARAMETER temperature 0.7
PARAMETER num_ctx 8192
```
```bash
ollama create darkidol -f darkidol_Modelfile
```
- Llama 3.1 家族模板：`<|begin_of_text|><|start_header_id|>...<|eot_id|>` 格式（上面这份可直接套用）
- Qwen 家族模板：`<|im_start|>system ... <|im_end|>` ChatML 格式
- 不同架构的 GGUF 都适用此流程：先 `ollama show` 查 Capabilities，缺 chat 就手动补 TEMPLATE

### 为什么官方库模型没这问题
`ollama pull <作者>/<模型>`（ollama.com 官方库）的 manifest 自带正确模板；hf.co 直拉依赖 GGUF 文件内嵌 template 元数据，mradermacher 这类静态量化有时缺失或不标准 → 退化。

## 二、下载速度实测（2026-08，本机网络）

20MB range 下载样本测速：

| 路径 | 速度 | 结论 |
|------|------|------|
| HuggingFace 官方 CDN 直连（无代理） | 6.8 MB/s | 国内直连 CF 节点可能很快 |
| HF 官方走本地代理 12450 | 6.1 MB/s | 代理多一跳，未必更快 |
| hf-mirror.com 直连 | 5.7 MB/s | 最稳（国内 CDN） |

**ollama pull 多线程分块下载**（29 MB/s，并发）比 curl 单线程快 4-5 倍——预估下载时间别用 curl 测速单线程数字，ollama 会快很多。

⚠️ 代理结论要看当次网络：本机直连 HF 就快时，开 VPN 反而略慢；代理「常断」时不值得为省 1 MB/s 冒险。晚上/高峰可能反转，掉速再切 hf-mirror。

## 三、DarkIdol vs Josiefied 实测对比（Q4_K_M，RTX 4060 Laptop 8GB）

两个模型都通过**审查边界测试**（酒吧微醺互撩 prompt）——都敢写，无安全拒绝。

| 维度 | DarkIdol（Llama 3.1 8B RP） | Josiefied（Qwen2.5 7B abliterated） |
|------|------|------|
| 视角 | 第一人称「我」心理独白 | 第三人称、给女主起名（林晓依） |
| 文风 | 暗黑阴郁系、网络小说腔、比喻有灵气（「天空就是个泪腺」） | 细腻言情小说笔法（「笑容温润如初夏的晨风」） |
| 性张力写法 | 直球三连：握手→搂腰→埋颈窝，19s/428字 | 温水煮青蛙：碰肩→滑手腕→勾耳垂→搂腰，22s/767字 |
| 中文流畅度 | 流畅，略翻译腔 | 更顺滑，用词考究 |
| 速度 | 20-34 字符/s（波动） | 24-34 字符/s（波动） |

选型结论（用户口味参考）：
- 想要**直球、暗黑、代入感强** → DarkIdol（但必须修模板）
- 想要**细腻、温暖、小说感** → Josiefied（官方库直拉即可，中文更顺）

## 四、测试脚本（可复用）

```
同一提示词跑两模型 → 记耗时/字符 → awk 算字符/s（git-bash 无 bc）
审查边界测试：直白暧昧 prompt，看是否拒绝
```
- 字符/s 不能跨基底直接比 tok/s：Qwen 中文 tokenizer 高效（1字≈1token），Llama 中文 token 多
- git-bash：`bc` 不存在 → `awk "BEGIN{print $END-$START}"`；curl `-o /dev/null` exit 23 → 写临时文件
