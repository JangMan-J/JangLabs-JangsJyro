# Knowledge base (Phase 8) — mapper behavior, evidence-backed

The lab's persistent answer to "what does this control / mapper function do?" — so agents
don't rediscover verified behavior. Layout per plan §9 / design §340–367.

> **Location note:** plan §9 says "repo-root `kb/`" — that wording predates the lab's fold-in
> to the jangsjyro fork. The fork root is upstream-facing (`../AGENTS.md`: keep diffs small),
> so the KB lives at `gamepad/kb/`, the lab root.

## Layers

| Layer | File(s) | Mutability | Who writes |
|---|---|---|---|
| **Lab notes** | `lab-notes/observations.jsonl` | Mutable, append-by-anyone, noisy | any agent, provenance required |
| **Canonical** | `canonical/*.json(l)` | Promoted semantics only — converters consume these by default | lead only, at gates |

Every lab note conforms to `../schemas/kb-note.schema.json` (validate via
`tools/validate_artifacts.py`'s `validate_kb_note`). One JSON object per line.

## Canonical files

- `canonical/control-catalog.json` — the declared controller profile (plan §8) the converter targets.
- `canonical/mapper-functions.steam.json` — verified Steam Input activator/mechanic semantics.
- `canonical/mapper-functions.jsm.json` — verified JSM binding/mechanic semantics.
- `canonical/equivalence-rules.jsonl` — cross-lane conversion rules; **only rows where BOTH
  lane halves are trace-verified** (anti-Goodhart D3). One JSON object per line.
- `canonical/capability-matrix.json` — mechanics × lanes verdict grid, untested cells explicit.

No JSON Schema exists yet for the canonical files (the Phase-3 schema set covers run artifacts
+ kb-note only). Until one lands, each canonical file keeps the envelope
`{schema_version: "1", generated: <date>, entries: [...]}` and every entry carries the
provenance block below. Adding canonical schemas is queued Phase-8 follow-up work.

## Provenance (required on every entry, both layers)

Canonical entries carry: `run_ids` (and trace/slice names where applicable), `mapper_version`,
`platform`, `device_profile`, `confidence`, `last_validated`. Constants for the current corpus:

- JSM = this fork (`branch-a-port`, Linux build `build-linux/`, clang + SDL3 3.4.8 via CPM).
- Steam client = publicbeta `1781139754`, Wayland/KDE, Desktop (legacy-mode) layout, XI2
  observation plane (**Raw\* events only** — key-layer events are flush artifacts, see
  `../findings/steam_lane_behavior.md` §XI2 delivery model).
- Device for all behavioral runs so far = **synthetic Xbox-360 uinput pad** (not the 8BitDo;
  the catalog's 8BitDo profile is the declared target for gyro phases).

`confidence` vocabulary (claim-strength ladder, strongest first): `trace-pinned` (statistics
over repeated raw-layer captures) · `trace-verified` (real-runtime capture, fewer repeats) ·
`trace-single-pass` (real-runtime but state not controlled — e.g. the batch-2a matrix) ·
`oracle-attested` (user expert claim, not yet traced) · `doc` / `static-audit` /
`source-review` / `inferred` (hypotheses — **never canonical** on their own).

## Promotion rules (gate-enforced)

1. Any agent may append lab notes — provenance mandatory.
2. Canonical entries require **real-runtime evidence + schema/envelope validation + conflict
   check + `last_validated` date**. (The synthetic-uinput → real-binary pipelines ARE real
   runtime; design-§291 "headless" — synthetic JslWrapper, deterministic time — is what cannot
   promote.)
3. Headless-only or hypothesis-class evidence may support a lab note, never a canonical entry.
4. Conflicting observations stay in lab notes until a validator task resolves or scopes the
   conflict; the canonical layer never carries two contradictory rows for one mechanic.

## Conflict handling (Phase-8 gate requirement)

On promotion the lead checks each candidate against existing canonical rows for the same
mechanic/lane:

- **No row** → promote.
- **Consistent row** → merge evidence refs, refresh `last_validated`.
- **Contradiction** → canonical row is frozen, candidate stays a lab note flagged
  `conflict_with: <canonical id>`, and a validator task is queued. Known precedent: the
  Phase-2 staged-trigger soft-pull observation vs the fresh-client adjudication — resolved by
  scoping (adaptive-threshold caveat lives inside the canonical trigger entry).

Known standing scope notes (not conflicts): batch-2a matrix rows carry `trace-single-pass`
(environment-trust doctrine, plan banner 2026-06-12 / commit `71da330`); double-press
boundary-EDGE inclusivity is MOOT under the human-food tolerance doctrine (~10–15 ms practical
equality) while the epoch difference itself stays product-relevant.

## Seeding history

- **2026-06-12 (session 9):** initial seed from gated findings — `findings/jsm_lane_behavior.md`,
  `findings/steam_lane_behavior.md` (incl. Phase-4 batch 1/1b/2a pins), `vdf/translation_audit.md`
  (section-level hypothesis pointers; row-level JSONL ingestion deliberately deferred — the audit
  file itself remains the readable source of unverified rows).
