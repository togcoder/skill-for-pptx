# T026 — Forge finds its own licensed photos and icons (2026-10-07)

Owner: "I have no nice assets — can it find and download them itself?" Yes.

## What changed

- `scripts/forge_assets.py`:
  - **Photos.** Search Openverse anonymously (CC0 / CC BY / CC BY-SA,
    commercial use + modification; illustrations and clip-art filtered; ≥1200 px).
    Pexels is used when `PEXELS_API_KEY` is set (code path untested here: no key).
  - **Contact sheet.** Numbered thumbnails let the agent *look* and choose `pick`.
    Openverse's thumbnail proxy returned HTTP 424 for every Commons file here,
    so thumbnails fall back to Wikimedia's own scaler, then to the original.
  - **Download and cache.** Files are validated with Pillow, downscaled to
    2400 px JPEG and stored with a licence sidecar. Searches are cached per
    query/orientation, so `pick` is stable. Retries cover resets and 5xx/429.
  - **Icons.** Iconify search over Lucide (ISC), Tabler (MIT) and Phosphor (MIT);
    the SVG is fetched in the theme colour.
- `slide_forge.py`:
  - `image: {"search", "pick"?, "orientation"?}`.
  - `icon` on KPI items and comparison sides, inserted as native SVG
    (`asvg:svgBlip`, transparent PNG fallback) inside the card, so the
    Director reveals it with the card.
  - Automatic closing **Image credits** slide (TASL attribution), a per-slide
    notes line and `image_credits` in the verdict.
- `[static]` in speaker notes keeps the Director off a slide (used for credits).

## Evidence

`examples/forge/coffee_report_photos.json` → 11 slides, 123 effects, QA ok.
Two Openverse photos (CC BY-SA 3.0, CC0) and five Lucide icons, rendered by
PowerPoint 16.0 build 17932:

- The SVG icons draw in theme colours.
- Photos crop correctly and the latte photo gets Ken Burns.
- The credits slide stays static.

The first auto-pick for the bullets slide was a clip-art cup, which led to the
illustration filter. The auto-picked hero (a cluttered roaster) is why the
skill now makes the agent look at the contact sheet before choosing.

The rendered PPTX/strips contain third-party CC BY-SA photos, so they are
not committed (share-alike + AGENTS.md media rule). The spec and verdict are
enough to rebuild them. Offline test: `AssetTests` seeds the cache the way a
real search leaves it.

## Limits

- Openverse quality is uneven (mostly documentary Commons photos). Pexels or Unsplash keys give stock-grade photos.
- No automatic aesthetic ranking. The agent's eye on the contact sheet is the filter.
- Anonymous Openverse limits: `page_size` ≤ 20, 1000 thumbnails per day.
