"""
Advisor Agent - Student Life & Tech Mentor

AI-powered personal mentor that analyzes student's current situation
and provides personalized, actionable advice across:
- Learning & Study
- Technical Career Growth
- Productivity & Habits
- Mindset & Motivation
- Life Balance
"""

import json
import re
from typing import Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage

from app.providers import get_langchain_llm
from app.agents.advisor_prompts import (
    ADVISOR_SYSTEM_PROMPT,
    ADVISOR_ANALYSIS_PROMPT,
    QUICK_CHECK_IN_PROMPT,
    CRISIS_INTERVENTION_PROMPT
)
from app.models.advisor_schemas import (
    StudentState,
    StudentProfile,
    LearningState,
    BehaviorState,
    EmotionalState,
    AdvisorResponse,
    StudentAnalysis,
    LearningAdvice,
    TechnicalCareerAdvice,
    ProductivityAdvice,
    MindsetAdvice,
    LifeBalanceAdvice,
    Level,
    SleepQuality,
    QuickAdvisorRequest
)


class AdvisorAgent:
    """AI Student Advisor that provides personalized mentorship."""
    
    def __init__(self, provider_type: str = None):
        """Initialize the advisor agent."""
        self.llm = get_langchain_llm(provider_type=provider_type)
    
    async def get_advice(self, state: StudentState) -> AdvisorResponse:
        """
        Analyze student state and provide comprehensive advice.
        
        Args:
            state: Complete StudentState with profile, learning, behavior, emotional data
            
        Returns:
            AdvisorResponse with all advice sections
        """
        # Check for crisis state
        if self._is_crisis_state(state):
            return await self._handle_crisis(state)
        
        # Build the analysis prompt
        prompt = ADVISOR_ANALYSIS_PROMPT.format(
            career_goal=state.student_profile.career_goal,
            current_level=state.student_profile.current_level.value,
            field_of_interest=state.student_profile.field_of_interest,
            available_hours=state.student_profile.available_hours_per_day,
            current_topic=state.learning_state.current_topic,
            understanding_level=state.learning_state.understanding_level.value,
            recent_struggles=", ".join(state.learning_state.recent_struggles) or "None specified",
            consistency_level=state.learning_state.consistency_level.value,
            focus_level=state.behavior_state.focus_level.value,
            procrastination_level=state.behavior_state.procrastination_level.value,
            energy_level=state.behavior_state.energy_level.value,
            sleep_quality=state.behavior_state.sleep_quality.value,
            motivation_level=state.emotional_state.motivation_level.value,
            stress_level=state.emotional_state.stress_level.value,
            confidence_level=state.emotional_state.confidence_level.value
        )
        
        messages = [
            SystemMessage(content=ADVISOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return self._parse_response(response.content, state)
    
    def get_advice_sync(self, state: StudentState) -> AdvisorResponse:
        """Synchronous version of get_advice."""
        if self._is_crisis_state(state):
            return self._handle_crisis_sync(state)
        
        prompt = ADVISOR_ANALYSIS_PROMPT.format(
            career_goal=state.student_profile.career_goal,
            current_level=state.student_profile.current_level.value,
            field_of_interest=state.student_profile.field_of_interest,
            available_hours=state.student_profile.available_hours_per_day,
            current_topic=state.learning_state.current_topic,
            understanding_level=state.learning_state.understanding_level.value,
            recent_struggles=", ".join(state.learning_state.recent_struggles) or "None specified",
            consistency_level=state.learning_state.consistency_level.value,
            focus_level=state.behavior_state.focus_level.value,
            procrastination_level=state.behavior_state.procrastination_level.value,
            energy_level=state.behavior_state.energy_level.value,
            sleep_quality=state.behavior_state.sleep_quality.value,
            motivation_level=state.emotional_state.motivation_level.value,
            stress_level=state.emotional_state.stress_level.value,
            confidence_level=state.emotional_state.confidence_level.value
        )
        
        messages = [
            SystemMessage(content=ADVISOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return self._parse_response(response.content, state)
    
    async def quick_check_in(
        self,
        current_topic: str,
        career_goal: str,
        motivation: str = "medium",
        energy: str = "medium",
        stress: str = "medium"
    ) -> str:
        """
        Quick check-in for a brief encouragement and advice.
        
        Returns a short, personalized message.
        """
        prompt = QUICK_CHECK_IN_PROMPT.format(
            current_topic=current_topic,
            career_goal=career_goal,
            motivation_level=motivation,
            energy_level=energy,
            stress_level=stress
        )
        
        messages = [
            SystemMessage(content="You are a supportive mentor. Be brief and real."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
    
    def _is_crisis_state(self, state: StudentState) -> bool:
        """Check if student is in a crisis state needing special handling."""
        crisis_indicators = 0
        
        if state.emotional_state.stress_level == Level.HIGH:
            crisis_indicators += 1
        if state.emotional_state.motivation_level == Level.LOW:
            crisis_indicators += 1
        if state.emotional_state.confidence_level == Level.LOW:
            crisis_indicators += 1
        if state.behavior_state.energy_level == Level.LOW:
            crisis_indicators += 1
        if state.behavior_state.sleep_quality == SleepQuality.POOR:
            crisis_indicators += 1
        
        return crisis_indicators >= 3
    
    async def _handle_crisis(self, state: StudentState) -> AdvisorResponse:
        """Handle a student in crisis state with compassionate support."""
        prompt = CRISIS_INTERVENTION_PROMPT.format(
            confidence_level=state.emotional_state.confidence_level.value,
            stress_level=state.emotional_state.stress_level.value,
            energy_level=state.behavior_state.energy_level.value,
            sleep_quality=state.behavior_state.sleep_quality.value
        )
        
        messages = [
            SystemMessage(content="You are a compassionate mentor. Wellbeing comes first."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        return self._build_crisis_response(state, response.content)
    
    def _handle_crisis_sync(self, state: StudentState) -> AdvisorResponse:
        """Sync version of crisis handling."""
        prompt = CRISIS_INTERVENTION_PROMPT.format(
            confidence_level=state.emotional_state.confidence_level.value,
            stress_level=state.emotional_state.stress_level.value,
            energy_level=state.behavior_state.energy_level.value,
            sleep_quality=state.behavior_state.sleep_quality.value
        )
        
        messages = [
            SystemMessage(content="You are a compassionate mentor. Wellbeing comes first."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return self._build_crisis_response(state, response.content)
    
    def _build_crisis_response(self, state: StudentState, crisis_message: str) -> AdvisorResponse:
        """Build a crisis-focused response."""
        return AdvisorResponse(
            situation_summary=f"⚠️ I notice you're going through a tough time right now. Your wellbeing is the priority. {crisis_message[:200]}",
            analysis=StudentAnalysis(
                main_weaknesses=["Currently overwhelmed - focus on recovery first"],
                hidden_risks=["Burnout risk is high", "Need to prioritize rest"],
                strengths_to_build=["Self-awareness to recognize when to pause", "Courage to keep going"]
            ),
            learning_advice=LearningAdvice(
                study_approach="Reduce study load by 50% until you recover",
                style_changes=["Study only when you feel ready", "No guilt for rest days"],
                likely_mistakes=["Pushing through exhaustion", "Ignoring body signals"],
                technique_to_try="Today: Just review one thing you already know well. Build confidence."
            ),
            technical_career_advice=TechnicalCareerAdvice(
                priority_skill="Right now: the skill of rest and recovery",
                recommended_focus="fundamentals",
                focus_reasoning="When stressed, complex learning doesn't stick. Simple revision builds confidence.",
                career_action="Update your LinkedIn with ONE recent accomplishment - remind yourself of progress"
            ),
            productivity_advice=ProductivityAdvice(
                harmful_habit="Trying to be productive while exhausted",
                habit_to_remove="Stop measuring your worth by daily output",
                habit_to_add="One 20-minute walk outside daily",
                day_structure="Permission to do less: 1-2 hours max of focused work, rest of day for recovery"
            ),
            mindset_advice=MindsetAdvice(
                wrong_belief="'I'm falling behind and need to catch up'",
                better_thinking="A rested mind learns in 1 hour what a tired mind takes 4 hours to learn",
                dealing_with_difficulty="This is temporary. Slow progress is still progress. Rest is part of growth."
            ),
            life_balance_advice=LifeBalanceAdvice(
                physical_impact="Your body is sending clear signals. Ignoring them will make everything harder.",
                sleep_energy_advice="Sleep is not optional. Aim for 8 hours. No screens 1 hour before bed.",
                non_tech_action="Talk to someone you trust today - friend, family, or counselor. You don't have to carry this alone."
            ),
            priority_focus="Take care of yourself first. Everything else can wait.",
            quick_wins=[
                "Drink a glass of water right now",
                "Step outside for 5 minutes of fresh air",
                "Message one friend or family member"
            ]
        )
    
    def _parse_response(self, response_content: str, state: StudentState) -> AdvisorResponse:
        """Parse LLM response into AdvisorResponse."""
        try:
            content = response_content.strip()
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                content = json_match.group(1).strip()
            
            data = json.loads(content)
            
            return AdvisorResponse(
                situation_summary=data.get("situation_summary", ""),
                analysis=StudentAnalysis(
                    main_weaknesses=data.get("analysis", {}).get("main_weaknesses", []),
                    hidden_risks=data.get("analysis", {}).get("hidden_risks", []),
                    strengths_to_build=data.get("analysis", {}).get("strengths_to_build", [])
                ),
                learning_advice=LearningAdvice(
                    study_approach=data.get("learning_advice", {}).get("study_approach", ""),
                    style_changes=data.get("learning_advice", {}).get("style_changes", []),
                    likely_mistakes=data.get("learning_advice", {}).get("likely_mistakes", []),
                    technique_to_try=data.get("learning_advice", {}).get("technique_to_try", "")
                ),
                technical_career_advice=TechnicalCareerAdvice(
                    priority_skill=data.get("technical_career_advice", {}).get("priority_skill", ""),
                    recommended_focus=data.get("technical_career_advice", {}).get("recommended_focus", ""),
                    focus_reasoning=data.get("technical_career_advice", {}).get("focus_reasoning", ""),
                    career_action=data.get("technical_career_advice", {}).get("career_action", "")
                ),
                productivity_advice=ProductivityAdvice(
                    harmful_habit=data.get("productivity_advice", {}).get("harmful_habit", ""),
                    habit_to_remove=data.get("productivity_advice", {}).get("habit_to_remove", ""),
                    habit_to_add=data.get("productivity_advice", {}).get("habit_to_add", ""),
                    day_structure=data.get("productivity_advice", {}).get("day_structure", "")
                ),
                mindset_advice=MindsetAdvice(
                    wrong_belief=data.get("mindset_advice", {}).get("wrong_belief", ""),
                    better_thinking=data.get("mindset_advice", {}).get("better_thinking", ""),
                    dealing_with_difficulty=data.get("mindset_advice", {}).get("dealing_with_difficulty", "")
                ),
                life_balance_advice=LifeBalanceAdvice(
                    physical_impact=data.get("life_balance_advice", {}).get("physical_impact", ""),
                    sleep_energy_advice=data.get("life_balance_advice", {}).get("sleep_energy_advice", ""),
                    non_tech_action=data.get("life_balance_advice", {}).get("non_tech_action", "")
                ),
                priority_focus=data.get("priority_focus", "Focus on consistent small steps"),
                quick_wins=data.get("quick_wins", [])
            )
            
        except (json.JSONDecodeError, Exception) as e:
            return self._fallback_response(state, str(e))
    
    def _fallback_response(self, state: StudentState, error: str) -> AdvisorResponse:
        """Create fallback response when parsing fails."""
        return AdvisorResponse(
            situation_summary=f"Based on your profile as a {state.student_profile.current_level.value} "
                            f"studying {state.learning_state.current_topic}, heading toward {state.student_profile.career_goal}.",
            analysis=StudentAnalysis(
                main_weaknesses=["Unable to fully analyze - provide more details"],
                hidden_risks=["Monitor your stress and energy levels"],
                strengths_to_build=["Your commitment to seeking guidance shows growth mindset"]
            ),
            learning_advice=LearningAdvice(
                study_approach=f"For {state.learning_state.current_topic}: Start with fundamentals, build up gradually",
                style_changes=["Focus on understanding over completion", "Take more breaks"],
                likely_mistakes=["Rushing through material", "Not practicing enough"],
                technique_to_try="Spend 25 minutes focused study, then 5 minute break (Pomodoro)"
            ),
            technical_career_advice=TechnicalCareerAdvice(
                priority_skill=state.student_profile.field_of_interest,
                recommended_focus="projects",
                focus_reasoning="Building projects creates tangible evidence of your skills",
                career_action="Start a small project using what you're learning"
            ),
            productivity_advice=ProductivityAdvice(
                harmful_habit="Inconsistent study schedule",
                habit_to_remove="Phone during study time",
                habit_to_add="Fixed daily study block, same time each day",
                day_structure="Study during your peak energy time, rest when energy is low"
            ),
            mindset_advice=MindsetAdvice(
                wrong_belief="I need to understand everything perfectly",
                better_thinking="Understanding comes through practice, not just study",
                dealing_with_difficulty="Confusion is a sign you're learning something new - embrace it"
            ),
            life_balance_advice=LifeBalanceAdvice(
                physical_impact="Your brain is part of your body - physical health affects learning",
                sleep_energy_advice="Prioritize 7-8 hours of sleep for better retention",
                non_tech_action="Take a 20-minute walk outside today"
            ),
            priority_focus="Build a consistent daily learning habit, even if just 30 minutes",
            quick_wins=[
                "Review what you learned yesterday for 10 minutes",
                "Write down your #1 goal for today",
                "Drink water and take a short walk"
            ]
        )
    
    @staticmethod
    def from_quick_request(request: QuickAdvisorRequest) -> StudentState:
        """Convert QuickAdvisorRequest to StudentState."""
        from app.models.advisor_schemas import SkillLevel, UnderstandingLevel
        
        # Map string levels to enums
        level_map = {"low": Level.LOW, "medium": Level.MEDIUM, "high": Level.HIGH}
        skill_map = {"beginner": SkillLevel.BEGINNER, "intermediate": SkillLevel.INTERMEDIATE, "advanced": SkillLevel.ADVANCED}
        understand_map = {"low": UnderstandingLevel.LOW, "medium": UnderstandingLevel.MEDIUM, "high": UnderstandingLevel.HIGH}
        sleep_map = {"poor": SleepQuality.POOR, "normal": SleepQuality.NORMAL, "good": SleepQuality.GOOD}
        
        return StudentState(
            student_profile=StudentProfile(
                career_goal=request.career_goal,
                current_level=skill_map.get(request.current_level.lower(), SkillLevel.BEGINNER),
                field_of_interest=request.field_of_interest,
                available_hours_per_day=request.hours_per_day
            ),
            learning_state=LearningState(
                current_topic=request.current_topic,
                understanding_level=understand_map.get(request.understanding.lower(), UnderstandingLevel.MEDIUM),
                recent_struggles=request.struggles,
                consistency_level=level_map.get(request.study_consistency.lower(), Level.MEDIUM)
            ),
            behavior_state=BehaviorState(
                focus_level=level_map.get(request.focus.lower(), Level.MEDIUM),
                procrastination_level=level_map.get(request.procrastination.lower(), Level.MEDIUM),
                energy_level=level_map.get(request.energy.lower(), Level.MEDIUM),
                sleep_quality=sleep_map.get(request.sleep.lower(), SleepQuality.NORMAL)
            ),
            emotional_state=EmotionalState(
                motivation_level=level_map.get(request.motivation.lower(), Level.MEDIUM),
                stress_level=level_map.get(request.stress.lower(), Level.MEDIUM),
                confidence_level=level_map.get(request.confidence.lower(), Level.MEDIUM)
            )
        )
