from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.match import router as match_router
from app.api.interview import router as interview_router
from app.api.career import router as career_router
from app.api.task_simulation import router as task_simulation_router
from app.api.recap import router as recap_router
from app.api.recommender import router as recommender_router
from app.api.cv import router as cv_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Education Platform - Multi-Agent System",
    description="""
## Multi-Agent Education Platform

This platform provides five main services:

### 1. Interview System
Adaptive technical and behavioral interviews with real-time evaluation, 
difficulty adjustment, and comprehensive reporting using 7 specialized AI agents.

### 2. Career Translator
Converts academic lectures into industry value, job skills, and company-style tasks.
Acts as an Industry Mentor translating learning into career acceleration.

### 3. Opportunity Matcher (Legacy)
Matches students with internship opportunities based on their profile and skills.

### 4. Recap Agent
Provides perfect summaries, study tips, learning tracks, and quick reference materials
for any lecture or topic. Includes flashcards, practice exercises, and milestones.

### 5. Recommender Multi-Agent
AI-powered recommendation system with specialized agents:
- **Internship Recommender**: Personalized internship matching with skill gap analysis
- **Event Recommender**: Hackathons, workshops, conferences, and competitions
- **Course Recommender**: Popular courses and certifications for any topic
- **Skills/Tools Recommender**: Related skills and tools for career development

### 6. CV Creator Agent (NEW)
AI-powered CV generation system that:
- Collects skills from interviews, courses, projects, and experience
- Allows students to add their own skills
- Generates professional, ATS-friendly CVs
    """,
    version="1.2.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(match_router)
app.include_router(interview_router)
app.include_router(career_router)
app.include_router(task_simulation_router)
app.include_router(recap_router)
app.include_router(recommender_router)
app.include_router(cv_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Education Platform - Multi-Agent System",
        "version": "1.1.0",
        "services": {
            "career_translator": {
                "description": "Convert lectures to industry value",
                "endpoint": "/api/career/translate"
            },
            "interview": {
                "description": "Adaptive interview system",
                "endpoint": "/api/interview"
            },
            "match": {
                "description": "Opportunity matching (legacy)",
                "endpoint": "/match"
            },
            "task_simulation": {
                "description": "Generate internship task scenarios",
                "endpoint": "/task-simulation"
            },
            "recap": {
                "description": "Lecture summaries and learning tracks",
                "endpoints": {
                    "full_recap": "/api/recap/generate",
                    "quick_summary": "/api/recap/quick-summary",
                    "study_plan": "/api/recap/study-plan",
                    "flashcards": "/api/recap/flashcards"
                }
            },
            "recommender": {
                "description": "AI-powered recommendations",
                "endpoints": {
                    "internships": "/api/recommend/internships",
                    "events": "/api/recommend/events",
                    "courses": "/api/recommend/courses",
                    "skills_tools": "/api/recommend/skills-tools",
                    "all": "/api/recommend/all"
                }
            },
            "cv_creator": {
                "description": "AI-powered CV generation with skill collection",
                "endpoints": {
                    "collect_skills": "/api/cv/skills/collect",
                    "add_skills": "/api/cv/skills/add",
                    "generate_cv": "/api/cv/generate",
                    "generate_summary": "/api/cv/summary"
                }
            }
        },
        "documentation": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
