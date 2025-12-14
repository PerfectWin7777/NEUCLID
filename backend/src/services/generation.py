import logging
from src.core.router_tools import router_service
from src.core.registry import tool_registry
from src.core.base_tool import ToolResult

log = logging.getLogger(__name__)

class GenerationService:
    """
    Main entry point for the API.
    Orchestrates the flow: Prompt -> Router -> Tool -> Result.
    """
    
    async def generate(self, user_prompt: str) -> ToolResult:
        log.info("🚀 Starting Generation Workflow...")
        
        # 1. Ask the Router which tool to use
        tool_name = await router_service.route_request(user_prompt)
        log.info(f"🎯 Router selected: {tool_name}")

        # 2. Get the tool instance
        tool = tool_registry.get_tool(tool_name)

        # 3. Execute the tool
        try:
            result = await tool.run(user_prompt)
            log.info(f"✅ Generation successful via {tool_name}")
            return result
        except Exception as e:
            log.error(f"❌ Tool execution failed: {e}")
            raise e

# Singleton
generation_service = GenerationService()