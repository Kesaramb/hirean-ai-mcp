# HireAn AI MCP

**Build editable video projects with your AI assistant.**

HireAn AI MCP connects MCP-compatible assistants to CapCut / Jianying draft
creation. Create a timeline, add video, audio, images, text, subtitles, stickers,
effects and keyframes, then save a project you can open, refine and export in
CapCut.

It is a thin client over [VectCutAPI](https://github.com/sun-guannan/VectCutAPI),
which does the actual draft manipulation. You run VectCutAPI's HTTP server;
this server talks to it.

```
AI assistant ──stdio──> HireAn AI MCP ──HTTP──> VectCutAPI:9001 ──> Editable drafts
```

This release runs locally using MCP's stdio transport. It produces editable
drafts; final video export happens in CapCut / Jianying. Hosted access,
subscriptions and billing are future work.

Product: [HireAn.AI](https://hirean.ai). CapCut and Jianying are third-party
editors; this project is not an official CapCut or ByteDance product.

## Setup

Requires Python 3.10+, FFmpeg, and a CapCut or Jianying install.

### 1. Install the VectCutAPI backend

It lives in `backend/` (gitignored — it's an upstream checkout, not part of this repo):

```bash
git clone https://github.com/sun-guannan/VectCutAPI.git backend/VectCutAPI
cd backend/VectCutAPI && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp config.json.example config.json   # set draft_profile + is_capcut_env
cd ../..
```

### 2. Install this server

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
```

### 3. Start the backend

**The MCP server does nothing unless this is running.** Leave it in its own terminal:

```bash
./scripts/start-backend.sh
```

It serves on `:9001` and exits early if something is already listening there.

### 4. Register with Claude

```bash
claude mcp add hirean-ai --scope user \
  --env HIREAN_AI_API_URL=http://localhost:9001 \
  --env "HIREAN_AI_DRAFT_FOLDER=$HOME/Movies/CapCut/User Data/Projects/com.lveditor.draft" \
  -- "$PWD/.venv/bin/hirean-ai-mcp"
```

Check it with `claude mcp get hirean-ai`. Other MCP clients can launch the
absolute path to `.venv/bin/hirean-ai-mcp` with the same environment variables.
See `.env.example` for all variables; this server reads its process environment
and does not automatically load an `.env` file.

With `HIREAN_AI_DRAFT_FOLDER` set, `save_draft` writes straight into CapCut — new
drafts get unique ids, so nothing existing is overwritten.

## Upgrading from CapCut MCP

Reinstall from this directory with `.venv/bin/pip install -e .` to add the new
`hirean-ai-mcp` command. The Python package is now `hirean_ai_mcp`, and the server
identifies itself as **HireAn AI**.

Existing launch configurations can continue using `capcut-mcp` or
`python -m capcut_mcp.server`. The `CAPCUT_API_URL`, `CAPCUT_TIMEOUT` and
`CAPCUT_DRAFT_FOLDER` environment variables remain supported. Their
`HIREAN_AI_*` equivalents take precedence when non-empty. Python integrations
should update imports to `hirean_ai_mcp`; the legacy package only retains its
version and server entry point. The 14 tool names and their arguments are unchanged.

## Tools

14 tools covering all 25 backend endpoints.

| Tool | What it does |
|---|---|
| `create_draft` | Start a draft, returns the `draft_id` everything else needs |
| `add_video` | Video clip with trim, transform, transition, mask, background blur |
| `add_audio` | Music / voiceover / SFX with volume, speed, audio effect |
| `add_image` | Still image with intro/outro/combo animation, transition, mask |
| `add_text` | Text overlay: font, border, background, shadow, animation, per-range styles |
| `add_subtitle` | Subtitles from SRT text, path or URL |
| `add_sticker` | Sticker by CapCut resource id |
| `add_effect` | Scene or character visual effect over a time range |
| `add_video_keyframe` | Animate a property; single or batch form |
| `list_asset_types` | Valid names for animations, transitions, fonts, masks, effects |
| `save_draft` | Write the draft to disk; polls to completion by default |
| `query_draft_status` | Poll a save task started with `wait=False` |
| `generate_draft_url` | Shareable / preview URL for a draft |
| `query_script` | Inspect the current timeline JSON |

### Why `list_asset_types` matters

Valid animation, transition, font, mask and effect names differ between CapCut
and Jianying installs. The backend exposes twelve separate endpoints to
enumerate them; this server folds them into one tool so the model can look up
real values instead of inventing them. The tool descriptions for `add_video`,
`add_image`, `add_text` and `add_effect` all point back to it.

## Notes

- **Errors.** VectCutAPI answers every request with HTTP 200 and signals failure
  only via `success: false` in the body. `client.py` checks that envelope and
  raises, so a failed edit surfaces as a tool error rather than a false success.
- **Omitted parameters.** Every optional parameter defaults to `None` and is
  stripped before the request, so the backend applies its own defaults rather
  than this server duplicating and drifting from them.
- **Default track names** are `video_main` for video, `text_main` for text.
  `add_video_keyframe` targets `video_main` unless you pass `track_name`; naming
  a track that doesn't exist is an error, so check `query_script` if unsure.
- **`add_effect` works around an upstream bug.** `add_effect_impl` runs
  `params=params[::-1]` unconditionally, so omitting `params` raises
  `'NoneType' object is not subscriptable` in the backend — breaking every
  effect call that doesn't tune intensities. This server always sends a list,
  so `add_effect` works with just an `effect_type`.

### How saving actually behaves

`save_draft` returns the full task status rather than the backend's thinner
`/save_draft` reply:

```json
{"status": "completed", "progress": 100, "completed_files": 1,
 "total_files": 1, "message": "Draft creation completed", "draft_url": ""}
```

Current upstream runs the save inline — the background-thread path in
`save_draft_impl` is commented out, so `/save_draft` returns no task id. It does
still record progress under `task_id == draft_id`, which is what this server
polls. Forks that re-enable threading return a real task id and finish
asynchronously; the same polling covers both. Pass `wait=False` to skip it.

`draft_url` is empty unless `is_upload_draft` is enabled in the backend's
`config.json`.

## Limitations

- **`get_video_duration` is not available.** VectCutAPI implements it only as an
  in-process module (`get_duration_impl.py`) with no HTTP route, so there is
  nothing to wrap. Probe durations with `ffprobe` if you need them.
- **Media paths aren't validated when you add them.** The backend accepts
  `add_video` with a path that doesn't exist and only fails later, at save time.
  That's upstream behavior, not something this server can detect at add time.

## Development

```bash
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest
```

Tests use a local stub backend and do not require CapCut or a running VectCutAPI
server. The backend checkout, virtual environments, secrets and generated media
are excluded from Git. Backend tests belong to its separate upstream checkout.

See [CHANGELOG.md](CHANGELOG.md) for release notes and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for dependency attribution.
