"""Event Recommender Agent - Recommends hackathons, workshops, and events."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.agents.base_agent import BaseInterviewAgent
from app.agents.recommender_prompts import EVENT_RECOMMENDER_PROMPT
from app.models.recommender_schemas import (
    EventMatch,
    EventRecommendation,
    EventRequest,
    UserPreferences,
    ProjectBuildRecommendation,
    YouTubeProjectPlaylist,
    GitHubGuidance,
)

logger = logging.getLogger(__name__)


class EventRecommenderAgent(BaseInterviewAgent):
    """
    AI Agent that recommends events, hackathons, and learning opportunities.
    
    Features:
    - Finds relevant hackathons and competitions
    - Recommends workshops and conferences
    - Matches events to student interests
    - Provides preparation tips and benefits
    """
    
    def __init__(self, **kwargs):
        super().__init__(temperature=0.7, **kwargs)
    
    def get_prompt_template(self) -> str:
        return EVENT_RECOMMENDER_PROMPT
    
    def get_default_response(self) -> Dict[str, Any]:
        """Return a default response structure."""
        return {
            "user_profile_summary": "Unable to analyze profile",
            "total_events": 0,
            "hackathons": [],
            "workshops": [],
            "conferences": [],
            "competitions": [],
            "meetups": [],
            "recommended_projects": [],
            "youtube_playlists": [],
            "preparation_tips": [],
            "benefits": [],
            "upcoming_deadlines": []
        }
    
    async def recommend(
        self, 
        request: EventRequest
    ) -> EventRecommendation:
        """
        Generate event recommendations based on user preferences.
        
        Args:
            request: EventRequest with user preferences
            
        Returns:
            EventRecommendation with matched events
        """
        prefs = request.preferences
        
        try:
            response = await self.invoke(
                academic_year=prefs.academic_year,
                track=prefs.track,
                skills=", ".join(prefs.skills) if prefs.skills else "Not specified",
                interests=", ".join(prefs.interests) if prefs.interests else "Not specified",
                location_preference=prefs.location_preference,
                availability=prefs.availability or "Flexible",
                event_types=", ".join(request.event_types),
                timeframe=request.timeframe,
                include_online=str(request.include_online),
            )
            
            parsed = self.parse_json_response(response)
            return self._build_recommendation(parsed, request.max_results)
            
        except Exception as e:
            logger.error(f"Error generating event recommendations: {e}")
            raise
    
    def recommend_sync(
        self, 
        request: EventRequest
    ) -> EventRecommendation:
        """Synchronous version of recommend."""
        prefs = request.preferences
        
        try:
            response = self.invoke_sync(
                academic_year=prefs.academic_year,
                track=prefs.track,
                skills=", ".join(prefs.skills) if prefs.skills else "Not specified",
                interests=", ".join(prefs.interests) if prefs.interests else "Not specified",
                location_preference=prefs.location_preference,
                availability=prefs.availability or "Flexible",
                event_types=", ".join(request.event_types),
                timeframe=request.timeframe,
                include_online=str(request.include_online),
            )
            
            parsed = self.parse_json_response(response)
            return self._build_recommendation(parsed, request.max_results)
            
        except Exception as e:
            logger.error(f"Error generating event recommendations: {e}")
            raise
    
    def _build_recommendation(
        self, 
        data: Dict[str, Any], 
        max_results: int
    ) -> EventRecommendation:
        """Build EventRecommendation from parsed JSON."""
        
        def parse_events(events_list: List[Dict], max_count: int) -> List[EventMatch]:
            """Parse a list of event dictionaries into EventMatch objects."""
            results = []
            for item in events_list[:max_count]:
                try:
                    event = EventMatch(
                        name=item.get("name", "Event"),
                        organizer=item.get("organizer", "Unknown"),
                        event_type=item.get("event_type", "event"),
                        format=item.get("format", "in-person"),
                        location=item.get("location"),
                        date_range=item.get("date_range", "TBD"),
                        description=item.get("description", ""),
                        themes=item.get("themes", []),
                        prizes=item.get("prizes"),
                        requirements=item.get("requirements", []),
                        match_score=min(100, max(0, int(item.get("match_score", 50)))),
                        match_reasons=item.get("match_reasons", []),
                        skills_to_gain=item.get("skills_to_gain", []),
                        networking_value=item.get("networking_value", "medium"),
                        registration_url=item.get("registration_url"),
                        registration_deadline=item.get("registration_deadline"),
                        difficulty_level=item.get("difficulty_level", "intermediate"),
                        team_size=item.get("team_size"),
                        icon=item.get("icon", "🎯")
                    )
                    results.append(event)
                except Exception as e:
                    logger.warning(f"Error parsing event: {e}")
                    continue
            return results
        
        def parse_projects(projects_list: List[Dict]) -> List[ProjectBuildRecommendation]:
            """Parse project recommendations with GitHub guidance."""
            results = []
            for item in projects_list:
                try:
                    github_data = item.get("github_guidance", {})
                    github_guidance = GitHubGuidance(
                        repo_name=github_data.get("repo_name", "project-name"),
                        folder_structure=github_data.get("folder_structure", "/src\nREADME.md"),
                        readme_should_contain=github_data.get("readme_should_contain", []),
                        professional_practices=github_data.get("professional_practices", []),
                        sample_commit_messages=github_data.get("sample_commit_messages", [])
                    )
                    
                    project = ProjectBuildRecommendation(
                        name=item.get("name", "Project"),
                        level=item.get("level", "intermediate"),
                        description=item.get("description", ""),
                        what_you_will_build=item.get("what_you_will_build", ""),
                        skills_gained=item.get("skills_gained", []),
                        real_work_connection=item.get("real_work_connection", ""),
                        cv_value=item.get("cv_value", ""),
                        relevant_roles=item.get("relevant_roles", []),
                        tech_stack=item.get("tech_stack", []),
                        estimated_duration=item.get("estimated_duration", ""),
                        github_guidance=github_guidance,
                        match_score=min(100, max(0, int(item.get("match_score", 75)))),
                        icon=item.get("icon", "💼")
                    )
                    results.append(project)
                except Exception as e:
                    logger.warning(f"Error parsing project: {e}")
                    continue
            return results
        
        def parse_youtube_playlists(playlists_list: List[Dict]) -> List[YouTubeProjectPlaylist]:
            """Parse YouTube project playlists."""
            results = []
            for item in playlists_list:
                try:
                    playlist = YouTubeProjectPlaylist(
                        title=item.get("title", ""),
                        focus=item.get("focus", ""),
                        level=item.get("level", "intermediate"),
                        url=item.get("url", ""),
                        channel=item.get("channel"),
                        duration=item.get("duration"),
                        icon=item.get("icon", "🎬")
                    )
                    results.append(playlist)
                except Exception as e:
                    logger.warning(f"Error parsing YouTube playlist: {e}")
                    continue
            return results
        
        hackathons = parse_events(data.get("hackathons", []), max_results)
        workshops = parse_events(data.get("workshops", []), max_results)
        conferences = parse_events(data.get("conferences", []), max_results)
        competitions = parse_events(data.get("competitions", []), max_results)
        meetups = parse_events(data.get("meetups", []), max_results)
        recommended_projects = parse_projects(data.get("recommended_projects", []))
        youtube_playlists = parse_youtube_playlists(data.get("youtube_playlists", []))
        
        total_events = len(hackathons) + len(workshops) + len(conferences) + len(competitions) + len(meetups)
        
        return EventRecommendation(
            user_profile_summary=data.get("user_profile_summary", "Profile analyzed"),
            total_events=data.get("total_events", total_events),
            hackathons=hackathons,
            workshops=workshops,
            conferences=conferences,
            competitions=competitions,
            meetups=meetups,
            recommended_projects=recommended_projects,
            youtube_playlists=youtube_playlists,
            preparation_tips=data.get("preparation_tips", []),
            benefits=data.get("benefits", []),
            upcoming_deadlines=data.get("upcoming_deadlines", [])
        )
