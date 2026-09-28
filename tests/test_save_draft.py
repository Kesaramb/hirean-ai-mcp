"""Tests for save_draft's polling loop.

Saving is asynchronous on the backend: /save_draft returns a task id and a
worker thread walks the task from "processing" to "completed". save_draft(
wait=True) hides that behind one call, so the polling has to actually terminate
on the right states.
"""

from __future__ import annotations

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from hirean_ai_mcp.tools import draft
from hirean_ai_mcp.tools.draft import _extract_task_id


class FakeClient:
    """Stands in for CapCutClient, scripting a sequence of status replies."""

    def __init__(self, save_result, statuses):
        self.save_result = save_result
        self.statuses = list(statuses)
        self.calls: list[tuple[str, dict]] = []

    def post(self, path, payload=None):
        self.calls.append((path, payload or {}))
        if path == "/save_draft":
            return self.save_result
        if path == "/query_draft_status":
            return self.statuses.pop(0) if self.statuses else {"status": "processing"}
        raise AssertionError(f"unexpected path {path}")


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(draft, "SAVE_POLL_INTERVAL", 0)


def use(monkeypatch, client):
    monkeypatch.setattr(draft, "get_client", lambda: client)
    return client


def test_polls_until_completed(monkeypatch):
    client = use(
        monkeypatch,
        FakeClient(
            {"task_id": "t1"},
            [
                {"status": "processing", "progress": 10},
                {"status": "processing", "progress": 70},
                {"status": "completed", "progress": 100, "draft_url": "file:///d"},
            ],
        ),
    )
    result = draft.save_draft(draft_id="d1")
    assert result["status"] == "completed"
    assert result["draft_url"] == "file:///d"
    assert [c[0] for c in client.calls].count("/query_draft_status") == 3


def test_failed_is_terminal_and_returned(monkeypatch):
    """A failed save must stop the loop and surface, not spin to timeout."""
    use(monkeypatch, FakeClient({"task_id": "t1"}, [{"status": "failed", "message": "boom"}]))
    result = draft.save_draft(draft_id="d1")
    assert result["status"] == "failed"
    assert result["message"] == "boom"


def test_wait_false_returns_immediately(monkeypatch):
    client = use(monkeypatch, FakeClient({"task_id": "t1"}, []))
    result = draft.save_draft(draft_id="d1", wait=False)
    assert result == {"task_id": "t1"}
    assert [c[0] for c in client.calls] == ["/save_draft"]


def test_timeout_reports_task_id_to_resume_with(monkeypatch):
    use(monkeypatch, FakeClient({"task_id": "t1"}, [{"status": "processing"}] * 50))
    result = draft.save_draft(draft_id="d1", timeout_seconds=0)
    assert result["status"] == "timeout"
    assert result["task_id"] == "t1"


def test_response_without_task_id_falls_back_to_draft_id(monkeypatch):
    """Current upstream saves inline and returns no task id, but still records
    progress under task_id == draft_id -- so status is still reachable."""
    client = use(
        monkeypatch,
        FakeClient(
            {"success": True, "draft_url": ""},
            [{"status": "completed", "progress": 100, "message": "Draft creation completed"}],
        ),
    )
    result = draft.save_draft(draft_id="d1")
    assert result["status"] == "completed"
    assert result["progress"] == 100
    assert client.calls[1] == ("/query_draft_status", {"task_id": "d1"})


def test_untracked_task_returns_raw_save_response(monkeypatch):
    """If the backend isn't tracking the id, don't spin -- return what we got."""

    class NoTracking:
        def post(self, path, payload=None):
            if path == "/save_draft":
                return {"success": True, "draft_url": "file:///done"}
            raise ToolError("Task with ID d1 not found.")

    use(monkeypatch, NoTracking())
    assert draft.save_draft(draft_id="d1") == {"success": True, "draft_url": "file:///done"}


def test_draft_url_carried_over_when_status_lacks_one(monkeypatch):
    use(
        monkeypatch,
        FakeClient(
            {"success": True, "draft_url": "https://host/d.zip"},
            [{"status": "completed", "draft_url": ""}],
        ),
    )
    assert draft.save_draft(draft_id="d1")["draft_url"] == "https://host/d.zip"


def test_status_draft_url_is_not_overwritten(monkeypatch):
    use(
        monkeypatch,
        FakeClient(
            {"success": True, "draft_url": "https://host/stale.zip"},
            [{"status": "completed", "draft_url": "https://host/fresh.zip"}],
        ),
    )
    assert draft.save_draft(draft_id="d1")["draft_url"] == "https://host/fresh.zip"


def test_draft_folder_env_default_is_applied(monkeypatch):
    monkeypatch.setenv("CAPCUT_DRAFT_FOLDER", "/drafts")
    client = use(monkeypatch, FakeClient({"task_id": "t"}, [{"status": "completed"}]))
    draft.save_draft(draft_id="d1")
    assert client.calls[0][1]["draft_folder"] == "/drafts"


def test_explicit_draft_folder_beats_env(monkeypatch):
    monkeypatch.setenv("CAPCUT_DRAFT_FOLDER", "/drafts")
    client = use(monkeypatch, FakeClient({"task_id": "t"}, [{"status": "completed"}]))
    draft.save_draft(draft_id="d1", draft_folder="/explicit")
    assert client.calls[0][1]["draft_folder"] == "/explicit"


def test_backend_error_propagates(monkeypatch):
    class Failing:
        def post(self, path, payload=None):
            raise ToolError("draft not found")

    use(monkeypatch, Failing())
    with pytest.raises(ToolError, match="draft not found"):
        draft.save_draft(draft_id="nope")


@pytest.mark.parametrize(
    "value,expected",
    [
        ("t-123", "t-123"),
        ({"task_id": "t-1"}, "t-1"),
        ({"taskId": "t-2"}, "t-2"),
        ({"id": "t-3"}, "t-3"),
        ({"draft_url": "x"}, None),
        ("", None),
        (None, None),
        (123, None),
    ],
)
def test_extract_task_id(value, expected):
    assert _extract_task_id(value) == expected
