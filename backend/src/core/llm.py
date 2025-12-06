import logging
from typing import Any, List, Optional, Iterator

import litellm
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, AIMessageChunk
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
from pydantic import Field

log = logging.getLogger(__name__)

# --- NEUCLID CHAT WRAPPER ---
class NeuclidChat(BaseChatModel):
    """
    A robust custom wrapper around `litellm.completion`.
    
    This class implements LangChain's BaseChatModel interface, making it
    compatible with the LangChain ecosystem.
    """
    model_name: str = Field(..., alias="model")
    """Model name in LiteLLM format (e.g., 'gemini/gemini-pro', 'gpt-4')."""
    
    temperature: float = 0.5
    """Model temperature to control creativity."""

    fallback_model_name: Optional[str] = None
    """Optional fallback model if the primary one fails."""

    class Config:
        """Configuration to allow 'model' alias."""
        populate_by_name = True

    @property
    def _llm_type(self) -> str:
        return "neuclid_chat_wrapper"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Main method calling LiteLLM.
        Converts LangChain messages to LiteLLM dicts, calls API, and converts back.
        """
        # 1. Convert LangChain messages to LiteLLM dicts
        message_dicts = []
        for msg in messages:
            role = "user" if msg.type == "human" else msg.type
            message_dicts.append({"role": role, "content": msg.content})

        # 2. Prepare arguments
        current_model = self.model_name
        litellm_kwargs = {
            "model": current_model,
            "messages": message_dicts,
            "temperature": self.temperature,
            **kwargs,
        }
        if stop:
            litellm_kwargs["stop"] = stop

        # 3. Call LiteLLM with robust error handling
        log.debug(f"Calling litellm.completion with: {litellm_kwargs}")
        
        try:
             response = litellm.completion(
                    **litellm_kwargs,
                    num_retries=3
                )
        except (litellm.InternalServerError, litellm.ServiceUnavailableError, litellm.RateLimitError) as e:
            log.warning(f"Error with primary model '{current_model}': {e}. Trying fallback.")
            if self.fallback_model_name:
                try:
                    log.info(f"Switching to fallback model: {self.fallback_model_name}")
                    response = litellm.completion(
                        model=self.fallback_model_name,
                        messages=message_dicts,
                        temperature=self.temperature,
                        stop=stop,
                        num_retries=5
                    )
                except Exception as fallback_e:
                    log.error(f"Fallback model also failed: {fallback_e}", exc_info=True)
                    raise fallback_e
            else:
                raise e
        except Exception as e:
             log.error(f"Unexpected error in litellm.completion: {e}", exc_info=True)
             raise e

        # 4. Validation
        if not response.choices or not response.choices[0].message or response.choices[0].message.content is None:
            finish_reason = response.choices[0].finish_reason if response.choices else "unknown"
            error_msg = f"LLM API response received but content is empty. Finish Reason: {finish_reason}"
            log.error(error_msg)
            raise ValueError(error_msg)
        
        # 5. Convert back to LangChain format
        content = response.choices[0].message.content
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])