# Domain: video (Motion Graphics, Video Editing & Master Audio)

## Scope
Headless video editing, motion sequencing, keyframe choreography, shot pacing, audio-visual asynchrony (J-cut/L-cut), and broadcast audio mastering (EBU R128) using FilmCraft and SoundCraft.

## Thesis
Compelling video pacing and broadcast quality require:
1. Strict canvas discipline: SMPTE RP 2046-2 / EBU R95 safe zones (Action Safe 3.5%, Title Safe 5.0%) for 16:9 landscape, and strict avoidance of mobile UI dead zones (top 220px, bottom 440px, right action rail) for 9:16 vertical.
2. Shot duration adherence: 1.2s - 2.5s for promos, 3.5s - 6.0s for technical explainers with Ken Burns zoom ($1.00 \to 1.06$) for static holds $> 4.0\text{s}$.
3. Seamless narrative continuity via asynchronous cuts: J-cuts (audio leads by 12–24 frames) and L-cuts (audio trails by 15–30 frames) rather than amateurish hard cuts.
4. Broadcast-compliant audio: Integrated Loudness $-14.0\text{ LUFS} \pm 1.0\text{ LU}$, True Peak $\le -1.0\text{ dBTP}$, and automatic sidechain ducking ($-12\text{ dB}$ to $-15\text{ dB}$) with 150ms lookahead and 250ms S-curve attack.

## Native canon and sources
- SMPTE RP 2046-2: Specifications for Safe Action and Safe Title Areas for Television.
- EBU Recommendation R95: Safe areas for 16:9 television production.
- EBU Recommendation R128 & ITU-R BS.1770-4: Loudness normalisation and permitted maximum level of audio signals.
- `knowledge/video_canon.json`: formal machine-readable specification.
- `knowledge/sound_canon.json`: SoundCraft mastering specification.

## Owners and reviewers
- Author: Antigravity + Argon (Gemini 4).
- Peer reviewers: Claude, OpenCode.

## Code (canonical / experimental)
| Module | Status | Tests |
|---|---|---|
| `scripts/multi_domain_canons.py` | Canonical (T042): Safe margins, pacing, cut asynchrony, LUFS validation | `tests/test_multi_domain_canons.py` |
| `scripts/filmcraft_bridge.py` | Experimental (T042): FilmCraft headless CLI runner | `tests/test_multi_domain_canons.py` |
| `scripts/soundcraft_bridge.py` | Experimental (T042): SoundCraft headless CLI runner | `tests/test_multi_domain_canons.py` |

## Data
- `knowledge/video_canon.json`: 16:9 / 9:16 safe coordinates, dead zones, ASL limits, easing curves, audio stems.
- `knowledge/sound_canon.json`: EBU R128 targets, stem levels, ducking envelope parameters.

## Evidence ladder
| Rung | Tool | Meaning |
|---|---|---|
| 0 | Python test suite | Mathematical calculation and safe-margin boundary tests |
| 1 | `ffprobe` / `filmcraft-cli probe` | Video stream format, frame rate, and codec verification |
| 3 | `filmcraft-cli render --seconds` | Individual frame PNG export and visual check |
| 4 | `filmcraft-cli export` | Full timeline render to MP4 / H.264 |
| 5 | Video player / NLE check | Playback and audio synchronization verification |

## State (2026-11-01)
- Video and sound canons established in `knowledge/video_canon.json` and `knowledge/sound_canon.json`.
- Calculation and verification utilities implemented in `scripts/multi_domain_canons.py`.
- FilmCraft and SoundCraft native bridges operational in `scripts/filmcraft_bridge.py` and `scripts/soundcraft_bridge.py`.
