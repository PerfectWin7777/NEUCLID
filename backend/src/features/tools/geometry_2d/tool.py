import logging
from pathlib import Path
from typing import Type

from langchain_core.messages import SystemMessage, HumanMessage

from src.core.base_tool import BaseTool, ToolResult
from src.core.llm import NeuclidChat
from src.core.prompt_manager import prompt_manager
from src.utils.parser import parse_llm_output_to_model

# Local feature imports
from .models import Geometry2DInput
from .translator import generate_geometry_2d # We assume this function returns image path AND code ideally

log = logging.getLogger(__name__)

class Geometry2DTool(BaseTool):
    def __init__(self):
        self.llm = NeuclidChat(model="gemini/gemini-2.5-flash", temperature=0.1)
        # Define path to the specific guide for this tool
        self.guide_path = Path(__file__).parent / "guide.md"

    @property
    def name(self) -> str:
        return "geometry_2d"

    @property
    def description(self) -> str:
        return (
            "Constructs complex 2D Euclidean geometry figures. "
            "Use for: triangles, circles, lines, angles, polygons, intersections. "
            "Do NOT use for function plots or data charts."
        )

    @property
    def input_model(self) -> Type[Geometry2DInput]:
        return Geometry2DInput

    async def run(self, user_prompt: str) -> ToolResult:
        log.info(f"[{self.name}] Processing: {user_prompt}")

        # 1. Load System Context via PromptManager
        # We read the raw guide content to inject into the system prompt
        guide_content = prompt_manager.load_template(self.guide_path)
        
        system_msg = (
            "### ROLE\n"
            "You are Neuclid, the world's most advanced Geometry AI Agent. "
            "Your goal is to translate natural language requests into a precise, sequential JSON construction plan.\n\n"
            
            "### KNOWLEDGE BASE (THE TOOLS)\n"
            "You have access to a specific library of geometric actions. "
            "You must ONLY use the actions defined in the documentation below:\n"
            f"{guide_content}\n\n"

            "### CRITICAL RULES (MUST FOLLOW)\n"
            "1. **Sequential Logic**: You cannot use a point (e.g., 'C') in a command if it hasn't been defined in a previous step.\n"
            "2. **Implicit Creation**: If the user says 'Draw triangle ABC', you must first DEFINE points A, B, and C (via coords or relative position) before DRAWING the polygon.\n"
            "3. **No Hallucinations**: Do not invent properties or tool types that are not in the documentation.\n"
            "4. **Output Format**: Return ONLY valid JSON matching the `Geometry2DInput` schema. No Markdown text before or after.\n"
            "5. **Coordinates**: If no coordinates are specified, infer logical, centered coordinates (e.g., A at 0,0, B at 5,0).\n\n"
            
            "### THINKING PROCESS\n"
            "Before generating the JSON, think step-by-step:\n"
            "- Extract all objects mentioned (Points, Lines, Circles).\n"
            "- Determine the order of construction (Dependencies first).\n"
            "- Select the correct tool 'type' for each step.\n"
        )

        # 2. LLM Generation
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)

        # 3. Parse JSON
        data_model: Geometry2DInput = parse_llm_output_to_model(response.content, Geometry2DInput)

        # 4. Generate Figure (Translator)
        # Note: You might need to update `generate_geometry_2d` to return the LaTeX code string too.
        # For now, let's assume it returns the path, and we reconstruct/fetch code differently if needed.
        image_path, latex_code = generate_geometry_2d(
            input_data=data_model,
            show_axes=data_model.figure_config.axes,
            show_grid=data_model.figure_config.grid
        )
        json_dict = data_model.model_dump()

        return ToolResult(
            image_url=image_path.name, # On met juste le nom ici, l'API ajoutera "http://localhost..."
            latex_code=latex_code,
            json_content=json_dict,
            tool_name=self.name,
            metadata={
                "steps_count": len(data_model.construction_steps),
                "model_used": self.llm.model_name
            }
        )