"""Entry point for the HireAn AI MCP server."""

from __future__ import annotations

from .app import mcp
from . import tools  # noqa: F401  -- importing registers every tool on `mcp`


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
