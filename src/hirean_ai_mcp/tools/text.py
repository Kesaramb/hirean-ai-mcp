"""Text overlays and SRT subtitles."""

from __future__ import annotations

from typing import Any

from ..app import mcp
from ..client import get_client


@mcp.tool()
def add_text(
    text: str,
    draft_id: str | None = None,
    start: float | None = None,
    end: float | None = None,
    track_name: str | None = None,
    font: str | None = None,
    font_size: float | None = None,
    font_color: str | None = None,
    font_alpha: float | None = None,
    vertical: bool | None = None,
    transform_x: float | None = None,
    transform_y: float | None = None,
    fixed_width: float | None = None,
    fixed_height: float | None = None,
    border_color: str | None = None,
    border_width: float | None = None,
    border_alpha: float | None = None,
    background_color: str | None = None,
    background_style: int | None = None,
    background_alpha: float | None = None,
    background_round_radius: float | None = None,
    background_width: float | None = None,
    background_height: float | None = None,
    background_horizontal_offset: float | None = None,
    background_vertical_offset: float | None = None,
    shadow_enabled: bool | None = None,
    shadow_color: str | None = None,
    shadow_alpha: float | None = None,
    shadow_angle: float | None = None,
    shadow_distance: float | None = None,
    shadow_smoothing: float | None = None,
    intro_animation: str | None = None,
    intro_duration: float | None = None,
    outro_animation: str | None = None,
    outro_duration: float | None = None,
    bubble_effect_id: str | None = None,
    bubble_resource_id: str | None = None,
    effect_effect_id: str | None = None,
    text_styles: list[dict[str, Any]] | None = None,
    width: int | None = None,
    height: int | None = None,
) -> Any:
    """Add a styled text overlay to a draft.

    Colors are hex strings like "#FFFFFF". Alpha values run 0.0-1.0.
    transform_x/transform_y position the text, normalized roughly -1.0..1.0
    with 0,0 at centre; negative transform_y moves it down.

    `text_styles` applies different styling to character ranges within the same
    text block. Each entry looks like:
        {"start": 0, "end": 5,
         "style": {"size": 10, "bold": true, "color": "#FF0000"},
         "border": {"width": 2, "color": "#000000"},
         "font": "..."}

    For `font`, `intro_animation` and `outro_animation`, call
    list_asset_types("font"), ("text_intro") and ("text_outro") for valid names.
    """
    return get_client().post(
        "/add_text",
        {
            "text": text,
            "draft_id": draft_id,
            "start": start,
            "end": end,
            "track_name": track_name,
            "font": font,
            "font_size": font_size,
            "font_color": font_color,
            "font_alpha": font_alpha,
            "vertical": vertical,
            "transform_x": transform_x,
            "transform_y": transform_y,
            "fixed_width": fixed_width,
            "fixed_height": fixed_height,
            "border_color": border_color,
            "border_width": border_width,
            "border_alpha": border_alpha,
            "background_color": background_color,
            "background_style": background_style,
            "background_alpha": background_alpha,
            "background_round_radius": background_round_radius,
            "background_width": background_width,
            "background_height": background_height,
            "background_horizontal_offset": background_horizontal_offset,
            "background_vertical_offset": background_vertical_offset,
            "shadow_enabled": shadow_enabled,
            "shadow_color": shadow_color,
            "shadow_alpha": shadow_alpha,
            "shadow_angle": shadow_angle,
            "shadow_distance": shadow_distance,
            "shadow_smoothing": shadow_smoothing,
            "intro_animation": intro_animation,
            "intro_duration": intro_duration,
            "outro_animation": outro_animation,
            "outro_duration": outro_duration,
            "bubble_effect_id": bubble_effect_id,
            "bubble_resource_id": bubble_resource_id,
            "effect_effect_id": effect_effect_id,
            "text_styles": text_styles,
            "width": width,
            "height": height,
        },
    )


@mcp.tool()
def add_subtitle(
    srt: str,
    draft_id: str | None = None,
    time_offset: float | None = None,
    track_name: str | None = None,
    font: str | None = None,
    font_size: float | None = None,
    font_color: str | None = None,
    bold: bool | None = None,
    italic: bool | None = None,
    underline: bool | None = None,
    vertical: bool | None = None,
    alpha: float | None = None,
    border_color: str | None = None,
    border_width: float | None = None,
    border_alpha: float | None = None,
    background_color: str | None = None,
    background_style: int | None = None,
    background_alpha: float | None = None,
    transform_x: float | None = None,
    transform_y: float | None = None,
    scale_x: float | None = None,
    scale_y: float | None = None,
    rotation: float | None = None,
    width: int | None = None,
    height: int | None = None,
) -> Any:
    """Add subtitles to a draft from SRT content.

    `srt` accepts raw SRT text, a local path, or a URL to an .srt file. Styling
    applies to every cue. `time_offset` shifts all cues by N seconds.

    For `font`, call list_asset_types("font") for valid names.
    """
    return get_client().post(
        "/add_subtitle",
        {
            "srt": srt,
            "draft_id": draft_id,
            "time_offset": time_offset,
            "track_name": track_name,
            "font": font,
            "font_size": font_size,
            "font_color": font_color,
            "bold": bold,
            "italic": italic,
            "underline": underline,
            "vertical": vertical,
            "alpha": alpha,
            "border_color": border_color,
            "border_width": border_width,
            "border_alpha": border_alpha,
            "background_color": background_color,
            "background_style": background_style,
            "background_alpha": background_alpha,
            "transform_x": transform_x,
            "transform_y": transform_y,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "rotation": rotation,
            "width": width,
            "height": height,
        },
    )
