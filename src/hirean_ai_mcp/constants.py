"""Static configuration and endpoint tables for the VectCutAPI backend."""

from typing import Literal

DEFAULT_BASE_URL = "http://localhost:9001"

# Media downloads during save_draft can be slow, so the default is generous.
DEFAULT_TIMEOUT_SECONDS = 300.0

# How long save_draft(wait=True) will poll before giving up and handing the
# caller a task_id to check manually.
DEFAULT_SAVE_POLL_TIMEOUT = 600.0
SAVE_POLL_INTERVAL = 2.0

# Terminal values of the "status" field in a /query_draft_status response.
# See save_task_cache.py in VectCutAPI.
TERMINAL_TASK_STATUSES = frozenset({"completed", "failed", "not_found"})

AssetCategory = Literal[
    "intro_animation",
    "outro_animation",
    "combo_animation",
    "transition",
    "mask",
    "audio_effect",
    "font",
    "text_intro",
    "text_outro",
    "text_loop_anim",
    "video_scene_effect",
    "video_character_effect",
]

# The backend exposes twelve near-identical GET endpoints that each return
# [{"name": ...}]. We surface them as one tool to keep the tool list small.
ASSET_TYPE_PATHS: dict[str, str] = {
    "intro_animation": "/get_intro_animation_types",
    "outro_animation": "/get_outro_animation_types",
    "combo_animation": "/get_combo_animation_types",
    "transition": "/get_transition_types",
    "mask": "/get_mask_types",
    "audio_effect": "/get_audio_effect_types",
    "font": "/get_font_types",
    "text_intro": "/get_text_intro_types",
    "text_outro": "/get_text_outro_types",
    "text_loop_anim": "/get_text_loop_anim_types",
    "video_scene_effect": "/get_video_scene_effect_types",
    "video_character_effect": "/get_video_character_effect_types",
}
