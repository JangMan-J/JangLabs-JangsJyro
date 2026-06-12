# Steam Input mechanics knowledge dump — "Steam Deck Controller Guide - A Visual Introduction"

**The knowledge dump the session-5 wait-state was holding for** (plan banner, 2026-06-11).
User-provided 2026-06-11; consult this (and the user — they are the deeper oracle) before new
Steam-lane probe loops, per the wait-state protocol.

## Provenance

- **Source:** Steam Community guide ID `2804823261`
  (https://steamcommunity.com/sharedfiles/filedetails/?id=2804823261),
  "Steam Deck Controller Guide - A Visual Introduction".
- **Captured:** saved-page snapshot, user-provided 2026-06-11 (third grab, `steam_g_3.*` series;
  earlier grabs of the same guide were redundant and not ingested).
- **Conversion:** `convert_guide_html_to_md.py` (user-written, BeautifulSoup) — HTML → MD,
  preserving the chapter TOC, bbcode headings/tables/quotes/links. **All image/media content is
  dropped** (the guide's 332 screenshots, ~814 MB, were deliberately left out of the repo; the
  visual content lives at the source URL). The script's `SRC`/`DST` constants still point at the
  original `~/Downloads` paths — edit them if re-running.

## Files

| File | What |
|------|------|
| `steam-deck-controller-guide-2804823261.md` | **Canonical text** — read this one |
| `steam-deck-controller-guide-2804823261.html` | Raw saved-page snapshot the MD was converted from (no images) |
| `steam-deck-controller-guide-2804823261.rendered.html` | User's clean single-file HTML render of the same content (for human reading; was `~/Documents/steam_input_guide.html`) |
| `convert_guide_html_to_md.py` | The HTML→MD converter, for provenance / re-conversion |

## Why it matters to the lab

Authored mechanics documentation for the Steam Input reference lane — the activation model the
lab has been characterizing empirically (Phases 0–3). High-value sections (MD heading anchors):

- **Commands and Game Actions** — activation conditions (Regular/Double/Long/Start/Release/
  Chorded/Analog/Soft Press), Double Tap Time, Long Press Time, **Interruptible**, activation
  **ordering** (Start → Regular/Long/Double/Chorded → Release; both presses of a Double Press
  fire Start/Release Press), **Fire Start/End Delay** worked examples, repeat/turbo, cycle
  bindings.
- **Triggers** — Soft Pull / Full Pull, Soft Press threshold, Analog activation.
- **Action Sets and Action Layers** — set vs layer semantics, Hold Action Set Layer.
- **Behaviors / Mode Shift / Virtual Menus** — scope comparison vs Button Chord and layers
  ("When should I use Button Chord, Mode Shift, Action Layer, and Action Set?").

**Epistemic status:** authored community documentation — *guide-claim* strength, below this
lab's trace-verified runtime evidence ("real-runtime evidence beats source review",
`../../CLAUDE.md`). Use it to generate hypotheses, name mechanics, and seed the Phase-8 KB;
every load-bearing conversion rule still needs a trace. Notably it corroborates the lab's
double-press pause finding (Regular Press waits out the Double Tap Timer when sharing a button
with Double Press) and gives emission timing for Double Press ("remains active while the button
is held down after the second press") — but it does **not** resolve the double-tap window's
epoch endpoints (down-to-down vs release-to-release), which stays an open question for the user.
