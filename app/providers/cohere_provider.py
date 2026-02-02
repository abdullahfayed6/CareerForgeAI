"""
Cohere LLM Provider Implementation.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

from .base import LLMProvider, LLMResponse, Message, ProviderType

logger = logging.getLogger(__name__)


class CohereProvider(LLMProvider):
    """Cohere API provider implementation."""
    
    # Available Cohere models
    AVAILABLE_MODELS = [
        "command-r-plus",
        "command-r",
        "command",
        "command-light",
        "command-nightly",
        "command-light-nightly",
    ]
    
    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        super().__init__(api_key, model, temperature, max_tokens)
        self._client = None
        self._async_client = None
    
    def _get_client(self):
        """Lazy load the Cohere client."""
        if self._client is None:
            try:
                import cohere
                self._client = cohere.Client(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "cohere package is required for Cohere provider. "
                    "Install it with: pip install cohere"
                )
        return self._client
    
    def _get_async_client(self):
        """Lazy load the async Cohere client."""
        if self._async_client is None:
            try:
                import cohere
                self._async_client = cohere.AsyncClient(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "cohere package is required for Cohere provider. "
                    "Install it with: pip install cohere"
                )
        return self._async_client
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.COHERE
    
    @property
    def default_model(self) -> str:
        return "command-r"
    
    def _convert_messages_to_cohere(self, messages: List[Message]) -> tuple:
        """Convert messages to Cohere format."""
        system_message = None
        chat_history = []
        current_message = None
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            elif msg.role == "user":
                current_message = msg.content
            elif msg.role == "assistant":
                if current_message:
                    chat_history.append({
                        "role": "USER",
                        "message": current_message
                    })
                chat_history.append({
                    "role": "CHATBOT",
                    "message": msg.content
                })
                current_message = None
        
        # If last message is user message, it becomes the current query
        if messages and messages[-1].role == "user":
            current_message = messages[-1].content
        
        return system_message, chat_history, current_message
    
    def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request to Cohere."""
        client = self._get_client()
        system_message, chat_history, message = self._convert_messages_to_cohere(messages)
        
        try:
            response = client.chat(
                model=self.model,
                message=message or "",
                chat_history=chat_history if chat_history else None,
                preamble=system_message,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs,
            )
            
            # Extract usage info if available
            usage = {}
            if hasattr(response, 'meta') and response.meta:
                billed_units = response.meta.billed_units
                if billed_units:
                    usage = {
                        "prompt_tokens": getattr(billed_units, 'input_tokens', 0),
                        "completion_tokens": getattr(billed_units, 'output_tokens', 0),
                        "total_tokens": getattr(billed_units, 'input_tokens', 0) + 
                                      getattr(billed_units, 'output_tokens', 0),
                    }
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                provider=self.provider_type,
                usage=usage,
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            raise
    
    async def achat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async chat completion request to Cohere."""
        client = self._get_async_client()
        system_message, chat_history, message = self._convert_messages_to_cohere(messages)
        
        try:
            response = await client.chat(
                model=self.model,
                message=message or "",
                chat_history=chat_history if chat_history else None,
                preamble=system_message,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs,
            )
            
            # Extract usage info if available
            usage = {}
            if hasattr(response, 'meta') and response.meta:
                billed_units = response.meta.billed_units
                if billed_units:
                    usage = {
                        "prompt_tokens": getattr(billed_units, 'input_tokens', 0),
                        "completion_tokens": getattr(billed_units, 'output_tokens', 0),
                        "total_tokens": getattr(billed_units, 'input_tokens', 0) + 
                                      getattr(billed_units, 'output_tokens', 0),
                    }
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                provider=self.provider_type,
                usage=usage,
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Return list of available Cohere models."""
        return self.AVAILABLE_MODELS.copy()
