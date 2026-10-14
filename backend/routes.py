"""
API routes for the IoT Troubleshooting Chatbot.
"""

from fastapi import APIRouter, HTTPException
from schemas import (
    ChatRequest, ChatResponse, FeedbackRequest, FeedbackResponse,
    DevicesResponse, DeviceInfo, HealthResponse,
    IssueCategory, ResolutionStatus,
)
from session_manager import get_session, save_session, reset_session
from troubleshooting_engine import (
    process_message, classify_issue, detect_device, build_query, get_summary_dict
)
from retrieval import retrieve_sources, RAG_AVAILABLE
from llm_config import is_available as llm_available, get_mode as llm_mode

router = APIRouter()

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        mode=llm_mode(),
        version="1.0.0",
        rag_available=RAG_AVAILABLE,
        llm_available=llm_available(),
    )


# ---------------------------------------------------------------------------
# Devices
# ---------------------------------------------------------------------------

@router.get("/devices", response_model=DevicesResponse)
def get_devices():
    devices = [
        DeviceInfo(
            id="smart_bulb",
            name="Smart Bulb",
            icon="💡",
            description="Wi-Fi or Bluetooth smart lighting",
            common_issues=["Offline", "Won't pair", "Keeps disconnecting", "Firmware update failed"],
        ),
        DeviceInfo(
            id="smart_plug",
            name="Smart Plug",
            icon="🔌",
            description="Wi-Fi smart plug / socket",
            common_issues=["Offline", "Won't pair", "Schedule not working", "App not detecting"],
        ),
        DeviceInfo(
            id="smart_speaker",
            name="Smart Speaker",
            icon="🔊",
            description="Voice assistant speaker (Echo, Nest, HomePod)",
            common_issues=["Offline", "Won't set up", "Audio issues", "Wi-Fi reconnect"],
        ),
        DeviceInfo(
            id="smart_camera",
            name="Smart Camera",
            icon="📷",
            description="Wi-Fi security / doorbell camera",
            common_issues=["Offline", "No stream", "Setup failure", "Firmware update"],
        ),
        DeviceInfo(
            id="other",
            name="Other Smart Device",
            icon="📡",
            description="Any other Wi-Fi smart home device",
            common_issues=["Offline", "Won't pair", "Connectivity", "General issue"],
        ),
    ]
    return DevicesResponse(devices=devices)


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    state = get_session(req.session_id)

    # Override device type if provided explicitly
    if req.device_type and not state.device_type:
        state.device_type = req.device_type

    # Store message in history
    state.conversation_history.append({"role": "user", "content": req.message})

    # Process the message through the rule-based engine
    reply, state = process_message(state, req.message)

    # Store reply in history
    state.conversation_history.append({"role": "assistant", "content": reply})
    save_session(state)

    # Retrieve knowledge base sources
    query = build_query(state)
    sources = retrieve_sources(query, top_k=2) if query.strip() else []

    # Determine if this is general guidance (no KB source found or low relevance)
    is_general = len(sources) == 0 or (sources and sources[0].relevance < 0.2)

    # Build summary if resolved or unresolved
    summary = None
    if state.resolution_status in (ResolutionStatus.RESOLVED, ResolutionStatus.UNRESOLVED):
        summary = get_summary_dict(state)

    steps = []
    from troubleshooting_engine import get_steps
    if state.issue_category != IssueCategory.UNKNOWN:
        steps = get_steps(state.issue_category, state.device_type)

    return ChatResponse(
        reply=reply,
        session_id=req.session_id,
        issue_category=state.issue_category,
        current_step=state.current_step_index,
        total_steps=len(steps),
        suggested_action=None,
        resolution_status=state.resolution_status,
        sources=sources,
        is_general_guidance=is_general,
        summary=summary,
    )


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

_feedback_log: list = []


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest):
    _feedback_log.append(req.model_dump())
    return FeedbackResponse(
        acknowledged=True,
        message="Thank you for your feedback! This helps improve the troubleshooting guides.",
    )
