"""
Nutrition Agent System - Services

⚠️ NOTE: The services in this package are currently DEPRECATED/UNUSED.

The current implementation uses:
- Direct InMemorySessionService from google.adk.sessions
- session.state for inter-agent data sharing

These classes are kept for reference and potential future use:
- SessionManager: Example of high-level session management
- MemoryBank: SQLite-based persistent storage (could be useful for future features)
"""

# These are not currently used but kept for reference
from .session_service import get_session_service, SessionManager
from .memory_bank import MemoryBank

__all__ = [
    "get_session_service",
    "SessionManager",
    "MemoryBank",
]
