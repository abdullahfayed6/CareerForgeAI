"""
Student Identity & Career Profiling Agent

AI-powered diagnostic system that builds structured student profiles
through step-by-step conversation. These profiles are used by other
AI agents to personalize the learning journey.
"""

import json
import re
import uuid
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage

from app.providers import get_langchain_llm
from app.agents.profiling_prompts import (
    PROFILING_SYSTEM_PROMPT,
    INTRO_PROMPT,
    CAREER_DIRECTION_PROMPT,
    CURRENT_BACKGROUND_PROMPT,
    SKILL_MAP_PROMPT,
    LEARNING_PROFILE_PROMPT,
    OBSTACLES_PROMPT,
    MOTIVATION_PROMPT,
    PROFILE_GENERATION_PROMPT,
    QUICK_PROFILE_ANALYSIS_PROMPT,
    PROFILE_SUMMARY_PROMPT,
    SECTION_TRANSITIONS,
    CLARIFICATION_PROMPT,
    ENCOURAGE_RESPONSE_PROMPT
)
from app.models.profiling_schemas import (
    StudentProfile,
    ProfilingConversation,
    ProfilingSection,
    SkillRatings,
    SkillRating,
    CareerGoalType,
    EducationLevel,
    LearningStyle,
    LearningApproach,
    PsychologicalState,
    EstimatedLevel,
    WorkModel,
    PriorityValue,
    QuickProfileRequest,
    ProfileSummaryResponse
)


class ProfilingAgent:
    """AI Career Profiling Agent that builds student profiles through conversation."""
    
    # Store active sessions in memory (in production, use Redis or database)
    _sessions: Dict[str, ProfilingConversation] = {}
    
    def __init__(self, provider_type: str = None):
        """Initialize the profiling agent."""
        self.llm = get_langchain_llm(provider_type=provider_type)
    
    # ============================================
    # Session Management
    # ============================================
    
    def start_session(self, student_name: Optional[str] = None, language: str = "en") -> Tuple[str, str]:
        """
        Start a new profiling session.
        
        Args:
            student_name: Optional student name
            language: Language for conversation
            
        Returns:
            Tuple of (session_id, welcome_message)
        """
        session_id = str(uuid.uuid4())
        
        # Create new conversation state
        conversation = ProfilingConversation(
            session_id=session_id,
            current_section=ProfilingSection.INTRO,
            collected_data={"student_name": student_name} if student_name else {},
            messages=[]
        )
        
        # Generate welcome message
        welcome_message = self._generate_welcome_message(student_name)
        
        # Store the welcome message
        conversation.messages.append({
            "role": "assistant",
            "content": welcome_message,
            "timestamp": datetime.now().isoformat()
        })
        conversation.current_section = ProfilingSection.CAREER_DIRECTION
        
        # Store session
        self._sessions[session_id] = conversation
        
        return session_id, welcome_message
    
    async def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Tuple[str, str, bool, int]:
        """
        Process a user message and return the agent's response.
        
        Args:
            session_id: Session ID
            user_message: User's message
            
        Returns:
            Tuple of (agent_message, current_section, is_complete, progress_percentage)
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        conversation = self._sessions[session_id]
        
        # Store user message
        conversation.messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process based on current section
        section = conversation.current_section
        
        # Get the appropriate prompt for this section
        section_prompt = self._get_section_prompt(section)
        
        # Build messages for LLM
        messages = [
            SystemMessage(content=PROFILING_SYSTEM_PROMPT),
            HumanMessage(content=section_prompt.format(
                collected_data=json.dumps(conversation.collected_data, indent=2),
                user_message=user_message
            ))
        ]
        
        # Get LLM response
        response = await self.llm.ainvoke(messages)
        agent_message = response.content.strip()
        
        # Extract any data from the conversation
        extracted_data = await self._extract_data_from_response(
            section, user_message, agent_message
        )
        conversation.collected_data.update(extracted_data)
        
        # Check if we should move to next section
        should_advance, next_section = self._should_advance_section(
            section, conversation.collected_data, user_message
        )
        
        if should_advance:
            conversation.current_section = next_section
            if next_section != ProfilingSection.COMPLETE:
                # Add transition message
                transition = self._get_transition_message(section, next_section)
                if transition:
                    agent_message += f"\n\n{transition}"
        
        # Store agent response
        conversation.messages.append({
            "role": "assistant",
            "content": agent_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update timestamp
        conversation.updated_at = datetime.now()
        
        # Calculate progress
        progress = self._calculate_progress(conversation.current_section)
        is_complete = conversation.current_section == ProfilingSection.COMPLETE
        
        return (
            agent_message,
            conversation.current_section.value,
            is_complete,
            progress
        )
    
    def process_message_sync(
        self,
        session_id: str,
        user_message: str
    ) -> Tuple[str, str, bool, int]:
        """Synchronous version of process_message."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.process_message(session_id, user_message)
            )
        finally:
            loop.close()
    
    async def generate_profile(self, session_id: str) -> StudentProfile:
        """
        Generate the final student profile from collected data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Complete StudentProfile
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        conversation = self._sessions[session_id]
        
        # Build conversation history string
        history = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation.messages
        ])
        
        # Generate profile using LLM
        prompt = PROFILE_GENERATION_PROMPT.format(
            collected_data=json.dumps(conversation.collected_data, indent=2),
            conversation_history=history
        )
        
        messages = [
            SystemMessage(content="You are a data extraction expert. Return valid JSON only."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        profile_data = self._parse_json_response(response.content)
        
        # Build StudentProfile from extracted data
        profile = self._build_profile_from_data(profile_data)
        
        return profile
    
    def generate_profile_sync(self, session_id: str) -> StudentProfile:
        """Synchronous version of generate_profile."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.generate_profile(session_id))
        finally:
            loop.close()
    
    # ============================================
    # Quick Profile (Non-Conversational)
    # ============================================
    
    async def create_quick_profile(self, request: QuickProfileRequest) -> StudentProfile:
        """
        Create a profile from direct input without conversation.
        
        Args:
            request: QuickProfileRequest with all data
            
        Returns:
            Complete StudentProfile with AI analysis
        """
        # Build skill ratings
        skill_ratings = SkillRatings(
            coding=SkillRating(str(request.coding_rating)),
            problem_solving=SkillRating(str(request.problem_solving_rating)),
            math_logic=SkillRating(str(request.math_logic_rating)),
            debugging=SkillRating(str(request.debugging_rating))
        )
        
        # Get AI analysis for level and risks
        analysis = await self._analyze_profile_data(request)
        
        # Build profile
        profile = StudentProfile(
            career_goal=request.career_goal,
            target_role=request.target_role,
            goal_type=CareerGoalType(request.goal_type),
            education_level=EducationLevel(request.education_level),
            field_of_study=request.field_of_study,
            experience_duration=request.experience_duration,
            project_experience=request.project_experience,
            technical_skills=request.technical_skills,
            tool_experience=request.tool_experience,
            skill_ratings=skill_ratings,
            learning_style=LearningStyle(request.learning_style),
            learning_approach=LearningApproach(request.learning_approach),
            study_time_per_week=request.study_hours_per_week,
            main_weaknesses=request.main_weaknesses,
            psychological_state=PsychologicalState(request.psychological_state),
            motivation_reason=request.motivation_reason,
            preferred_work_model=WorkModel(request.preferred_work_model),
            priority_value=PriorityValue(request.priority_value),
            estimated_level=EstimatedLevel(analysis.get("estimated_level", "beginner")),
            readiness_risk_areas=analysis.get("readiness_risk_areas", [])
        )
        
        return profile
    
    def create_quick_profile_sync(self, request: QuickProfileRequest) -> StudentProfile:
        """Synchronous version of create_quick_profile."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.create_quick_profile(request))
        finally:
            loop.close()
    
    # ============================================
    # Profile Summary
    # ============================================
    
    async def generate_profile_summary(self, profile: StudentProfile) -> str:
        """
        Generate a human-readable summary of a profile.
        
        Args:
            profile: StudentProfile to summarize
            
        Returns:
            Summary string
        """
        prompt = PROFILE_SUMMARY_PROMPT.format(
            profile_json=profile.model_dump_json(indent=2)
        )
        
        messages = [
            SystemMessage(content="You are a career counselor. Be encouraging but honest."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
    
    async def get_profile_recommendation(self, profile: StudentProfile) -> ProfileSummaryResponse:
        """
        Get a summary with recommendations for a profile.
        
        Args:
            profile: StudentProfile
            
        Returns:
            ProfileSummaryResponse with recommendations
        """
        summary = await self.generate_profile_summary(profile)
        
        return ProfileSummaryResponse(
            career_goal=profile.career_goal,
            target_role=profile.target_role,
            estimated_level=profile.estimated_level.value,
            top_skills=profile.technical_skills[:5] + profile.tool_experience[:3],
            main_weaknesses=profile.main_weaknesses,
            readiness_risk_areas=profile.readiness_risk_areas,
            psychological_state=profile.psychological_state.value,
            recommendation=summary
        )
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def _generate_welcome_message(self, student_name: Optional[str] = None) -> str:
        """Generate a welcome message for the student."""
        name_part = f", {student_name}" if student_name else ""
        
        return f"""👋 Hi{name_part}! Welcome to your Career Profiling Session!

I'm here to understand you better before your learning journey begins. Think of me as a diagnostic system - I'll ask you some questions to figure out:
- Where you want to go in your career
- Where you're starting from
- What gaps we need to close to get you job-ready

There are **no wrong answers** here. The more honest you are, the better I can help personalize your experience.

This will take about 5-10 minutes. Ready? Let's start!

**First, let's talk about your career goals:**
What career path are you aiming for? For example: AI Engineer, Data Analyst, Web Developer, Cybersecurity Specialist, etc."""
    
    def _get_section_prompt(self, section: ProfilingSection) -> str:
        """Get the prompt template for a given section."""
        prompts = {
            ProfilingSection.INTRO: INTRO_PROMPT,
            ProfilingSection.CAREER_DIRECTION: CAREER_DIRECTION_PROMPT,
            ProfilingSection.CURRENT_BACKGROUND: CURRENT_BACKGROUND_PROMPT,
            ProfilingSection.SKILL_MAP: SKILL_MAP_PROMPT,
            ProfilingSection.LEARNING_PROFILE: LEARNING_PROFILE_PROMPT,
            ProfilingSection.OBSTACLES: OBSTACLES_PROMPT,
            ProfilingSection.MOTIVATION: MOTIVATION_PROMPT,
        }
        return prompts.get(section, CAREER_DIRECTION_PROMPT)
    
    async def _extract_data_from_response(
        self,
        section: ProfilingSection,
        user_message: str,
        agent_response: str
    ) -> Dict:
        """Extract structured data from the conversation."""
        # Use LLM to extract data based on section
        extraction_prompt = f"""Extract relevant data from this conversation exchange.
        
Section: {section.value}
User said: "{user_message}"

Return a JSON object with extracted fields. Only include fields you're confident about.
For {section.value}, look for:
"""
        
        if section == ProfilingSection.CAREER_DIRECTION:
            extraction_prompt += """
- career_goal: The career they're aiming for
- target_role: Specific job title they want
- goal_type: internship/first_job/career_switch/promotion"""
        elif section == ProfilingSection.CURRENT_BACKGROUND:
            extraction_prompt += """
- education_level: school/university/graduate/self_taught
- field_of_study: Their field
- experience_duration: How long they've been learning
- project_experience: Projects they mentioned"""
        elif section == ProfilingSection.SKILL_MAP:
            extraction_prompt += """
- technical_skills: List of programming languages
- tool_experience: List of tools
- coding_rating: 1-5
- problem_solving_rating: 1-5
- math_logic_rating: 1-5
- debugging_rating: 1-5"""
        elif section == ProfilingSection.LEARNING_PROFILE:
            extraction_prompt += """
- learning_style: videos/reading/practice/stories_examples/mixed
- learning_approach: step_by_step/hard_challenges_first
- study_hours_per_week: Number"""
        elif section == ProfilingSection.OBSTACLES:
            extraction_prompt += """
- main_weaknesses: List of struggles
- past_blockers: What stopped them
- psychological_state: confident/neutral/overwhelmed"""
        elif section == ProfilingSection.MOTIVATION:
            extraction_prompt += """
- motivation_reason: Why they want this career
- preferred_work_model: stable_job/freelancing/startup
- priority_value: salary/passion/flexibility/prestige"""
        
        extraction_prompt += "\n\nReturn valid JSON only. If nothing can be extracted, return {}"
        
        messages = [
            SystemMessage(content="You extract data from conversations. Return valid JSON only."),
            HumanMessage(content=extraction_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return self._parse_json_response(response.content)
        except Exception:
            return {}
    
    def _should_advance_section(
        self,
        current_section: ProfilingSection,
        collected_data: Dict,
        user_message: str
    ) -> Tuple[bool, ProfilingSection]:
        """Determine if we should advance to the next section."""
        section_requirements = {
            ProfilingSection.CAREER_DIRECTION: ["career_goal", "target_role"],
            ProfilingSection.CURRENT_BACKGROUND: ["education_level", "field_of_study"],
            ProfilingSection.SKILL_MAP: ["technical_skills"],
            ProfilingSection.LEARNING_PROFILE: ["learning_style", "study_hours_per_week"],
            ProfilingSection.OBSTACLES: ["main_weaknesses", "psychological_state"],
            ProfilingSection.MOTIVATION: ["motivation_reason", "preferred_work_model"],
        }
        
        section_order = [
            ProfilingSection.INTRO,
            ProfilingSection.CAREER_DIRECTION,
            ProfilingSection.CURRENT_BACKGROUND,
            ProfilingSection.SKILL_MAP,
            ProfilingSection.LEARNING_PROFILE,
            ProfilingSection.OBSTACLES,
            ProfilingSection.MOTIVATION,
            ProfilingSection.COMPLETE,
        ]
        
        # Check if current section has minimum required data
        required = section_requirements.get(current_section, [])
        has_required = all(key in collected_data for key in required)
        
        if has_required:
            current_idx = section_order.index(current_section)
            if current_idx < len(section_order) - 1:
                return True, section_order[current_idx + 1]
        
        return False, current_section
    
    def _get_transition_message(
        self,
        from_section: ProfilingSection,
        to_section: ProfilingSection
    ) -> Optional[str]:
        """Get a transition message between sections."""
        transitions = {
            (ProfilingSection.CAREER_DIRECTION, ProfilingSection.CURRENT_BACKGROUND): 
                SECTION_TRANSITIONS["career_to_background"],
            (ProfilingSection.CURRENT_BACKGROUND, ProfilingSection.SKILL_MAP): 
                SECTION_TRANSITIONS["background_to_skills"],
            (ProfilingSection.SKILL_MAP, ProfilingSection.LEARNING_PROFILE): 
                SECTION_TRANSITIONS["skills_to_learning"],
            (ProfilingSection.LEARNING_PROFILE, ProfilingSection.OBSTACLES): 
                SECTION_TRANSITIONS["learning_to_obstacles"],
            (ProfilingSection.OBSTACLES, ProfilingSection.MOTIVATION): 
                SECTION_TRANSITIONS["obstacles_to_motivation"],
            (ProfilingSection.MOTIVATION, ProfilingSection.COMPLETE): 
                SECTION_TRANSITIONS["motivation_to_complete"],
        }
        return transitions.get((from_section, to_section))
    
    def _calculate_progress(self, section: ProfilingSection) -> int:
        """Calculate progress percentage based on current section."""
        progress_map = {
            ProfilingSection.INTRO: 0,
            ProfilingSection.CAREER_DIRECTION: 15,
            ProfilingSection.CURRENT_BACKGROUND: 30,
            ProfilingSection.SKILL_MAP: 50,
            ProfilingSection.LEARNING_PROFILE: 65,
            ProfilingSection.OBSTACLES: 80,
            ProfilingSection.MOTIVATION: 90,
            ProfilingSection.COMPLETE: 100,
        }
        return progress_map.get(section, 0)
    
    async def _analyze_profile_data(self, request: QuickProfileRequest) -> Dict:
        """Analyze profile data to determine level and risks."""
        prompt = QUICK_PROFILE_ANALYSIS_PROMPT.format(
            career_goal=request.career_goal,
            target_role=request.target_role,
            education_level=request.education_level,
            field_of_study=request.field_of_study,
            experience_duration=request.experience_duration,
            project_experience=request.project_experience,
            technical_skills=", ".join(request.technical_skills) or "None",
            tool_experience=", ".join(request.tool_experience) or "None",
            coding=request.coding_rating,
            problem_solving=request.problem_solving_rating,
            math_logic=request.math_logic_rating,
            debugging=request.debugging_rating,
            learning_style=request.learning_style,
            study_hours=request.study_hours_per_week,
            main_weaknesses=", ".join(request.main_weaknesses) or "None",
            psychological_state=request.psychological_state,
            motivation_reason=request.motivation_reason,
            work_model=request.preferred_work_model,
            priority_value=request.priority_value
        )
        
        messages = [
            SystemMessage(content="You analyze student profiles. Return valid JSON only."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return self._parse_json_response(response.content)
        except Exception:
            return {
                "estimated_level": "beginner",
                "readiness_risk_areas": ["Unable to assess - insufficient data"]
            }
    
    def _build_profile_from_data(self, data: Dict) -> StudentProfile:
        """Build a StudentProfile from extracted data."""
        # Helper to safely get enum values
        def safe_enum(enum_class, value, default):
            try:
                return enum_class(value.lower() if isinstance(value, str) else value)
            except (ValueError, AttributeError):
                return default
        
        # Build skill ratings
        ratings = data.get("Skill_Ratings", {})
        skill_ratings = SkillRatings(
            coding=SkillRating(str(ratings.get("Coding", "3"))),
            problem_solving=SkillRating(str(ratings.get("Problem_Solving", "3"))),
            math_logic=SkillRating(str(ratings.get("Math_Logic", "3"))),
            debugging=SkillRating(str(ratings.get("Debugging", "3")))
        )
        
        return StudentProfile(
            career_goal=data.get("Career_Goal", "Not specified"),
            target_role=data.get("Target_Role", "Not specified"),
            goal_type=safe_enum(CareerGoalType, data.get("Goal_Type"), CareerGoalType.FIRST_JOB),
            education_level=safe_enum(EducationLevel, data.get("Education_Level"), EducationLevel.UNIVERSITY),
            field_of_study=data.get("Field_of_Study", ""),
            experience_duration=data.get("Experience_Duration", ""),
            project_experience=data.get("Project_Experience", ""),
            technical_skills=data.get("Technical_Skills", []),
            tool_experience=data.get("Tool_Experience", []),
            skill_ratings=skill_ratings,
            can_explain_projects=data.get("Can_Explain_Projects", False),
            can_read_docs=data.get("Can_Read_Docs", False),
            learning_style=safe_enum(LearningStyle, data.get("Learning_Style"), LearningStyle.MIXED),
            learning_approach=safe_enum(LearningApproach, data.get("Learning_Approach"), LearningApproach.STEP_BY_STEP),
            study_time_per_week=int(data.get("Study_Time_Per_Week", 10)),
            main_weaknesses=data.get("Main_Weaknesses", []),
            past_blockers=data.get("Past_Blockers", ""),
            psychological_state=safe_enum(PsychologicalState, data.get("Psychological_State"), PsychologicalState.NEUTRAL),
            motivation_reason=data.get("Motivation_Reason", ""),
            preferred_work_model=safe_enum(WorkModel, data.get("Preferred_Work_Model"), WorkModel.STABLE_JOB),
            priority_value=safe_enum(PriorityValue, data.get("Priority_Value"), PriorityValue.PASSION),
            estimated_level=safe_enum(EstimatedLevel, data.get("Estimated_Level"), EstimatedLevel.BEGINNER),
            readiness_risk_areas=data.get("Readiness_Risk_Areas", [])
        )
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from LLM response."""
        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try direct JSON parsing
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON-like content
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass
            return {}
    
    # ============================================
    # Session Cleanup
    # ============================================
    
    def get_session(self, session_id: str) -> Optional[ProfilingConversation]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours."""
        now = datetime.now()
        to_delete = []
        
        for session_id, conversation in self._sessions.items():
            age = (now - conversation.created_at).total_seconds() / 3600
            if age > max_age_hours:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            del self._sessions[session_id]
        
        return len(to_delete)
