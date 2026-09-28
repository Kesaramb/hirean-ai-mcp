"""HTTP client for the VectCutAPI backend.

Every error path in the backend is funnelled through here. That matters more
than usual because VectCutAPI answers *every* request with HTTP 200 -- including
failures, which are signalled only by ``success: false`` in the body:

    {"success": false, "output": "", "error": "... 'draft_id' is missing ..."}

A client that trusted the status code would report broken calls as successes and
let the model keep building on a draft that was never modified.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.mcpserver.exceptions import ToolError

from .constants import DEFAULT_BASE_URL, DEFAULT_TIMEOUT_SECONDS


def _setting(name: str) -> str | None:
    """Prefer HireAn AI settings, with fallback for existing CapCut MCP installs."""
    return os.environ.get(f"HIREAN_AI_{name}") or os.environ.get(f"CAPCUT_{name}") or None


def _base_url() -> str:
    return (_setting("API_URL") or DEFAULT_BASE_URL).rstrip("/")


def _timeout() -> float:
    raw = _setting("TIMEOUT")
    if not raw:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS


def default_draft_folder() -> str | None:
    """CapCut drafts directory, if the user pinned one via the environment."""
    return _setting("DRAFT_FOLDER")


def prune(payload: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is None.

    Tool parameters default to None so that omitting one means "let the backend
    apply its own default". Sending an explicit null instead would override that
    default with None and blow up inside the impl functions.
    """
    return {key: value for key, value in payload.items() if value is not None}


class CapCutClient:
    """Thin synchronous wrapper around the VectCutAPI HTTP surface."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or _base_url()).rstrip("/")
        self._client = httpx.Client(timeout=timeout if timeout is not None else _timeout())

    def get(self, path: str) -> Any:
        return self._request("GET", path, None)

    def post(self, path: str, payload: dict[str, Any] | None = None) -> Any:
        return self._request("POST", path, prune(payload or {}))

    def _request(self, method: str, path: str, payload: dict[str, Any] | None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            if method == "GET":
                response = self._client.get(url)
            else:
                response = self._client.post(url, json=payload or {})
        except httpx.ConnectError as exc:
            raise ToolError(
                f"Cannot reach the CapCut backend at {self.base_url}. "
                "Start it with `python capcut_server.py` in your VectCutAPI checkout, "
                "or point HIREAN_AI_API_URL at the right host. "
                f"({exc})"
            ) from exc
        except httpx.TimeoutException as exc:
            raise ToolError(
                f"The CapCut backend did not respond within the timeout while calling {path}. "
                "Large media downloads can exceed it -- raise HIREAN_AI_TIMEOUT if this is expected. "
                f"({exc})"
            ) from exc

        if response.status_code != 200:
            raise ToolError(
                f"CapCut backend returned HTTP {response.status_code} for {path}: "
                f"{response.text[:500]}"
            )

        try:
            body = response.json()
        except ValueError as exc:
            raise ToolError(
                f"CapCut backend returned non-JSON for {path}: {response.text[:500]}"
            ) from exc

        # The endpoints that matter all use the {success, output, error} envelope.
        # Anything else is passed through rather than rejected.
        if not isinstance(body, dict) or "success" not in body:
            return body

        if not body.get("success"):
            message = body.get("error") or "The CapCut backend reported a failure with no message."
            raise ToolError(str(message))

        return body.get("output")


_client: CapCutClient | None = None


def get_client() -> CapCutClient:
    """Process-wide client, built on first use.

    Constructed lazily so importing the server never fails just because the
    backend happens to be down.
    """
    global _client
    if _client is None:
        _client = CapCutClient()
    return _client
