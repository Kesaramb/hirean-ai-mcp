---
name: shark-tank-story-video
description: "Turn a trimmed Shark Tank episode (one business) into a packaged, story-driven, YouTube-ready video. Finds the angle with the GAG Story Engine (five aftermath shapes, the Gap, package-first gate), scripts the 8-beat spine, renders receipt/stat overlays with Remotion, and assembles the timeline in CapCut via the HireAn AI MCP tools. Use when the user provides a Shark Tank episode or pitch clip to edit, asks for a Shark Tank aftermath/story video, says 'find the angle', or wants a YouTube-ready cut built with CapCut and/or Remotion."
---

# Shark Tank Story Video (GAG Engine)

Turns ONE trimmed Shark Tank episode into a YouTube-ready story video. The GAG Story Engine
supplies the editorial system (which story to tell, in what order), Remotion renders the
data-driven overlays (stat callouts, receipt cards, title cards, end screen), and the
`hirean-ai` MCP server assembles everything into a CapCut draft the user opens, tweaks, and exports.

**The one law everything serves:** a cold viewer makes three decisions — **stop** (thumbnail),
**click** (title), **stay** (the story re-earns attention every 30 seconds).
**Package first. Script second. Edit last.** If the package fails its gate, STOP and report —
do not produce the video. A great edit with a dead package is a dead video.

## Inputs

- **Required:** path to the episode video, already trimmed to one business.
- **Optional:** transcript/captions, aftermath research links, receipt images (filings,
  archived pages, screenshots), target length (default ≈ 8 minutes, mid-roll eligible).

All per-video artifacts live in `productions/<company-slug>/` inside the project
(canvas.md, script.md, captions.srt, props/, overlays/, qc.md). Never write them to the project root.

## Pipeline

Run the phases in order. Each has a gate; a failed gate means stop and report, not push through.

### Phase 0 — Intake & probe

1. Probe the file: `ffprobe -v error -show_entries format=duration -show_entries stream=width,height,r_frame_rate -of default=nw=1 "<episode>"`.
2. Get a transcript: use the provided one; else extract audio
   (`ffmpeg -i "<episode>" -vn -ac 1 -ar 16000 audio.wav`) and transcribe with `whisper`
   (or a video-analysis/transcription MCP tool if one is connected). If neither exists, ask the user for a transcript.
3. Build a **timecode log** of the raw episode: the entrance, the ask, each Shark's offer,
   counters, the handshake or rejection, and the 3–5 strongest reaction shots. Every timecode
   in the script references this log.

### Phase 1 — Find the angle (the editorial gate)

Read [references/story-engine.md](references/story-engine.md) in full, then:

1. Extract from the episode: company, founder, product, the ask, the offers, the outcome on TV.
2. **Research the aftermath** (web search): what happened after the cameras stopped — deal
   closed or collapsed, current status, filings, socials, press. Every factual claim gets a
   `⚑ VERIFY` flag until confirmed against a primary source.
3. Pick ONE of the five shapes (Collapse, Vindication, Copycat War, Disappearance,
   Devil's Bargain) and state **the Gap**: what the TV moment promised vs what actually happened.
4. Copy [resources/canvas-template.md](resources/canvas-template.md) to
   `productions/<slug>/canvas.md` and fill all 10 boxes.

**GATE (all must pass, in this order):**
- **Gap gate** — no gap between TV promise and reality → no video. Stop.
- **Stranger Test** — one sentence, zero prerequisite context, still creates an itch.
- **Package lock** — write 3 title+thumbnail pairs; thumbnail = the emotion/object, title = the
  unresolved half of the same question; they never repeat or resolve each other. Present the 3
  candidates with a recommendation and lock one BEFORE scripting.

If the gate fails: report which box wouldn't fill, why the story is weak, and (if possible) a
stronger shape or angle for the same footage. Do not script.

### Phase 2 — Script the 8 beats

Copy [resources/script-template.md](resources/script-template.md) to `productions/<slug>/script.md` and:

1. Write VO beat by beat on the 8-beat spine (timings in the template). THE TANK beat uses the
   actual episode footage as scenes — map each script line to timecodes from the Phase 0 log.
2. Apply the retention laws: every beat connects with **but** or **therefore** (never "and then");
   every 30-second block delivers a reveal, a number, or a reversal; the loop ledger never hits zero.
3. List the three receipts with sources. Resolve every `⚑ VERIFY` you can — **never ship an
   unverified claim about a company's status or finances**. If a ⚑ remains on a load-bearing
   claim (the Gap, the cold-open number, the verdict number), stop before Phase 3 and ask the
   user to confirm or supply a primary source — the engine's rule is every ⚑ resolved before
   production. Peripheral flags may ride to delivery, reported as publish blockers.
4. Estimate durations at ~150 words/minute of VO and fill the timeline column — this becomes the
   CapCut timing map.
5. Generate `captions.srt` from the VO lines.
6. VO audio: if the user will record, deliver the script with per-beat timings. If a TTS/audio
   MCP tool is connected, offer a scratch VO track so the timeline can be timed precisely.

### Phase 3 — Render overlays with Remotion

Follow [references/remotion-overlays.md](references/remotion-overlays.md). Copy
[resources/remotion/](resources/remotion/) into `productions/<slug>/overlays/`, install, drop
receipt images into `public/receipts/`, write one props JSON per overlay instance, and render
ProRes 4444 alpha `.mov` files (or PNG stills as fallback). Minimum kit per video: cold-open
title, one stat callout per major number, one receipt card per receipt, lower third for the
founder, end-screen handoff.

### Phase 4 — Assemble the CapCut draft

Follow [references/capcut-playbook.md](references/capcut-playbook.md). Non-negotiables:

- `create_draft(width=1920, height=1080)` — the default is portrait; YouTube is landscape.
- Never guess asset names — `list_asset_types` first for transitions, fonts, animations, effects.
- Cold open: story starts at 0.0s. No intro, no logo, no "welcome back".
- Every number on screen carries its source (that's what the Remotion overlays are for).
- Verify the built timeline with `query_script` against script.md, then `save_draft`.

### Phase 5 — QC & deliver

1. QC against the checklist in the playbook (cold open at zero, no gaps/overlaps on the main
   track, every stat has a visible source, timeline drift from script < 2s per beat, end-screen
   space clear in the last 20s).
2. `save_draft` (wait for completion), then `generate_draft_url`.
3. Deliver: draft id + URL, the locked package (title + thumbnail brief), canvas.md, script.md,
   captions.srt, overlay renders, and the list of **unresolved ⚑ flags** the user must verify
   before publishing.

## Failure modes

| Symptom | Action |
|---|---|
| Canvas box won't fill (no Gap, no But) | Kill the story now; report; suggest a different shape/angle |
| No aftermath information findable | That IS Shape 4 (Disappearance) — the investigation is the plot; if even that's thin, stop |
| CapCut rejects an animation/font/effect name | You guessed; call `list_asset_types` and retry with an exact name |
| Alpha `.mov` imports without transparency | Fall back to `remotion still` PNGs via `add_image` (see remotion-overlays.md) |
| Backend can't read a media path | Use absolute local paths readable by the capcut backend; remote URLs download at save time |
