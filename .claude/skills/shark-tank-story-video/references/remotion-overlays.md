# Remotion overlay kit

Remotion (https://github.com/remotion-dev/remotion) renders the data-driven graphics CapCut
can't do programmatically: stat callouts with visible sources (retention Law 5), receipt cards,
cold-open titles, lower thirds, and the end-screen handoff. Each overlay renders to a
**transparent ProRes 4444 `.mov`** that CapCut composites over the footage like any clip.

**Division of labor:** CapCut = cutting footage, transitions, subtitles, audio mix, final
export. Remotion = anything that displays *data* (numbers, sources, documents, titles).

## Setup (once per production)

```bash
cp -R ".claude/skills/shark-tank-story-video/resources/remotion" "productions/<slug>/overlays"
cd "productions/<slug>/overlays"
npm install
mkdir -p public/receipts out props
# drop receipt images (filings, archived pages, screenshots) into public/receipts/
npx remotion studio     # optional: live preview while tweaking
```

The scaffold registers five 1920×1080 @ 30fps compositions. Duration comes from the
`durationSec` prop via `calculateMetadata`, so one composition serves any length.

## The compositions

| id | Use (beat) | Props |
|---|---|---|
| `ColdOpenTitle` | THE WOUND / THE TURN | `line1`, `line2?`, `durationSec` |
| `StatCallout` | any number on screen | `value`, `label`, `source`, `align?` (`center`\|`lower`), `durationSec` |
| `ReceiptCard` | THE RECEIPTS | `imageSrc` (path under `public/` or URL), `caption`, `source`, `stamp?` (e.g. "IN LIQUIDATION"), `durationSec` |
| `LowerThird` | THE HUMAN / THE TANK | `name`, `role`, `durationSec` |
| `EndScreenHandoff` | THE LESSON + LOOP | `lesson`, `nextTitle`, `durationSec` — draws on the LEFT only; right stays clear for YouTube end-screen elements |

Every stat/receipt component renders its `source` line on screen — that's Law 5, and it is not
optional. If a claim has no source yet, it still carries a ⚑ and doesn't get rendered.

## Rendering

One props JSON per overlay instance, named by beat order:

```bash
# props/01-wound-stat.json
# {"value":"$2.5M","label":"The biggest deal in Australian Shark Tank history",
#  "source":"Source: Network Ten broadcast, 2017","align":"center","durationSec":5}

npx remotion render StatCallout out/01-wound-stat.mov \
  --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le \
  --image-format=png --props=props/01-wound-stat.json
```

- `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png` is the
  transparency recipe: 4444 keeps the alpha channel, PNG frames preserve it during render.
- Repeat per instance (`02-lowerthird.mov`, `05-turn-title.mov`, `06-receipt-1.mov`, …).
- Keep a manifest table in script.md: overlay file → composition → props file → `target_start`
  in the CapCut timeline. Phase 4 imports straight from that table.

### Static fallback (if CapCut ignores the alpha channel)

```bash
npx remotion still StatCallout out/01-wound-stat.png --frame=45 --image-format=png \
  --props=props/01-wound-stat.json
```
`--frame` matters: the default (frame 0) is the pre-animation state — springs at scale 0,
opacity 0 — i.e. a fully transparent PNG. Pick a frame ~1.5s in (45 @ 30fps), after the
intro animations settle and at least 12 frames before the end fade-out.
PNG stills keep transparency everywhere. Import with `add_image` and add motion with a native
CapCut `intro_animation` (via `list_asset_types("intro_animation")`) or keyframes. You lose the
spring animation, not the design.

## Editing the designs

All components live in `src/overlays.tsx` — plain React + inline styles, animated with
`spring()` / `interpolate()` on `useCurrentFrame()`. House style: white 800-weight type with
heavy shadow for legibility over footage, orange `#eb6834` / blue `#2a78d6` accents, sources in
a dark pill. Keep everything inside ~5% safe margins. Change defaults in `src/Root.tsx`
(`defaultProps` shows the iCapsulate worked example).

Gotchas:
- `ReceiptCard`'s default `imageSrc` points at `public/receipts/sample-filing.png` — put any
  image there (or pass real props) before opening Studio, or the preview shows a broken image.
- Props JSON must include `durationSec` — it drives the render length.
- Match the CapCut draft: 1920×1080, and keep fps at 30 unless the episode footage is 25fps
  (PAL/AU broadcasts often are) — then change `FPS` in `src/Root.tsx` to 25 so motion stays clean.
