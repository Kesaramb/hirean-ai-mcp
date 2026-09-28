# CapCut assembly playbook (HireAn AI MCP)

How to turn the finished 8-beat script into a CapCut draft with the `hirean-ai` MCP tools.

## Golden rules

1. `create_draft(width=1920, height=1080)` — **the tool defaults to portrait 1080×1920**;
   YouTube long-form is landscape. Capture the returned `draft_id` and pass it to EVERY call —
   `add_video` without a `draft_id` silently creates a new draft.
2. All timing is **seconds**. On `add_video`/`add_audio`, `start`/`end` trim the SOURCE clip
   and `target_start` places it on the TIMELINE. `add_image` has NO `target_start` — its
   `start`/`end` are themselves the timeline window (when it appears / when it leaves).
3. **Never guess names.** Before using any transition, mask, font, animation, or effect, call
   `list_asset_types(category)` — valid names differ between CapCut and Jianying installs:
   `transition`, `mask`, `font`, `intro_animation`/`outro_animation`/`combo_animation` (images),
   `text_intro`/`text_outro`/`text_loop_anim` (text), `video_scene_effect`/`video_character_effect`,
   `audio_effect`.
4. Coordinates (`transform_x`/`transform_y`) are normalized roughly −1.0..1.0 with (0,0) at
   centre — and **negative `transform_y` moves DOWN** (inverted vs. most tools).
5. The draft lives in the backend cache until `save_draft` — that call downloads remote media
   and writes the real CapCut draft folder. Verify structure with `query_script` before saving.

## Track plan

Use consistent `track_name` values so layers stay organized (create implicitly by first use):

| track_name | Content |
|---|---|
| `main` | Episode footage + b-roll/archive images, back to back |
| `overlay` | Remotion ProRes 4444 `.mov` renders (stats, receipts, titles, end screen) |
| `text` | Native CapCut text (only for quick one-off cards) |
| `subtitles` | `add_subtitle` output |
| `vo` | Voiceover |
| `music` | Music bed segments |
| `sfx` | Whooshes, stings, risers |

If stacking order between two visual tracks matters, set `relative_index` and confirm the
result with `query_script` — then keep the convention for the rest of the build.

## Timing map first

Before any tool call, extend script.md's timeline table into a shot list: one row per segment
with `source file, start, end, target_start, track` (image rows: write the timeline window
into `start`/`end` — `add_image` has no `target_start`). VO pacing ≈ 150 words/min gives each
beat's duration; the 8-beat spine gives the targets (Wound ends ~0:20, Tank ~1:00–2:30, etc.).
Build the whole draft from this table so `query_script` can be diffed against it.

## Beat-by-beat assembly

**1 · THE WOUND (0:00–0:20)** — cold open, story at frame zero:
```
add_video(draft_id, video_url="/abs/path/episode.mp4", start=<handshake_tc>, end=<+8s>,
          target_start=0, track_name="main", volume=0.6)
add_video(draft_id, video_url=".../overlays/out/01-wound-stat.mov",
          target_start=1.0, track_name="overlay")   # "$2.5M" + source
```
No logo, no intro. Optional slow punch-in via keyframes (below).

**2 · THE HUMAN (0:20–1:00)** — founder photos/archive stills:
```
list_asset_types("intro_animation")   # then:
add_image(draft_id, image_url="/abs/path/founder-garage.jpg", start=20, end=26,
          track_name="main", intro_animation="<exact name>",
          background_blur=3)
add_video(draft_id, video_url=".../out/02-lowerthird.mov", target_start=22, track_name="overlay")
```
`add_image` has no `target_start` — its `start`/`end` place the image directly on the
timeline (there is no source to trim). Blurred-background fill handles non-16:9 stills.

**3 · THE TANK (1:00–2:30)** — the episode as scenes. Cut the pitch into 4–8 trimmed
`add_video` segments (ask → key exchanges → offers → counters → handshake), natural audio up
(`volume=1.0`), music bed low. Punch in on the decisive moment:
```
add_video_keyframe(draft_id, track_name="main",
    property_types=["scale_x","scale_x","scale_y","scale_y"],
    times=[63.0, 64.2, 63.0, 64.2],
    values=["1.0","1.18","1.0","1.18"])
```
The plural form zips `property_types`/`times`/`values` positionally — list every (property,
time) pair, and each property needs ≥2 keyframes to animate. Values are strings. Property
names: `alpha`, `scale_x`, `scale_y`, `position_x`, `position_y`, `rotation`, `volume`.

**4 · THE HONEYMOON (2:30–3:30)** — press/archive images with transitions
(`list_asset_types("transition")` first, then `transition=` + `transition_duration=` on the
segments). Plant the seed of doom: one stat callout or highlighted detail the audience can see
is a problem.

**5 · THE TURN (3:30–4:00)** — one sentence where it breaks. Hard cut, music OUT (end the bed
segment here), 2–3s of near-silence, single overlay or text card:
```
add_video(draft_id, video_url=".../out/05-turn-title.mov", target_start=212, track_name="overlay")
```

**6 · THE RECEIPTS (4:00–6:00)** — one ReceiptCard `.mov` per receipt on `overlay`, over slow
push-ins of the documents on `main` (add the doc image, keyframe `scale_x`/`scale_y`
1.0→1.15 across its duration). Every card carries its source line. Escalate: each receipt
bigger than the last.

**7 · THE VERDICT (6:00–7:00)** — re-add the SAME trim as the cold open (same `start`/`end`,
new `target_start`) so the opening image replays, now understood; verdict StatCallout on top.

**8 · THE LESSON + LOOP (7:00–7:30)** — `08-endscreen.mov` occupies the left; keep the right
half visually clear for YouTube end-screen elements. Music up, VO delivers the lesson + the
handoff line.

## Audio

```
add_audio(draft_id, audio_url="/abs/path/vo.wav", target_start=0, track_name="vo", volume=1.0)
add_audio(draft_id, audio_url="/abs/path/music.mp3", start=0,  end=60,  target_start=20,
          volume=0.18, track_name="music")     # bed under VO
add_audio(draft_id, audio_url="/abs/path/music.mp3", start=60, end=66, target_start=240,
          volume=0.35, track_name="music")     # swell between beats
```
Ducking: split the music into consecutive trimmed segments with different `volume` values —
robust and predictable. `speed` can stretch a bed a few percent to land a hit on a beat
boundary. For audio effects, `list_asset_types("audio_effect")` first.

## Subtitles

Generate `captions.srt` from the VO script (≤ 2 lines, ≤ 42 chars/line per cue), then:
```
list_asset_types("font")   # exact font names, then:
add_subtitle(draft_id, srt="/abs/path/captions.srt", font="<exact>", font_size=8,
             font_color="#FFFFFF", border_color="#000000", border_width=2,
             transform_y=-0.72, track_name="subtitles")
```
`font_size` is in CapCut's internal units, not px — render once, eyeball in CapCut, adjust.
`transform_y=-0.72` ≈ lower-third safe area (negative = down).

## Remotion overlays

Import each render as a normal clip:
`add_video(draft_id, video_url="/abs/path/overlays/out/<name>.mov", target_start=<t>, track_name="overlay")`.
ProRes 4444 alpha composites directly over `main`. If transparency fails, use the PNG-still
fallback in [remotion-overlays.md](remotion-overlays.md) via `add_image` + a native intro animation.

## Save & handoff

1. `query_script(draft_id)` — diff tracks/segments/timings against the shot list (response can be large).
2. `save_draft(draft_id, draft_folder=...)` — `draft_folder` is the CapCut drafts directory;
   omitted, it falls back to `HIREAN_AI_DRAFT_FOLDER`, then the backend default. `wait=True`
   (default) polls to completion; remote URLs download now, so local absolute paths are faster
   and safer. If you used `wait=False`, poll `query_draft_status(task_id)`.
3. `generate_draft_url(draft_id)` for a shareable preview link.

## QC checklist (run before save, report after)

- [ ] Draft is 1920×1080
- [ ] First segment on `main` starts at 0.0 and is story, not branding
- [ ] `main` has no gaps or accidental overlaps (`query_script`)
- [ ] Every number/claim overlay includes its visible source (Law 5)
- [ ] Beat boundaries within ~2s of script.md targets
- [ ] Music ducked under every VO passage; THE TURN has its silence
- [ ] Verdict replays the cold-open image
- [ ] Last ~20s: right side clear for end-screen elements
- [ ] All ⚑ VERIFY flags either resolved or listed in the delivery report
