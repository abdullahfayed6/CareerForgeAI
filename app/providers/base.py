"""
Base LLM Provider Interface.
Defines the contract that all LLM providers must implement.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderType(str, Enum):
    """Supported LLM provider types."""
    OPENAI = "openai"
    GEMINI = "gemini"
    GROQ = "groq"
    
    @classmethod
    def from_string(cls, value: str) -> "ProviderType":
        """Convert string to ProviderType, case-insensitive."""
        value_lower = value.lower()
        for provider in cls:
            if provider.value == value_lower:
                return provider
        raise ValueError(f"Unknown provider: {value}. Supported: {[p.value for p in cls]}")


@dataclass
class LLMResponse:
    """Standardized response from LLM providers."""
    content: str
    model: str
    provider: ProviderType
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Any = None
    
    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return self.usage.get("total_tokens", 0)


@dataclass
class Message:
    """A chat message."""
    role: str  # "system", "user", "assistant"
    content: str


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    All providers must implement these methods.
    """
    
    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        self.api_key = api_key
        self._model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type."""
        pass
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model for this provider."""
        pass
    
    @property
    def model(self) -> str:
        """Return the model to use."""
        return self._model or self.default_model
    
    @model.setter
    def model(self, value: str) -> None:
        """Set the model to use."""
        self._model = value
    
    @abstractmethod
    def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Send a chat completion request.
        
        Args:
            messages: List of Message objects
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Provider-specific options
            
        Returns:
            LLMResponse with the completion
        """
        pass
    
    @abstractmethod
    async def achat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async version of chat."""
        pass
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Simple completion with a single prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            LLMResponse with the completion
        """
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))
        
        return self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
    
    async def acomplete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async version of complete."""
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))
        
        return await self.achat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of available models for this provider."""
        pass
    
    def validate_model(self, model: str) -> bool:
        """Check if a model is available for this provider."""
        return model in self.get_available_models()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"
