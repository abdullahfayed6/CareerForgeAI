"""
CV Creator Schemas

Data models for CV generation and skills collection.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategory(str, Enum):
    """Skill categories."""
    TECHNICAL = "technical"
    PROGRAMMING = "programming"
    FRAMEWORK = "framework"
    TOOL = "tool"
    DATABASE = "database"
    CLOUD = "cloud"
    SOFT_SKILL = "soft_skill"
    LANGUAGE = "language"
    OTHER = "other"


# ============================================
# Skills Models
# ============================================

class Skill(BaseModel):
    """Individual skill with details."""
    name: str = Field(..., description="Skill name")
    category: SkillCategory = Field(default=SkillCategory.TECHNICAL)
    level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE)
    years_experience: Optional[float] = Field(default=None, description="Years of experience")
    description: Optional[str] = Field(default=None, description="Brief description of experience")
    is_verified: bool = Field(default=False, description="Verified through projects/courses")
    source: Optional[str] = Field(default=None, description="Where this skill was learned/used")
    icon: str = Field(default="💡")


class SkillGroup(BaseModel):
    """Group of related skills."""
    category: str = Field(..., description="Category name")
    skills: List[Skill] = Field(default_factory=list)
    icon: str = Field(default="📚")


class SkillsProfile(BaseModel):
    """Complete skills profile for a student."""
    technical_skills: List[Skill] = Field(default_factory=list)
    programming_languages: List[Skill] = Field(default_factory=list)
    frameworks: List[Skill] = Field(default_factory=list)
    tools: List[Skill] = Field(default_factory=list)
    databases: List[Skill] = Field(default_factory=list)
    cloud_platforms: List[Skill] = Field(default_factory=list)
    soft_skills: List[Skill] = Field(default_factory=list)
    languages: List[Skill] = Field(default_factory=list)
    other_skills: List[Skill] = Field(default_factory=list)
    total_skills: int = Field(default=0)


# ============================================
# Education & Experience Models
# ============================================

class Education(BaseModel):
    """Education entry."""
    institution: str = Field(..., description="University/School name")
    degree: str = Field(..., description="Degree type (BS, MS, etc.)")
    field_of_study: str = Field(..., description="Major/Field")
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None, description="Or 'Present' if current")
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0)
    achievements: List[str] = Field(default_factory=list)
    relevant_coursework: List[str] = Field(default_factory=list)


class Experience(BaseModel):
    """Work/Internship experience entry."""
    company: str = Field(..., description="Company name")
    position: str = Field(..., description="Job title")
    location: Optional[str] = Field(default=None)
    start_date: str = Field(...)
    end_date: Optional[str] = Field(default=None, description="Or 'Present' if current")
    is_current: bool = Field(default=False)
    description: Optional[str] = Field(default=None)
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    skills_used: List[str] = Field(default_factory=list)
    experience_type: str = Field(default="work", description="work, internship, volunteer")


class Project(BaseModel):
    """Project entry."""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Brief description")
    role: Optional[str] = Field(default=None, description="Your role in the project")
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)
    technologies: List[str] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)
    url: Optional[str] = Field(default=None, description="Project/GitHub URL")
    is_team_project: bool = Field(default=False)


class Certification(BaseModel):
    """Certification entry."""
    name: str = Field(..., description="Certification name")
    issuer: str = Field(..., description="Issuing organization")
    issue_date: Optional[str] = Field(default=None)
    expiry_date: Optional[str] = Field(default=None)
    credential_id: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)


class Award(BaseModel):
    """Award/Achievement entry."""
    title: str = Field(..., description="Award title")
    issuer: str = Field(..., description="Issuing organization")
    date: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)


# ============================================
# Personal Info Models
# ============================================

class PersonalInfo(BaseModel):
    """Personal information for CV."""
    full_name: str = Field(..., description="Full name")
    email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None, description="City, Country")
    linkedin_url: Optional[str] = Field(default=None)
    github_url: Optional[str] = Field(default=None)
    portfolio_url: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None, description="Professional summary")


# ============================================
# Student Profile (Aggregated Data)
# ============================================

class StudentProfile(BaseModel):
    """Complete student profile from all sources."""
    # Personal Info
    personal_info: Optional[PersonalInfo] = None
    
    # Academic
    academic_year: Optional[int] = Field(default=None, ge=1, le=5)
    track: Optional[str] = Field(default=None, description="Major/Specialization")
    education: List[Education] = Field(default_factory=list)
    
    # Experience
    experiences: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    
    # Skills (from various sources)
    skills_from_interviews: List[str] = Field(default_factory=list)
    skills_from_courses: List[str] = Field(default_factory=list)
    skills_from_projects: List[str] = Field(default_factory=list)
    skills_from_experience: List[str] = Field(default_factory=list)
    skills_added_by_student: List[str] = Field(default_factory=list)
    
    # Certifications & Awards
    certifications: List[Certification] = Field(default_factory=list)
    awards: List[Award] = Field(default_factory=list)
    
    # Interests
    interests: List[str] = Field(default_factory=list)
    career_goals: Optional[str] = Field(default=None)


# ============================================
# CV Generation Models
# ============================================

class CVSection(BaseModel):
    """A section of the CV."""
    title: str = Field(..., description="Section title")
    content: Any = Field(..., description="Section content")
    order: int = Field(default=0, description="Order in CV")
    is_visible: bool = Field(default=True)


class GeneratedCV(BaseModel):
    """Complete generated CV."""
    # Header
    full_name: str
    title: Optional[str] = Field(default=None, description="Professional title")
    contact_info: Dict[str, str] = Field(default_factory=dict)
    
    # Summary
    professional_summary: str = Field(..., description="Professional summary paragraph")
    
    # Skills (organized)
    skills_profile: SkillsProfile
    
    # Education
    education: List[Education] = Field(default_factory=list)
    
    # Experience
    experiences: List[Experience] = Field(default_factory=list)
    
    # Projects
    projects: List[Project] = Field(default_factory=list)
    
    # Certifications
    certifications: List[Certification] = Field(default_factory=list)
    
    # Awards
    awards: List[Award] = Field(default_factory=list)
    
    # Additional
    languages: List[Dict[str, str]] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    cv_format: str = Field(default="standard", description="CV template format")
    target_role: Optional[str] = Field(default=None)
    
    # Tips
    improvement_suggestions: List[str] = Field(default_factory=list)
    missing_sections: List[str] = Field(default_factory=list)


# ============================================
# Request Models
# ============================================

class AddSkillsRequest(BaseModel):
    """Request to add skills manually."""
    skills: List[str] = Field(..., description="List of skill names to add")
    category: Optional[SkillCategory] = Field(default=None)
    level: Optional[SkillLevel] = Field(default=SkillLevel.INTERMEDIATE)


class CollectSkillsRequest(BaseModel):
    """Request to collect skills from various sources."""
    student_id: Optional[str] = Field(default=None)
    
    # Include skills from these sources
    include_interview_skills: bool = Field(default=True)
    include_course_skills: bool = Field(default=True)
    include_project_skills: bool = Field(default=True)
    include_experience_skills: bool = Field(default=True)
    
    # Manual additions
    additional_skills: List[str] = Field(default_factory=list)
    
    # Context for skill extraction
    interview_responses: Optional[List[str]] = Field(default=None)
    courses_taken: Optional[List[str]] = Field(default=None)
    project_descriptions: Optional[List[str]] = Field(default=None)
    experience_descriptions: Optional[List[str]] = Field(default=None)


class GenerateCVRequest(BaseModel):
    """Request to generate a CV."""
    # Student data
    student_profile: StudentProfile
    
    # Additional manual skills
    additional_skills: List[str] = Field(default_factory=list)
    
    # CV preferences
    target_role: Optional[str] = Field(default=None, description="Target job role")
    cv_format: str = Field(default="standard", description="standard, modern, academic")
    include_projects: bool = Field(default=True)
    include_certifications: bool = Field(default=True)
    max_experiences: int = Field(default=5)
    max_projects: int = Field(default=4)
    
    # Customization
    emphasize_skills: List[str] = Field(default_factory=list)
    hide_sections: List[str] = Field(default_factory=list)


class CVResponse(BaseModel):
    """Response containing generated CV."""
    success: bool
    cv: Optional[GeneratedCV] = None
    skills_collected: int = Field(default=0)
    message: str = Field(default="")
    suggestions: List[str] = Field(default_factory=list)
