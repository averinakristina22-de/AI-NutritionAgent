"""
Session Service - Manages user sessions and conversation state

⚠️ DEPRECATED: This service is no longer used in the current implementation.

The main.py file now uses InMemorySessionService directly from google.adk.sessions
and shares a single session instance across all agents. Data is shared between
agents using session.state dictionary instead of this service's methods.

WHAT REPLACED IT:
- Direct use of InMemorySessionService in NutritionOrchestrator
- Shared session across all agents
- session.state for inter-agent data sharing

This file is kept for reference only.

Based on ADK session management patterns (Day 3a - Agent Sessions).
"""

from google.adk.sessions import InMemorySessionService, Session
from typing import Optional
import os


# Global session service instance
_session_service_instance: Optional[InMemorySessionService] = None


def get_session_service() -> InMemorySessionService:
    """
    Get or create the global session service instance.

    This follows the singleton pattern to ensure we have one
    session service across the application.

    Returns:
        InMemorySessionService instance
    """
    global _session_service_instance

    if _session_service_instance is None:
        _session_service_instance = InMemorySessionService()

    return _session_service_instance


async def create_user_session(user_id: str, session_id: Optional[str] = None) -> Session:
    """
    Create a new session for a user.

    Args:
        user_id: Unique identifier for the user
        session_id: Optional custom session ID (auto-generated if not provided)

    Returns:
        Created Session object
    """
    service = get_session_service()

    if not session_id:
        # Auto-generate session ID based on user
        session_id = f"nutrition_session_{user_id}"

    # Create session with required app_name and user_id parameters (async call)
    session = await service.create_session(
        app_name="nutrition-agent",
        user_id=user_id,
        session_id=session_id
    )

    # Store additional metadata for tracking in session state
    session.state["user_id"] = user_id
    session.state["app_name"] = "nutrition-agent"

    return session


async def get_user_session(session_id: str, app_name: str = "nutrition-agent") -> Optional[Session]:
    """
    Retrieve an existing session.

    Args:
        session_id: Session identifier
        app_name: Application name (default: "nutrition-agent")

    Returns:
        Session object if found, None otherwise
    """
    service = get_session_service()
    try:
        return await service.get_session(app_name=app_name, session_id=session_id)
    except Exception:
        return None


def list_user_sessions(user_id: str) -> list:
    """
    List all sessions for a specific user.

    Args:
        user_id: User identifier

    Returns:
        List of session IDs for the user
    """
    service = get_session_service()

    # This is a simplified implementation
    # In production, you'd want to track user sessions in a database
    all_sessions = []

    # Note: InMemorySessionService doesn't provide a list method
    # For production, use a persistent session store with query capabilities
    # This is a placeholder to demonstrate the intended functionality

    return all_sessions


async def delete_session(session_id: str, app_name: str = "nutrition-agent") -> bool:
    """
    Delete a session.

    Args:
        session_id: Session to delete
        app_name: Application name (default: "nutrition-agent")

    Returns:
        True if deleted, False otherwise
    """
    service = get_session_service()
    try:
        await service.delete_session(app_name=app_name, session_id=session_id)
        return True
    except Exception:
        return False


class SessionManager:
    """
    Higher-level session manager for the nutrition agent system.

    ⚠️ DEPRECATED - NOT CURRENTLY USED

    This class was designed for tracking consultation stages and managing
    the workflow between agents. However, the current implementation:
    - Uses a single shared session across all agents
    - Tracks data in session.state instead of separate session manager
    - Agents communicate via session.state keys

    KEPT FOR REFERENCE: This pattern could be useful if you need:
    - Multi-stage workflow tracking
    - Complex consultation state management
    - Stage-based validation and progression
    """

    def __init__(self):
        self.service = get_session_service()

    async def start_consultation(self, user_id: str) -> str:
        """
        Start a new nutrition consultation session.

        Args:
            user_id: User identifier

        Returns:
            Session ID for the consultation
        """
        session = await create_user_session(user_id)
        session.state["user_id"] = user_id
        session.state["stage"] = "interview"  # Tracks consultation stage
        session.state["consultation_type"] = "nutrition"
        session.state["completed_agents"] = []
        return session.id

    async def update_consultation_stage(
        self,
        session_id: str,
        stage: str,
        completed_agent: Optional[str] = None
    ):
        """
        Update the current stage of a consultation.

        Args:
            session_id: Session identifier
            stage: New stage (interview, analysis, compatibility, recipe_generation)
            completed_agent: Name of agent that just completed
        """
        session = await get_user_session(session_id)
        if session:
            session.state["stage"] = stage
            if completed_agent:
                session.state["completed_agents"].append(completed_agent)

    async def get_consultation_stage(self, session_id: str) -> Optional[str]:
        """
        Get the current consultation stage.

        Args:
            session_id: Session identifier

        Returns:
            Current stage name or None
        """
        session = await get_user_session(session_id)
        if session and "stage" in session.state:
            return session.state["stage"]
        return None

    async def is_consultation_complete(self, session_id: str) -> bool:
        """
        Check if a consultation has completed all stages.

        Args:
            session_id: Session identifier

        Returns:
            True if all agents have completed
        """
        session = await get_user_session(session_id)
        if session and "completed_agents" in session.state:
            expected_agents = [
                "interview_agent",
                "analysis_agent",
                "compatibility_agent",
                "recipe_generator_agent"
            ]
            completed = session.state["completed_agents"]
            return all(agent in completed for agent in expected_agents)
        return False
