# hermes-comfyui MCP 502 → curl 直连 fallback（2026-08-30 实测）

## 症状

`mcp__hermes_comfyui__comfy_run_workflow` 提交时返回 `HTTP Error 502: Bad Gateway`（POST /prompt 失败），
但 ComfyUI 本身健康：`curl http://127.0.0.1:8188/system_stats` 正常、`/queue` 为空。

## 判断

- GET 端点正常、POST /prompt 502 → 是 hermes-comfyui MCP 代理到 ComfyUI 的通路问题，**不是 ComfyUI 挂了**，也不是 workflow 校验失败。
- 直接改用 curl 提交即可，无需重启 ComfyUI、无需改 workflow。

## curl 直连提交流程（已验证）

1. **workflow JSON 写到 `$LOCALAPPDATA/Temp`（Windows 原生路径）**，不要写 `/tmp`：
   - MSYS 的 `/tmp` 对原生 curl 的 `-d @文件` 不可读（报 `curl: option -d: error encountered when reading a file`）。
   - 用 write_file 写 `C:/Users/<user>/AppData/Local/Temp/wf.json`，或 `$LOCALAPPDATA/Temp`。
2. 提交：
   ```bash
   curl -s -m 30 -w "\nHTTP_CODE:%{http_code}\n" -X POST http://127.0.0.1:8188/prompt \
     -H "Content-Type: application/json" --data-binary @"C:/Users/80704/AppData/Local/Temp/wf.json"
   ```
   - 成功返回 `{"prompt_id": "...", "number": N, "node_errors": {}}`，HTTP 200。
   - 注意外层要包 `{"prompt": {...API workflow...}}`。
3. 轮询结果（别轮询 /queue，队列判空不可靠；直接查 history）：
   ```bash
   curl -s "http://127.0.0.1:8188/history/<prompt_id>"
   ```
   - 出现 `"status"` 字段即完成；`outputs.<node>.images[].filename` 给出文件名。
4. 输出文件在 `E:\Comfy-Desktop\ComfyUI-Shared\output\`（按 filename_prefix 找），
   别信任何脚本/MCP 报告的拼接路径。

## 同参数模型对比出图（选型方法论）

- 用 comfy_build_txt2img 构建两个 workflow（只换 ckpt_name），**同 positive/negative、同 seed、同尺寸、同 steps/CFG/采样器**。
- 8GB 卡串行提交（ComfyUI 队列会自动排队），每张 896×1152/30 步约 40–70s。
- 判据：视觉模型质检（五官/手部/构图/细节）+ 社区共识结合，不要只看单张。

## 结果（2026-08-30 NoobAI vs Animagine）

- 同 seed 42 / 896×1152 / euler_ancestral / 30 步 / CFG 6：NoobAI-XL-v1.1 头发层次、服装细节、光影过渡更精细；
  animagine-xl-4.0 带场景氛围（蓝天白云）。两者均无手部畸形。
- 结论：本机二次元画像首选 **NoobAI-XL-v1.1**（danbooru 标签同系，提示词写法与 animagine 一致，可直接换模型）。
