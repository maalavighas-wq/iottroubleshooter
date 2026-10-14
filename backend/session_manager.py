"""
Session management — in-memory store for active troubleshooting sessions.
"""

from typing import Dict, Optional
from schemas import SessionState, IssueCategory, ResolutionStatus


_sessions: Dict[str, SessionState] = {}


def get_session(session_id: str) -> SessionState:
    if session_id not in _sessions:
        _sessions[session_id] = SessionState(session_id=session_id)
    return _sessions[session_id]


def save_session(state: SessionState) -> None:
    _sessions[state.session_id] = state


def clear_session(session_id: str) -> None:
    if session_id in _sessions:
        del _sessions[session_id]


def reset_session(session_id: str) -> SessionState:
    """Reset troubleshooting state but keep session id."""
    clear_session(session_id)
    return get_session(session_id)
