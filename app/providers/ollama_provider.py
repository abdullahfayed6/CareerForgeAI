"""
Ollama LLM Provider Implementation.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

from .base import LLMProvider, LLMResponse, Message, ProviderType

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider implementation."""
    
    # Common Ollama models (user can have any installed)
    AVAILABLE_MODELS = [
        "llama3.2",
        "llama3.1",
        "llama3",
        "llama2",
        "mistral",
        "mixtral",
        "phi3",
        "gemma2",
        "codellama",
        "qwen2.5",
        "deepseek-coder",
        "neural-chat",
        "starling-lm",
    ]
    
    def __init__(
        self,
        api_key: str = "",  # Not needed for Ollama
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        base_url: str = "http://localhost:11434",
    ):
        super().__init__(api_key, model, temperature, max_tokens)
        self.base_url = base_url
        self._client = None
        self._async_client = None
    
    def _get_client(self):
        """Lazy load the Ollama client."""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.base_url)
            except ImportError:
                raise ImportError(
                    "ollama package is required for Ollama provider. "
                    "Install it with: pip install ollama"
                )
        return self._client
    
    def _get_async_client(self):
        """Lazy load the async Ollama client."""
        if self._async_client is None:
            try:
                import ollama
                self._async_client = ollama.AsyncClient(host=self.base_url)
            except ImportError:
                raise ImportError(
                    "ollama package is required for Ollama provider. "
                    "Install it with: pip install ollama"
                )
        return self._async_client
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OLLAMA
    
    @property
    def default_model(self) -> str:
        return "llama3.2"
    
    def _convert_messages_to_ollama(self, messages: List[Message]) -> List[dict]:
        """Convert messages to Ollama format."""
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
        """Send a chat completion request to Ollama."""
        client = self._get_client()
        ollama_messages = self._convert_messages_to_ollama(messages)
        
        try:
            options = {
                "temperature": temperature or self.temperature,
                "num_predict": max_tokens or self.max_tokens,
            }
            
            response = client.chat(
                model=self.model,
                messages=ollama_messages,
                options=options,
                **kwargs,
            )
            
            # Extract usage info if available
            usage = {}
            if hasattr(response, 'prompt_eval_count') and hasattr(response, 'eval_count'):
                usage = {
                    "prompt_tokens": response.prompt_eval_count or 0,
                    "completion_tokens": response.eval_count or 0,
                    "total_tokens": (response.prompt_eval_count or 0) + (response.eval_count or 0),
                }
            
            return LLMResponse(
                content=response['message']['content'] if isinstance(response, dict) else response.message.content,
                model=self.model,
                provider=self.provider_type,
                usage=usage,
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def achat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async chat completion request to Ollama."""
        client = self._get_async_client()
        ollama_messages = self._convert_messages_to_ollama(messages)
        
        try:
            options = {
                "temperature": temperature or self.temperature,
                "num_predict": max_tokens or self.max_tokens,
            }
            
            response = await client.chat(
                model=self.model,
                messages=ollama_messages,
                options=options,
                **kwargs,
            )
            
            # Extract usage info if available
            usage = {}
            if hasattr(response, 'prompt_eval_count') and hasattr(response, 'eval_count'):
                usage = {
                    "prompt_tokens": response.prompt_eval_count or 0,
                    "completion_tokens": response.eval_count or 0,
                    "total_tokens": (response.prompt_eval_count or 0) + (response.eval_count or 0),
                }
            
            return LLMResponse(
                content=response['message']['content'] if isinstance(response, dict) else response.message.content,
                model=self.model,
                provider=self.provider_type,
                usage=usage,
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Return list of commonly available Ollama models."""
        # Try to get actual installed models
        try:
            client = self._get_client()
            models_response = client.list()
            if models_response and 'models' in models_response:
                return [model['name'] for model in models_response['models']]
        except Exception as e:
            logger.warning(f"Could not fetch Ollama models: {e}")
        
        # Fallback to common models
        return self.AVAILABLE_MODELS.copy()
