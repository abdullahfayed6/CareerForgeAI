"""
Google Gemini LLM Provider Implementation.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

from .base import LLMProvider, LLMResponse, Message, ProviderType

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini API provider implementation."""
    
    # Available Gemini models
    AVAILABLE_MODELS = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
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
        self._model_instance = None
    
    def _get_client(self):
        """Lazy load the Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                raise ImportError(
                    "google-generativeai package is required for Gemini provider. "
                    "Install it with: pip install google-generativeai"
                )
        return self._client
    
    def _get_model(self):
        """Get or create the model instance."""
        if self._model_instance is None or self._model_instance.model_name != self.model:
            genai = self._get_client()
            self._model_instance = genai.GenerativeModel(self.model)
        return self._model_instance
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GEMINI
    
    @property
    def default_model(self) -> str:
        return "gemini-2.0-flash"
    
    def _convert_messages_to_gemini(self, messages: List[Message]) -> tuple:
        """Convert messages to Gemini format."""
        system_instruction = None
        history = []
        current_content = None
        
        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "user":
                current_content = msg.content
            elif msg.role == "assistant":
                # Add to history for multi-turn conversations
                if current_content:
                    history.append({"role": "user", "parts": [current_content]})
                    history.append({"role": "model", "parts": [msg.content]})
                    current_content = None
        
        return system_instruction, history, current_content or messages[-1].content
    
    def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request to Gemini."""
        genai = self._get_client()
        system_instruction, history, current_input = self._convert_messages_to_gemini(messages)
        
        # Create model with system instruction if provided
        generation_config = genai.types.GenerationConfig(
            temperature=temperature or self.temperature,
            max_output_tokens=max_tokens or self.max_tokens,
        )
        
        model = genai.GenerativeModel(
            self.model,
            system_instruction=system_instruction,
            generation_config=generation_config,
        )
        
        try:
            # Start chat with history if available
            chat = model.start_chat(history=history) if history else model.start_chat()
            response = chat.send_message(current_input)
            
            # Extract usage metadata
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                provider=self.provider_type,
                usage=usage,
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    async def achat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async chat completion request to Gemini."""
        genai = self._get_client()
        system_instruction, history, current_input = self._convert_messages_to_gemini(messages)
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature or self.temperature,
            max_output_tokens=max_tokens or self.max_tokens,
        )
        
        model = genai.GenerativeModel(
            self.model,
            system_instruction=system_instruction,
            generation_config=generation_config,
        )
        
        try:
            chat = model.start_chat(history=history) if history else model.start_chat()
            response = await chat.send_message_async(current_input)
            
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                provider=self.provider_type,
                usage=usage,
                raw_response=response,
            )
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Return list of available Gemini models."""
        return self.AVAILABLE_MODELS.copy()
