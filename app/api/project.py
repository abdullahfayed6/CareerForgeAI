"""API endpoints for practical project recommendations."""
from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.models.recommender_schemas import (
    PracticalProjectResponse,
    ProjectRequest,
)
from app.agents.project_recommender import PracticalProjectRecommenderAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/project", tags=["Project Recommendations"])


@router.post("/recommend", response_model=PracticalProjectResponse)
async def get_project_recommendations(
    request: ProjectRequest
) -> PracticalProjectResponse:
    """
    Generate practical, portfolio-ready project recommendations for a topic.
    
    This endpoint:
    - Recommends hands-on projects (beginner, intermediate, advanced)
    - Provides professional GitHub repository structure guidance
    - Suggests YouTube project-building tutorials
    - Focuses on employability and portfolio building
    
    Args:
        request: ProjectRequest with topic and preferences
        
    Returns:
        PracticalProjectResponse with project recommendations
        
    Example request:
    ```json
    {
        "topic": "Full-Stack Web Development",
        "current_level": "intermediate",
        "time_available": "moderate",
        "focus_on_portfolio": true,
        "max_projects": 6
    }
    ```
    """
    try:
        agent = PracticalProjectRecommenderAgent()
        
        # Generate recommendations
        recommendation = await agent.recommend(request)
        
        logger.info(
            f"Generated {len(recommendation.projects)} project recommendations "
            f"and {len(recommendation.youtube_project_playlists)} YouTube playlists "
            f"for topic: {request.topic}"
        )
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Error in project recommendation endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate project recommendations: {str(e)}"
        )


@router.post("/recommend-sync", response_model=PracticalProjectResponse)
def get_project_recommendations_sync(
    request: ProjectRequest
) -> PracticalProjectResponse:
    """
    Synchronous version of project recommendation endpoint.
    
    Args:
        request: ProjectRequest with topic and preferences
        
    Returns:
        PracticalProjectResponse with project recommendations
    """
    try:
        agent = PracticalProjectRecommenderAgent()
        recommendation = agent.recommend_sync(request)
        
        logger.info(
            f"Generated {len(recommendation.projects)} project recommendations "
            f"for topic: {request.topic} (sync)"
        )
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Error in sync project recommendation endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate project recommendations: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Practical Project Recommender",
        "version": "1.0.0"
    }
