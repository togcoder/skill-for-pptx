# T014 — KPI Counter Native Execution

Status: structural stepped-text counter implemented; PowerPoint playback pending.

## Goal

Execute T012 hero-metric number counters inside an existing slide without
changing the user's final KPI object/value and without creating extra slides.

## Mechanism

PowerPoint has no verified numeric-text tween primitive in the evidence reviewed.
Microsoft's documented countdown uses multiple overlaid number text boxes with
animation sequencing.

T014 adapts that pattern for count-up/count-down:

1. keep the original final KPI textbox untouched;
2. clone that source shape for intermediate numeric values;
3. preserve source geometry/style in the clones;
4. give every proxy a unique native ID/name;
5. animate proxies automatically inside one presenter click beat;
6. reveal the original source textbox last.

## Counter interpolation

Intermediate values use a cubic ease-out numeric schedule so the counter moves
quickly at first and settles near the final value.

Formatting preserves:

- prefix;
- suffix;
- decimal places;
- grouping commas when present in source text.

Generated intermediate strings deliberately exclude the exact final source text.

## Native timing hypothesis

For each proxy:

- entrance effect;
- short visible interval;
- exit effect.

After the last proxy:

- entrance effect on the untouched source textbox.

All effects use internal numeric delays inside the same click beat. These delays
represent the counter's own animation cadence, not presenter speech.

## Source protection

The low-level effect requires `preserve_final_text`. If the source textbox text
has drifted since planning, the writer aborts before cloning.

The original source shape XML is not rewritten.

## Evidence

Temporary GitHub Actions run 37238539416:

- Python compile pass;
- **120 tests passed in 0.618 s**.

New tests verify:

- eased counter value generation;
- percentage/currency/grouping formatting;
- proxy clones preserve source geometry and fill;
- source text remains exact;
- unique proxy IDs/names;
- edit-view z-order leaves the first counter value on top;
- v0.4 validation;
- source-text drift rejection;
- two timing effects per proxy plus final source entrance;
- one presenter click group;
- build list covers source + generated proxies.

## Boundary

Structural timing does not prove slideshow visibility semantics.

PowerPoint playback must confirm:

- entrance-animated source/proxies are hidden before their scheduled effect;
- only one counter value is visible at a time;
- transitions do not flicker;
- final value is the original source textbox;
- click count remains one for the counter beat;
- file opens without repair.

## Next

1. exact-file PowerPoint playback of a KPI counter fixture;
2. compare fade vs disappear/appear timing for flicker;
3. test negative values, currency, percent and large grouped values;
4. then prototype a smoother odometer-style digit reel if the stepped-text
   baseline is playback-safe.
