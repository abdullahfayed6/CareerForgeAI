"""
Student Identity & Career Profiling Agent Schemas

Data models for collecting and storing structured student profiles
used by other AI agents in the education platform.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# ============================================
# Enums for Profile Levels
# ============================================

class CareerGoalType(str, Enum):
    """Type of career goal."""
    INTERNSHIP = "internship"
    FIRST_JOB = "first_job"
    CAREER_SWITCH = "career_switch"
    PROMOTION = "promotion"


class EducationLevel(str, Enum):
    """Student's education level."""
    SCHOOL = "school"
    UNIVERSITY = "university"
    GRADUATE = "graduate"
    SELF_TAUGHT = "self_taught"


class SkillRating(str, Enum):
    """Skill rating from 1-5."""
    LEVEL_1 = "1"
    LEVEL_2 = "2"
    LEVEL_3 = "3"
    LEVEL_4 = "4"
    LEVEL_5 = "5"


class LearningStyle(str, Enum):
    """Preferred learning style."""
    VIDEOS = "videos"
    READING = "reading"
    PRACTICE = "practice"
    STORIES_EXAMPLES = "stories_examples"
    MIXED = "mixed"


class LearningApproach(str, Enum):
    """Preferred learning approach."""
    STEP_BY_STEP = "step_by_step"
    HARD_CHALLENGES_FIRST = "hard_challenges_first"


class PsychologicalState(str, Enum):
    """Student's psychological state."""
    CONFIDENT = "confident"
    NEUTRAL = "neutral"
    OVERWHELMED = "overwhelmed"


class EstimatedLevel(str, Enum):
    """Estimated proficiency level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class WorkModel(str, Enum):
    """Preferred work model."""
    STABLE_JOB = "stable_job"
    FREELANCING = "freelancing"
    STARTUP = "startup"


class PriorityValue(str, Enum):
    """What matters most to the student."""
    SALARY = "salary"
    PASSION = "passion"
    FLEXIBILITY = "flexibility"
    PRESTIGE = "prestige"


class ObstacleType(str, Enum):
    """Types of obstacles students face."""
    UNDERSTANDING_THEORY = "understanding_theory"
    WRITING_CODE = "writing_code"
    FINISHING_PROJECTS = "finishing_projects"
    STAYING_CONSISTENT = "staying_consistent"
    ENGLISH = "english"
    INTERVIEWS = "interviews"
    OTHER = "other"


# ============================================
# Skill Ratings Model
# ============================================

class SkillRatings(BaseModel):
    """Self-rated skill levels."""
    coding: SkillRating = Field(default=SkillRating.LEVEL_3, description="Coding ability (1-5)")
    problem_solving: SkillRating = Field(default=SkillRating.LEVEL_3, description="Problem solving ability (1-5)")
    math_logic: SkillRating = Field(default=SkillRating.LEVEL_3, description="Math and logic ability (1-5)")
    debugging: SkillRating = Field(default=SkillRating.LEVEL_3, description="Debugging ability (1-5)")


# ============================================
# Student Profile - Main Output Model
# ============================================

class StudentProfile(BaseModel):
    """
    Complete structured student profile used by other AI agents.
    This is the main output of the profiling agent.
    """
    # Career Direction
    career_goal: str = Field(..., description="Career path the student is aiming for")
    target_role: str = Field(..., description="Job title they want in 2-3 years")
    goal_type: CareerGoalType = Field(
        default=CareerGoalType.FIRST_JOB,
        description="Type of career goal: internship, first job, career switch, or promotion"
    )
    
    # Current Background
    education_level: EducationLevel = Field(
        default=EducationLevel.UNIVERSITY,
        description="Current education level"
    )
    field_of_study: str = Field(default="", description="Field of study")
    experience_duration: str = Field(default="", description="How long studying this field")
    project_experience: str = Field(default="", description="Description of real projects built")
    
    # Skill Map
    technical_skills: List[str] = Field(
        default_factory=list,
        description="Programming languages known"
    )
    tool_experience: List[str] = Field(
        default_factory=list,
        description="Tools used (Excel, Git, SQL, TensorFlow, React, etc.)"
    )
    skill_ratings: SkillRatings = Field(
        default_factory=SkillRatings,
        description="Self-rated abilities in coding, problem solving, math, debugging"
    )
    can_explain_projects: bool = Field(
        default=False,
        description="Whether student can explain a project they built"
    )
    can_read_docs: bool = Field(
        default=False,
        description="Whether student can understand documentation independently"
    )
    
    # Learning Profile
    learning_style: LearningStyle = Field(
        default=LearningStyle.MIXED,
        description="Preferred learning method"
    )
    learning_approach: LearningApproach = Field(
        default=LearningApproach.STEP_BY_STEP,
        description="Preferred learning approach"
    )
    study_time_per_week: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Hours available for study per week"
    )
    
    # Obstacles & Weaknesses
    main_weaknesses: List[str] = Field(
        default_factory=list,
        description="Main obstacles and struggles"
    )
    past_blockers: str = Field(
        default="",
        description="What stopped them from progressing before"
    )
    psychological_state: PsychologicalState = Field(
        default=PsychologicalState.NEUTRAL,
        description="Overall psychological state: confident, neutral, or overwhelmed"
    )
    
    # Motivation & Work Style
    motivation_reason: str = Field(
        default="",
        description="Why they want this career"
    )
    preferred_work_model: WorkModel = Field(
        default=WorkModel.STABLE_JOB,
        description="Preferred work arrangement"
    )
    priority_value: PriorityValue = Field(
        default=PriorityValue.PASSION,
        description="What matters most to them"
    )
    
    # AI-Computed Fields
    estimated_level: EstimatedLevel = Field(
        default=EstimatedLevel.BEGINNER,
        description="AI-estimated proficiency level"
    )
    readiness_risk_areas: List[str] = Field(
        default_factory=list,
        description="Areas where the student would fail in a real job tomorrow"
    )
    
    # Metadata
    profile_created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the profile was created"
    )
    profile_version: str = Field(
        default="1.0",
        description="Profile schema version"
    )


# ============================================
# Conversation State Management
# ============================================

class ProfilingSection(str, Enum):
    """Sections of the profiling conversation."""
    INTRO = "intro"
    CAREER_DIRECTION = "career_direction"
    CURRENT_BACKGROUND = "current_background"
    SKILL_MAP = "skill_map"
    LEARNING_PROFILE = "learning_profile"
    OBSTACLES = "obstacles"
    MOTIVATION = "motivation"
    COMPLETE = "complete"


class ProfilingConversation(BaseModel):
    """Tracks the state of a profiling conversation."""
    session_id: str = Field(..., description="Unique session ID")
    current_section: ProfilingSection = Field(
        default=ProfilingSection.INTRO,
        description="Current section of the profiling process"
    )
    collected_data: Dict = Field(
        default_factory=dict,
        description="Data collected so far"
    )
    messages: List[Dict] = Field(
        default_factory=list,
        description="Conversation history"
    )
    follow_up_needed: bool = Field(
        default=False,
        description="Whether a follow-up question is needed"
    )
    pending_clarification: Optional[str] = Field(
        default=None,
        description="Topic needing clarification"
    )
    created_at: datetime = Field(
        default_factory=datetime.now
    )
    updated_at: datetime = Field(
        default_factory=datetime.now
    )


# ============================================
# API Request/Response Models
# ============================================

class StartProfilingRequest(BaseModel):
    """Request to start a new profiling session."""
    student_name: Optional[str] = Field(None, example="Ahmed")
    language: str = Field(default="en", example="en", description="Language for conversation")


class StartProfilingResponse(BaseModel):
    """Response when starting a new profiling session."""
    session_id: str = Field(..., description="Session ID to use for subsequent messages")
    message: str = Field(..., description="Welcome message from the agent")
    current_section: str = Field(..., description="Current section of profiling")


class ProfilingMessageRequest(BaseModel):
    """Request to send a message in the profiling conversation."""
    session_id: str = Field(..., description="Session ID from start profiling")
    message: str = Field(..., description="Student's response message")


class ProfilingMessageResponse(BaseModel):
    """Response from the profiling agent."""
    session_id: str
    agent_message: str = Field(..., description="Agent's response/next question")
    current_section: str = Field(..., description="Current section")
    is_complete: bool = Field(default=False, description="Whether profiling is complete")
    progress_percentage: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Progress through the profiling process"
    )


class ProfilingCompleteResponse(BaseModel):
    """Response when profiling is complete."""
    session_id: str
    message: str = Field(..., description="Completion message")
    profile: StudentProfile = Field(..., description="Generated student profile")
    summary: str = Field(..., description="Human-readable summary of the profile")


class QuickProfileRequest(BaseModel):
    """Request for generating a profile from direct input (non-conversational)."""
    # Career Direction
    career_goal: str = Field(..., example="AI Engineer")
    target_role: str = Field(..., example="Machine Learning Engineer")
    goal_type: str = Field(default="first_job", example="first_job")
    
    # Background
    education_level: str = Field(default="university", example="university")
    field_of_study: str = Field(default="", example="Computer Science")
    experience_duration: str = Field(default="", example="2 years")
    project_experience: str = Field(default="", example="Built a sentiment analysis model")
    
    # Skills
    technical_skills: List[str] = Field(
        default_factory=list,
        example=["Python", "JavaScript", "SQL"]
    )
    tool_experience: List[str] = Field(
        default_factory=list,
        example=["Git", "TensorFlow", "React"]
    )
    coding_rating: int = Field(default=3, ge=1, le=5)
    problem_solving_rating: int = Field(default=3, ge=1, le=5)
    math_logic_rating: int = Field(default=3, ge=1, le=5)
    debugging_rating: int = Field(default=3, ge=1, le=5)
    
    # Learning
    learning_style: str = Field(default="mixed", example="practice")
    learning_approach: str = Field(default="step_by_step", example="step_by_step")
    study_hours_per_week: int = Field(default=10, ge=1, le=60)
    
    # Obstacles
    main_weaknesses: List[str] = Field(
        default_factory=list,
        example=["Finishing projects", "Interviews"]
    )
    psychological_state: str = Field(default="neutral", example="neutral")
    
    # Motivation
    motivation_reason: str = Field(default="", example="Passionate about AI")
    preferred_work_model: str = Field(default="stable_job", example="stable_job")
    priority_value: str = Field(default="passion", example="passion")


class GetProfileRequest(BaseModel):
    """Request to get an existing profile."""
    session_id: str = Field(..., description="Session ID of the completed profiling")


class ProfileSummaryResponse(BaseModel):
    """Summary response of a student profile."""
    career_goal: str
    target_role: str
    estimated_level: str
    top_skills: List[str]
    main_weaknesses: List[str]
    readiness_risk_areas: List[str]
    psychological_state: str
    recommendation: str = Field(..., description="AI recommendation for next steps")
