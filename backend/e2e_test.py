import httpx
import sys
import time
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

base = "http://127.0.0.1:8001"

time.sleep(3)

# Health check
r = httpx.get(f"{base}/health")
assert r.status_code == 200
h = r.json()
print("HEALTH:", h)
assert h["status"] == "ok"

# Devices
r = httpx.get(f"{base}/devices")
assert r.status_code == 200
devs = r.json()
print("DEVICES count:", len(devs["devices"]))
assert len(devs["devices"]) >= 4

# Acceptance scenario — use timestamp so each run gets fresh session
import uuid
sid = f"e2e_{uuid.uuid4().hex[:8]}"
msgs = [
    "My smart bulb is offline",
    "Yes",
    "They are working",
    "It works now",
]
last_data = None
for i, msg in enumerate(msgs):
    r = httpx.post(f"{base}/chat", json={"message": msg, "session_id": sid})
    assert r.status_code == 200, f"Unexpected status {r.status_code}: {r.text}"
    data = r.json()
    last_data = data
    status = data["resolution_status"]
    step = data["current_step"]
    total = data["total_steps"]
    reply = data["reply"][:120]
    print(f"MSG{i+1} [{status}] step={step}/{total}")
    print(f"  REPLY: {reply}")

assert last_data["resolution_status"] == "resolved", \
    f"Expected resolved, got {last_data['resolution_status']}"

# Invalid input test
r = httpx.post(f"{base}/chat", json={"message": "  ", "session_id": "badtest"})
assert r.status_code == 422, f"Expected 422, got {r.status_code}"
print("Empty message validation: PASS (422)")

# Feedback
r = httpx.post(f"{base}/feedback", json={"session_id": "e2e_test", "step_index": 0, "worked": True})
assert r.status_code == 200
print("Feedback: PASS")

print()
print("ALL E2E CHECKS PASSED")
