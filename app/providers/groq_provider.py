"""
Groq LLM Provider Implementation.
Groq provides ultra-fast inference for various open-source models.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

from .base import LLMProvider, LLMResponse, Message, ProviderType

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """Groq API provider implementation."""
    
    # Available Groq models (as of 2024)
    AVAILABLE_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "gemma-7b-it",
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
        """Lazy load the Groq client."""
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "groq package is required for Groq provider. "
                    "Install it with: pip install groq"
                )
        return self._client
    
    def _get_async_client(self):
        """Lazy load the async Groq client."""
        if self._async_client is None:
            try:
                from groq import AsyncGroq
                self._async_client = AsyncGroq(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "groq package is required for Groq provider. "
                    "Install it with: pip install groq"
                )
        return self._async_client
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GROQ
    
    @property
    def default_model(self) -> str:
        return "llama-3.3-70b-versatile"
    
    def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request to Groq."""
        client = self._get_client()
        
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs,
            )
            
            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                provider=self.provider_type,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    async def achat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async chat completion request to Groq."""
        client = self._get_async_client()
        
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs,
            )
            
            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                provider=self.provider_type,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Return list of available Groq models."""
        return self.AVAILABLE_MODELS.copy()
