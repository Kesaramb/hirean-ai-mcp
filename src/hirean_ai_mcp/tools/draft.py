"""Draft lifecycle: create, inspect, save, share."""

from __future__ import annotations

import time
from typing import Any

from mcp.server.mcpserver.exceptions import ToolError

from ..app import mcp
from ..client import default_draft_folder, get_client
from ..constants import (
    DEFAULT_SAVE_POLL_TIMEOUT,
    SAVE_POLL_INTERVAL,
    TERMINAL_TASK_STATUSES,
)


@mcp.tool()
def create_draft(width: int = 1080, height: int = 1920) -> Any:
    """Create a new empty CapCut draft and return its draft_id.

    Every other editing tool needs this draft_id. Defaults are portrait
    1080x1920 (TikTok / Reels / Shorts); use 1920x1080 for landscape.

    The draft lives in the backend's cache until you call save_draft, which is
    what actually writes it into the CapCut drafts folder.
    """
    return get_client().post("/create_draft", {"width": width, "height": height})


@mcp.tool()
def query_script(draft_id: str, force_update: bool | None = None) -> Any:
    """Return the raw draft script JSON, to inspect the current timeline state.

    Useful for checking what tracks and segments exist, and their timings,
    before adding more material. The response can be large.
    """
    return get_client().post(
        "/query_script", {"draft_id": draft_id, "force_update": force_update}
    )


@mcp.tool()
def query_draft_status(task_id: str) -> Any:
    """Check the progress of a save_draft task.

    Returns status ("initialized", "processing", "completed", "failed"), a
    progress percentage, and a message. Only needed if you called save_draft
    with wait=False -- otherwise save_draft already polled to completion.
    """
    return get_client().post("/query_draft_status", {"task_id": task_id})


@mcp.tool()
def generate_draft_url(draft_id: str, draft_folder: str | None = None) -> Any:
    """Get a shareable/preview URL for a draft."""
    return get_client().post(
        "/generate_draft_url",
        {"draft_id": draft_id, "draft_folder": draft_folder or default_draft_folder()},
    )


@mcp.tool()
def save_draft(
    draft_id: str,
    draft_folder: str | None = None,
    wait: bool = True,
    timeout_seconds: float = DEFAULT_SAVE_POLL_TIMEOUT,
) -> Any:
    """Save a draft to disk so it opens in CapCut. Call this when editing is done.

    Saving downloads every remote media file referenced by the timeline, then
    writes the draft folder. With wait=True (default) this returns the final
    task status, including progress and any failure message. With wait=False it
    returns the backend's raw response immediately.

    draft_folder should be your CapCut drafts directory. If omitted, the
    HIREAN_AI_DRAFT_FOLDER (or legacy CAPCUT_DRAFT_FOLDER) environment variable
    is used, and failing that the backend's own configured default.
    """
    client = get_client()
    result = client.post(
        "/save_draft",
        {"draft_id": draft_id, "draft_folder": draft_folder or default_draft_folder()},
    )

    if not wait:
        return result

    # Current upstream runs the save inline and returns no task id (the
    # threading path in save_draft_impl is commented out), but it still records
    # progress under task_id == draft_id. Older and forked builds do return a
    # task id and finish asynchronously. Polling covers both: in the inline case
    # the first poll already reports the terminal state, and it carries the
    # progress/message detail that the bare save response omits.
    task_id = _extract_task_id(result) or draft_id

    deadline = time.monotonic() + timeout_seconds
    status: Any = None
    while True:
        try:
            status = client.post("/query_draft_status", {"task_id": task_id})
        except ToolError:
            # Backend isn't tracking this id -- nothing to poll, so the save
            # response is the best answer available.
            return result

        state = status.get("status") if isinstance(status, dict) else None
        if state in TERMINAL_TASK_STATUSES:
            return _merge_draft_url(status, result)
        if time.monotonic() >= deadline:
            break
        time.sleep(SAVE_POLL_INTERVAL)

    return {
        "status": "timeout",
        "task_id": task_id,
        "message": (
            f"Draft was still saving after {timeout_seconds:.0f}s. The task is still "
            "running -- poll query_draft_status with this task_id."
        ),
        "last_status": status,
    }


def _merge_draft_url(status: Any, save_result: Any) -> Any:
    """Carry draft_url over from the save response when the status lacks one.

    Only /save_draft returns a URL when draft uploading is enabled; the task
    record can be missing it.
    """
    if not isinstance(status, dict) or not isinstance(save_result, dict):
        return status
    if not status.get("draft_url") and save_result.get("draft_url"):
        return {**status, "draft_url": save_result["draft_url"]}
    return status


def _extract_task_id(result: Any) -> str | None:
    """Pull the task id out of a /save_draft response.

    The backend returns whatever save_draft_impl produced, so accept both a
    bare id and the usual dict shapes rather than assuming one.
    """
    if isinstance(result, str):
        return result or None
    if isinstance(result, dict):
        for key in ("task_id", "taskId", "id"):
            value = result.get(key)
            if isinstance(value, str) and value:
                return value
    return None
