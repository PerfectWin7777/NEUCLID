import logging
from pathlib import Path

# LangChain imports for message structuring
from langchain_core.messages import SystemMessage, HumanMessage

# Internal modules
from src.config import settings
from src.core.llm import NeuclidChat
from src.utils.parser import parse_llm_output_to_model
from src.features.geometry.models import Geometry2DInput
from src.features.geometry.translator import generate_geometry_2d

log = logging.getLogger(__name__)

class GeometryService:
    """
    Orchestrates the generation of 2D Geometry figures from natural language.
    Process: User Prompt -> LLM -> JSON -> Validation -> LaTeX -> Image.
    """

    def __init__(self):
        # We initialize the LLM with a low temperature (0.1) because we need 
        # precise JSON structure, not creative poetry.
        # TODO: Make the model configurable via .env (e.g., gemini-1.5-flash for speed)
        self.llm = NeuclidChat(model="gemini/gemini-2.5-flash", temperature=0.1)
        
        # Path to the "Tool Guide" (your documentation)
        self.prompts_dir = Path(__file__).parent / "prompts"
        self.guide_filename = "tool_guide.md"

    def _load_system_context(self) -> str:
        """
        Loads the 'Brain' of the tool: the documentation explaining how to use the JSON tools.
        """
        guide_path = self.prompts_dir / self.guide_filename
        
        if not guide_path.exists():
            error_msg = f"Critical Error: The tool guide was not found at {guide_path}"
            log.error(error_msg)
            raise FileNotFoundError(error_msg)

        guide_content = guide_path.read_text(encoding="utf-8")

        # We construct a strict System Prompt
        system_prompt = (
            "You are Neuclid, an expert AI in Geometry and LaTeX construction.\n"
            "Your mission is to convert the user's natural language description into a "
            "precise JSON structure matching the `Geometry2DInput` schema.\n\n"
            "### YOUR TOOLBOX (DOCUMENTATION)\n"
            f"{guide_content}\n\n"
            "### CRITICAL RULES\n"
            "1. You must ONLY output valid JSON. No Markdown, no explanations before/after.\n"
            "2. Respect the sequential logic: Define points BEFORE using them.\n"
            "3. Use the exact types defined in the documentation (e.g., 'def_point_coords', 'draw_segments').\n"
        )
        return system_prompt

    async def generate_figure_from_text(self, user_prompt: str) -> Path:
        """
        Main pipeline: Text -> Image Path.
        """
        log.info(f"GeometryService: Processing request -> '{user_prompt}'")

        # 1. Prepare the Prompt
        system_msg = self._load_system_context()
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=user_prompt)
        ]

        # 2. Call the LLM
        # The wrapper handles retries and basic errors
        ai_response = self.llm.invoke(messages)
        raw_content = ai_response.content
        
        log.info(f"LLM Raw Output:\n{raw_content[:200]}...") # Log first 200 chars

        # 3. Parse and Validate JSON
        # This step is crucial. It uses our robust parser to fix common LLM mistakes.
        # If this passes, we are 99% sure the image generation will work.
        try:
            geometry_data: Geometry2DInput = parse_llm_output_to_model(
                raw_text=raw_content, 
                model_class=Geometry2DInput
            )
            log.info("JSON successfully parsed and validated against Pydantic schema.")
        except Exception as e:
            log.error(f"Failed to parse LLM output: {e}")
            raise ValueError("The AI failed to generate a valid geometry configuration.") from e

        # 4. Translate to Image (LaTeX Compilation)
        try:
            # We set show_axes/grid to False by default, or we could infer it from the prompt later
            image_path = generate_geometry_2d(
                input_data=geometry_data,
                show_axes=geometry_data.figure_config.axes, # Uses the LLM's decision
                show_grid=geometry_data.figure_config.grid
            )
            log.info(f"Figure generated successfully: {image_path}")
            return image_path
            
        except Exception as e:
            log.error(f"Error during image generation: {e}")
            raise RuntimeError("The geometry engine failed to render the image.") from e

# Singleton instance for easy import
geometry_service = GeometryService()