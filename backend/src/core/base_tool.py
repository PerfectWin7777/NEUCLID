from abc import ABC, abstractmethod
from typing import Type, Any, Dict, Optional
from pathlib import Path
from pydantic import BaseModel, Field

# --- Standardized Result for ANY tool ---
class ToolResult(BaseModel):
    """
    Standard output for all tools. 
    Frontend will always receive this structure, no matter the tool used.
    """
    tool_name: str
    image_url: Path
    latex_code: str = ""
    json_content: Dict[str, Any] # Le JSON intermédiaire (Geometry2DInput)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# --- The Contract ---
class BaseTool(ABC):
    """
    Abstract Base Class that all Neuro-Symbolic tools must implement.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the tool (e.g., 'geometry_2d', 'function_plotter')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Short description used by the LLM Router to decide when to use this tool.
        Example: 'Draws 2D Euclidean geometry figures like triangles, circles...'
        """
        pass

    @property
    @abstractmethod
    def input_model(self) -> Type[BaseModel]:
        """Returns the Pydantic model class used to validate the LLM's JSON output."""
        pass

    @abstractmethod
    async def run(self, user_prompt: str, context: Optional[Dict] = None) -> ToolResult:
        """
        The main execution logic:
        Prompt -> LLM (Specific) -> JSON -> Validation -> LaTeX -> Image
        """
        pass