"""Internship Recommender Agent - Recommends internships based on user profile."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.agents.base_agent import BaseInterviewAgent
from app.agents.recommender_prompts import INTERNSHIP_RECOMMENDER_PROMPT
from app.models.recommender_schemas import (
    InternshipMatch,
    InternshipRecommendation,
    InternshipRequest,
    UserPreferences,
)

logger = logging.getLogger(__name__)


class InternshipRecommenderAgent(BaseInterviewAgent):
    """
    AI Agent that recommends internships based on student profiles.
    
    Features:
    - Matches skills and interests with opportunities
    - Considers location preferences
    - Provides match scores and reasons
    - Identifies skill gaps and recommended actions
    """
    
    def __init__(self, **kwargs):
        super().__init__(temperature=0.7, **kwargs)
    
    def get_prompt_template(self) -> str:
        return INTERNSHIP_RECOMMENDER_PROMPT
    
    def get_default_response(self) -> Dict[str, Any]:
        """Return a default response structure."""
        return {
            "user_profile_summary": "Unable to analyze profile",
            "total_matches": 0,
            "top_recommendations": [],
            "alternative_paths": [],
            "skill_gaps": [],
            "recommended_actions": ["Please try again with more details"],
            "search_tips": []
        }
    
    async def recommend(
        self, 
        request: InternshipRequest
    ) -> InternshipRecommendation:
        """
        Generate internship recommendations based on user preferences.
        
        Args:
            request: InternshipRequest with user preferences
            
        Returns:
            InternshipRecommendation with matched opportunities
        """
        prefs = request.preferences
        
        try:
            response = await self.invoke(
                academic_year=prefs.academic_year,
                track=prefs.track,
                skills=", ".join(prefs.skills) if prefs.skills else "Not specified",
                interests=", ".join(prefs.interests) if prefs.interests else "Not specified",
                location_preference=prefs.location_preference,
                availability=prefs.availability or "Flexible",
                notes=prefs.notes or "None",
            )
            
            parsed = self.parse_json_response(response)
            return self._build_recommendation(parsed, request.max_results)
            
        except Exception as e:
            logger.error(f"Error generating internship recommendations: {e}")
            raise
    
    def recommend_sync(
        self, 
        request: InternshipRequest
    ) -> InternshipRecommendation:
        """Synchronous version of recommend."""
        prefs = request.preferences
        
        try:
            response = self.invoke_sync(
                academic_year=prefs.academic_year,
                track=prefs.track,
                skills=", ".join(prefs.skills) if prefs.skills else "Not specified",
                interests=", ".join(prefs.interests) if prefs.interests else "Not specified",
                location_preference=prefs.location_preference,
                availability=prefs.availability or "Flexible",
                notes=prefs.notes or "None",
            )
            
            parsed = self.parse_json_response(response)
            return self._build_recommendation(parsed, request.max_results)
            
        except Exception as e:
            logger.error(f"Error generating internship recommendations: {e}")
            raise
    
    def _build_recommendation(
        self, 
        data: Dict[str, Any], 
        max_results: int
    ) -> InternshipRecommendation:
        """Build InternshipRecommendation from parsed JSON."""
        
        # Build internship matches
        recommendations = []
        for item in data.get("top_recommendations", [])[:max_results]:
            try:
                match = InternshipMatch(
                    title=item.get("title", "Internship"),
                    company=item.get("company", "Company"),
                    location=item.get("location", "Unknown"),
                    work_type=item.get("work_type", "on-site"),
                    description=item.get("description", ""),
                    requirements=item.get("requirements", []),
                    match_score=min(100, max(0, int(item.get("match_score", 50)))),
                    match_reasons=item.get("match_reasons", []),
                    skills_matched=item.get("skills_matched", []),
                    skills_to_develop=item.get("skills_to_develop", []),
                    application_url=item.get("application_url"),
                    deadline=item.get("deadline"),
                    icon=item.get("icon", "💼")
                )
                recommendations.append(match)
            except Exception as e:
                logger.warning(f"Error parsing internship match: {e}")
                continue
        
        return InternshipRecommendation(
            user_profile_summary=data.get("user_profile_summary", "Profile analyzed"),
            total_matches=data.get("total_matches", len(recommendations)),
            top_recommendations=recommendations,
            alternative_paths=data.get("alternative_paths", []),
            skill_gaps=data.get("skill_gaps", []),
            recommended_actions=data.get("recommended_actions", []),
            search_tips=data.get("search_tips", [])
        )
