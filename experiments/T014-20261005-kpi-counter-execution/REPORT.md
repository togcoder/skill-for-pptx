# T014 — KPI stepped-text counter execution

Date: 2026-10-05 Vietnam.

## Result

Hero KPI counters now have a structural execution backend that preserves the
user's original final KPI object.

The implementation follows the same broad mechanism Microsoft documents for an
animated countdown: multiple number textboxes plus sequenced animation. Microsoft
documents a countdown using five number boxes and automatic after-previous timing.
citeturn791313search0

T014 uses cloned source-style proxies for intermediate count values and keeps the
original source textbox as the final state.

## Why not rewrite the source textbox

Rewriting the source KPI for each step would destroy the strongest preservation
guarantee and make source-vs-output auditing ambiguous.

Instead:

- source value/text remains exact;
- source geometry/style remains exact;
- generated proxy components are explicit and auditable;
- final timing target returns to the original source object.

## Component generation

`scripts/counter_component.py`:

- locates exact source ID + name;
- rejects a source-text mismatch;
- generates eased intermediate values;
- preserves decimal/prefix/suffix/grouping;
- deep-clones the source shape;
- changes only clone IDs/names/text;
- inserts proxies at the source z-order location.

## Timing

The v0.4 `number_counter` effect creates:

- proxy entrance;
- proxy exit;
- repeated automatically for all proxy values;
- final entrance of the untouched source KPI.

All of this remains inside one presenter click beat.

## Automated evidence

GitHub Actions run 37238539416:

- Python compile pass;
- **120 tests passed in 0.618 s**.

The tests prove structural source preservation, proxy formatting/style parity,
unique IDs, one-click timing grouping, and source-final targeting.

## Evidence boundary

No Microsoft PowerPoint slideshow was run.

The critical unresolved runtime question is whether entrance effects keep the
source/proxy shapes hidden until their scheduled time exactly as expected in the
generated timing hierarchy.

Do not call the counter playback-safe until that is observed on the exact file.

## Next research

The highest-value next step is a semantic-to-execution compiler so Director v0.3
chart/KPI decisions can become v0.4 patch plans automatically, followed by
PowerPoint fixture playback. Without that adapter, the semantic and low-level
layers still require manual bridging.
