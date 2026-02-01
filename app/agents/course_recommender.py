"""
Course and Certification Recommender Agent

Recommends relevant courses, certifications, and learning paths
based on user topic, level, and learning goals.
"""

import json
import re
from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage

from app.providers import get_langchain_llm
from app.agents.recommender_prompts import COURSE_RECOMMENDER_PROMPT
from app.models.recommender_schemas import (
    CourseRecommendation,
    CourseMatch,
    CertificationMatch,
    CourseRequest
)


class CourseRecommenderAgent:
    """Agent that recommends courses and certifications for learning topics."""
    
    def __init__(self, provider_type: str = None):
        """Initialize the course recommender agent."""
        self.llm = get_langchain_llm(provider_type=provider_type)
    
    async def recommend(self, request: CourseRequest) -> CourseRecommendation:
        """
        Generate course and certification recommendations.
        
        Args:
            request: CourseRequest containing topic and preferences
            
        Returns:
            CourseRecommendation with courses and certifications
        """
        # Build the prompt
        prompt = COURSE_RECOMMENDER_PROMPT.format(
            topic=request.topic,
            current_level=request.current_level or "beginner",
            learning_goal=request.learning_goal or "gain proficiency",
            time_available=request.time_available or "flexible",
            budget=request.budget or "flexible",
            prefer_certificates=request.prefer_certificates
        )
        
        messages = [
            SystemMessage(content="You are an expert learning advisor. Return only valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        # Get LLM response
        response = await self.llm.ainvoke(messages)
        
        # Parse and build recommendation
        return self._build_recommendation(response.content, request)
    
    def recommend_sync(self, request: CourseRequest) -> CourseRecommendation:
        """
        Synchronous version of recommend.
        
        Args:
            request: CourseRequest containing topic and preferences
            
        Returns:
            CourseRecommendation with courses and certifications
        """
        # Build the prompt
        prompt = COURSE_RECOMMENDER_PROMPT.format(
            topic=request.topic,
            current_level=request.current_level or "beginner",
            learning_goal=request.learning_goal or "gain proficiency",
            time_available=request.time_available or "flexible",
            budget=request.budget or "flexible",
            prefer_certificates=request.prefer_certificates
        )
        
        messages = [
            SystemMessage(content="You are an expert learning advisor. Return only valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        # Get LLM response
        response = self.llm.invoke(messages)
        
        # Parse and build recommendation
        return self._build_recommendation(response.content, request)
    
    def _build_recommendation(
        self, 
        response_content: str, 
        request: CourseRequest
    ) -> CourseRecommendation:
        """
        Parse LLM response and build CourseRecommendation.
        
        Args:
            response_content: Raw LLM response
            request: Original request for context
            
        Returns:
            Structured CourseRecommendation
        """
        try:
            # Clean response - extract JSON
            content = response_content.strip()
            
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                content = json_match.group(1).strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Build course objects
            free_courses = [
                CourseMatch(**course) for course in data.get("free_courses", [])
            ]
            paid_courses = [
                CourseMatch(**course) for course in data.get("paid_courses", [])
            ]
            beginner_courses = [
                CourseMatch(**course) for course in data.get("beginner_courses", [])
            ]
            advanced_courses = [
                CourseMatch(**course) for course in data.get("advanced_courses", [])
            ]
            
            # Build certification objects
            certifications = [
                CertificationMatch(**cert) for cert in data.get("certifications", [])
            ]
            
            return CourseRecommendation(
                topic=data.get("topic", request.topic),
                user_profile_summary=data.get("user_profile_summary", ""),
                total_courses=data.get("total_courses", len(free_courses) + len(paid_courses)),
                total_certifications=data.get("total_certifications", len(certifications)),
                free_courses=free_courses,
                paid_courses=paid_courses,
                beginner_courses=beginner_courses,
                advanced_courses=advanced_courses,
                certifications=certifications,
                recommended_learning_path=data.get("recommended_learning_path", []),
                time_to_proficiency=data.get("time_to_proficiency", "3-6 months"),
                study_tips=data.get("study_tips", [])
            )
            
        except json.JSONDecodeError as e:
            # Return fallback recommendation on parse error
            return self._fallback_recommendation(request, str(e))
        except Exception as e:
            return self._fallback_recommendation(request, str(e))
    
    def _fallback_recommendation(
        self, 
        request: CourseRequest, 
        error: str
    ) -> CourseRecommendation:
        """
        Create fallback recommendation when parsing fails.
        
        Args:
            request: Original request
            error: Error message
            
        Returns:
            Basic CourseRecommendation
        """
        return CourseRecommendation(
            topic=request.topic,
            user_profile_summary=f"Parse error: {error}. Showing general recommendations.",
            total_courses=1,
            total_certifications=0,
            free_courses=[
                CourseMatch(
                    name=f"Introduction to {request.topic}",
                    provider="Coursera",
                    instructor="Various",
                    course_type="course",
                    difficulty="beginner",
                    duration="4-6 weeks",
                    description=f"Foundational course covering {request.topic} basics.",
                    topics_covered=[request.topic, "Fundamentals", "Best Practices"],
                    skills_gained=["Basic understanding", "Practical application"],
                    match_score=70,
                    match_reasons=["Matches your topic interest"],
                    rating=4.5,
                    num_reviews="10,000+",
                    price="Free",
                    is_free=True,
                    has_certificate=True,
                    url=None,
                    icon="📚"
                )
            ],
            paid_courses=[],
            beginner_courses=[],
            advanced_courses=[],
            certifications=[],
            recommended_learning_path=[
                "Start with fundamentals",
                "Practice with exercises",
                "Build projects",
                "Get certified"
            ],
            time_to_proficiency="3-6 months",
            study_tips=[
                "Set a consistent learning schedule",
                "Practice regularly with hands-on exercises",
                "Join learning communities for support"
            ]
        )
