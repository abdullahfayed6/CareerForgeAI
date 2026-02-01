from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # LLM Provider settings
    llm_provider: str  # "openai", "gemini", or "groq"
    llm_model: str | None  # Optional: override default model
    
    # API Keys for different providers
    openai_api_key: str | None
    gemini_api_key: str | None
    groq_api_key: str | None
    
    # Other API keys
    search_api_key: str | None
    rapidapi_key: str | None  # RapidAPI key for LinkedIn API
    
    # Application settings
    search_provider: str
    max_results: int
    top_k: int


def _load_settings() -> Settings:
    return Settings(
        # LLM Provider configuration
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        llm_model=os.getenv("LLM_MODEL"),
        
        # Provider API keys
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        
        # Other settings
        search_api_key=os.getenv("SEARCH_API_KEY"),
        rapidapi_key=os.getenv("RAPIDAPI_KEY"),
        search_provider=os.getenv("SEARCH_PROVIDER", "mock"),
        max_results=int(os.getenv("MAX_RESULTS", "20")),
        top_k=int(os.getenv("TOP_K", "5")),
    )


settings = _load_settings()
