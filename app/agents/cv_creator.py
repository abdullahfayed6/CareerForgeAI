"""
CV Creator Agent

Agent that collects skills from various sources and generates professional CVs.
Supports:
1. Collecting skills from interviews, courses, projects, experience
2. Allowing students to add their own skills
3. Generating complete, ATS-friendly CVs
"""

import json
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage

from app.providers import get_langchain_llm
from app.agents.cv_prompts import (
    SKILL_EXTRACTOR_PROMPT,
    CV_GENERATOR_PROMPT,
    SUMMARY_GENERATOR_PROMPT
)
from app.models.cv_schemas import (
    Skill,
    SkillLevel,
    SkillCategory,
    SkillsProfile,
    StudentProfile,
    GeneratedCV,
    CVResponse,
    CollectSkillsRequest,
    GenerateCVRequest,
    Education,
    Experience,
    Project,
    Certification,
    Award,
)


class CVCreatorAgent:
    """Agent that creates professional CVs by collecting and organizing student information."""
    
    def __init__(self, provider_type: str = None):
        """Initialize the CV creator agent."""
        self.llm = get_langchain_llm(provider_type=provider_type)
    
    # ============================================
    # Skill Collection Methods
    # ============================================
    
    async def collect_skills(self, request: CollectSkillsRequest) -> SkillsProfile:
        """
        Collect and organize skills from various sources.
        
        Args:
            request: CollectSkillsRequest with source data
            
        Returns:
            SkillsProfile with organized skills
        """
        # Build prompt with available data
        prompt = SKILL_EXTRACTOR_PROMPT.format(
            name=request.student_id or "Student",
            academic_year="N/A",
            track="N/A",
            career_goal="Career growth",
            interview_responses=self._format_list(request.interview_responses),
            courses_taken=self._format_list(request.courses_taken),
            project_descriptions=self._format_list(request.project_descriptions),
            experience_descriptions=self._format_list(request.experience_descriptions),
            additional_skills=", ".join(request.additional_skills) if request.additional_skills else "None"
        )
        
        messages = [
            SystemMessage(content="You are an expert skills analyst. Return only valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return self._parse_skills_response(response.content, request)
    
    def collect_skills_sync(self, request: CollectSkillsRequest) -> SkillsProfile:
        """Synchronous version of collect_skills."""
        prompt = SKILL_EXTRACTOR_PROMPT.format(
            name=request.student_id or "Student",
            academic_year="N/A",
            track="N/A",
            career_goal="Career growth",
            interview_responses=self._format_list(request.interview_responses),
            courses_taken=self._format_list(request.courses_taken),
            project_descriptions=self._format_list(request.project_descriptions),
            experience_descriptions=self._format_list(request.experience_descriptions),
            additional_skills=", ".join(request.additional_skills) if request.additional_skills else "None"
        )
        
        messages = [
            SystemMessage(content="You are an expert skills analyst. Return only valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return self._parse_skills_response(response.content, request)
    
    def add_manual_skills(
        self, 
        profile: SkillsProfile, 
        skills: List[str],
        category: SkillCategory = SkillCategory.TECHNICAL,
        level: SkillLevel = SkillLevel.INTERMEDIATE
    ) -> SkillsProfile:
        """
        Add skills manually to an existing profile.
        
        Args:
            profile: Existing SkillsProfile
            skills: List of skill names to add
            category: Category for the skills
            level: Proficiency level
            
        Returns:
            Updated SkillsProfile
        """
        for skill_name in skills:
            skill = Skill(
                name=skill_name,
                category=category,
                level=level,
                source="Added by student",
                is_verified=False,
                icon=self._get_skill_icon(category)
            )
            
            # Add to appropriate list
            if category == SkillCategory.PROGRAMMING:
                profile.programming_languages.append(skill)
            elif category == SkillCategory.FRAMEWORK:
                profile.frameworks.append(skill)
            elif category == SkillCategory.TOOL:
                profile.tools.append(skill)
            elif category == SkillCategory.DATABASE:
                profile.databases.append(skill)
            elif category == SkillCategory.CLOUD:
                profile.cloud_platforms.append(skill)
            elif category == SkillCategory.SOFT_SKILL:
                profile.soft_skills.append(skill)
            elif category == SkillCategory.LANGUAGE:
                profile.languages.append(skill)
            else:
                profile.technical_skills.append(skill)
        
        # Update total count
        profile.total_skills = self._count_total_skills(profile)
        return profile
    
    # ============================================
    # CV Generation Methods
    # ============================================
    
    async def generate_cv(self, request: GenerateCVRequest) -> CVResponse:
        """
        Generate a complete CV from student profile.
        
        Args:
            request: GenerateCVRequest with student data and preferences
            
        Returns:
            CVResponse with generated CV
        """
        try:
            # First collect all skills
            all_skills = self._aggregate_skills(request.student_profile)
            
            # Add additional skills from request
            all_skills.extend(request.additional_skills)
            
            # Build prompt
            prompt = CV_GENERATOR_PROMPT.format(
                personal_info=self._format_personal_info(request.student_profile.personal_info),
                education=self._format_education(request.student_profile.education),
                experiences=self._format_experiences(request.student_profile.experiences),
                projects=self._format_projects(request.student_profile.projects),
                skills_profile=", ".join(all_skills) if all_skills else "Not specified",
                certifications=self._format_certifications(request.student_profile.certifications),
                awards=self._format_awards(request.student_profile.awards),
                career_goal=request.student_profile.career_goals or "Not specified",
                target_role=request.target_role or "General",
                cv_format=request.cv_format,
                emphasize_skills=", ".join(request.emphasize_skills) if request.emphasize_skills else "None",
                hide_sections=", ".join(request.hide_sections) if request.hide_sections else "None"
            )
            
            messages = [
                SystemMessage(content="You are an expert CV writer. Return only valid JSON."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            cv = self._parse_cv_response(response.content, request)
            
            return CVResponse(
                success=True,
                cv=cv,
                skills_collected=len(all_skills),
                message="CV generated successfully",
                suggestions=cv.improvement_suggestions if cv else []
            )
            
        except Exception as e:
            return CVResponse(
                success=False,
                cv=None,
                message=f"Error generating CV: {str(e)}",
                suggestions=["Try providing more information about your experience"]
            )
    
    def generate_cv_sync(self, request: GenerateCVRequest) -> CVResponse:
        """Synchronous version of generate_cv."""
        try:
            all_skills = self._aggregate_skills(request.student_profile)
            all_skills.extend(request.additional_skills)
            
            prompt = CV_GENERATOR_PROMPT.format(
                personal_info=self._format_personal_info(request.student_profile.personal_info),
                education=self._format_education(request.student_profile.education),
                experiences=self._format_experiences(request.student_profile.experiences),
                projects=self._format_projects(request.student_profile.projects),
                skills_profile=", ".join(all_skills) if all_skills else "Not specified",
                certifications=self._format_certifications(request.student_profile.certifications),
                awards=self._format_awards(request.student_profile.awards),
                career_goal=request.student_profile.career_goals or "Not specified",
                target_role=request.target_role or "General",
                cv_format=request.cv_format,
                emphasize_skills=", ".join(request.emphasize_skills) if request.emphasize_skills else "None",
                hide_sections=", ".join(request.hide_sections) if request.hide_sections else "None"
            )
            
            messages = [
                SystemMessage(content="You are an expert CV writer. Return only valid JSON."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            cv = self._parse_cv_response(response.content, request)
            
            return CVResponse(
                success=True,
                cv=cv,
                skills_collected=len(all_skills),
                message="CV generated successfully",
                suggestions=cv.improvement_suggestions if cv else []
            )
            
        except Exception as e:
            return CVResponse(
                success=False,
                cv=None,
                message=f"Error generating CV: {str(e)}",
                suggestions=["Try providing more information about your experience"]
            )
    
    async def generate_summary(
        self,
        profile: StudentProfile,
        target_role: Optional[str] = None
    ) -> str:
        """
        Generate just the professional summary.
        
        Args:
            profile: Student profile
            target_role: Target job role
            
        Returns:
            Professional summary string
        """
        all_skills = self._aggregate_skills(profile)
        
        prompt = SUMMARY_GENERATOR_PROMPT.format(
            name=profile.personal_info.full_name if profile.personal_info else "Student",
            academic_year=profile.academic_year or "N/A",
            track=profile.track or "N/A",
            top_skills=", ".join(all_skills[:5]) if all_skills else "Various technical skills",
            target_role=target_role or "General",
            career_goal=profile.career_goals or "Career growth",
            key_experience=self._get_key_experience(profile),
            key_projects=self._get_key_projects(profile)
        )
        
        messages = [
            SystemMessage(content="You are an expert CV writer. Write a professional summary."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
    
    # ============================================
    # Helper Methods - Formatting
    # ============================================
    
    def _format_list(self, items: Optional[List[str]]) -> str:
        """Format a list of items for the prompt."""
        if not items:
            return "None provided"
        return "\n".join([f"- {item}" for item in items])
    
    def _format_personal_info(self, info) -> str:
        """Format personal info for prompt."""
        if not info:
            return "Not provided"
        parts = []
        if info.full_name:
            parts.append(f"Name: {info.full_name}")
        if info.email:
            parts.append(f"Email: {info.email}")
        if info.location:
            parts.append(f"Location: {info.location}")
        if info.linkedin_url:
            parts.append(f"LinkedIn: {info.linkedin_url}")
        if info.github_url:
            parts.append(f"GitHub: {info.github_url}")
        return "\n".join(parts) if parts else "Not provided"
    
    def _format_education(self, education: List[Education]) -> str:
        """Format education entries for prompt."""
        if not education:
            return "Not provided"
        entries = []
        for edu in education:
            entry = f"- {edu.degree} in {edu.field_of_study} at {edu.institution}"
            if edu.gpa:
                entry += f" (GPA: {edu.gpa})"
            entries.append(entry)
        return "\n".join(entries)
    
    def _format_experiences(self, experiences: List[Experience]) -> str:
        """Format experience entries for prompt."""
        if not experiences:
            return "Not provided"
        entries = []
        for exp in experiences:
            entry = f"- {exp.position} at {exp.company}"
            if exp.start_date:
                entry += f" ({exp.start_date} - {exp.end_date or 'Present'})"
            if exp.responsibilities:
                entry += f"\n  Responsibilities: {', '.join(exp.responsibilities[:3])}"
            entries.append(entry)
        return "\n".join(entries)
    
    def _format_projects(self, projects: List[Project]) -> str:
        """Format project entries for prompt."""
        if not projects:
            return "Not provided"
        entries = []
        for proj in projects:
            entry = f"- {proj.name}: {proj.description[:100]}..."
            if proj.technologies:
                entry += f"\n  Tech: {', '.join(proj.technologies)}"
            entries.append(entry)
        return "\n".join(entries)
    
    def _format_certifications(self, certs: List[Certification]) -> str:
        """Format certification entries for prompt."""
        if not certs:
            return "None"
        return "\n".join([f"- {c.name} by {c.issuer}" for c in certs])
    
    def _format_awards(self, awards: List[Award]) -> str:
        """Format award entries for prompt."""
        if not awards:
            return "None"
        return "\n".join([f"- {a.title} from {a.issuer}" for a in awards])
    
    # ============================================
    # Helper Methods - Aggregation
    # ============================================
    
    def _aggregate_skills(self, profile: StudentProfile) -> List[str]:
        """Aggregate all skills from student profile."""
        all_skills = []
        all_skills.extend(profile.skills_from_interviews or [])
        all_skills.extend(profile.skills_from_courses or [])
        all_skills.extend(profile.skills_from_projects or [])
        all_skills.extend(profile.skills_from_experience or [])
        all_skills.extend(profile.skills_added_by_student or [])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in all_skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills
    
    def _get_key_experience(self, profile: StudentProfile) -> str:
        """Get key experience summary."""
        if not profile.experiences:
            return "Academic projects"
        exp = profile.experiences[0]
        return f"{exp.position} at {exp.company}"
    
    def _get_key_projects(self, profile: StudentProfile) -> str:
        """Get key projects summary."""
        if not profile.projects:
            return "Various academic projects"
        return ", ".join([p.name for p in profile.projects[:2]])
    
    def _count_total_skills(self, profile: SkillsProfile) -> int:
        """Count total skills in profile."""
        return (
            len(profile.technical_skills) +
            len(profile.programming_languages) +
            len(profile.frameworks) +
            len(profile.tools) +
            len(profile.databases) +
            len(profile.cloud_platforms) +
            len(profile.soft_skills) +
            len(profile.languages) +
            len(profile.other_skills)
        )
    
    def _get_skill_icon(self, category: SkillCategory) -> str:
        """Get icon for skill category."""
        icons = {
            SkillCategory.PROGRAMMING: "💻",
            SkillCategory.FRAMEWORK: "🔧",
            SkillCategory.TOOL: "🛠️",
            SkillCategory.DATABASE: "🗄️",
            SkillCategory.CLOUD: "☁️",
            SkillCategory.TECHNICAL: "⚙️",
            SkillCategory.SOFT_SKILL: "🤝",
            SkillCategory.LANGUAGE: "🌐",
            SkillCategory.OTHER: "📌"
        }
        return icons.get(category, "💡")
    
    # ============================================
    # Helper Methods - Parsing
    # ============================================
    
    def _parse_skills_response(
        self, 
        response_content: str, 
        request: CollectSkillsRequest
    ) -> SkillsProfile:
        """Parse LLM response into SkillsProfile."""
        try:
            content = response_content.strip()
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                content = json_match.group(1).strip()
            
            data = json.loads(content)
            skills_data = data.get("skills_by_category", {})
            
            return SkillsProfile(
                programming_languages=[Skill(**s) for s in skills_data.get("programming_languages", [])],
                frameworks=[Skill(**s) for s in skills_data.get("frameworks", [])],
                tools=[Skill(**s) for s in skills_data.get("tools", [])],
                databases=[Skill(**s) for s in skills_data.get("databases", [])],
                cloud_platforms=[Skill(**s) for s in skills_data.get("cloud_platforms", [])],
                technical_skills=[Skill(**s) for s in skills_data.get("technical_skills", [])],
                soft_skills=[Skill(**s) for s in skills_data.get("soft_skills", [])],
                languages=[Skill(**s) for s in skills_data.get("languages", [])],
                other_skills=[Skill(**s) for s in skills_data.get("other_skills", [])],
                total_skills=data.get("total_skills_found", 0)
            )
            
        except Exception as e:
            # Return profile with manual skills only
            profile = SkillsProfile()
            if request.additional_skills:
                for skill in request.additional_skills:
                    profile.technical_skills.append(Skill(
                        name=skill,
                        category=SkillCategory.TECHNICAL,
                        level=SkillLevel.INTERMEDIATE,
                        source="Added by student"
                    ))
            profile.total_skills = len(profile.technical_skills)
            return profile
    
    def _parse_cv_response(
        self, 
        response_content: str, 
        request: GenerateCVRequest
    ) -> GeneratedCV:
        """Parse LLM response into GeneratedCV."""
        try:
            content = response_content.strip()
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                content = json_match.group(1).strip()
            
            data = json.loads(content)
            
            # Parse skills profile
            skills_data = data.get("skills_profile", {})
            skills_profile = SkillsProfile(
                technical_skills=[Skill(**s) for s in skills_data.get("technical_skills", [])],
                programming_languages=[Skill(**s) for s in skills_data.get("programming_languages", [])],
                frameworks=[Skill(**s) for s in skills_data.get("frameworks", [])],
                tools=[Skill(**s) for s in skills_data.get("tools", [])],
                databases=[Skill(**s) for s in skills_data.get("databases", [])],
                cloud_platforms=[Skill(**s) for s in skills_data.get("cloud_platforms", [])],
                soft_skills=[Skill(**s) for s in skills_data.get("soft_skills", [])],
                languages=[Skill(**s) for s in skills_data.get("languages", [])],
                other_skills=[Skill(**s) for s in skills_data.get("other_skills", [])],
                total_skills=skills_data.get("total_skills", 0)
            )
            
            return GeneratedCV(
                full_name=data.get("full_name", ""),
                title=data.get("title"),
                contact_info=data.get("contact_info", {}),
                professional_summary=data.get("professional_summary", ""),
                skills_profile=skills_profile,
                education=[Education(**e) for e in data.get("education", [])],
                experiences=[Experience(**e) for e in data.get("experiences", [])],
                projects=[Project(**p) for p in data.get("projects", [])],
                certifications=[Certification(**c) for c in data.get("certifications", [])],
                awards=[Award(**a) for a in data.get("awards", [])],
                languages=data.get("languages", []),
                interests=data.get("interests", []),
                cv_format=data.get("cv_format", "standard"),
                target_role=data.get("target_role"),
                improvement_suggestions=data.get("improvement_suggestions", []),
                missing_sections=data.get("missing_sections", [])
            )
            
        except Exception as e:
            # Return basic CV
            return self._fallback_cv(request, str(e))
    
    def _fallback_cv(self, request: GenerateCVRequest, error: str) -> GeneratedCV:
        """Create fallback CV when parsing fails."""
        profile = request.student_profile
        name = profile.personal_info.full_name if profile.personal_info else "Student"
        
        return GeneratedCV(
            full_name=name,
            title=f"{profile.track} Student" if profile.track else "Student",
            contact_info={},
            professional_summary=f"Motivated {profile.track or 'Computer Science'} student seeking opportunities to apply skills and grow professionally.",
            skills_profile=SkillsProfile(total_skills=0),
            education=profile.education,
            experiences=profile.experiences,
            projects=profile.projects,
            certifications=profile.certifications,
            awards=profile.awards,
            languages=[],
            interests=profile.interests,
            cv_format=request.cv_format,
            target_role=request.target_role,
            improvement_suggestions=[
                f"Parse error occurred: {error}",
                "Try providing more structured information"
            ],
            missing_sections=[]
        )
