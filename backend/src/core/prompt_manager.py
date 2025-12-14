import logging
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Template

log = logging.getLogger(__name__)

class PromptManager:
    """
    Centralized manager for LLM system prompts and templates.
    Uses Jinja2 for dynamic placeholder replacement.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        # Default to a global prompts directory if not provided
        self.templates_dir = templates_dir or Path(__file__).resolve().parent.parent.parent / "prompts"

    def load_template(self, template_path: Path, context: Dict[str, Any] = None) -> str:
        """
        Loads a file and renders it with the given context variables.
        """
        if not template_path.exists():
            log.error(f"Prompt template not found at: {template_path}")
            raise FileNotFoundError(f"Template {template_path} missing.")

        raw_content = template_path.read_text(encoding="utf-8")
        
        try:
            template = Template(raw_content)
            rendered = template.render(**(context or {}))
            return rendered
        except Exception as e:
            log.error(f"Failed to render prompt template {template_path}: {e}")
            raise ValueError(f"Prompt rendering error: {e}")

# Global instance
prompt_manager = PromptManager()