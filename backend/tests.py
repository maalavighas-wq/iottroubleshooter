"""
Backend tests for the IoT Troubleshooting Chatbot.
Run with: pytest tests.py -v
"""

import sys
import os

# Make sure imports resolve from backend/
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from fastapi.testclient import TestClient
from main import app
from troubleshooting_engine import (
    classify_issue, detect_device, is_positive_response,
    is_negative_response, is_restart_request, process_message,
)
from schemas import IssueCategory, ResolutionStatus, SessionState
from retrieval import retrieve, retrieve_sources, get_documents
from session_manager import get_session, clear_session, reset_session

client = TestClient(app)


# ---------------------------------------------------------------------------
# Issue classification tests
# ---------------------------------------------------------------------------

class TestClassification:
    def test_connectivity_offline(self):
        assert classify_issue("My smart bulb is offline") == IssueCategory.CONNECTIVITY

    def test_connectivity_wifi(self):
        assert classify_issue("Device won't connect to Wi-Fi") == IssueCategory.CONNECTIVITY

    def test_connectivity_disconnecting(self):
        assert classify_issue("My plug keeps disconnecting") == IssueCategory.CONNECTIVITY

    def test_setup_pairing(self):
        assert classify_issue("Can't pair my smart speaker") == IssueCategory.SETUP

    def test_setup_adding(self):
        assert classify_issue("App is not finding the device during setup") == IssueCategory.SETUP

    def test_firmware(self):
        assert classify_issue("Firmware update failed on my camera") == IssueCategory.FIRMWARE

    def test_configuration(self):
        assert classify_issue("My schedule automation is not running") == IssueCategory.CONFIGURATION

    def test_unknown(self):
        result = classify_issue("hello there")
        assert result == IssueCategory.UNKNOWN


class TestDeviceDetection:
    def test_bulb(self):
        assert detect_device("My smart bulb won't connect") == "smart_bulb"

    def test_plug(self):
        assert detect_device("Smart plug is offline") == "smart_plug"

    def test_speaker(self):
        assert detect_device("Alexa speaker not working") == "smart_speaker"

    def test_camera(self):
        assert detect_device("Ring camera is offline") == "smart_camera"

    def test_none(self):
        assert detect_device("device is broken") is None


class TestResponses:
    def test_positive(self):
        assert is_positive_response("yes") is True
        assert is_positive_response("it works now") is True
        assert is_positive_response("they are working") is True

    def test_negative(self):
        assert is_negative_response("no") is True
        assert is_negative_response("still not working") is True

    def test_restart(self):
        assert is_restart_request("restart") is True
        assert is_restart_request("start over") is True


# ---------------------------------------------------------------------------
# Retrieval tests
# ---------------------------------------------------------------------------

class TestRetrieval:
    def test_documents_loaded(self):
        docs = get_documents()
        assert len(docs) > 0

    def test_retrieval_bulb(self):
        results = retrieve("smart bulb offline connectivity", top_k=2)
        assert len(results) > 0
        # Top result should be related to smart bulb
        top_doc = results[0][0]
        assert "bulb" in top_doc["category"].lower() or "bulb" in top_doc["title"].lower()

    def test_retrieval_wifi(self):
        results = retrieve("wi-fi connectivity router", top_k=2)
        assert len(results) > 0

    def test_sources_shape(self):
        sources = retrieve_sources("smart plug setup pairing")
        assert isinstance(sources, list)
        for s in sources:
            assert s.title
            assert s.document
            assert 0.0 <= s.relevance <= 1.0


# ---------------------------------------------------------------------------
# Conversation / troubleshooting engine tests
# ---------------------------------------------------------------------------

class TestConversationEngine:
    def _fresh_state(self, session_id="test_session"):
        clear_session(session_id)
        return get_session(session_id)

    def test_initial_greeting_bulb_offline(self):
        state = self._fresh_state("t1")
        reply, updated = process_message(state, "My smart bulb is offline")
        assert "step" in reply.lower() or "bulb" in reply.lower() or "light" in reply.lower()
        assert updated.device_type == "smart_bulb"
        assert updated.issue_category == IssueCategory.CONNECTIVITY

    def test_step_progression_no(self):
        state = self._fresh_state("t2")
        _, state = process_message(state, "My smart bulb is offline")
        _, state = process_message(state, "No")  # step didn't work
        assert state.current_step_index >= 2

    def test_resolution_on_yes(self):
        """After exhausting all steps with No, status becomes UNRESOLVED.
        If user says 'it works now' at any point during troubleshooting, status becomes RESOLVED."""
        state = self._fresh_state("t3")
        _, state = process_message(state, "My smart bulb is offline")
        # Say 'it works now' after only 1 step — should become RESOLVED
        reply, state = process_message(state, "it works now")
        assert state.resolution_status == ResolutionStatus.RESOLVED

    def test_exhausted_steps_become_unresolved(self):
        state = self._fresh_state("t3b")
        _, state = process_message(state, "My smart bulb is offline")
        # Advance through ALL steps
        for _ in range(8):
            _, state = process_message(state, "No")
        # All steps exhausted → UNRESOLVED
        assert state.resolution_status == ResolutionStatus.UNRESOLVED

    def test_restart_clears_state(self):
        state = self._fresh_state("t4")
        _, state = process_message(state, "My smart plug is offline")
        _, state = process_message(state, "restart")
        assert state.issue_category == IssueCategory.UNKNOWN
        assert state.current_step_index == 0

    def test_acceptance_scenario(self):
        """
        End-to-end acceptance test:
        User: "My smart bulb is offline."
        → Bot asks about power
        User: "Yes."
        → Bot suggests router/other devices check
        User: "They are working."
        → Bot suggests Wi-Fi band / pairing check
        User: "It works now."
        → Bot confirms resolution with summary
        """
        state = self._fresh_state("acceptance")
        reply1, state = process_message(state, "My smart bulb is offline")
        assert "step" in reply1.lower() or "switch" in reply1.lower() or "power" in reply1.lower()

        reply2, state = process_message(state, "Yes")
        # Should NOT say resolved — should move to next step
        assert state.resolution_status != ResolutionStatus.RESOLVED
        assert "step" in reply2.lower() or "router" in reply2.lower() or "cycle" in reply2.lower()

        reply3, state = process_message(state, "They are working")
        assert state.resolution_status != ResolutionStatus.RESOLVED

        reply4, state = process_message(state, "It works now")
        assert state.resolution_status == ResolutionStatus.RESOLVED
        assert "summary" in reply4.lower() or "resolved" in reply4.lower() or "excellent" in reply4.lower()


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestAPI:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "mode" in data
        assert "version" in data

    def test_devices(self):
        resp = client.get("/devices")
        assert resp.status_code == 200
        data = resp.json()
        assert "devices" in data
        assert len(data["devices"]) >= 4

    def test_chat_basic(self):
        resp = client.post("/chat", json={
            "message": "My smart bulb is offline",
            "session_id": "api_test_1",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert data["reply"]
        assert "session_id" in data

    def test_chat_empty_message(self):
        resp = client.post("/chat", json={
            "message": "   ",
            "session_id": "api_test_2",
        })
        assert resp.status_code == 422

    def test_chat_session_continuity(self):
        sid = "api_session_continuity"
        client.post("/chat", json={"message": "My smart bulb is offline", "session_id": sid})
        resp = client.post("/chat", json={"message": "No", "session_id": sid})
        assert resp.status_code == 200
        data = resp.json()
        assert data["current_step"] >= 2

    def test_feedback(self):
        resp = client.post("/feedback", json={
            "session_id": "api_test_fb",
            "step_index": 0,
            "worked": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["acknowledged"] is True


# ---------------------------------------------------------------------------
# Session management tests
# ---------------------------------------------------------------------------

class TestSessionManager:
    def test_create_and_retrieve(self):
        sid = "sm_test_1"
        clear_session(sid)
        s1 = get_session(sid)
        s2 = get_session(sid)
        assert s1.session_id == s2.session_id == sid

    def test_reset(self):
        sid = "sm_test_2"
        state = get_session(sid)
        state.device_type = "smart_bulb"
        from session_manager import save_session
        save_session(state)
        fresh = reset_session(sid)
        assert fresh.device_type is None
