"""Career Translator data models."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


# Input Models
class LectureInput(BaseModel):
    """Input from other agents or API."""
    lecture_topic: str = Field(description="The topic of the lecture")
    lecture_text: Optional[str] = Field(default=None, description="Optional detailed lecture content")
    target_track: Optional[str] = Field(default=None, description="Target career track (e.g., 'Data Scientist', 'Backend Developer', 'DevOps Engineer')")


# ============================================================
# OVERVIEW & CONTEXT SECTION
# ============================================================

class TopicOverview(BaseModel):
    """Quick overview of the topic."""
    one_liner: str = Field(description="One-sentence summary of what this topic is about")
    importance_level: str = Field(description="Critical / High / Medium - how important for the career track")
    difficulty: str = Field(description="Beginner / Intermediate / Advanced")
    estimated_learning_time: str = Field(description="Time to understand basics (e.g., '2-4 hours', '1-2 days')")
    key_takeaway: str = Field(description="The single most important thing to remember")


class LifeStoryExplanation(BaseModel):
    """Real-life story that explains the concept intuitively."""
    story_title: str = Field(description="Short relatable title for the story")
    story: str = Field(description="A simple real-life story using everyday situations")
    concept_mapping: str = Field(description="Explanation of how story elements map to the technical concept")


class PrerequisiteTopic(BaseModel):
    """A prerequisite topic required before studying the main lecture."""
    topic: str = Field(description="Prerequisite topic name")
    why_needed: str = Field(description="How it directly supports understanding the lecture")
    risk_if_missing: str = Field(description="What confusion or mistakes happen without it")


class PrerequisiteKnowledge(BaseModel):
    """Essential prerequisite knowledge before studying the lecture."""
    why_prerequisites_matter: str = Field(description="Why missing foundations cause problems")
    required_topics: List[PrerequisiteTopic] = Field(description="5 essential prerequisite topics")


# ============================================================
# REAL-WORLD APPLICATION SECTION
# ============================================================

class RealWorldRelevance(BaseModel):
    """Real-world relevance of the lecture topic."""
    where_used: List[str] = Field(description="System/context examples where this is used")
    problems_it_solves: List[str] = Field(description="Real problems this concept solves")
    risk_if_not_known: str = Field(description="Production failure or business impact if not understood")


class IndustryUseCase(BaseModel):
    """Industry use case for the concept."""
    domain: str = Field(description="AI / Backend / Cloud / Security / etc")
    scenario: str = Field(description="Real situation where this is applied")
    how_concept_is_used: str = Field(description="Practical application details")


class ProductionChallenge(BaseModel):
    """Real production engineering challenge."""
    challenge: str = Field(description="Common real-world issue engineers face with this topic")
    why_it_happens: str = Field(description="Technical, system, scale, or data reason behind the issue")
    professional_solution: str = Field(description="How experienced engineers solve or prevent it in production")


# ============================================================
# HANDS-ON TASKS SECTION
# ============================================================

class CompanyStyleTask(BaseModel):
    """Company-style practical task."""
    task_title: str = Field(description="Short realistic title")
    company_context: str = Field(description="Startup / Big tech / Product team situation")
    your_mission: str = Field(description="What the learner must do")
    constraints: List[str] = Field(description="Time, performance, data, cost limits")
    expected_output: str = Field(description="Deliverable expected")
    difficulty_level: str = Field(default="Intermediate", description="Beginner / Intermediate / Advanced")


class AdvancedChallenge(BaseModel):
    """Industry-level advanced challenge."""
    title: str = Field(description="Challenge title")
    description: str = Field(description="Hard real-world extension problem")


# ============================================================
# SKILLS & CAREER SECTION
# ============================================================

class SkillsBuilt(BaseModel):
    """Skills developed from learning this concept."""
    technical: List[str] = Field(description="Hard skills developed")
    engineering_thinking: List[str] = Field(description="System design thinking, performance awareness")
    problem_solving: List[str] = Field(description="Debugging, optimization skills")
    team_relevance: List[str] = Field(description="Collaboration impact")


class CareerImpact(BaseModel):
    """Career impact of mastering this concept."""
    relevant_roles: List[str] = Field(description="ML Engineer, Backend Dev, etc")
    interview_relevance: str = Field(description="How it appears in interviews")
    junior_vs_senior_difference: str = Field(description="How seniors apply this differently")


# ============================================================
# LEARNING PATH SECTION
# ============================================================

class LearningAdvice(BaseModel):
    """Actionable learning advice for mastering the topic."""
    advice_title: str = Field(description="Short actionable advice title")
    what_to_do: str = Field(description="Specific action the learner should take")
    why_this_matters: str = Field(description="How this improves understanding or real-world ability")
    common_mistake_to_avoid: str = Field(description="Typical learner error related to this advice")


class QuickReference(BaseModel):
    """Quick reference for the topic."""
    key_terms: List[str] = Field(description="5 key terms/concepts to remember")
    common_tools: List[str] = Field(description="Tools/libraries commonly used with this concept")
    related_topics: List[str] = Field(description="Topics to explore next")
    resources: List[str] = Field(description="Recommended resources (docs, tutorials, books)")


# ============================================================
# MAIN OUTPUT MODEL - REORDERED FOR BETTER FLOW
# ============================================================

class CareerTranslation(BaseModel):
    """
    Complete career translation output - structured for readability.
    
    Response Flow:
    1. Overview & Context - Understand what this is
    2. Prerequisites - What you need to know first
    3. Intuitive Understanding - Life story explanation
    4. Real-World Application - Where and how it's used
    5. Hands-On Practice - Tasks to build skills
    6. Skills & Career - What you gain
    7. Learning Path - How to master it
    8. Quick Reference - Cheat sheet
    """
    
    # 1. OVERVIEW & CONTEXT
    lecture_topic: str = Field(description="The main topic being translated")
    topic_overview: TopicOverview = Field(
        description="Quick overview with importance, difficulty, and key takeaway"
    )
    
    # 2. PREREQUISITES
    prerequisite_knowledge: PrerequisiteKnowledge = Field(
        description="5 essential topics required before studying this lecture"
    )
    
    # 3. INTUITIVE UNDERSTANDING
    life_story_explanation: LifeStoryExplanation = Field(
        description="Real-life story that explains the concept intuitively"
    )
    
    # 4. REAL-WORLD APPLICATION
    real_world_relevance: RealWorldRelevance = Field(
        description="Where this is used and why it matters"
    )
    industry_use_cases: List[IndustryUseCase] = Field(
        description="3 industry use cases showing practical application"
    )
    production_challenges: List[ProductionChallenge] = Field(
        description="7 most common real engineering challenges related to this topic"
    )
    
    # 5. HANDS-ON PRACTICE
    company_style_tasks: List[CompanyStyleTask] = Field(
        description="3 company-style tasks to practice the concept"
    )
    advanced_challenge: AdvancedChallenge = Field(
        description="Industry-level advanced challenge for mastery"
    )
    
    # 6. SKILLS & CAREER
    skills_built: SkillsBuilt = Field(
        description="Skills developed from learning this concept"
    )
    career_impact: CareerImpact = Field(
        description="How this impacts your career and interviews"
    )
    
    # 7. LEARNING PATH
    learning_success_advice: List[LearningAdvice] = Field(
        description="10 practical pieces of advice to help learner succeed"
    )
    
    # 8. QUICK REFERENCE
    quick_reference: QuickReference = Field(
        description="Quick reference cheat sheet with key terms, tools, and resources"
    )


# API Request/Response Models
class TranslateLectureRequest(BaseModel):
    """API request to translate a lecture."""
    lecture_topic: str = Field(description="The topic of the lecture")
    lecture_text: Optional[str] = Field(default=None, description="Optional detailed lecture content")
    target_track: Optional[str] = Field(default=None, description="Target career track (e.g., 'Data Scientist', 'Backend Developer', 'DevOps Engineer')")


class TranslateLectureResponse(BaseModel):
    """API response with career translation."""
    success: bool = True
    data: CareerTranslation
