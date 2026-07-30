#!/usr/bin/env python3
"""
orchestrate-feature.py: 全栈功能开发编排脚本
通过 Hermes CLI 执行完整的多 Agent 流水线
"""
import subprocess
import json
import sys


class HermesOrchestrator:
    def __init__(self, profile="orchestrator"):
        self.profile = profile

    def chat(self, prompt: str, profile: str = None) -> str:
        """发送消息到指定 Profile"""
        p = profile or self.profile
        result = subprocess.run(
            ["hermes", "chat", "-p", p, "-q", prompt],
            capture_output=True, text=True, timeout=600
        )
        return result.stdout

    def delegate(self, role: str, task: str, parallel: int = 1) -> str:
        """委派任务给临时子 Agent"""
        prompt = f"delegate_task(role='{role}', task='{task}', parallel={parallel})"
        return self.chat(prompt)

    def kanban_create(self, title: str, assignee: str, depends_on: list = None):
        """创建 Kanban 任务卡片"""
        deps = json.dumps(depends_on or [])
        prompt = f"创建看板任务: title='{title}', assignee='{assignee}', depends_on={deps}"
        return self.chat(prompt)

    def mcp_delegate(self, server: str, tool: str, **kwargs):
        """通过 MCP 委派给外部 Agent"""
        args = json.dumps(kwargs)
        prompt = f"调用 MCP server '{server}' 的工具 '{tool}'，参数: {args}"
        return self.chat(prompt)


# ===== 流水线编排 =====
if __name__ == "__main__":
    orch = HermesOrchestrator()

    feature = sys.argv[1] if len(sys.argv) > 1 else "用户认证模块"

    # Step 1: 研究
    print("📋 Phase 1: Research...")
    orch.kanban_create(f"调研: {feature}", "researcher")
    research_result = orch.chat(
        f"调研 {feature} 的最佳实践、常见架构、安全注意事项",
        profile="researcher"
    )

    # Step 2: 编码
    print("💻 Phase 2: Code...")
    orch.kanban_create(f"实现: {feature}", "coder", depends_on=["research"])
    code_result = orch.chat(
        f"基于以下调研结果实现 {feature}:\n{research_result}",
        profile="coder"
    )

    # Step 3: 审查
    print("🔍 Phase 3: Review...")
    orch.kanban_create(f"审查: {feature}", "reviewer", depends_on=["code"])
    review_result = orch.chat(
        f"审查以下代码实现:\n{code_result}",
        profile="reviewer"
    )

    # Step 4: 文档
    print("📝 Phase 4: Document...")
    orch.kanban_create(f"文档: {feature}", "documenter", depends_on=["review"])
    orch.chat(
        f"为 {feature} 编写 API 文档和使用说明",
        profile="documenter"
    )

    print("✅ 流水线完成")
