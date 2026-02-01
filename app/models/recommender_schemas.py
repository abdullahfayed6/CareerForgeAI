"""Schemas for the Recommender Multi-Agent System."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field


# ============================================
# Common Models
# ============================================

class UserPreferences(BaseModel):
    """User preferences for recommendations."""
    academic_year: int = Field(ge=1, le=5, description="1-5 academic year")
    track: str = Field(..., description="Field of study or specialization")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    interests: List[str] = Field(default_factory=list, description="Areas of interest")
    location_preference: Literal["egypt", "abroad", "remote", "hybrid"] = Field(
        default="egypt",
        description="Location preference"
    )
    availability: Optional[str] = Field(None, description="When available (e.g., 'Summer 2025')")
    notes: Optional[str] = Field(None, description="Additional notes or requirements")


# ============================================
# Internship Recommender Models
# ============================================

class InternshipMatch(BaseModel):
    """A matched internship opportunity."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    work_type: str = Field(default="on-site", description="remote, hybrid, on-site")
    description: str = Field(..., description="Job description")
    requirements: List[str] = Field(default_factory=list, description="Job requirements")
    match_score: int = Field(ge=0, le=100, description="Match score 0-100")
    match_reasons: List[str] = Field(default_factory=list, description="Why this matches")
    skills_matched: List[str] = Field(default_factory=list, description="Skills that match")
    skills_to_develop: List[str] = Field(default_factory=list, description="Skills to learn for this role")
    application_url: Optional[str] = Field(None, description="Application link")
    deadline: Optional[str] = Field(None, description="Application deadline")
    icon: str = Field(default="💼", description="Display icon")


class InternshipRecommendation(BaseModel):
    """Complete internship recommendation response."""
    user_profile_summary: str = Field(..., description="Summary of user profile")
    total_matches: int = Field(..., description="Total opportunities found")
    top_recommendations: List[InternshipMatch] = Field(
        default_factory=list, 
        description="Top matching internships"
    )
    alternative_paths: List[str] = Field(
        default_factory=list, 
        description="Alternative career paths to consider"
    )
    skill_gaps: List[str] = Field(
        default_factory=list, 
        description="Skills to develop for better matches"
    )
    recommended_actions: List[str] = Field(
        default_factory=list, 
        description="Action items for the user"
    )
    search_tips: List[str] = Field(
        default_factory=list, 
        description="Tips for job searching"
    )


# ============================================
# Event/Hackathon Recommender Models
# ============================================

class EventType(BaseModel):
    """Type of event."""
    category: Literal["hackathon", "workshop", "conference", "bootcamp", "competition", "meetup", "webinar"]
    format: Literal["online", "in-person", "hybrid"]


class EventMatch(BaseModel):
    """A matched event or hackathon."""
    name: str = Field(..., description="Event name")
    organizer: str = Field(..., description="Event organizer")
    event_type: str = Field(..., description="hackathon, workshop, conference, etc.")
    format: str = Field(default="in-person", description="online, in-person, hybrid")
    location: Optional[str] = Field(None, description="Event location if in-person")
    date_range: str = Field(..., description="Event dates")
    description: str = Field(..., description="Event description")
    themes: List[str] = Field(default_factory=list, description="Event themes/tracks")
    prizes: Optional[str] = Field(None, description="Prizes or rewards")
    requirements: List[str] = Field(default_factory=list, description="Participation requirements")
    match_score: int = Field(ge=0, le=100, description="Match score 0-100")
    match_reasons: List[str] = Field(default_factory=list, description="Why this matches")
    skills_to_gain: List[str] = Field(default_factory=list, description="Skills you'll develop")
    networking_value: str = Field(default="medium", description="Networking opportunity level")
    registration_url: Optional[str] = Field(None, description="Registration link")
    registration_deadline: Optional[str] = Field(None, description="Registration deadline")
    difficulty_level: str = Field(default="intermediate", description="beginner, intermediate, advanced")
    team_size: Optional[str] = Field(None, description="Required team size")
    icon: str = Field(default="🎯", description="Display icon")


class EventRecommendation(BaseModel):
    """Complete event/hackathon recommendation response."""
    user_profile_summary: str = Field(..., description="Summary of user profile")
    total_events: int = Field(..., description="Total events found")
    hackathons: List[EventMatch] = Field(default_factory=list, description="Recommended hackathons")
    workshops: List[EventMatch] = Field(default_factory=list, description="Recommended workshops")
    conferences: List[EventMatch] = Field(default_factory=list, description="Recommended conferences")
    competitions: List[EventMatch] = Field(default_factory=list, description="Recommended competitions")
    meetups: List[EventMatch] = Field(default_factory=list, description="Recommended meetups")
    preparation_tips: List[str] = Field(
        default_factory=list, 
        description="Tips to prepare for events"
    )
    benefits: List[str] = Field(
        default_factory=list, 
        description="Benefits of participating"
    )
    upcoming_deadlines: List[dict] = Field(
        default_factory=list, 
        description="Events with upcoming deadlines"
    )


# ============================================
# Combined Recommendation Response
# ============================================

class FullRecommendation(BaseModel):
    """Complete recommendation from both agents."""
    request_id: UUID = Field(..., description="Request ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp")
    user_preferences: UserPreferences = Field(..., description="User input")
    internships: InternshipRecommendation = Field(..., description="Internship recommendations")
    events: EventRecommendation = Field(..., description="Event recommendations")
    personalized_roadmap: List[str] = Field(
        default_factory=list, 
        description="Personalized next steps"
    )


# ============================================
# Course/Certification Recommender Models
# ============================================

class CourseMatch(BaseModel):
    """A recommended course."""
    name: str = Field(..., description="Course name")
    provider: str = Field(..., description="Platform/Provider (Coursera, Udemy, etc.)")
    instructor: Optional[str] = Field(None, description="Instructor name")
    course_type: str = Field(default="course", description="course, specialization, bootcamp")
    difficulty: str = Field(default="intermediate", description="beginner, intermediate, advanced")
    duration: str = Field(..., description="Course duration (e.g., '4 weeks', '20 hours')")
    description: str = Field(..., description="Course description")
    topics_covered: List[str] = Field(default_factory=list, description="Key topics")
    skills_gained: List[str] = Field(default_factory=list, description="Skills you'll learn")
    match_score: int = Field(ge=0, le=100, description="Relevance score 0-100")
    match_reasons: List[str] = Field(default_factory=list, description="Why this matches")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Course rating")
    num_reviews: Optional[str] = Field(None, description="Number of reviews")
    price: str = Field(default="Free", description="Price or 'Free'")
    is_free: bool = Field(default=False, description="Whether the course is free")
    has_certificate: bool = Field(default=True, description="Offers certificate")
    url: Optional[str] = Field(None, description="Course URL")
    icon: str = Field(default="📚", description="Display icon")


class CertificationMatch(BaseModel):
    """A recommended certification."""
    name: str = Field(..., description="Certification name")
    issuer: str = Field(..., description="Issuing organization (Google, AWS, Microsoft, etc.)")
    certification_type: str = Field(default="professional", description="professional, associate, expert")
    difficulty: str = Field(default="intermediate", description="beginner, intermediate, advanced")
    description: str = Field(..., description="Certification description")
    skills_validated: List[str] = Field(default_factory=list, description="Skills this cert validates")
    prerequisites: List[str] = Field(default_factory=list, description="Required prerequisites")
    exam_details: str = Field(default="", description="Exam format and duration")
    preparation_time: str = Field(..., description="Typical prep time")
    match_score: int = Field(ge=0, le=100, description="Relevance score 0-100")
    match_reasons: List[str] = Field(default_factory=list, description="Why this matches")
    industry_recognition: str = Field(default="high", description="low, medium, high")
    validity_period: Optional[str] = Field(None, description="How long it's valid")
    cost: str = Field(default="Varies", description="Exam cost")
    url: Optional[str] = Field(None, description="Certification URL")
    icon: str = Field(default="🏅", description="Display icon")


class CourseRecommendation(BaseModel):
    """Complete course and certification recommendation response."""
    topic: str = Field(..., description="Topic searched")
    user_profile_summary: str = Field(..., description="Summary of user context")
    total_courses: int = Field(..., description="Total courses found")
    total_certifications: int = Field(..., description="Total certifications found")
    
    # Courses by category
    free_courses: List[CourseMatch] = Field(default_factory=list, description="Free courses")
    paid_courses: List[CourseMatch] = Field(default_factory=list, description="Paid courses")
    beginner_courses: List[CourseMatch] = Field(default_factory=list, description="Beginner-friendly")
    advanced_courses: List[CourseMatch] = Field(default_factory=list, description="Advanced courses")
    
    # Certifications
    certifications: List[CertificationMatch] = Field(default_factory=list, description="Recommended certifications")
    
    # Learning path
    recommended_learning_path: List[str] = Field(
        default_factory=list, 
        description="Suggested order to take courses"
    )
    time_to_proficiency: str = Field(default="3-6 months", description="Estimated time to become proficient")
    study_tips: List[str] = Field(default_factory=list, description="Study tips for this topic")


# ============================================
# Skills/Tools Recommender Models
# ============================================

class SkillMatch(BaseModel):
    """A recommended skill to learn."""
    name: str = Field(..., description="Skill name")
    category: str = Field(..., description="technical, soft, domain-specific")
    skill_type: str = Field(default="hard", description="hard, soft, hybrid")
    difficulty_to_learn: str = Field(default="medium", description="easy, medium, hard")
    time_to_learn: str = Field(..., description="Typical time to learn")
    description: str = Field(..., description="What this skill is about")
    why_important: str = Field(..., description="Why this skill matters")
    match_score: int = Field(ge=0, le=100, description="Relevance score 0-100")
    related_to_topic: List[str] = Field(default_factory=list, description="How it relates to the topic")
    job_demand: str = Field(default="high", description="low, medium, high, very high")
    salary_impact: str = Field(default="medium", description="low, medium, high")
    learning_resources: List[str] = Field(default_factory=list, description="Where to learn")
    prerequisites: List[str] = Field(default_factory=list, description="Skills needed first")
    icon: str = Field(default="💡", description="Display icon")


class ToolMatch(BaseModel):
    """A recommended tool to learn."""
    name: str = Field(..., description="Tool name")
    category: str = Field(..., description="IDE, framework, library, platform, etc.")
    tool_type: str = Field(..., description="software, library, framework, platform, service")
    description: str = Field(..., description="What this tool does")
    why_use: str = Field(..., description="Why use this tool")
    use_cases: List[str] = Field(default_factory=list, description="Common use cases")
    match_score: int = Field(ge=0, le=100, description="Relevance score 0-100")
    related_to_topic: List[str] = Field(default_factory=list, description="How it relates to the topic")
    difficulty_to_learn: str = Field(default="medium", description="easy, medium, hard")
    time_to_learn: str = Field(..., description="Time to become proficient")
    popularity: str = Field(default="high", description="low, medium, high, industry-standard")
    alternatives: List[str] = Field(default_factory=list, description="Alternative tools")
    is_free: bool = Field(default=True, description="Whether it's free")
    official_url: Optional[str] = Field(None, description="Official website")
    icon: str = Field(default="🔧", description="Display icon")


class SkillsToolsRecommendation(BaseModel):
    """Complete skills and tools recommendation response."""
    topic: str = Field(..., description="Topic searched")
    user_profile_summary: str = Field(..., description="Summary of user context")
    
    # Skills
    core_skills: List[SkillMatch] = Field(default_factory=list, description="Essential skills for this topic")
    complementary_skills: List[SkillMatch] = Field(default_factory=list, description="Skills that complement this topic")
    advanced_skills: List[SkillMatch] = Field(default_factory=list, description="Advanced skills to grow into")
    soft_skills: List[SkillMatch] = Field(default_factory=list, description="Relevant soft skills")
    
    # Tools
    essential_tools: List[ToolMatch] = Field(default_factory=list, description="Must-know tools")
    recommended_tools: List[ToolMatch] = Field(default_factory=list, description="Recommended tools")
    emerging_tools: List[ToolMatch] = Field(default_factory=list, description="New/trending tools")
    
    # Tech stack recommendations
    recommended_stack: List[str] = Field(default_factory=list, description="Recommended tech stack")
    learning_order: List[str] = Field(default_factory=list, description="Suggested order to learn")
    
    # Market insights
    industry_trends: List[str] = Field(default_factory=list, description="Current industry trends")
    job_market_demand: str = Field(default="high", description="Overall job market demand")


# ============================================
# Request Models
# ============================================

class InternshipRequest(BaseModel):
    """Request for internship recommendations."""
    preferences: UserPreferences
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum results to return")
    include_remote: bool = Field(default=True, description="Include remote opportunities")
    company_size_preference: Optional[Literal["startup", "mid-size", "enterprise", "any"]] = Field(
        default="any",
        description="Preferred company size"
    )


class EventRequest(BaseModel):
    """Request for event/hackathon recommendations."""
    preferences: UserPreferences
    event_types: List[str] = Field(
        default=["hackathon", "workshop", "competition"],
        description="Types of events to include"
    )
    timeframe: str = Field(
        default="next_3_months",
        description="Timeframe: next_month, next_3_months, next_6_months, anytime"
    )
    include_online: bool = Field(default=True, description="Include online events")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum results per category")


class CombinedRequest(BaseModel):
    """Request for both internship and event recommendations."""
    preferences: UserPreferences
    include_internships: bool = Field(default=True)
    include_events: bool = Field(default=True)
    max_results_per_category: int = Field(default=5, ge=1, le=20)


class CourseRequest(BaseModel):
    """Request for course and certification recommendations."""
    topic: str = Field(..., description="Topic to find courses for")
    current_level: str = Field(
        default="beginner",
        description="Current level: beginner, intermediate, advanced"
    )
    learning_goal: Optional[str] = Field(
        None,
        description="Specific learning goal or outcome"
    )
    time_available: str = Field(
        default="flexible",
        description="Time available: limited, moderate, flexible"
    )
    budget: str = Field(
        default="any",
        description="Budget: free_only, low, moderate, any"
    )
    prefer_certificates: bool = Field(default=True, description="Prefer courses with certificates")
    max_results: int = Field(default=10, ge=1, le=30, description="Max results per category")


class SkillsToolsRequest(BaseModel):
    """Request for skills and tools recommendations."""
    topic: str = Field(..., description="Topic to find skills/tools for")
    current_skills: List[str] = Field(
        default_factory=list,
        description="Skills the user already has"
    )
    career_goal: Optional[str] = Field(
        None,
        description="Career goal or target role"
    )
    experience_level: str = Field(
        default="intermediate",
        description="Experience level: beginner, intermediate, senior"
    )
    focus_area: Optional[str] = Field(
        None,
        description="Specific focus area within the topic"
    )
    include_soft_skills: bool = Field(default=True, description="Include soft skills")
    max_results: int = Field(default=10, ge=1, le=30, description="Max results per category")
