"""API endpoints for the Advisor Agent - Student Life & Tech Mentor."""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.advisor_agent import AdvisorAgent
from app.models.advisor_schemas import (
    StudentState,
    StudentProfile,
    LearningState,
    BehaviorState,
    EmotionalState,
    AdvisorResponse,
    QuickAdvisorRequest,
    DetailedAdvisorRequest,
    Level,
    SkillLevel,
    UnderstandingLevel,
    SleepQuality
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advisor", tags=["Advisor - Student Mentor"])


# ============================================
# Request Models
# ============================================

class SimpleAdvisorRequest(BaseModel):
    """Simplified request for quick advice."""
    # Required
    career_goal: str = Field(..., example="Become a Data Scientist")
    current_topic: str = Field(..., example="Machine Learning")
    field_of_interest: str = Field(..., example="AI/ML")
    
    # Optional with defaults
    current_level: str = Field(default="beginner", example="intermediate")
    hours_per_day: float = Field(default=4, ge=0.5, le=16)
    struggles: List[str] = Field(default_factory=list, example=["Math concepts", "Model tuning"])
    
    # States (all default to medium)
    understanding: str = Field(default="medium")
    study_consistency: str = Field(default="medium")
    focus: str = Field(default="medium")
    procrastination: str = Field(default="medium")
    energy: str = Field(default="medium")
    sleep: str = Field(default="normal")
    motivation: str = Field(default="medium")
    stress: str = Field(default="medium")
    confidence: str = Field(default="medium")


class QuickCheckInRequest(BaseModel):
    """Quick check-in request."""
    current_topic: str = Field(..., example="React.js")
    career_goal: str = Field(..., example="Frontend Developer")
    motivation: str = Field(default="medium")
    energy: str = Field(default="medium")
    stress: str = Field(default="medium")


# ============================================
# Main Endpoints
# ============================================

@router.post(
    "/advice",
    response_model=AdvisorResponse,
    summary="Get Personalized Mentor Advice",
    description="""
## Get comprehensive personalized advice from your AI mentor

### What you'll receive:

🔍 **Situation Analysis**
- Main weaknesses identified
- Hidden risks (burnout, overload, etc.)
- Strengths to build on

📘 **Learning Advice**
- How to study your current topic
- Study style improvements
- Mistakes to avoid
- Technique to try today

💻 **Technical Career Advice**
- Priority skill to focus on
- Whether to: learn theory, build projects, revise, or practice
- One career-building action

⏳ **Productivity & Habits**
- Harmful habit to address
- Habit to remove and add
- How to structure your day

🧠 **Mindset Shift**
- Limiting belief to overcome
- Better way to think
- Handling frustration

🌿 **Life Balance**
- Physical state impact
- Sleep/energy advice
- Non-tech action to improve performance

### The advice is:
- Specific to YOUR situation
- Actionable and practical
- Honest but supportive
- From a mentor who understands real struggle
"""
)
async def get_advice(request: SimpleAdvisorRequest) -> AdvisorResponse:
    """Get comprehensive personalized advice based on current state."""
    try:
        agent = AdvisorAgent()
        
        # Convert to QuickAdvisorRequest
        quick_request = QuickAdvisorRequest(
            career_goal=request.career_goal,
            current_level=request.current_level,
            field_of_interest=request.field_of_interest,
            hours_per_day=request.hours_per_day,
            current_topic=request.current_topic,
            understanding=request.understanding,
            struggles=request.struggles,
            study_consistency=request.study_consistency,
            focus=request.focus,
            procrastination=request.procrastination,
            energy=request.energy,
            sleep=request.sleep,
            motivation=request.motivation,
            stress=request.stress,
            confidence=request.confidence
        )
        
        # Convert to StudentState
        state = AdvisorAgent.from_quick_request(quick_request)
        
        # Get advice
        result = await agent.get_advice(state)
        
        logger.info(f"Generated advice for student studying {request.current_topic}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting advice: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate advice: {str(e)}"
        )


@router.post(
    "/advice/detailed",
    response_model=AdvisorResponse,
    summary="Get Advice with Full State Details",
    description="Get advice with complete state specification"
)
async def get_detailed_advice(request: DetailedAdvisorRequest) -> AdvisorResponse:
    """Get advice with full detailed state."""
    try:
        agent = AdvisorAgent()
        
        state = StudentState(
            student_profile=request.student_profile,
            learning_state=request.learning_state,
            behavior_state=request.behavior_state,
            emotional_state=request.emotional_state
        )
        
        result = await agent.get_advice(state)
        return result
        
    except Exception as e:
        logger.error(f"Error getting detailed advice: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate advice: {str(e)}"
        )


@router.post(
    "/check-in",
    summary="Quick Mentor Check-In",
    description="""
## Quick check-in for brief encouragement and advice

Perfect for:
- Start of day motivation
- Mid-study boost
- When feeling stuck

Returns a brief, personalized message from your mentor.
"""
)
async def quick_check_in(request: QuickCheckInRequest) -> dict:
    """Quick check-in for brief encouragement."""
    try:
        agent = AdvisorAgent()
        
        message = await agent.quick_check_in(
            current_topic=request.current_topic,
            career_goal=request.career_goal,
            motivation=request.motivation,
            energy=request.energy,
            stress=request.stress
        )
        
        return {
            "message": message,
            "topic": request.current_topic,
            "timestamp": "now"
        }
        
    except Exception as e:
        logger.error(f"Error in check-in: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate check-in message: {str(e)}"
        )


# ============================================
# Specialized Endpoints
# ============================================

@router.post(
    "/learning",
    summary="Get Learning-Focused Advice",
    description="Get advice focused specifically on learning and studying"
)
async def get_learning_advice(
    current_topic: str,
    understanding: str = "medium",
    struggles: List[str] = None,
    hours_available: float = 4
) -> dict:
    """Get focused learning advice."""
    try:
        agent = AdvisorAgent()
        
        request = QuickAdvisorRequest(
            career_goal="Learning effectively",
            current_level="intermediate",
            field_of_interest=current_topic,
            hours_per_day=hours_available,
            current_topic=current_topic,
            understanding=understanding,
            struggles=struggles or []
        )
        
        state = AdvisorAgent.from_quick_request(request)
        result = await agent.get_advice(state)
        
        return {
            "topic": current_topic,
            "learning_advice": result.learning_advice,
            "technique_to_try": result.learning_advice.technique_to_try,
            "quick_wins": result.quick_wins[:2]
        }
        
    except Exception as e:
        logger.error(f"Error getting learning advice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/productivity",
    summary="Get Productivity-Focused Advice",
    description="Get advice focused specifically on productivity and habits"
)
async def get_productivity_advice(
    focus_level: str = "medium",
    procrastination_level: str = "medium",
    energy_level: str = "medium"
) -> dict:
    """Get focused productivity advice."""
    try:
        agent = AdvisorAgent()
        
        request = QuickAdvisorRequest(
            career_goal="Be more productive",
            current_level="intermediate",
            field_of_interest="Productivity",
            hours_per_day=4,
            current_topic="Current work",
            focus=focus_level,
            procrastination=procrastination_level,
            energy=energy_level
        )
        
        state = AdvisorAgent.from_quick_request(request)
        result = await agent.get_advice(state)
        
        return {
            "productivity_advice": result.productivity_advice,
            "day_structure": result.productivity_advice.day_structure,
            "habit_to_add": result.productivity_advice.habit_to_add,
            "quick_wins": result.quick_wins
        }
        
    except Exception as e:
        logger.error(f"Error getting productivity advice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/mindset",
    summary="Get Mindset & Motivation Advice",
    description="Get advice for dealing with motivation and mental blocks"
)
async def get_mindset_advice(
    motivation_level: str = "medium",
    stress_level: str = "medium",
    confidence_level: str = "medium",
    main_struggle: str = None
) -> dict:
    """Get focused mindset advice."""
    try:
        agent = AdvisorAgent()
        
        request = QuickAdvisorRequest(
            career_goal="Build better mindset",
            current_level="intermediate",
            field_of_interest="Personal growth",
            hours_per_day=4,
            current_topic=main_struggle or "Current challenge",
            motivation=motivation_level,
            stress=stress_level,
            confidence=confidence_level,
            struggles=[main_struggle] if main_struggle else []
        )
        
        state = AdvisorAgent.from_quick_request(request)
        result = await agent.get_advice(state)
        
        return {
            "situation": result.situation_summary,
            "mindset_advice": result.mindset_advice,
            "life_balance_advice": result.life_balance_advice,
            "priority_focus": result.priority_focus,
            "quick_wins": result.quick_wins
        }
        
    except Exception as e:
        logger.error(f"Error getting mindset advice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Utility Endpoints
# ============================================

@router.get(
    "/states",
    summary="Get State Options",
    description="Get available options for all state levels"
)
async def get_state_options() -> dict:
    """Get available state level options."""
    return {
        "levels": {
            "low": "Struggling / Below average",
            "medium": "Average / Okay",
            "high": "Good / Above average"
        },
        "skill_levels": {
            "beginner": "Just starting out",
            "intermediate": "Some experience",
            "advanced": "Significant experience"
        },
        "sleep_quality": {
            "poor": "Less than 5-6 hours, restless",
            "normal": "6-7 hours, okay quality",
            "good": "7-8+ hours, restful"
        },
        "state_categories": {
            "learning": ["understanding", "study_consistency"],
            "behavior": ["focus", "procrastination", "energy", "sleep"],
            "emotional": ["motivation", "stress", "confidence"]
        }
    }


@router.get(
    "/prompts",
    summary="Get Self-Reflection Prompts",
    description="Get prompts to help students self-assess"
)
async def get_reflection_prompts() -> dict:
    """Get prompts for self-reflection."""
    return {
        "learning_prompts": [
            "What topic am I currently studying?",
            "On a scale of 1-10, how well do I understand it?",
            "What specific part confuses me?",
            "When did I last study consistently for a week?"
        ],
        "behavior_prompts": [
            "How easily can I focus for 30 minutes straight?",
            "How often do I delay starting my work?",
            "Do I feel energized or tired during study time?",
            "How was my sleep last night?"
        ],
        "emotional_prompts": [
            "How excited am I about my learning goals?",
            "How stressed do I feel about deadlines/progress?",
            "Do I believe I can achieve my career goal?"
        ],
        "career_prompts": [
            "What is my dream job/role?",
            "What skills does that role require?",
            "How many hours can I realistically dedicate daily?"
        ]
    }
