"""
Anthropic Claude LLM Provider Implementation.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

from .base import LLMProvider, LLMResponse, Message, ProviderType

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider implementation."""
    
    # Available Claude models
    AVAILABLE_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0",
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
        """Lazy load the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package is required for Anthropic provider. "
                    "Install it with: pip install anthropic"
                )
        return self._client
    
    def _get_async_client(self):
        """Lazy load the async Anthropic client."""
        if self._async_client is None:
            try:
                import anthropic
                self._async_client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package is required for Anthropic provider. "
                    "Install it with: pip install anthropic"
                )
        return self._async_client
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC
    
    @property
    def default_model(self) -> str:
        return "claude-3-5-sonnet-20241022"
    
    def _convert_messages_to_anthropic(self, messages: List[Message]) -> tuple:
        """Convert messages to Anthropic format."""
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return system_message, anthropic_messages
    
    def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request to Anthropic."""
        client = self._get_client()
        system_message, anthropic_messages = self._convert_messages_to_anthropic(messages)
        
        try:
            params = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
                **kwargs,
            }
            
            # Add system message if present
            if system_message:
                params["system"] = system_message
            
            response = client.messages.create(**params)
            
            # Extract content
            content = ""
            if response.content:
                # Claude returns content as list of blocks
                content = " ".join([
                    block.text for block in response.content 
                    if hasattr(block, 'text')
                ])
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider=self.provider_type,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def achat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async chat completion request to Anthropic."""
        client = self._get_async_client()
        system_message, anthropic_messages = self._convert_messages_to_anthropic(messages)
        
        try:
            params = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
                **kwargs,
            }
            
            # Add system message if present
            if system_message:
                params["system"] = system_message
            
            response = await client.messages.create(**params)
            
            # Extract content
            content = ""
            if response.content:
                # Claude returns content as list of blocks
                content = " ".join([
                    block.text for block in response.content 
                    if hasattr(block, 'text')
                ])
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider=self.provider_type,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Return list of available Anthropic models."""
        return self.AVAILABLE_MODELS.copy()
