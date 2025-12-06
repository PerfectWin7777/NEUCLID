import json
import re
import logging
from typing import Any, Dict, Union, Type, TypeVar
from pydantic import BaseModel, ValidationError
import json_repair

log = logging.getLogger(__name__)

# Generic type for Pydantic models
T = TypeVar("T", bound=BaseModel)

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Robustly extracts and parses JSON from a raw LLM string response.
    
    Strategies:
    1. Direct parsing (best case).
    2. Regex extraction of code blocks (```json ... ```).
    3. `json_repair` library (for missing quotes, trailing commas, etc.).
    """
    text = text.strip()
    
    # Strategy 1: The "Clean" attempt
    # Sometimes the LLM returns just the JSON.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass # Continue to Strategy 2

    # Strategy 2: Extract from Markdown Code Blocks
    # LLMs love to wrap JSON in ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass # Continue to Strategy 3 with the extracted string
    
    # Strategy 3: The "Heavy Lifter" (json_repair)
    # This library fixes trailing commas, missing quotes, comments, etc.
    try:
        # We try on the regex match if it existed, otherwise on the full text
        target_text = match.group(1) if match else text
        decoded = json_repair.loads(target_text)
        
        # Security check: json_repair sometimes returns a string if it fails hard
        if isinstance(decoded, (dict, list)):
            return decoded
        else:
            raise ValueError("Parsed result is not a JSON object or list.")
            
    except Exception as e:
        log.error(f"Failed to parse JSON from LLM output. Error: {e}")
        log.debug(f"Raw output causing failure: {text}")
        raise ValueError(f"CRITICAL: Could not extract valid JSON from LLM response. {e}")

def parse_llm_output_to_model(raw_text: str, model_class: Type[T]) -> T:
    """
    Helper that extracts JSON and immediately validates it against a Pydantic Model.
    This is the function you will use in your Service.
    """
    try:
        # 1. Get the dictionary
        data_dict = extract_json_from_text(raw_text)
        
        # 2. Validate with Pydantic
        return model_class.model_validate(data_dict)
        
    except ValidationError as ve:
        log.error(f"JSON Structure matches schema but data is invalid: {ve}")
        raise ve
    except Exception as e:
        raise e