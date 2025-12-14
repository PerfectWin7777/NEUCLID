import logging
from typing import Dict, List, Type
from src.core.base_tool import BaseTool

log = logging.getLogger(__name__)

class ToolRegistry:
    """
    Singleton that holds all available tools.
    The Router will query this to know what it can do.
    """
    _instance = None
    _tools: Dict[str, BaseTool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
        return cls._instance

    def register(self, tool: BaseTool):
        """Registers a new tool instance."""
        if tool.name in self._tools:
            log.warning(f"Tool '{tool.name}' is being overwritten.")
        
        self._tools[tool.name] = tool
        log.info(f"✅ Tool registered: {tool.name}")

    def get_tool(self, name: str) -> BaseTool:
        """Retrieves a tool by name."""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return tool

    def get_all_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_descriptions_for_router(self) -> str:
        """
        Generates the text block for the Router LLM, describing available tools.
        """
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(f"- '{tool.name}': {tool.description}")
        return "\n".join(descriptions)

# Global instance
tool_registry = ToolRegistry()