"""
Skills and Tools Recommender Agent

Recommends relevant skills, tools, and technologies
based on user topic, experience level, and career goals.
"""

import json
import re
from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage

from app.providers import get_langchain_llm
from app.agents.recommender_prompts import SKILLS_TOOLS_RECOMMENDER_PROMPT
from app.models.recommender_schemas import (
    SkillsToolsRecommendation,
    SkillMatch,
    ToolMatch,
    SkillsToolsRequest
)


class SkillsToolsRecommenderAgent:
    """Agent that recommends skills and tools for topics."""
    
    def __init__(self, provider_type: str = None):
        """Initialize the skills/tools recommender agent."""
        self.llm = get_langchain_llm(provider_type=provider_type)
    
    async def recommend(self, request: SkillsToolsRequest) -> SkillsToolsRecommendation:
        """
        Generate skills and tools recommendations.
        
        Args:
            request: SkillsToolsRequest containing topic and preferences
            
        Returns:
            SkillsToolsRecommendation with skills and tools
        """
        # Build the prompt
        prompt = SKILLS_TOOLS_RECOMMENDER_PROMPT.format(
            topic=request.topic,
            current_skills=", ".join(request.current_skills) if request.current_skills else "none specified",
            career_goal=request.career_goal or "career growth",
            experience_level=request.experience_level or "beginner",
            focus_area=request.focus_area or "general",
            include_soft_skills=request.include_soft_skills
        )
        
        messages = [
            SystemMessage(content="You are an expert tech advisor. Return only valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        # Get LLM response
        response = await self.llm.ainvoke(messages)
        
        # Parse and build recommendation
        return self._build_recommendation(response.content, request)
    
    def recommend_sync(self, request: SkillsToolsRequest) -> SkillsToolsRecommendation:
        """
        Synchronous version of recommend.
        
        Args:
            request: SkillsToolsRequest containing topic and preferences
            
        Returns:
            SkillsToolsRecommendation with skills and tools
        """
        # Build the prompt
        prompt = SKILLS_TOOLS_RECOMMENDER_PROMPT.format(
            topic=request.topic,
            current_skills=", ".join(request.current_skills) if request.current_skills else "none specified",
            career_goal=request.career_goal or "career growth",
            experience_level=request.experience_level or "beginner",
            focus_area=request.focus_area or "general",
            include_soft_skills=request.include_soft_skills
        )
        
        messages = [
            SystemMessage(content="You are an expert tech advisor. Return only valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        # Get LLM response
        response = self.llm.invoke(messages)
        
        # Parse and build recommendation
        return self._build_recommendation(response.content, request)
    
    def _build_recommendation(
        self, 
        response_content: str, 
        request: SkillsToolsRequest
    ) -> SkillsToolsRecommendation:
        """
        Parse LLM response and build SkillsToolsRecommendation.
        
        Args:
            response_content: Raw LLM response
            request: Original request for context
            
        Returns:
            Structured SkillsToolsRecommendation
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
            
            # Build skill objects
            core_skills = [
                SkillMatch(**skill) for skill in data.get("core_skills", [])
            ]
            complementary_skills = [
                SkillMatch(**skill) for skill in data.get("complementary_skills", [])
            ]
            advanced_skills = [
                SkillMatch(**skill) for skill in data.get("advanced_skills", [])
            ]
            soft_skills = [
                SkillMatch(**skill) for skill in data.get("soft_skills", [])
            ]
            
            # Build tool objects
            essential_tools = [
                ToolMatch(**tool) for tool in data.get("essential_tools", [])
            ]
            recommended_tools = [
                ToolMatch(**tool) for tool in data.get("recommended_tools", [])
            ]
            emerging_tools = [
                ToolMatch(**tool) for tool in data.get("emerging_tools", [])
            ]
            
            return SkillsToolsRecommendation(
                topic=data.get("topic", request.topic),
                user_profile_summary=data.get("user_profile_summary", ""),
                core_skills=core_skills,
                complementary_skills=complementary_skills,
                advanced_skills=advanced_skills,
                soft_skills=soft_skills,
                essential_tools=essential_tools,
                recommended_tools=recommended_tools,
                emerging_tools=emerging_tools,
                recommended_stack=data.get("recommended_stack", []),
                learning_order=data.get("learning_order", []),
                industry_trends=data.get("industry_trends", []),
                job_market_demand=data.get("job_market_demand", "medium")
            )
            
        except json.JSONDecodeError as e:
            # Return fallback recommendation on parse error
            return self._fallback_recommendation(request, str(e))
        except Exception as e:
            return self._fallback_recommendation(request, str(e))
    
    def _fallback_recommendation(
        self, 
        request: SkillsToolsRequest, 
        error: str
    ) -> SkillsToolsRecommendation:
        """
        Create fallback recommendation when parsing fails.
        
        Args:
            request: Original request
            error: Error message
            
        Returns:
            Basic SkillsToolsRecommendation
        """
        return SkillsToolsRecommendation(
            topic=request.topic,
            user_profile_summary=f"Parse error: {error}. Showing general recommendations.",
            core_skills=[
                SkillMatch(
                    name=f"{request.topic} Fundamentals",
                    category="technical",
                    skill_type="hard",
                    difficulty_to_learn="medium",
                    time_to_learn="2-3 months",
                    description=f"Core understanding of {request.topic} concepts and practices.",
                    why_important=f"Foundation for all {request.topic}-related work.",
                    match_score=85,
                    related_to_topic=["Direct core skill", "Essential for proficiency"],
                    job_demand="high",
                    salary_impact="medium",
                    learning_resources=["Online courses", "Documentation", "Practice projects"],
                    prerequisites=[],
                    icon="💡"
                )
            ],
            complementary_skills=[],
            advanced_skills=[],
            soft_skills=[],
            essential_tools=[
                ToolMatch(
                    name="VS Code",
                    category="IDE",
                    tool_type="software",
                    description="Popular code editor with extensive extensions.",
                    why_use="Industry standard, free, highly extensible.",
                    use_cases=["Code editing", "Debugging", "Version control"],
                    match_score=80,
                    related_to_topic=["General development tool"],
                    difficulty_to_learn="easy",
                    time_to_learn="1 week",
                    popularity="industry-standard",
                    alternatives=["Sublime Text", "Vim", "JetBrains IDEs"],
                    is_free=True,
                    official_url=None,
                    icon="🔧"
                )
            ],
            recommended_tools=[],
            emerging_tools=[],
            recommended_stack=["Learn fundamentals", "Choose appropriate tools"],
            learning_order=["Start with basics", "Build practical skills"],
            industry_trends=["Continuous learning is key"],
            job_market_demand="medium"
        )
