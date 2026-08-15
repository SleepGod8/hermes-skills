# 本地 Ollama 行为怪癖卡（darkidol / josiefied / bge-m3）

> 状态：怪癖最明确的一张，重点维护

## 定位 / 用途

- 本地零审查 RP / 色情 / 纯文字创作
- 模型：darkidol（默认 RP）、josiefied、bge-m3（embedding）

## 已知怪癖

| # | 怪癖 | 现象/触发 | 影响 |
|---|------|----------|------|
| 1 | 8B 模型工具调用弱 | skill 读取 / 文件操作 / 复杂机制运算（等级制、面板存档） | 可能不稳定或失败 |
| 2 | GGUF 模板未识别 | hf.co 拉 GGUF 后只输出 safe | 模型乱答 |
| 3 | 中文命令行乱码 | git-bash 命令行直接传中文 | 请求变乱码 |

## 矫正话术

- 怪癖 1 → 纯文字创作（言情/RP/露骨）才切本地；涉及工具调用/复杂机制切回云端 DeepSeek
- 怪癖 2 → Modelfile 手写 TEMPLATE（详见 ollama-hf-gguf-import）
- 怪癖 3 → 中文请求用 UTF-8 文件 + `--data-binary @file`

## 使用提醒

- 验证连接：`curl http://127.0.0.1:11434/v1/models`
- provider 配置（custom:Ollama）：base_url `http://127.0.0.1:11434/v1`，api_key 任意（不校验）
