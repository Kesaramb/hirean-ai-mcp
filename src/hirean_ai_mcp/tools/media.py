"""Video, audio and image material."""

from __future__ import annotations

from typing import Any

from ..app import mcp
from ..client import default_draft_folder, get_client


@mcp.tool()
def add_video(
    video_url: str,
    draft_id: str | None = None,
    start: float | None = None,
    end: float | None = None,
    target_start: float | None = None,
    duration: float | None = None,
    speed: float | None = None,
    volume: float | None = None,
    track_name: str | None = None,
    relative_index: int | None = None,
    transform_x: float | None = None,
    transform_y: float | None = None,
    scale_x: float | None = None,
    scale_y: float | None = None,
    transition: str | None = None,
    transition_duration: float | None = None,
    mask_type: str | None = None,
    mask_center_x: float | None = None,
    mask_center_y: float | None = None,
    mask_size: float | None = None,
    mask_rotation: float | None = None,
    mask_feather: float | None = None,
    mask_invert: bool | None = None,
    mask_rect_width: float | None = None,
    mask_round_corner: float | None = None,
    background_blur: int | None = None,
    width: int | None = None,
    height: int | None = None,
    draft_folder: str | None = None,
) -> Any:
    """Add a video clip to a draft timeline.

    video_url must be a remote URL or a local path the backend can read. `start`
    and `end` trim the source clip; `target_start` is where it lands on the
    timeline (all in seconds). Omit draft_id to have a new draft created.

    For `transition` and `mask_type`, call list_asset_types("transition") and
    list_asset_types("mask") to get valid names -- do not guess them.
    """
    return get_client().post(
        "/add_video",
        {
            "video_url": video_url,
            "draft_id": draft_id,
            "start": start,
            "end": end,
            "target_start": target_start,
            "duration": duration,
            "speed": speed,
            "volume": volume,
            "track_name": track_name,
            "relative_index": relative_index,
            "transform_x": transform_x,
            "transform_y": transform_y,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "transition": transition,
            "transition_duration": transition_duration,
            "mask_type": mask_type,
            "mask_center_x": mask_center_x,
            "mask_center_y": mask_center_y,
            "mask_size": mask_size,
            "mask_rotation": mask_rotation,
            "mask_feather": mask_feather,
            "mask_invert": mask_invert,
            "mask_rect_width": mask_rect_width,
            "mask_round_corner": mask_round_corner,
            "background_blur": background_blur,
            "width": width,
            "height": height,
            "draft_folder": draft_folder or default_draft_folder(),
        },
    )


@mcp.tool()
def add_audio(
    audio_url: str,
    draft_id: str | None = None,
    start: float | None = None,
    end: float | None = None,
    target_start: float | None = None,
    duration: float | None = None,
    speed: float | None = None,
    volume: float | None = None,
    track_name: str | None = None,
    effect_type: str | None = None,
    effect_params: list[Any] | None = None,
    width: int | None = None,
    height: int | None = None,
    draft_folder: str | None = None,
) -> Any:
    """Add an audio track (music, voiceover, sound effect) to a draft.

    `start`/`end` trim the source audio, `target_start` places it on the
    timeline, all in seconds. `volume` is a multiplier where 1.0 is unchanged.

    For `effect_type`, call list_asset_types("audio_effect") for valid names.
    """
    return get_client().post(
        "/add_audio",
        {
            "audio_url": audio_url,
            "draft_id": draft_id,
            "start": start,
            "end": end,
            "target_start": target_start,
            "duration": duration,
            "speed": speed,
            "volume": volume,
            "track_name": track_name,
            "effect_type": effect_type,
            "effect_params": effect_params,
            "width": width,
            "height": height,
            "draft_folder": draft_folder or default_draft_folder(),
        },
    )


@mcp.tool()
def add_image(
    image_url: str,
    draft_id: str | None = None,
    start: float | None = None,
    end: float | None = None,
    track_name: str | None = None,
    relative_index: int | None = None,
    transform_x: float | None = None,
    transform_y: float | None = None,
    scale_x: float | None = None,
    scale_y: float | None = None,
    intro_animation: str | None = None,
    intro_animation_duration: float | None = None,
    outro_animation: str | None = None,
    outro_animation_duration: float | None = None,
    combo_animation: str | None = None,
    combo_animation_duration: float | None = None,
    transition: str | None = None,
    transition_duration: float | None = None,
    mask_type: str | None = None,
    mask_center_x: float | None = None,
    mask_center_y: float | None = None,
    mask_size: float | None = None,
    mask_rotation: float | None = None,
    mask_feather: float | None = None,
    mask_invert: bool | None = None,
    mask_rect_width: float | None = None,
    mask_round_corner: float | None = None,
    background_blur: int | None = None,
    width: int | None = None,
    height: int | None = None,
    draft_folder: str | None = None,
) -> Any:
    """Add a still image to a draft, optionally animated.

    `start` and `end` set how long the image is on screen, in seconds.

    Animation and mask names are install-specific: call
    list_asset_types("intro_animation"), ("outro_animation"),
    ("combo_animation"), ("transition") or ("mask") rather than guessing.
    """
    return get_client().post(
        "/add_image",
        {
            "image_url": image_url,
            "draft_id": draft_id,
            "start": start,
            "end": end,
            "track_name": track_name,
            "relative_index": relative_index,
            "transform_x": transform_x,
            "transform_y": transform_y,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "intro_animation": intro_animation,
            "intro_animation_duration": intro_animation_duration,
            "outro_animation": outro_animation,
            "outro_animation_duration": outro_animation_duration,
            "combo_animation": combo_animation,
            "combo_animation_duration": combo_animation_duration,
            "transition": transition,
            "transition_duration": transition_duration,
            "mask_type": mask_type,
            "mask_center_x": mask_center_x,
            "mask_center_y": mask_center_y,
            "mask_size": mask_size,
            "mask_rotation": mask_rotation,
            "mask_feather": mask_feather,
            "mask_invert": mask_invert,
            "mask_rect_width": mask_rect_width,
            "mask_round_corner": mask_round_corner,
            "background_blur": background_blur,
            "width": width,
            "height": height,
            "draft_folder": draft_folder or default_draft_folder(),
        },
    )
