from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class IssueCategory(str, Enum):
    CONNECTIVITY = "connectivity"
    SETUP = "setup"
    CONFIGURATION = "configuration"
    FIRMWARE = "firmware"
    COMPATIBILITY = "compatibility"
    GENERAL = "general"
    UNKNOWN = "unknown"


class ResolutionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    ESCALATED = "escalated"


class DeviceType(str, Enum):
    SMART_BULB = "smart_bulb"
    SMART_PLUG = "smart_plug"
    SMART_SPEAKER = "smart_speaker"
    SMART_CAMERA = "smart_camera"
    ROUTER = "router"
    OTHER = "other"


class Source(BaseModel):
    title: str
    document: str
    relevance: float = 0.0


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=1, max_length=100)
    device_type: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    issue_category: IssueCategory = IssueCategory.UNKNOWN
    current_step: int = 0
    total_steps: int = 0
    suggested_action: Optional[str] = None
    resolution_status: ResolutionStatus = ResolutionStatus.IN_PROGRESS
    sources: List[Source] = []
    is_general_guidance: bool = False
    summary: Optional[dict] = None


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    step_index: int = Field(..., ge=0)
    worked: bool
    message: Optional[str] = None


class FeedbackResponse(BaseModel):
    acknowledged: bool
    message: str


class DeviceInfo(BaseModel):
    id: str
    name: str
    icon: str
    description: str
    common_issues: List[str]


class DevicesResponse(BaseModel):
    devices: List[DeviceInfo]


class HealthResponse(BaseModel):
    status: str
    mode: str
    version: str
    rag_available: bool
    llm_available: bool


class SessionState(BaseModel):
    session_id: str
    device_type: Optional[str] = None
    issue_category: IssueCategory = IssueCategory.UNKNOWN
    symptoms: List[str] = []
    attempted_steps: List[str] = []
    current_step_index: int = 0
    resolution_status: ResolutionStatus = ResolutionStatus.IN_PROGRESS
    conversation_history: List[dict] = []
    awaiting: Optional[str] = None  # what the bot is waiting for
