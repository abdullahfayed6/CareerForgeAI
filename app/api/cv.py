"""API endpoints for CV Creator Agent."""
from __future__ import annotations

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.cv_creator import CVCreatorAgent
from app.models.cv_schemas import (
    Skill,
    SkillLevel,
    SkillCategory,
    SkillsProfile,
    StudentProfile,
    PersonalInfo,
    Education,
    Experience,
    Project,
    Certification,
    Award,
    GeneratedCV,
    CVResponse,
    CollectSkillsRequest,
    GenerateCVRequest,
    AddSkillsRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cv", tags=["CV Creator"])


# ============================================
# Request Models for API
# ============================================

class QuickSkillsRequest(BaseModel):
    """Quick request to collect skills from text."""
    interview_responses: Optional[List[str]] = Field(
        default=None, 
        example=["I have experience with Python and machine learning projects"]
    )
    courses_taken: Optional[List[str]] = Field(
        default=None,
        example=["Data Structures", "Machine Learning", "Web Development"]
    )
    project_descriptions: Optional[List[str]] = Field(
        default=None,
        example=["Built a React web app with Node.js backend"]
    )
    experience_descriptions: Optional[List[str]] = Field(
        default=None,
        example=["Software Engineering Intern - worked with Python and AWS"]
    )
    additional_skills: List[str] = Field(
        default_factory=list,
        example=["Docker", "Git", "SQL"]
    )


class QuickCVRequest(BaseModel):
    """Quick request to generate CV with minimal input."""
    # Personal Info
    full_name: str = Field(..., example="Ahmed Mohamed")
    email: Optional[str] = Field(default=None, example="ahmed@example.com")
    phone: Optional[str] = Field(default=None, example="+20 123 456 7890")
    location: Optional[str] = Field(default=None, example="Cairo, Egypt")
    linkedin_url: Optional[str] = Field(default=None)
    github_url: Optional[str] = Field(default=None)
    
    # Academic
    academic_year: int = Field(ge=1, le=5, example=3)
    track: str = Field(..., example="Computer Science")
    university: Optional[str] = Field(default=None, example="Cairo University")
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0, example=3.5)
    
    # Skills from different sources
    skills_from_courses: List[str] = Field(default_factory=list, example=["Python", "Java"])
    skills_from_projects: List[str] = Field(default_factory=list, example=["React", "Node.js"])
    skills_from_experience: List[str] = Field(default_factory=list, example=["AWS", "Docker"])
    additional_skills: List[str] = Field(default_factory=list, example=["Git", "SQL"])
    
    # Experience (optional)
    experiences: Optional[List[dict]] = Field(default=None)
    
    # Projects (optional)
    projects: Optional[List[dict]] = Field(default=None)
    
    # Target
    target_role: Optional[str] = Field(default=None, example="Software Engineer")
    career_goal: Optional[str] = Field(default=None, example="Become a full-stack developer")


class ManualSkillsRequest(BaseModel):
    """Request to add manual skills."""
    skills: List[str] = Field(..., example=["Python", "JavaScript", "React"])
    category: str = Field(default="technical", example="programming")
    level: str = Field(default="intermediate", example="advanced")


# ============================================
# Skills Collection Endpoints
# ============================================

@router.post(
    "/skills/collect",
    response_model=SkillsProfile,
    summary="Collect Skills from Various Sources",
    description="""
## Collect and organize skills from multiple sources

### Data Sources:
- 💬 **Interview Responses**: Extract skills mentioned in interviews
- 📚 **Courses Taken**: Infer skills from course names
- 🚀 **Project Descriptions**: Extract technologies and skills from projects
- 💼 **Experience Descriptions**: Identify skills from work experience
- ✍️ **Manual Additions**: Skills added directly by the student

### Returns:
- Organized skills by category
- Proficiency level estimates
- Total skill count
"""
)
async def collect_skills(request: QuickSkillsRequest) -> SkillsProfile:
    """Collect and organize skills from provided information."""
    try:
        agent = CVCreatorAgent()
        
        full_request = CollectSkillsRequest(
            interview_responses=request.interview_responses,
            courses_taken=request.courses_taken,
            project_descriptions=request.project_descriptions,
            experience_descriptions=request.experience_descriptions,
            additional_skills=request.additional_skills,
        )
        
        result = await agent.collect_skills(full_request)
        
        logger.info(f"Collected {result.total_skills} skills")
        return result
        
    except Exception as e:
        logger.error(f"Error collecting skills: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect skills: {str(e)}"
        )


@router.post(
    "/skills/add",
    response_model=SkillsProfile,
    summary="Add Skills Manually",
    description="""
## Add skills manually to a profile

Students can directly add their own skills with:
- Skill names
- Category (technical, programming, soft_skill, etc.)
- Proficiency level (beginner, intermediate, advanced, expert)
"""
)
async def add_manual_skills(request: ManualSkillsRequest) -> SkillsProfile:
    """Add skills manually to a new profile."""
    try:
        agent = CVCreatorAgent()
        
        # Create empty profile
        profile = SkillsProfile()
        
        # Map category string to enum
        category_map = {
            "technical": SkillCategory.TECHNICAL,
            "programming": SkillCategory.PROGRAMMING,
            "framework": SkillCategory.FRAMEWORK,
            "tool": SkillCategory.TOOL,
            "database": SkillCategory.DATABASE,
            "cloud": SkillCategory.CLOUD,
            "soft_skill": SkillCategory.SOFT_SKILL,
            "language": SkillCategory.LANGUAGE,
            "other": SkillCategory.OTHER,
        }
        
        level_map = {
            "beginner": SkillLevel.BEGINNER,
            "intermediate": SkillLevel.INTERMEDIATE,
            "advanced": SkillLevel.ADVANCED,
            "expert": SkillLevel.EXPERT,
        }
        
        category = category_map.get(request.category.lower(), SkillCategory.TECHNICAL)
        level = level_map.get(request.level.lower(), SkillLevel.INTERMEDIATE)
        
        # Add skills
        result = agent.add_manual_skills(profile, request.skills, category, level)
        
        logger.info(f"Added {len(request.skills)} skills manually")
        return result
        
    except Exception as e:
        logger.error(f"Error adding skills: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add skills: {str(e)}"
        )


# ============================================
# CV Generation Endpoints
# ============================================

@router.post(
    "/generate",
    response_model=CVResponse,
    summary="Generate Professional CV",
    description="""
## Generate a complete professional CV

### Features:
- 📝 **Professional Summary**: AI-generated compelling summary
- 💡 **Skills Organization**: Categorized and prioritized skills
- 📊 **ATS-Friendly**: Optimized for Applicant Tracking Systems
- 💼 **Experience Formatting**: Professional experience descriptions
- 🎯 **Role Targeting**: Tailored to target role

### Input:
Provide student profile with education, experience, projects, and skills.

### Returns:
- Complete generated CV
- Improvement suggestions
- Missing sections to consider
"""
)
async def generate_cv(request: QuickCVRequest) -> CVResponse:
    """Generate a professional CV from student profile."""
    try:
        agent = CVCreatorAgent()
        
        # Build personal info
        personal_info = PersonalInfo(
            full_name=request.full_name,
            email=request.email,
            phone=request.phone,
            location=request.location,
            linkedin_url=request.linkedin_url,
            github_url=request.github_url,
        )
        
        # Build education
        education = []
        if request.university:
            education.append(Education(
                institution=request.university,
                degree="Bachelor of Science",
                field_of_study=request.track,
                start_date=str(2025 - request.academic_year),
                end_date=str(2025 + (4 - request.academic_year)),
                gpa=request.gpa,
            ))
        
        # Parse experiences if provided
        experiences = []
        if request.experiences:
            for exp in request.experiences:
                experiences.append(Experience(
                    company=exp.get("company", "Company"),
                    position=exp.get("position", "Position"),
                    location=exp.get("location"),
                    start_date=exp.get("start_date", "2024"),
                    end_date=exp.get("end_date"),
                    responsibilities=exp.get("responsibilities", []),
                    achievements=exp.get("achievements", []),
                    skills_used=exp.get("skills_used", []),
                    experience_type=exp.get("type", "internship"),
                ))
        
        # Parse projects if provided
        projects = []
        if request.projects:
            for proj in request.projects:
                projects.append(Project(
                    name=proj.get("name", "Project"),
                    description=proj.get("description", ""),
                    role=proj.get("role"),
                    technologies=proj.get("technologies", []),
                    highlights=proj.get("highlights", []),
                    url=proj.get("url"),
                ))
        
        # Build student profile
        student_profile = StudentProfile(
            personal_info=personal_info,
            academic_year=request.academic_year,
            track=request.track,
            education=education,
            experiences=experiences,
            projects=projects,
            skills_from_courses=request.skills_from_courses,
            skills_from_projects=request.skills_from_projects,
            skills_from_experience=request.skills_from_experience,
            skills_added_by_student=request.additional_skills,
            career_goals=request.career_goal,
        )
        
        # Generate CV
        full_request = GenerateCVRequest(
            student_profile=student_profile,
            additional_skills=[],
            target_role=request.target_role,
            cv_format="standard",
        )
        
        result = await agent.generate_cv(full_request)
        
        logger.info(f"Generated CV with {result.skills_collected} skills")
        return result
        
    except Exception as e:
        logger.error(f"Error generating CV: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate CV: {str(e)}"
        )


@router.post(
    "/generate/detailed",
    response_model=CVResponse,
    summary="Generate CV with Full Options",
    description="Generate CV with complete customization options"
)
async def generate_detailed_cv(request: GenerateCVRequest) -> CVResponse:
    """Generate CV with full customization options."""
    try:
        agent = CVCreatorAgent()
        result = await agent.generate_cv(request)
        return result
        
    except Exception as e:
        logger.error(f"Error generating CV: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate CV: {str(e)}"
        )


@router.post(
    "/summary",
    summary="Generate Professional Summary Only",
    description="Generate just the professional summary for a CV"
)
async def generate_summary(
    full_name: str = "Student",
    track: str = "Computer Science",
    academic_year: int = 3,
    skills: List[str] = None,
    target_role: str = None,
    career_goal: str = None
) -> dict:
    """Generate just the professional summary."""
    try:
        agent = CVCreatorAgent()
        
        profile = StudentProfile(
            personal_info=PersonalInfo(full_name=full_name),
            academic_year=academic_year,
            track=track,
            skills_added_by_student=skills or [],
            career_goals=career_goal,
        )
        
        summary = await agent.generate_summary(profile, target_role)
        
        return {
            "full_name": full_name,
            "target_role": target_role,
            "professional_summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )


# ============================================
# Quick Endpoints
# ============================================

@router.get(
    "/skills/categories",
    summary="Get Skill Categories",
    description="Get list of available skill categories"
)
async def get_skill_categories() -> dict:
    """Get available skill categories."""
    return {
        "categories": [
            {"id": "technical", "name": "Technical Skills", "icon": "⚙️"},
            {"id": "programming", "name": "Programming Languages", "icon": "💻"},
            {"id": "framework", "name": "Frameworks & Libraries", "icon": "🔧"},
            {"id": "tool", "name": "Tools & Software", "icon": "🛠️"},
            {"id": "database", "name": "Databases", "icon": "🗄️"},
            {"id": "cloud", "name": "Cloud Platforms", "icon": "☁️"},
            {"id": "soft_skill", "name": "Soft Skills", "icon": "🤝"},
            {"id": "language", "name": "Languages", "icon": "🌐"},
            {"id": "other", "name": "Other", "icon": "📌"},
        ],
        "levels": [
            {"id": "beginner", "name": "Beginner", "description": "Just learning"},
            {"id": "intermediate", "name": "Intermediate", "description": "Comfortable, some experience"},
            {"id": "advanced", "name": "Advanced", "description": "Proficient, significant experience"},
            {"id": "expert", "name": "Expert", "description": "Mastery level"},
        ]
    }


@router.get(
    "/templates",
    summary="Get CV Templates",
    description="Get available CV templates/formats"
)
async def get_cv_templates() -> dict:
    """Get available CV templates."""
    return {
        "templates": [
            {
                "id": "standard",
                "name": "Standard",
                "description": "Classic professional format",
                "best_for": ["General applications", "Traditional companies"]
            },
            {
                "id": "modern",
                "name": "Modern",
                "description": "Contemporary design with visual elements",
                "best_for": ["Tech companies", "Startups"]
            },
            {
                "id": "academic",
                "name": "Academic",
                "description": "Detailed format for research/academic positions",
                "best_for": ["Research positions", "Graduate school"]
            },
        ]
    }
