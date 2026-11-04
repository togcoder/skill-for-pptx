# Wiring proposal — DeckCraft as a labelled fallback renderer

Status: **PROPOSED, not wired**. The T059 code (`scripts/deckcraft_fidelity.py`)
is `EXPERIMENTAL`; a product-path change needs the T059 review first.

## Contract

1. PowerPoint stays the default and the only source of rung-5 claims.
2. DeckCraft is used only when PowerPoint (or ffmpeg) is absent, or when the
   caller explicitly asks for `renderer="deckcraft"`.
3. Every result carries `renderer`, `frame_source`, `label` and `evidence_rung`.
   A DeckCraft result has **no** `powerpoint` key and is never labelled
   "PowerPoint". Label: `DeckCraft render (not PowerPoint)`.
4. DeckCraft supplies **static settled frames only**. It has no in-slide
   animation renderer, so `video` is `null` and `sheets` are one PNG per slide,
   not a 6-frame strip.
5. A directory of frames read by `design_critic` can carry `frame_source.json`
   (`{"source": "deckcraft", "evidence_rung": 2}`), so a later reader cannot
   mistake the frames for PowerPoint output.

## `scripts/slide_forge.py`

```python
def render(pptx, outdir, seconds=8, renderer="auto"):
    """PowerPoint by default; DeckCraft static frames when PowerPoint is absent.

    DeckCraft is labelled as such and never contributes a motion claim.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if renderer in ("auto", "powerpoint"):
        try:
            ...existing PowerPoint + ffmpeg path...
            result = {...existing...}
            result.update(renderer="powerpoint", frame_source="powerpoint",
                          evidence_rung=5, label="PowerPoint")
            return result
        except Exception as exc:
            if renderer == "powerpoint":
                raise
            fallback_reason = str(exc)
    from deckcraft_bridge import is_available, render_slides
    if not is_available():
        raise RuntimeError(f"no renderer: PowerPoint failed ({fallback_reason}); "
                           "DeckCraft CLI is not installed")
    frames = render_slides(pptx, outdir / "deckcraft", scale=2)
    (outdir / "frame_source.json").write_text(
        json.dumps({"source": "deckcraft", "evidence_rung": 2}), encoding="utf-8")
    return {
        "ok": True, "stage": "render",
        "renderer": "deckcraft", "frame_source": "deckcraft", "evidence_rung": 2,
        "label": "DeckCraft render (not PowerPoint)",
        "sheets": [str(p) for p in frames], "video": None,
        "fallback_reason": fallback_reason,
        "note": "DeckCraft has no in-slide animation renderer; static frames only.",
    }
```

`render_frames_with_fallback()` in `scripts/deckcraft_fidelity.py` implements
this contract and is unit-tested
(`tests/test_deckcraft_fidelity.py::FallbackTests`). Example output:
`artifacts/frame_source_example.json`.

## `scripts/design_critic.py`

The critic already accepts `--render deckcraft`; it does not record where the
frames came from. Add a source field:

```python
frame_source = {"deckcraft": "deckcraft", "dc": "deckcraft",
                "lo": "libreoffice"}.get(str(render), "directory")
# if render is a directory with frame_source.json, read source/evidence_rung
return {..., "frame_source": frame_source,
        "evidence_rung": 5 if frame_source == "powerpoint" else 2}
```

Markdown output adds one line:

```
Frames: DeckCraft render (not PowerPoint) — frame checks are rung 2.
```

The three frame checks (`LAY-DENSITY`, `LAY-BALANCE`, `COL-COLOURFUL`) keep
their scores; the source is metadata. Do not let a DeckCraft frame raise a
"PowerPoint verified" claim in `forge_qa` or the REPORT.

## Why not auto-enable in `build()`

`slide_forge.build()` currently calls `design_critic.critique(out)` without
frames. Enabling DeckCraft frames there would slow every build and would not
add motion evidence. Keep frames opt-in (`render(..., renderer="auto")` or
`design_critic --render deckcraft`).

## Measured consequence

On the 7 corpus decks the critic score difference between PowerPoint and
DeckCraft frames is at most **+0.01 overall** (T059 `critic_parity.csv`), well
below the 0.2 falsifier. That makes DeckCraft frames safe for the critic's
static checks — but not for Morph, animations or "PowerPoint verified".
