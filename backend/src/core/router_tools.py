import logging
import json
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from src.core.llm import NeuclidChat
from src.core.registry import tool_registry

log = logging.getLogger(__name__)

# --- Router Output Schema ---
class RouterDecision(BaseModel):
    """Structured decision from the Router LLM."""
    reasoning: str = Field(..., description="Explain why this tool was chosen based on the user prompt.")
    tool_name: str = Field(..., description="The exact name of the tool to use.")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0.")

class RouterService:
    def __init__(self):
        # We use a fast, smart model for routing (e.g., Gemini Flash or GPT-4o-mini)
        self.llm = NeuclidChat(model="gemini/gemini-2.5-flash-lite", temperature=0.0)

    async def route_request(self, user_prompt: str) -> str:
        """
        Analyzes the prompt and returns the name of the tool to use.
        """
        # 1. Get available tools dynamically
        tools_description = tool_registry.get_descriptions_for_router()

        # On demande à Pydantic : "Donne-moi le plan de la classe RouterDecision en JSON"
        schema_dict = RouterDecision.model_json_schema()
        
        # On le convertit en une belle chaîne de caractères lisible
        schema_str = json.dumps(schema_dict, indent=2)
        
        # 2. Build System Prompt (Hardcoded here for safety, but could use PromptManager)
        system_prompt = (
            "You are the Orchestrator for the Neuclid Scientific Platform.\n"
            "Your job is to analyze the user's request and select the single best tool to execute it.\n\n"
            "### AVAILABLE TOOLS\n"
            f"{tools_description}\n\n"
            "### OUTPUT FORMAT RULES\n"
            "You must strictly output a JSON object that matches this schema:\n"
            f"```json\n{schema_str}\n```\n\n"
            "### INSTRUCTIONS\n"
            "1. Analyze the user's intent carefully.\n"
            "2. Select the tool_name that best fits.\n"
            "3. If the request is ambiguous, choose the most likely one based on keywords.\n"
            "4. Return a JSON object matching the RouterDecision schema."
        )

        # 3. Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # 4. Parse 
        from src.utils.parser import parse_llm_output_to_model
        
        try:
            decision = parse_llm_output_to_model(response.content, RouterDecision)
            log.info(f"Router Decision: {decision.tool_name} (Confidence: {decision.confidence})")
            
            # Verify tool exists
            try:
                tool_registry.get_tool(decision.tool_name)
                return decision.tool_name
            except ValueError:
                log.error(f"Router hallucinated a tool name: {decision.tool_name}")
                # Fallback mechanism could go here
                raise ValueError(f"Router selected non-existent tool: {decision.tool_name}")

        except Exception as e:
            log.error(f"Routing failed: {e}")
            raise e

router_service = RouterService()