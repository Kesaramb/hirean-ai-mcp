"""Stickers, visual effects, keyframes, and asset-name discovery."""

from __future__ import annotations

from typing import Any, Literal

from ..app import mcp
from ..client import get_client
from ..constants import ASSET_TYPE_PATHS, AssetCategory


@mcp.tool()
def list_asset_types(category: AssetCategory) -> Any:
    """List the asset names this CapCut/Jianying install actually accepts.

    Call this before using any animation, transition, font, mask or effect
    parameter. The valid names differ between CapCut and Jianying installs, so
    a guessed name will fail or be silently ignored.

    Categories map to parameters as follows:
      - "transition"              -> add_video/add_image transition
      - "mask"                    -> add_video/add_image mask_type
      - "intro_animation",
        "outro_animation",
        "combo_animation"         -> add_image animations
      - "font"                    -> add_text/add_subtitle font
      - "text_intro",
        "text_outro",
        "text_loop_anim"          -> add_text animations
      - "video_scene_effect"      -> add_effect with effect_category="scene"
      - "video_character_effect"  -> add_effect with effect_category="character"
      - "audio_effect"            -> add_audio effect_type
    """
    return get_client().get(ASSET_TYPE_PATHS[category])


@mcp.tool()
def add_sticker(
    sticker_id: str,
    draft_id: str | None = None,
    start: float | None = None,
    end: float | None = None,
    track_name: str | None = None,
    relative_index: int | None = None,
    transform_x: float | None = None,
    transform_y: float | None = None,
    scale_x: float | None = None,
    scale_y: float | None = None,
    rotation: float | None = None,
    alpha: float | None = None,
    flip_horizontal: bool | None = None,
    flip_vertical: bool | None = None,
    width: int | None = None,
    height: int | None = None,
) -> Any:
    """Add a sticker to a draft by its CapCut resource id.

    `sticker_id` is a CapCut sticker resource identifier -- there is no endpoint
    that enumerates these, so it must come from the user or from an existing
    draft inspected via query_script.
    """
    return get_client().post(
        "/add_sticker",
        {
            "sticker_id": sticker_id,
            "draft_id": draft_id,
            "start": start,
            "end": end,
            "track_name": track_name,
            "relative_index": relative_index,
            "transform_x": transform_x,
            "transform_y": transform_y,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "rotation": rotation,
            "alpha": alpha,
            "flip_horizontal": flip_horizontal,
            "flip_vertical": flip_vertical,
            "width": width,
            "height": height,
        },
    )


@mcp.tool()
def add_effect(
    effect_type: str,
    draft_id: str | None = None,
    effect_category: Literal["scene", "character"] = "scene",
    start: float | None = None,
    end: float | None = None,
    track_name: str | None = None,
    params: list[Any] | None = None,
    width: int | None = None,
    height: int | None = None,
) -> Any:
    """Apply a visual effect over a time range.

    `effect_category` picks which catalogue `effect_type` is looked up in:
    "scene" for full-frame effects, "character" for subject/person effects.
    Get valid names from list_asset_types("video_scene_effect") or
    list_asset_types("video_character_effect") to match.

    `params` is an ordered list of effect intensity values; entries left as null
    fall back to that effect's defaults.
    """
    return get_client().post(
        "/add_effect",
        {
            "effect_type": effect_type,
            "draft_id": draft_id,
            "effect_category": effect_category,
            "start": start,
            "end": end,
            "track_name": track_name,
            # Always send a list, never omit. add_effect_impl does
            # `params=params[::-1]` unconditionally, so a missing params raises
            # "'NoneType' object is not subscriptable" upstream -- which would
            # break every add_effect call that doesn't tune intensities.
            "params": params if params is not None else [],
            "width": width,
            "height": height,
        },
    )


@mcp.tool()
def add_video_keyframe(
    draft_id: str,
    track_name: str | None = None,
    property_type: str | None = None,
    time: float | None = None,
    value: str | None = None,
    property_types: list[str] | None = None,
    times: list[float] | None = None,
    values: list[str] | None = None,
) -> Any:
    """Animate a video property over time by adding keyframes.

    Two forms. For a single keyframe use property_type / time / value. For many
    at once use the plural property_types / times / values, which must be equal
    length and are zipped positionally.

    `property_type` names a track property such as "alpha", "scale_x",
    "scale_y", "position_x", "position_y", "rotation", "volume". `time` is in
    seconds. `value` is passed through as a string, e.g. "1.0" or "0.5".

    A property needs at least two keyframes at different times to animate --
    one keyframe alone just pins a constant value.
    """
    return get_client().post(
        "/add_video_keyframe",
        {
            "draft_id": draft_id,
            "track_name": track_name,
            "property_type": property_type,
            "time": time,
            "value": value,
            "property_types": property_types,
            "times": times,
            "values": values,
        },
    )
