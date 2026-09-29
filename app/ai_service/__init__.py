"""Agent 能力包：工具注册、绑定当前用户、接到问答。"""

from app.ai_service.runner import get_agent_runner, set_agent_runner
from app.ai_service.tools import register_builtin_tools

register_builtin_tools()

__all__ = ["get_agent_runner", "set_agent_runner"]
