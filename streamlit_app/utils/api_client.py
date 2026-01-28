"""API Client for communicating with the FastAPI backend."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from uuid import UUID

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


class APIClient:
    """Centralized API client for all backend calls."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.timeout = 120  # 2 minutes for LLM calls
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)
            raise APIError(f"API Error: {error_detail}", response.status_code)
        except requests.exceptions.RequestException as e:
            raise APIError(f"Connection Error: {str(e)}", 0)
    
    # ============ Interview Endpoints ============
    
    def start_interview(
        self,
        user_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Start a new interview session."""
        response = requests.post(
            f"{self.base_url}/api/interview/start",
            json={"user_id": user_id, "config": config},
            timeout=self.timeout,
        )
        return self._handle_response(response)
    
    def submit_answer(
        self,
        session_id: str,
        question: str,
        answer: str,
    ) -> Dict[str, Any]:
        """Submit an answer to the current interview question."""
        response = requests.post(
            f"{self.base_url}/api/interview/answer",
            json={
                "session_id": session_id,
                "question": question,
                "answer": answer,
            },
            timeout=self.timeout,
        )
        return self._handle_response(response)
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status."""
        response = requests.get(
            f"{self.base_url}/api/interview/{session_id}",
            timeout=self.timeout,
        )
        return self._handle_response(response)
    
    def get_final_report(self, session_id: str) -> Dict[str, Any]:
        """Get the final interview report."""
        response = requests.get(
            f"{self.base_url}/api/interview/{session_id}/report",
            timeout=self.timeout,
        )
        return self._handle_response(response)
    
    # ============ Career Translator Endpoints ============
    
    def translate_lecture(
        self,
        lecture_topic: str,
        lecture_text: Optional[str] = None,
        target_track: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Translate a lecture to career-relevant content."""
        payload = {"lecture_topic": lecture_topic}
        if lecture_text:
            payload["lecture_text"] = lecture_text
        if target_track:
            payload["target_track"] = target_track
        
        response = requests.post(
            f"{self.base_url}/api/career/translate",
            json=payload,
            timeout=self.timeout,
        )
        return self._handle_response(response)
    
    # ============ Opportunity Matcher Endpoints ============
    
    def match_opportunities(
        self,
        academic_year: int,
        preference: str,
        track: str,
        skills: List[str],
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Match user with internship opportunities."""
        payload = {
            "academic_year": academic_year,
            "preference": preference,
            "track": track,
            "skills": skills,
        }
        if notes:
            payload["notes"] = notes
        
        response = requests.post(
            f"{self.base_url}/match",
            json=payload,
            timeout=self.timeout,
        )
        return self._handle_response(response)
    
    # ============ Task Simulation Endpoints ============
    
    def get_companies(self) -> List[Dict[str, str]]:
        """Get list of available companies for task simulation."""
        response = requests.get(
            f"{self.base_url}/companies",
            timeout=self.timeout,
        )
        return self._handle_response(response)
    
    def generate_task_simulation(
        self,
        company_name: str,
        task_title: str,
    ) -> Dict[str, Any]:
        """Generate a task simulation scenario."""
        response = requests.post(
            f"{self.base_url}/task-simulation",
            json={
                "company_name": company_name,
                "task_title": task_title,
            },
            timeout=self.timeout,
        )
        return self._handle_response(response)
    
    # ============ Health Check ============
    
    def health_check(self) -> bool:
        """Check if the API is healthy."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False


class APIError(Exception):
    """Custom exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 0):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Singleton instance
api_client = APIClient()
