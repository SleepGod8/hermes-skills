---
name: ollama-hf-gguf-import
description: Use when Ollama hf.co GGUF 模板未识别致模型乱答，用 Modelfile 修复。
---

# Ollama 从 HuggingFace 直拉 GGUF 的模板坑与修复

## 触发条件

- `ollama pull hf.co/<user>/<repo>:<quant>` 下载完成后，`ollama run` 输出异常：
  - 只输出一个词（如 `safe`）、短乱码、或不按对话格式回答
- `ollama show <model>` 显示 `Capabilities: completion`（**没有 chat**）
- `Parameters: temperature 0`（hf.co 拉取时默认值异常）

## 根因

Ollama 从 `hf.co/...` 引用 GGUF 时，依赖 GGUF 文件内嵌的 chat template（jinja）来注册为 chat 模型。部分量化作者（如 mradermacher）的 GGUF 内嵌模板缺失/不标准，Ollama 退化为 **completion-only** 模型，输入未按聊天模板格式化 → 模型乱答。

## 诊断

```bash
ollama show hf.co/<user>/<repo>:<quant>
# 看 Capabilities: 如果只有 completion 而非 chat/completion → 模板没识别
```

## 修复流程

1. **写 Modelfile**（注意 `FROM` 直接引用已下载的 ollama 模型名，不会重复下载）：

```dockerfile
FROM hf.co/<user>/<repo>:<quant>

TEMPLATE """<按模型架构的模板，见下表>"""

PARAMETER temperature 0.7
PARAMETER num_ctx 8192
```

2. **重新导入短名模型**：

```bash
ollama create <shortname> -f Modelfile
```

3. **验证**：

```bash
ollama show <shortname>   # Capabilities 出现 chat（显示 completion 也未必影响，实测为准）
ollama run <shortname> "test"
```

## 常用架构聊天模板

### Llama 3.1（DarkIdol 等 8B 模型）

```dockerfile
TEMPLATE """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{{ if .System }}{{ .System }}<|eot_id|>{{ end }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
```

### Qwen 2.5 / Qwen3（Josiefied 等）

```dockerfile
TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""
```

### Mistral / Gemma / 其他

- Mistral: `<s>[INST] {{ .Prompt }} [/INST]`
- Gemma: `<start_of_turn>user\n{{ .Prompt }}<end_of_turn>\n<start_of_turn>model\n`
- 或直接查模型卡 / GGUF 元数据（`strings model.gguf | grep -i template`）

## 实测案例（2026-08, RTX 4060 Laptop 8GB）

- **DarkIdol-Llama-3.1-8B Q4_K_M**：hf.co 直拉后只输出 `safe`，Capabilities 仅 completion → 用 Llama 3.1 模板重建 `darkidol` 短名后恢复正常
- **Josiefied-Qwen2.5-7B（Ollama 官方库）**：无此问题，官方库模型自带正确模板

## 另一个坑：Llama 3.1 系 API 中文乱码（字节级 BPE 解码 bug）

- 现象：`darkidol` 通过 Ollama **API 端点**（/api/chat、/api/generate、/v1/chat/completions）输入中文 prompt，输出为乱码（含大量 U+FFFD 替换符）；**英文 prompt 正常**；`ollama run darkidol` CLI 中文**正常**。
- 根因：Llama 3.1 的 byte-level BPE tokenizer 对中文处理，在 Ollama API 层解码出错；CLI 与 API 走不同解码路径。
- 影响：SillyTavern 等走 API 的前端用 DarkIdol 写中文会乱码 → **中文 RP 用 Josiefied（Qwen tokenizer 正常），DarkIdol 只适合 CLI 或英文场景**。
- 判断方法：`curl http://127.0.0.1:11434/api/generate -d '{"model":"xxx","prompt":"你是谁？","stream":false}'` 看输出是否正常。
- 排查注意：Windows git-bash 管道到 python 有编码干扰，写文件再读（用 Windows 绝对路径，勿用 /tmp）。

## 其他经验

- **国内下载速度**：不要盲目开代理。实测 HF 官方 CDN 直连可达 6.8 MB/s（Cloudflare 边缘节点），代理绕路反而慢（6.1 MB/s）。Ollama 多线程下载更快（实测 29 MB/s）。
- **hf-mirror.com 备用**：直连慢时用 `curl -L` 手动下 GGUF + Modelfile `FROM ./local.gguf` 导入。
- 速度对比测试脚本参考 `test_models.sh` / `test_models_censorship.sh`（workspace）：注意 git-bash 没有 `bc`，用 `awk "BEGIN{print ...}"` 计算。
- 模型下载后 `ollama list` 确认；hf.co 引用模型名很长，建议重建短名。

## Pitfalls

- 修复后 `ollama show` 的 Capabilities 可能仍显示 completion——**以实际输出为准**，模板生效就能正常对话
- `FROM` 引用 ollama 模型名（`hf.co/...:quant`）时确保先 pull 过，否则会尝试从 HF 重新下载
- Windows git-bash 下 curl `-o /dev/null` 可能报 exit 23（写入错误），写临时文件测速更稳
