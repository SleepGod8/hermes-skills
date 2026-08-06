# Sources

- https://docs.comfy.org/zh/get_started/first_generation
- https://docs.comfy.org/zh/development/core-concepts/workflow
- https://docs.comfy.org/zh/built-in-nodes/overview
- https://docs.comfy.org/tutorials/basic/text-to-image
- https://docs.comfy.org/zh/agent-tools/local
- https://docs.comfy.org/zh/agent-tools/mcp
- https://comfyui-wiki.com/zh
- https://github.com/ZHO-ZHO-ZHO/ComfyUI-Workflows-ZHO

参考要点：官方文档把 workflow 定义为节点图，工作流 JSON 可保存/版本控制；本地 MCP 的核心循环为 `server_info → run_workflow → fetch_outputs`，并可查询实际节点与模型；ZHO 工作流合集覆盖 Flux、SD3、Stable Cascade、ControlNet、IP/参考图等多模型路线，因此 Hermes 应按模型家族选模板，而不是单一 KSampler 模板。
