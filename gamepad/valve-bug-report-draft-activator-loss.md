# DRAFT — Valve bug report: state-dependent activator loss (Start/Release Press × Long/Double Press)

> **Status: DRAFT, not filed.** Filing is a user decision (outward-facing). Before filing:
> (1) decide channel — `ValveSoftware/steam-for-linux` GitHub tracker is the natural home;
> (2) optionally re-confirm on the then-current client version (evidence below is publicbeta
> 1781139754); (3) pick which artifacts to attach (the matrix run dir is self-contained);
> (4) strip lab-internal terminology. Everything below is written to be pasted nearly as-is.

---

## Title

Steam Input: Start Press / Release Press / Double Press activators silently stop firing when
combined with a state-bound activator on the same button (state-dependent, not reproducible
from binding order alone)

## Summary

When a button binds **Start Press** or **Release Press** together with **Long Press** or
**Double Press** (the activators that delay/queue others on the same input), some activators
on that button **silently never fire**. Which activator is lost varies with hidden client
state — not with the visible "Command 1..N" slot order. Each activator works perfectly alone;
the loss appears only under co-residency.

## Environment

- Steam client: publicbeta **1781139754** (Linux)
- OS: Arch-family (CachyOS), KDE Plasma on Wayland (Steam under XWayland)
- Controller: Xbox-360-class pad (uinput-backed test device; also reproduced with GUI-made
  bindings on a real user session — see "Two independent reproductions")
- Config: Desktop layout (legacy-mode bindings), all activator settings default unless noted

## Two independent reproductions

**A. GUI-native (human, real session, app-plane observation):** on one button bind
Start Press→A, Release Press→B, Long Press→C in the configurator. Press-and-hold produced
`B C C C…` — **Start Press never fired**, and Release Press fired **near press-down** (before
any physical release). After rebinding so the slot order changed (Release, Start, Long), all
three fired (`B A C C…`). After further rebinding churn, the ORIGINAL visible order **also
worked** — i.e. pure order-dependence is falsified; some hidden state (per-controller config
cache? retired/ghost command slots? configurator session state) decides whether an activator
is eaten.

**B. Systematic matrix (instrumented, X11 raw-input capture, 16 configurations):** all slot
permutations of {Start, Release} × {Long | Double | Regular+Double} written as clean disk-loaded
layouts (edit autosave vdf → restart Steam — verified-live technique), driven by scripted
button presses, observed at the XInput2 **raw** event layer:

- **Release Press: absent in all 16 cells, at every slot position (1st–4th).** In this
  environment the suppression is universal, not order-specific.
- **Start Press: fires in every cell.**
- **Double Press: completely dead when Start+Release co-reside on the button** — even for
  clean in-window double-taps (~120 ms down-to-down, Double Tap Time 190 ms). With only
  Regular+Double on the button, Double Press behaves exactly as documented (fires on the
  second down).
- Control observations: Release Press bound **alone** on a button fires correctly; the
  combination Start+Release+Regular (no state-bound activator) fires **all** activators
  correctly. The trigger condition is specifically co-residency with Long/Double.

## Why this matters

Multiple activators per button are created implicitly by binding order in the GUI and are
common in shared community configs. Authors get no warning: the lost activator simply never
emits, and which one is lost can change after unrelated rebinding churn. This breaks
click-and-drag helpers, push-to-talk-on-release patterns, and any layout using press/release
edge bindings alongside long/double presses.

## Possibly-related observations

- **Ghost slot indices:** after rebinding experiments, a button showed "Executes 3 Commands"
  with slots numbered **3, 4, 5** — removed commands retire their indices, new ones append.
  If activator scheduling keys on absolute slot index or retired slots, that would be
  consistent with the state-dependence above.
- The desktop-layout autosave is not flushed to disk while the client runs (and in our
  observation not even on client exit), so we could not capture how a GUI-evolved layout with
  ghost slots serializes.

## Repro recipe (minimal)

1. Desktop layout, any button: bind Start Press→A, Release Press→B, Long Press→C.
2. Press and hold the button past the long-press threshold; release.
3. Expected: A at down, C at threshold, B at release. Observed (state-dependent): A and/or B
   missing; in a freshly disk-loaded layout B (Release) is consistently missing; after GUI
   rebinding churn the loss pattern can change or vanish.
4. For the Double Press variant: bind Start→A, Release→B, Double→D; double-tap inside the
   Double Tap Time. Observed: D never fires while A fires per tap.

## Attachments (lab artifacts, available on request)

- 16-cell matrix run: layouts (vdf), scripted stimuli, raw XI2 captures, per-cell results table
- Screenshots of the GUI slot model and the ghost-slot (3/4/5) state
- App-plane keylogger transcripts of the GUI reproduction

---

*Lab provenance (internal, strip before filing): run
`runs/20260612T072850Z-phase4-batch2-matrix/`, GUI evidence
`reference/oracle-gui-observations/`, durable summary
`findings/steam_lane_behavior.md` §Order-dependent edge-activator loss. Matrix claim strength:
single-pass, state not controlled (environment-trust doctrine, commit 71da330).*
