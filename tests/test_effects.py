"""Tests for the effects tools."""

from __future__ import annotations

import pytest

from hirean_ai_mcp.tools import effects


class FakeClient:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def post(self, path, payload=None):
        self.calls.append((path, payload or {}))
        return {"draft_id": "d1"}

    def get(self, path):
        self.calls.append((path, {}))
        return [{"name": "Split"}]


@pytest.fixture
def client(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr(effects, "get_client", lambda: fake)
    return fake


def test_add_effect_sends_empty_list_when_params_omitted(client):
    """Guards an upstream crash.

    add_effect_impl runs `params=params[::-1]` unconditionally, so omitting
    params raises "'NoneType' object is not subscriptable" in the backend.
    Sending [] keeps every effect usable without tuning intensities.
    """
    effects.add_effect(effect_type="Blur")
    assert client.calls[0][1]["params"] == []


def test_add_effect_passes_explicit_params_through(client):
    effects.add_effect(effect_type="Blur", params=[0.5, 1.0])
    assert client.calls[0][1]["params"] == [0.5, 1.0]


def test_add_effect_defaults_to_scene_category(client):
    effects.add_effect(effect_type="Blur")
    assert client.calls[0][1]["effect_category"] == "scene"


def test_list_asset_types_maps_category_to_path(client):
    effects.list_asset_types("mask")
    assert client.calls[0][0] == "/get_mask_types"


def test_list_asset_types_rejects_unknown_category(client):
    with pytest.raises(KeyError):
        effects.list_asset_types("not_a_category")


def test_keyframe_batch_form_drops_unset_singular_fields(client):
    """The singular form must not reach the backend as explicit nulls.

    Pruning happens inside the real client, so check the payload the way the
    client would serialize it.
    """
    from hirean_ai_mcp.client import prune

    effects.add_video_keyframe(
        draft_id="d1", property_types=["alpha"], times=[0.0], values=["1.0"]
    )
    sent = prune(client.calls[0][1])
    assert sent == {
        "draft_id": "d1",
        "property_types": ["alpha"],
        "times": [0.0],
        "values": ["1.0"],
    }
