"""Practical Project Recommender Agent - Converts topics into hands-on projects."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.agents.base_agent import BaseInterviewAgent
from app.agents.recommender_prompts import PRACTICAL_PROJECT_RECOMMENDER_PROMPT
from app.models.recommender_schemas import (
    ProjectBuildRecommendation,
    YouTubeProjectPlaylist,
    GitHubGuidance,
    PracticalProjectResponse,
    ProjectRequest,
)

logger = logging.getLogger(__name__)


class PracticalProjectRecommenderAgent(BaseInterviewAgent):
    """
    AI Agent that converts learning topics into hands-on, portfolio-ready projects.
    
    Features:
    - Recommends beginner, intermediate, and advanced projects
    - Provides professional GitHub repository structure guidance
    - Suggests YouTube project-building tutorials
    - Focuses on employability and portfolio building
    - Teaches industry best practices
    """
    
    def __init__(self, **kwargs):
        super().__init__(temperature=0.7, **kwargs)
    
    def get_prompt_template(self) -> str:
        return PRACTICAL_PROJECT_RECOMMENDER_PROMPT
    
    def get_default_response(self) -> Dict[str, Any]:
        """Return a default response structure."""
        return {
            "topic": "Unknown",
            "topic_summary": "Unable to analyze topic",
            "projects": [],
            "youtube_project_playlists": [],
            "why_build_projects": [],
            "portfolio_tips": [],
            "next_steps": []
        }
    
    async def recommend(
        self, 
        request: ProjectRequest
    ) -> PracticalProjectResponse:
        """
        Generate practical project recommendations.
        
        Args:
            request: ProjectRequest with topic and preferences
            
        Returns:
            PracticalProjectResponse with project recommendations
        """
        try:
            response = await self.invoke(
                topic=request.topic,
                current_level=request.current_level,
                time_available=request.time_available,
                focus_on_portfolio=str(request.focus_on_portfolio),
            )
            
            parsed = self.parse_json_response(response)
            return self._build_recommendation(parsed, request.max_projects)
            
        except Exception as e:
            logger.error(f"Error generating project recommendations: {e}")
            raise
    
    def recommend_sync(
        self, 
        request: ProjectRequest
    ) -> PracticalProjectResponse:
        """Synchronous version of recommend."""
        try:
            response = self.invoke_sync(
                topic=request.topic,
                current_level=request.current_level,
                time_available=request.time_available,
                focus_on_portfolio=str(request.focus_on_portfolio),
            )
            
            parsed = self.parse_json_response(response)
            return self._build_recommendation(parsed, request.max_projects)
            
        except Exception as e:
            logger.error(f"Error generating project recommendations: {e}")
            raise
    
    def _build_recommendation(
        self, 
        data: Dict[str, Any],
        max_projects: int
    ) -> PracticalProjectResponse:
        """Build PracticalProjectResponse from parsed JSON."""
        
        def parse_projects(projects_list: List[Dict]) -> List[ProjectBuildRecommendation]:
            """Parse project recommendations with GitHub guidance."""
            results = []
            for item in projects_list[:max_projects]:
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
        
        projects = parse_projects(data.get("projects", []))
        youtube_playlists = parse_youtube_playlists(data.get("youtube_project_playlists", []))
        
        return PracticalProjectResponse(
            topic=data.get("topic", "Unknown"),
            topic_summary=data.get("topic_summary", ""),
            projects=projects,
            youtube_project_playlists=youtube_playlists,
            why_build_projects=data.get("why_build_projects", []),
            portfolio_tips=data.get("portfolio_tips", []),
            next_steps=data.get("next_steps", [])
        )
