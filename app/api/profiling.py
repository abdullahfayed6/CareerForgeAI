"""API endpoints for the Student Identity & Career Profiling Agent."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.profiling_agent import ProfilingAgent
from app.models.profiling_schemas import (
    StudentProfile,
    StartProfilingRequest,
    StartProfilingResponse,
    ProfilingMessageRequest,
    ProfilingMessageResponse,
    ProfilingCompleteResponse,
    QuickProfileRequest,
    ProfileSummaryResponse,
    GetProfileRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profiling", tags=["Student Profiling Agent"])


# ============================================
# Session-Based Conversational Endpoints
# ============================================

@router.post(
    "/start",
    response_model=StartProfilingResponse,
    summary="Start a New Profiling Session",
    description="""
## Start a Conversational Profiling Session

Begin a step-by-step conversation to build a comprehensive student profile.

### What happens:
1. You receive a session ID and welcome message
2. Use the session ID to send subsequent messages
3. The agent asks questions one at a time
4. After all questions, call /complete to get the final profile

### The agent collects:
- 🎯 Career Direction (goals, target role)
- 📚 Current Background (education, experience)
- 💻 Skill Map (technical skills, self-ratings)
- 📖 Learning Profile (style, study time)
- ⚠️ Obstacles & Weaknesses
- 💪 Motivation & Work Style

### Best for:
- New students who need guidance
- Detailed profiling with follow-up questions
- Students unsure about their goals
"""
)
async def start_profiling(request: StartProfilingRequest) -> StartProfilingResponse:
    """Start a new profiling session."""
    try:
        agent = ProfilingAgent()
        session_id, welcome_message = agent.start_session(
            student_name=request.student_name,
            language=request.language
        )
        
        logger.info(f"Started profiling session: {session_id}")
        
        return StartProfilingResponse(
            session_id=session_id,
            message=welcome_message,
            current_section="career_direction"
        )
    except Exception as e:
        logger.error(f"Error starting profiling session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/message",
    response_model=ProfilingMessageResponse,
    summary="Send a Message in Profiling Session",
    description="""
## Continue the Profiling Conversation

Send your response to the agent's questions.

### Response includes:
- Agent's next question or follow-up
- Current section of profiling
- Whether profiling is complete
- Progress percentage (0-100)

### Tips:
- Answer honestly for better personalization
- If you're unsure, say so - the agent will help
- Vague answers get follow-up questions
"""
)
async def send_message(request: ProfilingMessageRequest) -> ProfilingMessageResponse:
    """Send a message and receive the agent's response."""
    try:
        agent = ProfilingAgent()
        
        agent_message, current_section, is_complete, progress = await agent.process_message(
            session_id=request.session_id,
            user_message=request.message
        )
        
        logger.info(f"Processed message for session {request.session_id}, section: {current_section}")
        
        return ProfilingMessageResponse(
            session_id=request.session_id,
            agent_message=agent_message,
            current_section=current_section,
            is_complete=is_complete,
            progress_percentage=progress
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/complete",
    response_model=ProfilingCompleteResponse,
    summary="Complete Profiling and Get Profile",
    description="""
## Generate the Final Student Profile

Call this after the conversation is complete to generate the structured profile.

### The profile includes:
- Career goal and target role
- Education and experience
- Technical skills and ratings
- Learning preferences
- Weaknesses and obstacles
- **AI-Estimated Level** (Beginner/Intermediate/Advanced)
- **Readiness Risk Areas** (what they'd fail at in a real job)

### Use this profile with other agents:
- Advisor Agent for personalized mentorship
- Interview Agent for targeted practice
- Recommender Agent for relevant opportunities
"""
)
async def complete_profiling(request: GetProfileRequest) -> ProfilingCompleteResponse:
    """Complete profiling and generate the final profile."""
    try:
        agent = ProfilingAgent()
        
        # Generate the profile
        profile = await agent.generate_profile(request.session_id)
        
        # Generate a summary
        summary = await agent.generate_profile_summary(profile)
        
        logger.info(f"Completed profiling for session {request.session_id}")
        
        return ProfilingCompleteResponse(
            session_id=request.session_id,
            message="Your profile has been created successfully!",
            profile=profile,
            summary=summary
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error completing profiling: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Quick Profile (Non-Conversational)
# ============================================

@router.post(
    "/quick",
    response_model=StudentProfile,
    summary="Create Quick Profile (No Conversation)",
    description="""
## Create a Profile Directly

Skip the conversation and submit all information at once.

### Best for:
- Students who know exactly what they want
- API integrations
- Bulk profile creation
- Students with limited time

### AI still analyzes:
- Your estimated level (Beginner/Intermediate/Advanced)
- Readiness risk areas (job preparation gaps)
"""
)
async def create_quick_profile(request: QuickProfileRequest) -> StudentProfile:
    """Create a profile from direct input without conversation."""
    try:
        agent = ProfilingAgent()
        profile = await agent.create_quick_profile(request)
        
        logger.info(f"Created quick profile for {request.career_goal}")
        
        return profile
    except Exception as e:
        logger.error(f"Error creating quick profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/analyze",
    response_model=ProfileSummaryResponse,
    summary="Analyze Profile and Get Recommendations",
    description="""
## Get Profile Analysis and Recommendations

Submit profile data and receive:
- AI assessment of your level
- Top skills identified
- Main weaknesses
- Readiness risk areas
- Personalized recommendation for next steps
"""
)
async def analyze_profile(request: QuickProfileRequest) -> ProfileSummaryResponse:
    """Analyze a profile and get recommendations."""
    try:
        agent = ProfilingAgent()
        
        # Create profile
        profile = await agent.create_quick_profile(request)
        
        # Get summary with recommendations
        result = await agent.get_profile_recommendation(profile)
        
        logger.info(f"Analyzed profile for {request.career_goal}")
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Session Management
# ============================================

@router.get(
    "/session/{session_id}",
    summary="Get Session Status",
    description="Check the current status and progress of a profiling session."
)
async def get_session_status(session_id: str):
    """Get the status of a profiling session."""
    try:
        agent = ProfilingAgent()
        session = agent.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "current_section": session.current_section.value,
            "progress_percentage": agent._calculate_progress(session.current_section),
            "messages_count": len(session.messages),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/session/{session_id}",
    summary="Delete Profiling Session",
    description="Delete a profiling session and its data."
)
async def delete_session(session_id: str):
    """Delete a profiling session."""
    try:
        agent = ProfilingAgent()
        deleted = agent.delete_session(session_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Utility Endpoints
# ============================================

@router.get(
    "/sections",
    summary="Get Profiling Sections",
    description="Get information about the profiling sections and what data is collected."
)
async def get_profiling_sections():
    """Get information about profiling sections."""
    return {
        "sections": [
            {
                "id": "career_direction",
                "name": "Career Direction",
                "description": "Career path, target role, and goal type",
                "fields": ["career_goal", "target_role", "goal_type"]
            },
            {
                "id": "current_background",
                "name": "Current Background",
                "description": "Education, field of study, experience",
                "fields": ["education_level", "field_of_study", "experience_duration", "project_experience"]
            },
            {
                "id": "skill_map",
                "name": "Skill Map",
                "description": "Technical skills, tools, and self-ratings",
                "fields": ["technical_skills", "tool_experience", "skill_ratings"]
            },
            {
                "id": "learning_profile",
                "name": "Learning Profile",
                "description": "Learning style, approach, and study time",
                "fields": ["learning_style", "learning_approach", "study_time_per_week"]
            },
            {
                "id": "obstacles",
                "name": "Obstacles & Weaknesses",
                "description": "Struggles, blockers, and psychological state",
                "fields": ["main_weaknesses", "past_blockers", "psychological_state"]
            },
            {
                "id": "motivation",
                "name": "Motivation & Work Style",
                "description": "Why they want this career and work preferences",
                "fields": ["motivation_reason", "preferred_work_model", "priority_value"]
            }
        ],
        "ai_computed_fields": [
            {
                "field": "estimated_level",
                "description": "AI assessment of proficiency: Beginner, Intermediate, or Advanced"
            },
            {
                "field": "readiness_risk_areas",
                "description": "Areas where the student would fail in a real job"
            }
        ]
    }


@router.get(
    "/options",
    summary="Get Field Options",
    description="Get valid options for enum fields in the profile."
)
async def get_field_options():
    """Get valid options for profile fields."""
    return {
        "goal_type": ["internship", "first_job", "career_switch", "promotion"],
        "education_level": ["school", "university", "graduate", "self_taught"],
        "skill_rating": ["1", "2", "3", "4", "5"],
        "learning_style": ["videos", "reading", "practice", "stories_examples", "mixed"],
        "learning_approach": ["step_by_step", "hard_challenges_first"],
        "psychological_state": ["confident", "neutral", "overwhelmed"],
        "estimated_level": ["beginner", "intermediate", "advanced"],
        "work_model": ["stable_job", "freelancing", "startup"],
        "priority_value": ["salary", "passion", "flexibility", "prestige"],
        "obstacle_types": [
            "understanding_theory",
            "writing_code",
            "finishing_projects",
            "staying_consistent",
            "english",
            "interviews",
            "other"
        ]
    }
