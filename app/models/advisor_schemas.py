"""
Advisor Agent Schemas

Data models for the Student Life & Tech Mentor Advisor Agent.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# ============================================
# Enums for State Levels
# ============================================

class Level(str, Enum):
    """Generic level enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SkillLevel(str, Enum):
    """Student skill level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UnderstandingLevel(str, Enum):
    """Understanding level for current topic."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SleepQuality(str, Enum):
    """Sleep quality level."""
    POOR = "poor"
    NORMAL = "normal"
    GOOD = "good"


# ============================================
# Input Models - Student State
# ============================================

class StudentProfile(BaseModel):
    """Student's profile and goals."""
    career_goal: str = Field(..., description="Student's career goal", example="Become a Data Scientist")
    current_level: SkillLevel = Field(default=SkillLevel.BEGINNER, example="intermediate")
    field_of_interest: str = Field(..., description="Main field of interest", example="Machine Learning")
    available_hours_per_day: float = Field(ge=0.5, le=16, default=4, example=4)


class LearningState(BaseModel):
    """Student's current learning state."""
    current_topic: str = Field(..., description="Topic currently studying", example="Neural Networks")
    understanding_level: UnderstandingLevel = Field(default=UnderstandingLevel.MEDIUM)
    recent_struggles: List[str] = Field(
        default_factory=list,
        example=["Understanding backpropagation", "Math concepts"]
    )
    consistency_level: Level = Field(default=Level.MEDIUM, description="How consistent is their studying")


class BehaviorState(BaseModel):
    """Student's behavioral patterns."""
    focus_level: Level = Field(default=Level.MEDIUM, description="Ability to focus")
    procrastination_level: Level = Field(default=Level.MEDIUM, description="Tendency to procrastinate")
    energy_level: Level = Field(default=Level.MEDIUM, description="Daily energy levels")
    sleep_quality: SleepQuality = Field(default=SleepQuality.NORMAL)


class EmotionalState(BaseModel):
    """Student's emotional/mental state."""
    motivation_level: Level = Field(default=Level.MEDIUM)
    stress_level: Level = Field(default=Level.MEDIUM)
    confidence_level: Level = Field(default=Level.MEDIUM)


class StudentState(BaseModel):
    """Complete student state for analysis."""
    student_profile: StudentProfile
    learning_state: LearningState
    behavior_state: BehaviorState
    emotional_state: EmotionalState


# ============================================
# Output Models - Advice Sections
# ============================================

class LearningAdvice(BaseModel):
    """Advice for learning and studying."""
    study_approach: str = Field(..., description="How they should study their current topic")
    style_changes: List[str] = Field(..., description="What to change in study style")
    likely_mistakes: List[str] = Field(..., description="Mistakes they're likely making")
    technique_to_try: str = Field(..., description="One specific technique to try today")
    icon: str = Field(default="📘")


class TechnicalCareerAdvice(BaseModel):
    """Advice for technical career growth."""
    priority_skill: str = Field(..., description="Skill area to prioritize next")
    recommended_focus: str = Field(
        ..., 
        description="What to focus on: theory, projects, fundamentals, or practice"
    )
    focus_reasoning: str = Field(..., description="Why this focus is recommended")
    career_action: str = Field(..., description="One career-building action to take")
    icon: str = Field(default="💻")


class ProductivityAdvice(BaseModel):
    """Advice for productivity and habits."""
    harmful_habit: str = Field(..., description="Daily habit hurting them most")
    habit_to_remove: str = Field(..., description="One habit to remove")
    habit_to_add: str = Field(..., description="One habit to add")
    day_structure: str = Field(..., description="How to structure their day")
    icon: str = Field(default="⏳")


class MindsetAdvice(BaseModel):
    """Advice for mindset and motivation."""
    wrong_belief: str = Field(..., description="A wrong belief they might have")
    better_thinking: str = Field(..., description="A better way to think")
    dealing_with_difficulty: str = Field(..., description="How to deal with frustration/slow progress")
    icon: str = Field(default="🧠")


class LifeBalanceAdvice(BaseModel):
    """Advice for life balance and wellness."""
    physical_impact: str = Field(..., description="How physical state affects learning")
    sleep_energy_advice: str = Field(..., description="Advice on sleep/energy/breaks")
    non_tech_action: str = Field(..., description="One non-tech action to improve performance")
    icon: str = Field(default="🌿")


class StudentAnalysis(BaseModel):
    """Analysis of student's current situation."""
    main_weaknesses: List[str] = Field(..., description="Main weaknesses identified")
    hidden_risks: List[str] = Field(..., description="Hidden risks: burnout, confusion, etc.")
    strengths_to_build: List[str] = Field(..., description="Strengths to build on")


class AdvisorResponse(BaseModel):
    """Complete advisor response with all advice sections."""
    # Summary
    situation_summary: str = Field(..., description="2-3 line summary of student situation")
    
    # Analysis
    analysis: StudentAnalysis
    
    # Advice Sections
    learning_advice: LearningAdvice
    technical_career_advice: TechnicalCareerAdvice
    productivity_advice: ProductivityAdvice
    mindset_advice: MindsetAdvice
    life_balance_advice: LifeBalanceAdvice
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    priority_focus: str = Field(..., description="The #1 thing to focus on right now")
    
    # Quick Actions
    quick_wins: List[str] = Field(
        default_factory=list,
        description="3 quick wins they can do today"
    )


# ============================================
# Request Models
# ============================================

class QuickAdvisorRequest(BaseModel):
    """Simplified request for quick advice."""
    # Profile
    career_goal: str = Field(..., example="Become a Full Stack Developer")
    current_level: str = Field(default="beginner", example="intermediate")
    field_of_interest: str = Field(..., example="Web Development")
    hours_per_day: float = Field(default=4, ge=0.5, le=16)
    
    # Learning
    current_topic: str = Field(..., example="React.js")
    understanding: str = Field(default="medium", example="low")
    struggles: List[str] = Field(default_factory=list, example=["State management", "Hooks"])
    study_consistency: str = Field(default="medium")
    
    # Behavior
    focus: str = Field(default="medium")
    procrastination: str = Field(default="medium")
    energy: str = Field(default="medium")
    sleep: str = Field(default="normal")
    
    # Emotional
    motivation: str = Field(default="medium")
    stress: str = Field(default="medium")
    confidence: str = Field(default="medium")


class DetailedAdvisorRequest(BaseModel):
    """Full detailed request matching the spec."""
    student_profile: StudentProfile
    learning_state: LearningState
    behavior_state: BehaviorState
    emotional_state: EmotionalState
