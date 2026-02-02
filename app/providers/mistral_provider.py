"""
Mistral AI LLM Provider Implementation.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

from .base import LLMProvider, LLMResponse, Message, ProviderType

logger = logging.getLogger(__name__)


class MistralProvider(LLMProvider):
    """Mistral AI API provider implementation."""
    
    # Available Mistral models
    AVAILABLE_MODELS = [
        "mistral-large-latest",
        "mistral-medium-latest",
        "mistral-small-latest",
        "mistral-tiny",
        "open-mistral-7b",
        "open-mixtral-8x7b",
        "open-mixtral-8x22b",
        "codestral-latest",
        "ministral-8b-latest",
        "ministral-3b-latest",
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
        """Lazy load the Mistral client."""
        if self._client is None:
            try:
                from mistralai import Mistral
                self._client = Mistral(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "mistralai package is required for Mistral provider. "
                    "Install it with: pip install mistralai"
                )
        return self._client
    
    def _get_async_client(self):
        """Lazy load the async Mistral client."""
        if self._async_client is None:
            try:
                from mistralai import Mistral
                self._async_client = Mistral(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "mistralai package is required for Mistral provider. "
                    "Install it with: pip install mistralai"
                )
        return self._async_client
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.MISTRAL
    
    @property
    def default_model(self) -> str:
        return "mistral-small-latest"
    
    def _convert_messages_to_mistral(self, messages: List[Message]) -> List[dict]:
        """Convert messages to Mistral format."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request to Mistral."""
        client = self._get_client()
        mistral_messages = self._convert_messages_to_mistral(messages)
        
        try:
            response = client.chat.complete(
                model=self.model,
                messages=mistral_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs,
            )
            
            # Extract content
            content = ""
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content or ""
            
            # Extract usage info
            usage = {}
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider=self.provider_type,
                usage=usage,
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            raise
    
    async def achat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async chat completion request to Mistral."""
        client = self._get_async_client()
        mistral_messages = self._convert_messages_to_mistral(messages)
        
        try:
            response = await client.chat.complete_async(
                model=self.model,
                messages=mistral_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs,
            )
            
            # Extract content
            content = ""
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content or ""
            
            # Extract usage info
            usage = {}
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider=self.provider_type,
                usage=usage,
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Return list of available Mistral models."""
        return self.AVAILABLE_MODELS.copy()
