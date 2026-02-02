"""
Provider Factory.
Creates and manages LLM provider instances.
"""
from __future__ import annotations

import logging
from typing import Optional, Union

from app.config import settings

from .base import LLMProvider, ProviderType
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from .cohere_provider import CohereProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider
from .mistral_provider import MistralProvider

logger = logging.getLogger(__name__)


def get_provider(
    provider_type: Optional[Union[str, ProviderType]] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    api_key: Optional[str] = None,
) -> LLMProvider:
    """
    Factory function to get an LLM provider.
    
    Args:
        provider_type: The provider to use. If None, uses settings.llm_provider
        model: The model to use. If None, uses provider default
        temperature: Temperature for generation
        max_tokens: Maximum tokens for generation
        api_key: API key override. If None, uses settings
        
    Returns:
        An LLMProvider instance
        
    Raises:
        ValueError: If provider is unknown or API key is missing
    """
    # Determine provider type
    if provider_type is None:
        provider_type = settings.llm_provider
    
    if isinstance(provider_type, str):
        provider_type = ProviderType.from_string(provider_type)
    
    # Get API key
    if api_key is None:
        api_key = _get_api_key_for_provider(provider_type)
    
    if not api_key:
        raise ValueError(
            f"No API key configured for {provider_type.value}. "
            f"Set the appropriate environment variable."
        )
    
    # Create provider
    if provider_type == ProviderType.OPENAI:
        return OpenAIProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider_type == ProviderType.GEMINI:
        return GeminiProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider_type == ProviderType.GROQ:
        return GroqProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider_type == ProviderType.COHERE:
        return CohereProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider_type == ProviderType.ANTHROPIC:
        return AnthropicProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider_type == ProviderType.OLLAMA:
        return OllamaProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider_type == ProviderType.MISTRAL:
        return MistralProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")


def _get_api_key_for_provider(provider_type: ProviderType) -> Optional[str]:
    """Get the API key for a specific provider from settings."""
    if provider_type == ProviderType.OPENAI:
        return settings.openai_api_key
    elif provider_type == ProviderType.GEMINI:
        return settings.gemini_api_key
    elif provider_type == ProviderType.GROQ:
        return settings.groq_api_key
    elif provider_type == ProviderType.COHERE:
        return getattr(settings, 'cohere_api_key', None)
    elif provider_type == ProviderType.ANTHROPIC:
        return getattr(settings, 'anthropic_api_key', None)
    elif provider_type == ProviderType.OLLAMA:
        return ""  # Ollama doesn't require API key
    elif provider_type == ProviderType.MISTRAL:
        return getattr(settings, 'mistral_api_key', None)
    return None


def get_langchain_llm(
    provider_type: Optional[Union[str, ProviderType]] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
):
    """
    Get a LangChain-compatible LLM instance.
    
    This provides backward compatibility with existing code using LangChain.
    
    Args:
        provider_type: The provider to use
        model: The model to use
        temperature: Temperature for generation
        
    Returns:
        A LangChain ChatModel instance
    """
    if provider_type is None:
        provider_type = settings.llm_provider
    
    if isinstance(provider_type, str):
        provider_type = ProviderType.from_string(provider_type)
    
    if provider_type == ProviderType.OPENAI:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or "gpt-4o-mini",
            temperature=temperature,
            api_key=settings.openai_api_key,
        )
    
    elif provider_type == ProviderType.GEMINI:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=model or "gemini-2.0-flash",
                temperature=temperature,
                google_api_key=settings.gemini_api_key,
            )
        except ImportError:
            raise ImportError(
                "langchain-google-genai is required for Gemini with LangChain. "
                "Install it with: pip install langchain-google-genai"
            )
    
    elif provider_type == ProviderType.GROQ:
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=model or "llama-3.3-70b-versatile",
                temperature=temperature,
                groq_api_key=settings.groq_api_key,
            )
        except ImportError:
            raise ImportError(
                "langchain-groq is required for Groq with LangChain. "
                "Install it with: pip install langchain-groq"
            )
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")


def get_available_providers() -> list[dict]:
    """
    Get list of available providers with their configuration status.
    
    Returns:
        List of dicts with provider info and availability status
    """
    providers = []
    
    for provider_type in ProviderType:
        api_key = _get_api_key_for_provider(provider_type)
        providers.append({
            "provider": provider_type.value,
            "available": bool(api_key),
            "configured": bool(api_key),
        })
    
    return providers
