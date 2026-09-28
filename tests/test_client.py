"""Tests against a stub VectCutAPI backend.

The behaviour that matters most here is that a failure arriving as HTTP 200 with
``success: false`` is raised rather than returned. VectCutAPI never uses error
status codes, so a client that only checked ``response.status_code`` would
report every failed edit as a success.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from hirean_ai_mcp.client import CapCutClient, prune

# Set by each test to control what the stub returns.
RESPONSES: dict[str, object] = {}
REQUESTS: list[dict] = []


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep test output clean
        pass

    def _reply(self, path: str, body: dict | None):
        REQUESTS.append({"path": path, "body": body})
        spec = RESPONSES.get(path, {"success": True, "output": "ok", "error": ""})
        status = spec.pop("__status", 200) if isinstance(spec, dict) else 200
        raw = spec.get("__raw") if isinstance(spec, dict) else None
        payload = raw if raw is not None else json.dumps(spec).encode()
        if isinstance(payload, str):
            payload = payload.encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        self._reply(self.path, None)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}")
        self._reply(self.path, body)


@pytest.fixture
def backend():
    RESPONSES.clear()
    REQUESTS.clear()
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def client(backend):
    return CapCutClient(base_url=backend, timeout=5.0)


def test_success_envelope_returns_output(client):
    RESPONSES["/create_draft"] = {
        "success": True,
        "output": {"draft_id": "abc123"},
        "error": "",
    }
    assert client.post("/create_draft", {"width": 1080}) == {"draft_id": "abc123"}


def test_failure_envelope_raises_despite_http_200(client):
    """The whole reason client.py exists."""
    RESPONSES["/add_video"] = {
        "success": False,
        "output": "",
        "error": "Hi, the required parameter 'draft_id' is missing.",
    }
    with pytest.raises(ToolError, match="draft_id"):
        client.post("/add_video", {"video_url": "http://x/v.mp4"})


def test_failure_envelope_with_empty_error_still_raises(client):
    RESPONSES["/add_text"] = {"success": False, "output": "", "error": ""}
    with pytest.raises(ToolError):
        client.post("/add_text", {"text": "hi"})


def test_none_params_are_stripped_before_send(client):
    """Omitted params must not become explicit nulls that clobber backend defaults."""
    client.post("/add_video", {"video_url": "u", "transition": None, "speed": 2.0})
    sent = REQUESTS[-1]["body"]
    assert sent == {"video_url": "u", "speed": 2.0}
    assert "transition" not in sent


def test_falsy_but_meaningful_values_survive_pruning():
    assert prune({"volume": 0.0, "vertical": False, "start": 0, "x": None}) == {
        "volume": 0.0,
        "vertical": False,
        "start": 0,
    }


def test_non_200_raises(client):
    RESPONSES["/add_audio"] = {"__status": 500, "success": True, "output": "x"}
    with pytest.raises(ToolError, match="HTTP 500"):
        client.post("/add_audio", {"audio_url": "u"})


def test_non_json_body_raises(client):
    RESPONSES["/query_script"] = {"__raw": "<html>gateway error</html>"}
    with pytest.raises(ToolError, match="non-JSON"):
        client.post("/query_script", {"draft_id": "d"})


def test_envelopeless_response_passes_through(client):
    RESPONSES["/get_font_types"] = {"__raw": json.dumps([{"name": "Arial"}])}
    assert client.get("/get_font_types") == [{"name": "Arial"}]


def test_connection_refused_names_the_cause():
    client = CapCutClient(base_url="http://127.0.0.1:1", timeout=5.0)
    with pytest.raises(ToolError, match="capcut_server.py"):
        client.post("/create_draft", {})
