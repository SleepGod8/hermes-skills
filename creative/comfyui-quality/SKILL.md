---
name: comfyui-quality
description: "Use when generating or debugging ComfyUI images. Compile prompts, select a compatible workflow/model, validate API-format graphs, and run a measurable quality loop through the Hermes ComfyUI MCP tools."
version: 1.0.0
author: Hermes workflow enhancement
license: MIT
platforms: [windows, linux, macos]
compatibility: "Requires a running local ComfyUI server and the hermes-comfyui MCP server; keep Hermes' bundled creative/comfyui skill for lifecycle, video, and audio workflows."
metadata:
  hermes:
    tags: [comfyui, image-generation, workflow-quality, stable-diffusion, sdxl, prompt-engineering]
    related_skills: [comfyui]
    category: creative
---

# ComfyUI Quality

把图像生成当作“需求编译 → 工作流验证 → 低成本试跑 → 质量提升 → 输出回收”的闭环。本 skill 与 Hermes 自带的 `creative/comfyui` 互补：自带 skill 负责安装、生命周期、视频/音频和通用 REST 脚本；本 skill 负责图像质量决策和 MCP 质量门槛。

## 每次请求的执行顺序

1. **澄清可执行规格**：提取主体、动作、场景、构图、镜头/焦段、材质、光线、色彩、风格、输出尺寸、数量和是否需要文字。缺失时使用 `balanced` 预设，并在结果中报告假设。
2. **检查运行时**：先调用 `comfy_server_info`；若服务不可达，报告需要启动 ComfyUI，不要伪造成功。再调用 `comfy_inventory` 或 `comfy_search_nodes`，确认 checkpoint、VAE、LoRA 和节点实际存在。
3. **选择工作流策略**：
   - SD1.5/SDXL 且只有核心节点：调用 `comfy_build_txt2img`，使用兼容的 `CheckpointLoaderSimple → CLIPTextEncode(正/负) → EmptyLatentImage → KSampler → VAEDecode → SaveImage`。
   - 需要 Flux、SD3、ControlNet、IP-Adapter、参考图或复杂 LoRA：先查模板/现有 workflow，再进行最小修改；不要把 SDXL 的节点图强行套用到其它架构。
   - 用户给出 workflow JSON：保留图结构，只替换明确允许的输入；先 `comfy_validate_workflow`，再运行。
4. **编译提示词**：使用短语和英文逗号分隔；先主体与数量，再动作/姿态，再环境与构图，再镜头/光线/材质，最后风格与质量。把用户明确禁止的内容放入负面提示词。只在模型支持时使用权重（如 `(detail:1.15)`），不要堆叠互相冲突的风格词。
5. **先小后大**：用一个 seed 进行 composition check；构图、主体数量和手部/脸部明显错误时先修 prompt、模型或条件，不能靠盲目增加 steps 补救。通过后才启用二阶段 latent upscale 或专用 upscaler。
6. **提交并回收**：调用 `comfy_run_workflow`，等待完成并将输出复制到用户指定目录。返回 prompt id、seed、模型、尺寸、采样器、steps、CFG、输出路径和任何 warning。
7. **质量门槛**：至少检查任务成功、输出文件存在且可读、分辨率正确、workflow 无缺失节点/模型；若能看到图像，检查主体数量、裁切、明显解剖错误、文字可读性和过度锐化。失败时给出下一次只改 1–2 个变量的建议。

## 默认质量预设

| 预设 | 首次尺寸 | steps | CFG | 采样器/调度器 | 二阶段 |
| --- | --- | ---: | ---: | --- | --- |
| `draft` | 512（SD1.5）/768（SDXL） | 16 | 5.5 | `dpmpp_2m` / `karras` | 否 |
| `balanced` | 512（SD1.5）/1024（SDXL） | 24 | 6.5 | `dpmpp_2m` / `karras` | 可选 |
| `quality` | 768（SD1.5）/1024（SDXL） | 32 | 6.5 | `dpmpp_2m_sde` / `karras` | 1.35x，denoise 0.28 |

这些是起点，不是普适真值。以本地 workflow/template 和模型说明为准。SD1.5 不要默认生成 1024；低显存先用 `draft` 或关闭二阶段。

## MCP 工具使用约定

- `comfy_server_info()`：每个新会话首次调用。
- `comfy_inventory(kind)`：`kind` 可为 `models`、`nodes`、`all`；只选择返回清单里的名称。
- `comfy_workflow_summary(workflow)`：在修改已有 workflow 前先读取它的模型、提示词、采样器、尺寸和输出节点。
- `comfy_patch_workflow(workflow, ...)`：只替换正/负面提示词、seed、steps、CFG、采样器、尺寸等常见旋钮，保留 ControlNet/LoRA/参考图的图结构。
- `comfy_build_txt2img(...)`：仅用于支持的 checkpoint 家族；返回 API-format prompt JSON 和可审计的参数摘要，不自动提交。
- `comfy_validate_workflow(workflow, strict=true)`：提交前必调。检查节点类、连线引用、模型名、尺寸、seed、steps/CFG 范围，以及 SaveImage 输出节点。
- `comfy_run_workflow(workflow, wait=true, output_dir=...)`：只运行已校验的 JSON；轮询 history，收集所有图片输出。不要把 base64 图片塞进对话，返回路径。
- `comfy_get_outputs(prompt_id, output_dir)`：异步任务完成后调用。

只把 MCP 工具用于当前请求需要的能力。读操作（探测/搜索/校验）可以连续执行；生成和文件写入必须在 workflow 校验通过后执行。

## 失败处理

- `null` checkpoint、找不到节点或 `Prompt outputs failed validation`：先刷新/重新探测 inventory，再修 workflow。
- 显存不足：降低尺寸/批量和二阶段，必要时改用现有模板；不要静默改变用户比例。
- 生成“质量不好”：按顺序检查模型家族与 VAE、尺寸/比例、提示词结构、采样器/调度器、seed，再考虑 LoRA/ControlNet 或二阶段放大。
- 文字、手指、复杂角色数量等结构性问题不能承诺一次解决；输出失败原因和下一次实验变量。

## 完成标准

生成任务只有同时满足以下条件才算完成：ComfyUI 返回成功状态；至少一个输出文件已下载且位于目标目录内；输出分辨率与请求一致；workflow 参数摘要、seed 和 prompt id 已记录；若校验有 warning，已向用户说明。

## 参考资料

- 详细节点与 API 兼容性规则：见 `references/quality-playbook.md`。
- 官方工作流/本地 MCP 配置：见 `references/sources.md`。
