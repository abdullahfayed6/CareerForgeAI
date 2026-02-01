"""API endpoints for the Recommender Multi-Agent System."""
from __future__ import annotations

import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from app.agents.internship_recommender import InternshipRecommenderAgent
from app.agents.event_recommender import EventRecommenderAgent
from app.agents.course_recommender import CourseRecommenderAgent
from app.agents.skills_tools_recommender import SkillsToolsRecommenderAgent
from app.models.recommender_schemas import (
    UserPreferences,
    InternshipRequest,
    InternshipRecommendation,
    EventRequest,
    EventRecommendation,
    CourseRequest,
    CourseRecommendation,
    SkillsToolsRequest,
    SkillsToolsRecommendation,
    CombinedRequest,
    FullRecommendation,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recommend", tags=["Recommender - Internships & Events"])


# ============================================
# Request Models for API
# ============================================

class QuickInternshipRequest(BaseModel):
    """Simplified request for quick internship recommendations."""
    academic_year: int = Field(ge=1, le=5, example=3)
    track: str = Field(..., example="Computer Science")
    skills: List[str] = Field(default_factory=list, example=["Python", "Machine Learning", "SQL"])
    location_preference: Literal["egypt", "abroad", "remote", "hybrid"] = Field(default="egypt")
    interests: List[str] = Field(default_factory=list, example=["AI", "Data Science"])


class QuickEventRequest(BaseModel):
    """Simplified request for quick event recommendations."""
    academic_year: int = Field(ge=1, le=5, example=3)
    track: str = Field(..., example="Computer Science")
    skills: List[str] = Field(default_factory=list, example=["Python", "Web Development"])
    interests: List[str] = Field(default_factory=list, example=["Hackathons", "AI"])
    location_preference: Literal["egypt", "abroad", "remote", "hybrid"] = Field(default="egypt")
    event_types: List[str] = Field(
        default=["hackathon", "workshop", "competition"],
        example=["hackathon", "workshop"]
    )


class QuickCourseRequest(BaseModel):
    """Simplified request for quick course recommendations."""
    topic: str = Field(..., example="Machine Learning")
    current_level: Literal["beginner", "intermediate", "advanced"] = Field(default="beginner")
    learning_goal: Optional[str] = Field(default=None, example="Become a data scientist")
    time_available: Optional[str] = Field(default=None, example="5 hours per week")
    budget: Optional[str] = Field(default="flexible", example="$50/month")
    prefer_certificates: bool = Field(default=True)


class QuickSkillsToolsRequest(BaseModel):
    """Simplified request for quick skills/tools recommendations."""
    topic: str = Field(..., example="Web Development")
    current_skills: List[str] = Field(default_factory=list, example=["HTML", "CSS"])
    career_goal: Optional[str] = Field(default=None, example="Full Stack Developer")
    experience_level: Literal["beginner", "intermediate", "advanced"] = Field(default="beginner")
    focus_area: Optional[str] = Field(default=None, example="Frontend")
    include_soft_skills: bool = Field(default=True)


# ============================================
# Internship Recommendation Endpoints
# ============================================

@router.post(
    "/internships",
    response_model=InternshipRecommendation,
    summary="Get Internship Recommendations",
    description="""
## Get personalized internship recommendations

### Features:
- 🎯 **Smart Matching**: Matches your skills and interests with opportunities
- 📍 **Location-Aware**: Considers your location preferences (Egypt, abroad, remote)
- 📊 **Match Scores**: Each opportunity includes a match score and reasons
- 🚀 **Skill Gaps**: Identifies skills to develop for better opportunities
- 💡 **Action Items**: Provides recommended next steps

### Returns:
- Top matching internships with detailed information
- Skills matched and skills to develop
- Alternative career paths to consider
- Job searching tips
"""
)
async def get_internship_recommendations(request: QuickInternshipRequest) -> InternshipRecommendation:
    """Get personalized internship recommendations based on profile."""
    try:
        agent = InternshipRecommenderAgent()
        
        # Convert to full request
        full_request = InternshipRequest(
            preferences=UserPreferences(
                academic_year=request.academic_year,
                track=request.track,
                skills=request.skills,
                interests=request.interests,
                location_preference=request.location_preference,
            ),
            max_results=10,
            include_remote=True,
        )
        
        result = await agent.recommend(full_request)
        
        logger.info(f"Generated {len(result.top_recommendations)} internship recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error getting internship recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post(
    "/internships/detailed",
    response_model=InternshipRecommendation,
    summary="Get Detailed Internship Recommendations",
    description="Get internship recommendations with full customization options"
)
async def get_detailed_internship_recommendations(
    request: InternshipRequest
) -> InternshipRecommendation:
    """Get internship recommendations with full request options."""
    try:
        agent = InternshipRecommenderAgent()
        result = await agent.recommend(request)
        return result
        
    except Exception as e:
        logger.error(f"Error getting internship recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


# ============================================
# Event/Hackathon Recommendation Endpoints
# ============================================

@router.post(
    "/events",
    response_model=EventRecommendation,
    summary="Get Event & Hackathon Recommendations",
    description="""
## Get personalized event and hackathon recommendations

### Event Types Covered:
- 🏆 **Hackathons**: Major and local hackathons
- 📚 **Workshops**: Technical skill-building workshops
- 🎤 **Conferences**: Tech conferences and summits
- 🏅 **Competitions**: Coding and innovation competitions
- 👥 **Meetups**: Networking and community events

### Features:
- Match scores based on your interests
- Skills you'll gain from each event
- Preparation tips
- Upcoming deadlines highlighted

### Returns:
- Categorized event recommendations
- Match reasons for each event
- Networking value assessment
- Registration deadlines
"""
)
async def get_event_recommendations(request: QuickEventRequest) -> EventRecommendation:
    """Get personalized event and hackathon recommendations."""
    try:
        agent = EventRecommenderAgent()
        
        # Convert to full request
        full_request = EventRequest(
            preferences=UserPreferences(
                academic_year=request.academic_year,
                track=request.track,
                skills=request.skills,
                interests=request.interests,
                location_preference=request.location_preference,
            ),
            event_types=request.event_types,
            timeframe="next_3_months",
            include_online=True,
            max_results=5,
        )
        
        result = await agent.recommend(full_request)
        
        logger.info(f"Generated {result.total_events} event recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error getting event recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post(
    "/events/detailed",
    response_model=EventRecommendation,
    summary="Get Detailed Event Recommendations",
    description="Get event recommendations with full customization options"
)
async def get_detailed_event_recommendations(
    request: EventRequest
) -> EventRecommendation:
    """Get event recommendations with full request options."""
    try:
        agent = EventRecommenderAgent()
        result = await agent.recommend(request)
        return result
        
    except Exception as e:
        logger.error(f"Error getting event recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


# ============================================
# Combined Recommendation Endpoints
# ============================================

@router.post(
    "/all",
    response_model=FullRecommendation,
    summary="Get All Recommendations",
    description="""
## Get both internship and event recommendations in one call

### Returns:
- 💼 **Internship Recommendations**: Top matching opportunities
- 🎯 **Event Recommendations**: Hackathons, workshops, and more
- 🗺️ **Personalized Roadmap**: Next steps tailored to your profile

This endpoint combines both the internship and event recommender agents
to provide a comprehensive view of opportunities.
"""
)
async def get_all_recommendations(request: CombinedRequest) -> FullRecommendation:
    """Get both internship and event recommendations."""
    try:
        internship_agent = InternshipRecommenderAgent()
        event_agent = EventRecommenderAgent()
        
        internships = None
        events = None
        
        if request.include_internships:
            internship_request = InternshipRequest(
                preferences=request.preferences,
                max_results=request.max_results_per_category,
            )
            internships = await internship_agent.recommend(internship_request)
        
        if request.include_events:
            event_request = EventRequest(
                preferences=request.preferences,
                max_results=request.max_results_per_category,
            )
            events = await event_agent.recommend(event_request)
        
        # Build personalized roadmap
        roadmap = _build_roadmap(request.preferences, internships, events)
        
        return FullRecommendation(
            request_id=uuid4(),
            created_at=datetime.now(),
            user_preferences=request.preferences,
            internships=internships or InternshipRecommendation(
                user_profile_summary="Internships not requested",
                total_matches=0,
                top_recommendations=[]
            ),
            events=events or EventRecommendation(
                user_profile_summary="Events not requested",
                total_events=0
            ),
            personalized_roadmap=roadmap
        )
        
    except Exception as e:
        logger.error(f"Error getting combined recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


def _build_roadmap(
    preferences: UserPreferences,
    internships: Optional[InternshipRecommendation],
    events: Optional[EventRecommendation]
) -> List[str]:
    """Build a personalized roadmap based on recommendations."""
    roadmap = []
    
    # Add immediate actions
    roadmap.append(f"📍 Focus on {preferences.track} opportunities in {preferences.location_preference}")
    
    if preferences.skills:
        roadmap.append(f"💪 Leverage your top skills: {', '.join(preferences.skills[:3])}")
    
    # Add internship-based actions
    if internships and internships.skill_gaps:
        roadmap.append(f"📚 Develop these skills: {', '.join(internships.skill_gaps[:3])}")
    
    if internships and internships.top_recommendations:
        roadmap.append(f"💼 Apply to top {len(internships.top_recommendations)} matched internships")
    
    # Add event-based actions
    if events and events.hackathons:
        roadmap.append(f"🏆 Participate in {len(events.hackathons)} upcoming hackathons")
    
    if events and events.workshops:
        roadmap.append(f"📚 Attend {len(events.workshops)} skill-building workshops")
    
    # Add general advice
    roadmap.append("🔄 Update your resume and LinkedIn profile")
    roadmap.append("🤝 Network with professionals in your field")
    
    return roadmap


# ============================================
# Quick Recommendation Endpoints
# ============================================

@router.get(
    "/hackathons",
    summary="Get Quick Hackathon Recommendations",
    description="Get hackathon recommendations with minimal input"
)
async def get_quick_hackathons(
    track: str = "Computer Science",
    location: Literal["egypt", "abroad", "remote"] = "egypt"
):
    """Get quick hackathon recommendations."""
    try:
        agent = EventRecommenderAgent()
        
        request = EventRequest(
            preferences=UserPreferences(
                academic_year=3,
                track=track,
                skills=[],
                interests=["hackathons"],
                location_preference=location,
            ),
            event_types=["hackathon"],
            max_results=5,
        )
        
        result = await agent.recommend(request)
        
        return {
            "track": track,
            "location": location,
            "hackathons": result.hackathons,
            "preparation_tips": result.preparation_tips[:3]
        }
        
    except Exception as e:
        logger.error(f"Error getting hackathon recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


# ============================================
# Course & Certification Recommendation Endpoints
# ============================================

@router.post(
    "/courses",
    response_model=CourseRecommendation,
    summary="Get Course & Certification Recommendations",
    description="""
## Get personalized course and certification recommendations

### Features:
- 📚 **Free Courses**: Quality free learning options
- 💰 **Paid Courses**: Premium comprehensive courses
- 🎓 **Certifications**: Industry-recognized certifications
- 📈 **Learning Path**: Recommended order to learn
- 💡 **Study Tips**: Personalized study advice

### Returns:
- Categorized courses (free, paid, beginner, advanced)
- Top certifications for the topic
- Recommended learning path
- Time to proficiency estimate
"""
)
async def get_course_recommendations(request: QuickCourseRequest) -> CourseRecommendation:
    """Get personalized course and certification recommendations."""
    try:
        agent = CourseRecommenderAgent()
        
        # Convert to full request
        full_request = CourseRequest(
            topic=request.topic,
            current_level=request.current_level,
            learning_goal=request.learning_goal,
            time_available=request.time_available,
            budget=request.budget,
            prefer_certificates=request.prefer_certificates,
        )
        
        result = await agent.recommend(full_request)
        
        logger.info(f"Generated {result.total_courses} course recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error getting course recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post(
    "/courses/detailed",
    response_model=CourseRecommendation,
    summary="Get Detailed Course Recommendations",
    description="Get course recommendations with full customization options"
)
async def get_detailed_course_recommendations(
    request: CourseRequest
) -> CourseRecommendation:
    """Get course recommendations with full request options."""
    try:
        agent = CourseRecommenderAgent()
        result = await agent.recommend(request)
        return result
        
    except Exception as e:
        logger.error(f"Error getting course recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get(
    "/courses/quick",
    summary="Get Quick Course Recommendations",
    description="Get course recommendations with minimal input"
)
async def get_quick_courses(
    topic: str = "Python Programming",
    level: Literal["beginner", "intermediate", "advanced"] = "beginner",
    free_only: bool = False
):
    """Get quick course recommendations."""
    try:
        agent = CourseRecommenderAgent()
        
        request = CourseRequest(
            topic=topic,
            current_level=level,
            budget="free" if free_only else "flexible",
            prefer_certificates=True,
        )
        
        result = await agent.recommend(request)
        
        courses = result.free_courses if free_only else result.free_courses + result.paid_courses
        
        return {
            "topic": topic,
            "level": level,
            "free_only": free_only,
            "courses": courses[:5],
            "certifications": result.certifications[:3],
            "learning_path": result.recommended_learning_path[:5]
        }
        
    except Exception as e:
        logger.error(f"Error getting quick course recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


# ============================================
# Skills & Tools Recommendation Endpoints
# ============================================

@router.post(
    "/skills-tools",
    response_model=SkillsToolsRecommendation,
    summary="Get Skills & Tools Recommendations",
    description="""
## Get personalized skills and tools recommendations

### Features:
- 💡 **Core Skills**: Essential skills for the topic
- 🔧 **Essential Tools**: Must-know tools
- 📈 **Advanced Skills**: For senior-level proficiency
- 🚀 **Emerging Tools**: New and trending tools
- 📊 **Industry Trends**: Current market trends

### Returns:
- Categorized skills (core, complementary, advanced, soft)
- Categorized tools (essential, recommended, emerging)
- Recommended tech stack
- Learning order
- Job market demand assessment
"""
)
async def get_skills_tools_recommendations(
    request: QuickSkillsToolsRequest
) -> SkillsToolsRecommendation:
    """Get personalized skills and tools recommendations."""
    try:
        agent = SkillsToolsRecommenderAgent()
        
        # Convert to full request
        full_request = SkillsToolsRequest(
            topic=request.topic,
            current_skills=request.current_skills,
            career_goal=request.career_goal,
            experience_level=request.experience_level,
            focus_area=request.focus_area,
            include_soft_skills=request.include_soft_skills,
        )
        
        result = await agent.recommend(full_request)
        
        total_skills = len(result.core_skills) + len(result.complementary_skills)
        total_tools = len(result.essential_tools) + len(result.recommended_tools)
        logger.info(f"Generated {total_skills} skill and {total_tools} tool recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error getting skills/tools recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post(
    "/skills-tools/detailed",
    response_model=SkillsToolsRecommendation,
    summary="Get Detailed Skills & Tools Recommendations",
    description="Get skills/tools recommendations with full customization options"
)
async def get_detailed_skills_tools_recommendations(
    request: SkillsToolsRequest
) -> SkillsToolsRecommendation:
    """Get skills/tools recommendations with full request options."""
    try:
        agent = SkillsToolsRecommenderAgent()
        result = await agent.recommend(request)
        return result
        
    except Exception as e:
        logger.error(f"Error getting skills/tools recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get(
    "/skills",
    summary="Get Quick Skills Recommendations",
    description="Get skill recommendations with minimal input"
)
async def get_quick_skills(
    topic: str = "Data Science",
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
):
    """Get quick skills recommendations."""
    try:
        agent = SkillsToolsRecommenderAgent()
        
        request = SkillsToolsRequest(
            topic=topic,
            experience_level=level,
            include_soft_skills=True,
        )
        
        result = await agent.recommend(request)
        
        return {
            "topic": topic,
            "level": level,
            "core_skills": result.core_skills[:5],
            "soft_skills": result.soft_skills[:3],
            "learning_order": result.learning_order[:5],
            "job_market_demand": result.job_market_demand
        }
        
    except Exception as e:
        logger.error(f"Error getting quick skill recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get(
    "/tools",
    summary="Get Quick Tools Recommendations",
    description="Get tool recommendations with minimal input"
)
async def get_quick_tools(
    topic: str = "Web Development",
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
):
    """Get quick tools recommendations."""
    try:
        agent = SkillsToolsRecommenderAgent()
        
        request = SkillsToolsRequest(
            topic=topic,
            experience_level=level,
            include_soft_skills=False,
        )
        
        result = await agent.recommend(request)
        
        return {
            "topic": topic,
            "level": level,
            "essential_tools": result.essential_tools[:5],
            "emerging_tools": result.emerging_tools[:3],
            "recommended_stack": result.recommended_stack,
            "industry_trends": result.industry_trends[:4]
        }
        
    except Exception as e:
        logger.error(f"Error getting quick tool recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
