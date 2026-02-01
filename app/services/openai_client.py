"""
LLM Client for AI-powered job matching reasons.
Generates personalized explanations for why a job matches a candidate.
Supports multiple providers: OpenAI, Gemini, Groq.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional, Union

from app.config import settings
from app.providers import LLMProvider, LLMResponse, ProviderType, get_provider
from app.providers.base import Message

logger = logging.getLogger("llm_client")


class LLMClient:
    """LLM client for generating AI-powered match reasons. Supports multiple providers."""
    
    def __init__(
        self,
        provider: Optional[Union[str, ProviderType, LLMProvider]] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize the LLM client.
        
        Args:
            provider: Provider type ("openai", "gemini", "groq") or LLMProvider instance
            model: Optional model override
        """
        if isinstance(provider, LLMProvider):
            self._provider = provider
        else:
            self._provider = get_provider(
                provider_type=provider,
                model=model,
            )
    
    @property
    def provider(self) -> LLMProvider:
        return self._provider
    
    @property
    def model(self) -> str:
        return self._provider.model
    
    def generate_match_reasons(
        self,
        job_title: str,
        company: str,
        job_description: str,
        user_track: str,
        user_skills: list[str],
        user_year: str,
        location_preference: str,
        job_location: str,
        score: int,
    ) -> list[str]:
        """
        Generate AI-powered personalized reasons for why this job matches the user.
        
        Returns a list of 3-5 concise, specific reasons.
        """
        prompt = f"""You are a career advisor analyzing a job match for a student.

**Student Profile:**
- Track/Major: {user_track}
- Skills: {', '.join(user_skills) if user_skills else 'Not specified'}
- Academic Year: {user_year}
- Location Preference: {location_preference}

**Job Details:**
- Title: {job_title}
- Company: {company}
- Location: {job_location}
- Description: {job_description[:500] if job_description else 'No description available'}

**Match Score: {score}/100**

Write 3-5 short, specific reasons explaining why this job is a good match for this student. 
Be specific about skills, company, and role alignment.
Use emojis sparingly (1-2 max).
Each reason should be 1 sentence, direct and actionable.

Return ONLY a JSON array of strings, like:
["Reason 1", "Reason 2", "Reason 3"]
"""

        try:
            response = self._provider.complete(
                prompt=prompt,
                system_prompt="You are a helpful career advisor. Return only valid JSON.",
                temperature=0.7,
                max_tokens=300,
            )
            
            content = response.content.strip()
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            reasons = json.loads(content)
            
            if isinstance(reasons, list) and all(isinstance(r, str) for r in reasons):
                return reasons[:5]  # Max 5 reasons
            
            logger.warning("Invalid AI response format, using fallback")
            return self._fallback_reasons(score, job_title, company)
            
        except Exception as e:
            logger.error(f"LLM error ({self._provider.provider_type.value}): {e}")
            return self._fallback_reasons(score, job_title, company)
    
    def _fallback_reasons(self, score: int, job_title: str, company: str) -> list[str]:
        """Fallback reasons if AI fails."""
        if score >= 70:
            return [
                f"Strong alignment with the {job_title} role.",
                f"{company} offers great learning opportunities.",
                "Your skills match the job requirements well."
            ]
        elif score >= 50:
            return [
                f"Good potential match for {job_title}.",
                "This role can help you grow your skills.",
                f"Consider applying to {company}."
            ]
        else:
            return [
                "This is an entry-level opportunity.",
                "Could be a stepping stone for your career.",
            ]

    def score_opportunity_ai(
        self,
        profile: Any,
        opportunity: Any,
    ) -> dict[str, Any] | None:
        """
        Score a job opportunity against a user profile using AI.
        
        Returns a dict with 'score' (int 0-100) and 'reasons' (list of strings).
        """
        # Extract profile info
        user_track = getattr(profile, 'track', 'Not specified')
        user_year = getattr(profile, 'year_level', 'Not specified')
        location_pref = getattr(profile, 'location_preference', 'Not specified')
        
        # Get skills from profile
        skills_obj = getattr(profile, 'skills', None)
        if skills_obj:
            hard_skills = getattr(skills_obj, 'hard', [])
            tools = getattr(skills_obj, 'tools', [])
            soft_skills = getattr(skills_obj, 'soft', [])
            all_skills = hard_skills + tools + soft_skills
        else:
            all_skills = []
        
        # Extract opportunity info
        job_title = getattr(opportunity, 'title', 'Unknown')
        company = getattr(opportunity, 'company', 'Unknown')
        job_location = getattr(opportunity, 'location', 'Unknown')
        description = getattr(opportunity, 'description', '')
        
        prompt = f"""You are a career advisor scoring a job opportunity for a student.

**Student Profile:**
- Track/Major: {user_track}
- Skills: {', '.join(all_skills) if all_skills else 'Not specified'}
- Academic Year: {user_year}
- Location Preference: {location_pref}

**Job Opportunity:**
- Title: {job_title}
- Company: {company}
- Location: {job_location}
- Description: {description[:800] if description else 'No description available'}

Score this job match from 0-100 based on:
1. Skills alignment (40%)
2. Role fit for their academic level (25%)
3. Location preference match (20%)
4. Career growth potential (15%)

Also provide 3-4 specific reasons explaining the score.

Return ONLY valid JSON in this exact format:
{{"score": 75, "reasons": ["Reason 1", "Reason 2", "Reason 3"]}}
"""

        try:
            response = self._provider.complete(
                prompt=prompt,
                system_prompt="You are a helpful career advisor. Return only valid JSON.",
                temperature=0.5,
                max_tokens=400,
            )
            
            content = response.content.strip()
            
            # Handle potential markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            
            if isinstance(result, dict) and "score" in result and "reasons" in result:
                # Ensure score is within bounds
                score = max(0, min(100, int(result["score"])))
                reasons = result["reasons"] if isinstance(result["reasons"], list) else []
                return {"score": score, "reasons": reasons[:5]}
            
            logger.warning("Invalid AI response format for scoring")
            return None
            
        except Exception as e:
            logger.error(f"LLM scoring error ({self._provider.provider_type.value}): {e}")
            return None


# Backward compatibility alias
OpenAIClient = LLMClient


def get_llm_client(
    provider: Optional[Union[str, ProviderType]] = None,
    model: Optional[str] = None,
) -> LLMClient | None:
    """
    Get an LLM client for the specified or configured provider.
    
    Args:
        provider: Provider type ("openai", "gemini", "groq"). Uses settings if None.
        model: Optional model override
        
    Returns:
        LLMClient instance or None if no API key configured
    """
    try:
        return LLMClient(provider=provider, model=model)
    except ValueError as e:
        logger.warning(f"LLM client creation failed: {e}")
        return None


def get_openai_client() -> LLMClient | None:
    """
    Get OpenAI client if API key is configured.
    DEPRECATED: Use get_llm_client() instead.
    """
    if settings.openai_api_key:
        return LLMClient(provider="openai")
    logger.warning("OpenAI API key not configured")
    return None
