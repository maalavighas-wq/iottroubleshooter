"""
Rule-based troubleshooting engine.
Stateful, step-by-step conversation logic for IoT device issues.
"""

import re
from typing import List, Optional, Tuple

from schemas import IssueCategory, ResolutionStatus, SessionState


# ---------------------------------------------------------------------------
# Issue classification
# ---------------------------------------------------------------------------

_CONNECTIVITY_KEYWORDS = [
    "offline", "not connecting", "cannot connect", "disconnecting",
    "disconnects", "keeps dropping", "no wi-fi", "wifi", "wi-fi",
    "network", "internet", "router", "signal", "connection",
]
_SETUP_KEYWORDS = [
    "setup", "set up", "setting up", "pairing", "pair", "can't add",
    "cannot add", "not found", "not detected", "discovery", "install",
    "first time", "new device", "app", "adding",
]
_CONFIG_KEYWORDS = [
    "schedule", "automation", "configuration", "configure", "settings",
    "time zone", "timer", "routine", "rule", "group",
]
_FIRMWARE_KEYWORDS = [
    "firmware", "update", "upgrade", "bricked", "unresponsive after update",
    "update fail", "software update",
]
_DEVICE_KEYWORDS = {
    "smart_bulb": ["bulb", "light", "lamp", "led", "smart light", "hue", "lifx"],
    "smart_plug": ["plug", "socket", "outlet", "smart plug", "kasa", "meross"],
    "smart_speaker": ["speaker", "echo", "alexa", "google home", "nest", "homepod", "siri"],
    "smart_camera": ["camera", "cam", "doorbell", "security camera", "ring", "arlo", "wyze"],
}


def classify_issue(text: str) -> IssueCategory:
    t = text.lower()
    if any(k in t for k in _FIRMWARE_KEYWORDS):
        return IssueCategory.FIRMWARE
    if any(k in t for k in _SETUP_KEYWORDS):
        return IssueCategory.SETUP
    if any(k in t for k in _CONNECTIVITY_KEYWORDS):
        return IssueCategory.CONNECTIVITY
    if any(k in t for k in _CONFIG_KEYWORDS):
        return IssueCategory.CONFIGURATION
    return IssueCategory.UNKNOWN


def detect_device(text: str) -> Optional[str]:
    t = text.lower()
    for device, keywords in _DEVICE_KEYWORDS.items():
        if any(k in t for k in keywords):
            return device
    return None


def is_positive_response(text: str) -> bool:
    t = text.lower().strip()
    positive = [
        "yes", "yeah", "yep", "yup", "sure", "it works", "working",
        "it worked", "fixed", "resolved", "done", "ok", "okay",
        "it's working", "its working", "they are working", "it work",
        "all good", "good now", "works now",
    ]
    return any(p in t for p in positive)


def is_negative_response(text: str) -> bool:
    t = text.lower().strip()
    negative = [
        "no", "nope", "not working", "still not", "doesn't work",
        "does not work", "still offline", "didn't work", "did not work",
        "no luck", "same issue", "still the same", "not fixed",
    ]
    return any(n in t for n in negative)


def is_restart_request(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in ["restart", "start over", "reset chat", "begin again", "new issue"])


# ---------------------------------------------------------------------------
# Step libraries
# ---------------------------------------------------------------------------

_STEPS = {
    "connectivity_bulb": [
        "Is the **wall switch** or lamp switch for the bulb turned **ON**? Smart bulbs need constant power to stay connected.",
        "Try a **power cycle**: turn the bulb off at the switch, wait **10 seconds**, then turn it back on. Wait up to 60 seconds for reconnection.",
        "Are **other Wi-Fi devices** (phone, laptop) in the same room working normally? This will help us know if the router is the issue.",
        "Most smart bulbs only support **2.4 GHz Wi-Fi**. If your router broadcasts both 2.4 GHz and 5 GHz under one name, try creating a separate 2.4 GHz network in your router's admin panel.",
        "Check the **Wi-Fi signal strength** at the bulb's location — it should ideally be within 10 metres of your router with few walls in between.",
        "Try **re-pairing** the bulb in the manufacturer's app (e.g., Philips Hue, LIFX, Kasa): delete the bulb and add it again.",
    ],
    "connectivity_plug": [
        "Is the **smart plug firmly inserted** into the wall socket? Test the socket with another device to make sure the socket is working.",
        "Check the **LED indicator** on the plug — amber/red usually means it is not connected to Wi-Fi.",
        "Try **unplugging the smart plug** from the wall, waiting 15 seconds, then plugging it back in. Allow 60 seconds for reconnection.",
        "Are **other Wi-Fi devices** in the same area working? If not, restart your router.",
        "Smart plugs typically only support **2.4 GHz Wi-Fi**. Make sure your phone is connected to the 2.4 GHz network before re-pairing.",
        "Try **removing and re-adding** the plug in the manufacturer's app (e.g., TP-Link Kasa, Meross).",
    ],
    "connectivity_speaker": [
        "Is the **speaker plugged in and powered on**? Check the power indicator light.",
        "Try **unplugging the speaker** for 30 seconds, then plugging it back in. Wait for the startup chime.",
        "Open the **manufacturer's app** (Alexa, Google Home) and check whether the speaker shows a status. Sometimes the status resolves on its own.",
        "In the app, try **updating the Wi-Fi network** in the speaker's settings and follow the steps to reconnect it.",
    ],
    "connectivity_camera": [
        "Is the **camera powered on**? Check the indicator LED or battery level in the app.",
        "Check the **Wi-Fi signal strength** at the camera's location — cameras are very sensitive to poor signal.",
        "Try **power cycling the camera**: unplug it, wait 15 seconds, then plug it back in. Allow 60 seconds to reconnect.",
        "Verify that your router is working and other devices can access the internet.",
        "If connectivity persists, try **re-pairing** the camera in the app.",
    ],
    "connectivity_general": [
        "Is the **device powered on**? Check any LED indicators.",
        "Try **power cycling the device**: unplug it, wait 15–30 seconds, then plug it back in.",
        "Are **other Wi-Fi devices** working? If not, restart your router.",
        "Most smart home devices only support **2.4 GHz Wi-Fi**. Ensure your 2.4 GHz network is available and your phone is connected to it.",
        "Try **re-pairing the device** using the manufacturer's app.",
    ],
    "setup_general": [
        "First, **reset the device** to factory defaults. For most devices: hold the reset button 5–10 seconds, or rapidly power cycle 5 times.",
        "Make sure your **phone is connected to the 2.4 GHz Wi-Fi** network (not 5 GHz) that you want to use.",
        "Ensure the manufacturer's app has **Location and Local Network permissions** enabled on your phone.",
        "If your phone has a **VPN active**, disable it — VPNs can block device discovery.",
        "Open the app, tap **'Add Device'**, select your device type, and follow the on-screen instructions carefully.",
    ],
    "firmware_general": [
        "Open the **manufacturer's app**, go to the device settings, and check if there is a **firmware update** option.",
        "Make sure the device has **stable power** and is **close to your router** during the update.",
        "Tap **'Update'** and allow the process to complete — do **not** turn off the device during the update (typically 2–10 minutes).",
        "If the update failed and the device is unresponsive, try **power cycling** it and retrying the update from the app.",
        "If the device remains unresponsive after multiple attempts, perform a **factory reset** and re-pair it.",
    ],
    "config_general": [
        "Check that the **app has notification and background refresh permissions** enabled for automations to run reliably.",
        "Verify the **device's time zone** is set correctly in the app settings.",
        "Check for **app updates** in the App Store or Google Play — an outdated app can cause configuration issues.",
        "Try **removing the automation/schedule** and recreating it from scratch in the app.",
    ],
}


def get_steps(category: IssueCategory, device_type: Optional[str]) -> List[str]:
    key = f"{category.value}_{device_type}" if device_type else None
    if key and key in _STEPS:
        return _STEPS[key]
    fallback = f"{category.value}_general"
    if fallback in _STEPS:
        return _STEPS[fallback]
    return _STEPS["connectivity_general"]


# ---------------------------------------------------------------------------
# Conversation engine
# ---------------------------------------------------------------------------

def build_query(state: SessionState) -> str:
    parts = []
    if state.device_type:
        parts.append(state.device_type.replace("_", " "))
    parts.extend(state.symptoms)
    parts.append(state.issue_category.value)
    return " ".join(parts)


def process_message(state: SessionState, message: str) -> Tuple[str, SessionState]:
    """
    Core stateful conversation logic.
    Returns (reply_text, updated_state).
    """

    # --- Restart request ---
    if is_restart_request(message):
        state.issue_category = IssueCategory.UNKNOWN
        state.device_type = None
        state.symptoms = []
        state.attempted_steps = []
        state.current_step_index = 0
        state.resolution_status = ResolutionStatus.IN_PROGRESS
        state.awaiting = None
        state.conversation_history = []
        reply = (
            "Sure! Let's start fresh.\n\n"
            "Please describe your issue. Which device is affected and what symptoms are you seeing? "
            "For example: *\"My smart bulb is offline\"* or *\"My smart plug won't connect to Wi-Fi\"*."
        )
        return reply, state

    # --- Detect device and category if not yet set ---
    detected_device = detect_device(message)
    if detected_device and not state.device_type:
        state.device_type = detected_device

    detected_category = classify_issue(message)
    if state.issue_category == IssueCategory.UNKNOWN and detected_category != IssueCategory.UNKNOWN:
        state.issue_category = detected_category

    # Collect symptoms
    if message.strip() and message not in state.symptoms:
        state.symptoms.append(message.strip())

    # --- Initial greeting or empty state ---
    if not state.awaiting and state.current_step_index == 0 and not state.attempted_steps:
        # First message — start the diagnostic
        if state.issue_category == IssueCategory.UNKNOWN:
            # Couldn't classify yet — ask for more info
            state.awaiting = "category"
            reply = (
                f"I see you're having an issue"
                + (f" with your **{state.device_type.replace('_', ' ')}**" if state.device_type else "") + ".\n\n"
                "Could you describe the problem a bit more? For example:\n"
                "- Is the device **offline** or **not responding**?\n"
                "- Is this a **setup/pairing** problem?\n"
                "- Or is it a **configuration or schedule** issue?"
            )
            return reply, state

        # We have enough info — ask the first confirming question
        state.awaiting = "troubleshooting"
        steps = get_steps(state.issue_category, state.device_type)
        state.current_step_index = 0
        device_label = (state.device_type.replace("_", " ") if state.device_type else "device").title()
        reply = (
            f"Got it — your **{device_label}** appears to have a **{state.issue_category.value}** issue.\n\n"
            f"Let's work through this step by step.\n\n"
            f"**Step 1:** {steps[0]}\n\n"
            "Does this apply / have you tried this? (Reply **Yes** if it resolves the issue, or **No** to continue.)"
        )
        state.current_step_index = 1
        return reply, state

    # --- Awaiting clarification on category ---
    if state.awaiting == "category":
        detected_category = classify_issue(message)
        if detected_category != IssueCategory.UNKNOWN:
            state.issue_category = detected_category
        else:
            state.issue_category = IssueCategory.CONNECTIVITY  # sensible default
        state.awaiting = "troubleshooting"
        steps = get_steps(state.issue_category, state.device_type)
        state.current_step_index = 0
        device_label = (state.device_type.replace("_", " ") if state.device_type else "device").title()
        reply = (
            f"Thanks! It looks like this is a **{state.issue_category.value}** issue with your **{device_label}**.\n\n"
            f"**Step 1:** {steps[0]}\n\n"
            "Did this help? (Reply **Yes** if resolved, **No** to continue.)"
        )
        state.current_step_index = 1
        return reply, state

    # --- Troubleshooting in progress ---
    if state.awaiting == "troubleshooting":
        steps = get_steps(state.issue_category, state.device_type)
        prev_step_index = state.current_step_index - 1

        if is_positive_response(message):
            # Check if this is the first step confirmation (i.e., just confirming the device is on, etc.)
            # We need to distinguish "yes the device is on" from "yes it's fixed"
            # Heuristic: if step index <= 1 and message sounds like confirmation not resolution,
            # present the next step.
            first_step_keywords = [
                "yes", "yeah", "it is", "it's on", "they are", "they're",
                "it is on", "powered", "working fine", "they are working",
            ]
            resolution_keywords = [
                "it works", "it worked", "fixed", "resolved", "working now",
                "works now", "good now", "it's working", "its working",
            ]
            t = message.lower()
            is_resolution = any(k in t for k in resolution_keywords)

            if is_resolution or state.current_step_index >= len(steps):
                # Resolved!
                state.resolution_status = ResolutionStatus.RESOLVED
                summary = _build_summary(state)
                state.awaiting = "done"
                reply = (
                    "**Excellent! Glad to hear it's working now!**\n\n"
                    + summary
                )
                return reply, state
            else:
                # User confirmed the step condition is true — move to next step
                state.attempted_steps.append(steps[prev_step_index])
                if state.current_step_index < len(steps):
                    next_step = steps[state.current_step_index]
                    step_num = state.current_step_index + 1
                    state.current_step_index += 1
                    reply = (
                        f"Thanks for confirming. Let's try the next step.\n\n"
                        f"**Step {step_num}:** {next_step}\n\n"
                        "Did this resolve the issue? (Reply **Yes** if fixed, **No** to continue.)"
                    )
                    return reply, state
                else:
                    # All steps exhausted
                    state.resolution_status = ResolutionStatus.UNRESOLVED
                    summary = _build_summary(state)
                    state.awaiting = "done"
                    reply = (
                        "We've gone through all the standard troubleshooting steps. "
                        "Here's a summary:\n\n"
                        + summary +
                        "\n\n**Recommendation:** Please contact the **manufacturer's official support** "
                        "for further assistance. They may offer a repair, replacement, or advanced diagnostics."
                    )
                    return reply, state

        elif is_negative_response(message):
            # Step didn't work — record and move on
            if prev_step_index >= 0 and prev_step_index < len(steps):
                state.attempted_steps.append(steps[prev_step_index])

            if state.current_step_index < len(steps):
                next_step = steps[state.current_step_index]
                step_num = state.current_step_index + 1
                state.current_step_index += 1
                reply = (
                    f"No problem — let's try the next step.\n\n"
                    f"**Step {step_num}:** {next_step}\n\n"
                    "Did this resolve the issue?"
                )
                return reply, state
            else:
                # All steps exhausted
                state.resolution_status = ResolutionStatus.UNRESOLVED
                summary = _build_summary(state)
                state.awaiting = "done"
                reply = (
                    "We've gone through all the available troubleshooting steps. "
                    "Unfortunately, I wasn't able to resolve the issue remotely.\n\n"
                    + summary +
                    "\n\n**Recommendation:** Please contact the **manufacturer's official support** "
                    "with the steps you've already tried so they can assist you further."
                )
                return reply, state
        else:
            # Unclear response — re-ask
            current = steps[prev_step_index] if prev_step_index < len(steps) else "the previous step"
            reply = (
                f"I'm not sure I understood. Regarding **\"{current}\"** — "
                "did this resolve your issue? Please reply with **Yes** or **No**."
            )
            return reply, state

    # --- Done state ---
    if state.awaiting == "done":
        reply = (
            "The troubleshooting session for this issue is complete. "
            "If you have a new problem, please describe it or click **Restart Troubleshooting** to begin again."
        )
        return reply, state

    # --- Fallback (should not normally reach here) ---
    state.awaiting = None
    state.current_step_index = 0
    device_label = (state.device_type.replace("_", " ") if state.device_type else "device").title()
    reply = (
        "I'm here to help troubleshoot your IoT device. "
        "Could you tell me which device is affected and what problem you're experiencing? "
        "For example: *\"My smart bulb is offline\"* or *\"My smart camera can't connect.\"*"
    )
    return reply, state


def _build_summary(state: SessionState) -> str:
    device = (state.device_type.replace("_", " ") if state.device_type else "Unknown device").title()
    category = state.issue_category.value.title()
    symptoms = "; ".join(state.symptoms[:3]) if state.symptoms else "Not specified"
    steps_text = "\n".join(
        f"  {i + 1}. {s}" for i, s in enumerate(state.attempted_steps)
    ) if state.attempted_steps else "  No steps attempted."
    status = "[Resolved]" if state.resolution_status == ResolutionStatus.RESOLVED else "[Unresolved]"

    return (
        f"**Troubleshooting Summary**\n\n"
        f"- **Device:** {device}\n"
        f"- **Issue Category:** {category}\n"
        f"- **Reported Symptoms:** {symptoms}\n"
        f"- **Steps Attempted:**\n{steps_text}\n"
        f"- **Outcome:** {status}"
    )


def get_summary_dict(state: SessionState) -> dict:
    return {
        "device": (state.device_type.replace("_", " ") if state.device_type else "Unknown").title(),
        "issue_category": state.issue_category.value,
        "symptoms": state.symptoms,
        "attempted_steps": state.attempted_steps,
        "resolution_status": state.resolution_status.value,
    }
