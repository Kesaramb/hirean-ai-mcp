"""The shared MCP server instance.

Lives in its own module so tool modules can register against it without
importing ``server``, which would be circular.
"""

from mcp.server.mcpserver import MCPServer

from . import __version__

mcp = MCPServer(
    "HireAn AI",
    version=__version__,
    instructions=(
        "HireAn AI builds editable CapCut / Jianying video drafts using VectCutAPI. "
        "Typical flow: create_draft to get a "
        "draft_id, then add_video / add_image / add_audio / add_text / add_subtitle / "
        "add_sticker / add_effect to build the timeline, then save_draft to write it "
        "into the CapCut drafts folder. Open the draft in CapCut to export a video.\n\n"
        "Timing is in seconds. Positions (transform_x/transform_y) are normalized to "
        "roughly -1.0..1.0 with 0,0 at centre.\n\n"
        "Never guess an animation, transition, font, mask or effect name. Call "
        "list_asset_types first to get the exact values the backend accepts -- they "
        "differ between CapCut and Jianying installs."
    ),
)
