#!/usr/bin/env python3
"""validate_artifacts.py — validate a run dir against the Phase-3 artifact schemas.

Checks `run-manifest.json` (required) and any normalized-stream, delta, and
classification JSON files present in a runs/<slug>/ directory.

No external dependencies — the schemas are codified directly in the validators
below (pure stdlib).  This keeps the tool in sync with the schemas in
`gamepad/schemas/` without requiring `jsonschema` to be installed.

Usage
  validate_artifacts.py RUNS_DIR [RUNS_DIR ...]
      Validate one or more run directories; exit 0 iff all pass.

  validate_artifacts.py --all
      Find and validate all runs/ dirs under the repo's gamepad/ subtree.

Exit codes: 0 = all pass, 1 = one or more failures.

Tests: tools/test_validate_artifacts.py (stdlib unittest, no deps).
"""
import argparse
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

_VERDICT_ENUM = {
    "exact", "bounded_approximation", "degraded_approximation",
    "unsupported_omitted", "requires_user_choice", "blocked",
}
_VERDICT_OR_NULL = _VERDICT_ENUM | {None}
_LANE_ENUM = {"jsm", "steam"}
_PLANES = {"evdev", "xi2"}
_EVENT_KINDS = {"key", "mousebtn", "button", "rel", "other"}
_NOTE_ENUM = {"up-only", "still-held-at-end", "noise-stimulus-gap", "deduped-raw"}
_SOURCE_ENUM = {"trace", "source-review", "doc", "static-audit", "inferred"}
_DELTA_TYPES = {"jsm-only", "steam-only", "dur-differs", "count-differs", "order-differs", "rel-total-differs"}


class ValidationError(Exception):
    pass


def _require(d, key, path):
    if key not in d:
        raise ValidationError(f"{path}: missing required key '{key}'")
    return d[key]


def _check_type(val, types, path):
    if not isinstance(val, types):
        raise ValidationError(f"{path}: expected {types}, got {type(val).__name__} ({val!r})")


def _check_enum(val, allowed, path):
    if val not in allowed:
        raise ValidationError(f"{path}: value {val!r} not in allowed set {sorted(str(x) for x in allowed)}")


def _check_string_pattern(val, pattern, path):
    import re
    if not re.match(pattern, val):
        raise ValidationError(f"{path}: value {val!r} does not match pattern {pattern!r}")


# ---------------------------------------------------------------------------
# Per-schema validators
# ---------------------------------------------------------------------------

def validate_run_manifest(data, path="run-manifest.json"):
    """Validate a run-manifest dict. Raises ValidationError on failure."""
    _check_type(data, dict, path)
    sv = _require(data, "schema_version", path)
    if sv != "1":
        raise ValidationError(f"{path}: schema_version must be '1', got {sv!r}")
    run_id = _require(data, "run_id", path)
    _check_type(run_id, str, f"{path}.run_id")
    _check_string_pattern(run_id, r"^\d{8}T\d{6}Z-.+$", f"{path}.run_id")
    date = _require(data, "date", path)
    _check_type(date, str, f"{path}.date")
    _check_string_pattern(date, r"^\d{4}-\d{2}-\d{2}$", f"{path}.date")
    _require(data, "phase", path)
    _check_type(data["phase"], str, f"{path}.phase")
    _require(data, "host", path)
    _check_type(data["host"], str, f"{path}.host")
    lanes = _require(data, "lanes", path)
    _check_type(lanes, list, f"{path}.lanes")
    if not lanes:
        raise ValidationError(f"{path}.lanes: must have at least one lane")
    for i, lane in enumerate(lanes):
        _check_enum(lane, _LANE_ENUM, f"{path}.lanes[{i}]")
    slices = _require(data, "slices", path)
    _check_type(slices, list, f"{path}.slices")
    for i, s in enumerate(slices):
        sp = f"{path}.slices[{i}]"
        _check_type(s, dict, sp)
        _require(s, "slice", sp)
        _check_type(s["slice"], str, f"{sp}.slice")
        verdict = _require(s, "verdict", sp)
        _check_enum(verdict, _VERDICT_OR_NULL, f"{sp}.verdict")
        for key in ("jsm_capture", "steam_capture", "injector_log", "notes"):
            if key in s and s[key] is not None:
                _check_type(s[key], str, f"{sp}.{key}")


def validate_normalized_stream(data, path="normalized-stream.json"):
    _check_type(data, dict, path)
    sv = _require(data, "schema_version", path)
    if sv != "1":
        raise ValidationError(f"{path}: schema_version must be '1', got {sv!r}")
    plane = _require(data, "plane", path)
    _check_enum(plane, _PLANES, f"{path}.plane")
    n_raw = _require(data, "n_raw", path)
    _check_type(n_raw, int, f"{path}.n_raw")
    events = _require(data, "events", path)
    _check_type(events, list, f"{path}.events")
    for i, ev in enumerate(events):
        ep = f"{path}.events[{i}]"
        _check_type(ev, dict, ep)
        _check_enum(_require(ev, "kind", ep), _EVENT_KINDS, f"{ep}.kind")
        _check_type(_require(ev, "name", ep), str, f"{ep}.name")
        t_ms = _require(ev, "t_ms", ep)
        _check_type(t_ms, (int, float), f"{ep}.t_ms")
        if "note" in ev and ev["note"] is not None:
            _check_enum(ev["note"], _NOTE_ENUM, f"{ep}.note")
    summary = _require(data, "summary", path)
    _check_type(summary, dict, f"{path}.summary")
    _require(summary, "presses", f"{path}.summary")
    _require(summary, "rel_totals", f"{path}.summary")


def validate_classification(data, path="classification.json"):
    _check_type(data, dict, path)
    sv = _require(data, "schema_version", path)
    if sv != "1":
        raise ValidationError(f"{path}: schema_version must be '1', got {sv!r}")
    _require(data, "mechanic", path)
    _check_type(data["mechanic"], str, f"{path}.mechanic")
    verdict = _require(data, "verdict", path)
    _check_enum(verdict, {v for v in _VERDICT_ENUM if v != "blocked"}, f"{path}.verdict")
    refs = _require(data, "evidence_refs", path)
    _check_type(refs, list, f"{path}.evidence_refs")
    for i, r in enumerate(refs):
        _check_type(r, str, f"{path}.evidence_refs[{i}]")


def validate_delta(data, path="delta.json"):
    _check_type(data, dict, path)
    sv = _require(data, "schema_version", path)
    if sv != "1":
        raise ValidationError(f"{path}: schema_version must be '1', got {sv!r}")
    _require(data, "mechanic", path)
    _require(data, "jsm_run", path)
    _require(data, "steam_run", path)
    entries = _require(data, "entries", path)
    _check_type(entries, list, f"{path}.entries")
    for i, e in enumerate(entries):
        ep = f"{path}.entries[{i}]"
        _check_type(e, dict, ep)
        _check_enum(_require(e, "kind", ep), _EVENT_KINDS, f"{ep}.kind")
        _check_type(_require(e, "name", ep), str, f"{ep}.name")
        _check_enum(_require(e, "delta_type", ep), _DELTA_TYPES, f"{ep}.delta_type")


def validate_kb_note(data, path="kb-note.json"):
    _check_type(data, dict, path)
    sv = _require(data, "schema_version", path)
    if sv != "1":
        raise ValidationError(f"{path}: schema_version must be '1', got {sv!r}")
    _require(data, "id", path)
    _require(data, "date", path)
    _check_string_pattern(data["date"], r"^\d{4}-\d{2}-\d{2}$", f"{path}.date")
    _check_enum(_require(data, "source", path), _SOURCE_ENUM, f"{path}.source")
    _require(data, "mechanic", path)
    _check_enum(_require(data, "lane", path), {"jsm", "steam", "both", "neither"}, f"{path}.lane")
    _check_type(_require(data, "text", path), str, f"{path}.text")


# ---------------------------------------------------------------------------
# Schema-type dispatch by filename suffix
# ---------------------------------------------------------------------------

def _infer_validator(filename):
    """Return (validator_fn, label) for a JSON filename, or None if unrecognized."""
    name = os.path.basename(filename).lower()
    if name == "run-manifest.json":
        return validate_run_manifest, "run-manifest"
    if name.endswith(".normalized.json"):
        return validate_normalized_stream, "normalized-stream"
    if name.endswith(".classification.json"):
        return validate_classification, "classification"
    if name.endswith(".delta.json"):
        return validate_delta, "delta"
    if name.endswith(".kb-note.json"):
        return validate_kb_note, "kb-note"
    return None


# ---------------------------------------------------------------------------
# Run-dir validation
# ---------------------------------------------------------------------------

def validate_run_dir(run_dir):
    """Validate all recognized JSON artifacts in run_dir. Returns list of (file, error_or_None)."""
    run_dir = Path(run_dir)
    results = []

    manifest_path = run_dir / "run-manifest.json"
    if not manifest_path.exists():
        results.append((str(manifest_path), "MISSING: run-manifest.json not found"))
        return results

    # Validate manifest first
    with open(manifest_path) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            results.append((str(manifest_path), f"JSON parse error: {e}"))
            return results
    try:
        validate_run_manifest(data, str(manifest_path))
        results.append((str(manifest_path), None))
    except ValidationError as e:
        results.append((str(manifest_path), str(e)))

    # Validate any other recognized artifact files
    for f in sorted(run_dir.glob("*.json")):
        if f.name == "run-manifest.json":
            continue
        entry = _infer_validator(f.name)
        if entry is None:
            continue
        validator, _ = entry
        with open(f) as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError as e:
                results.append((str(f), f"JSON parse error: {e}"))
                continue
        try:
            validator(data, str(f))
            results.append((str(f), None))
        except ValidationError as e:
            results.append((str(f), str(e)))

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _find_all_run_dirs(root):
    runs = Path(root) / "runs"
    if not runs.is_dir():
        return []
    return sorted(p for p in runs.iterdir() if p.is_dir())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="*", help="run directories to validate")
    ap.add_argument("--all", action="store_true",
                    help="find and validate all runs/ dirs under gamepad/")
    ap.add_argument("--gamepad-root", default=None,
                    help="path to gamepad/ (default: auto-detect from this script's location)")
    args = ap.parse_args(argv)

    if args.all:
        if args.gamepad_root:
            root = Path(args.gamepad_root)
        else:
            root = Path(__file__).resolve().parent.parent  # tools/../ = gamepad/
        dirs = _find_all_run_dirs(root)
        if not dirs:
            print("No runs/ directories found.", file=sys.stderr)
            return 1
    elif args.dirs:
        dirs = [Path(d) for d in args.dirs]
    else:
        ap.print_help()
        return 2

    total_files = 0
    total_errors = 0
    total_runs = 0
    run_errors = 0

    for run_dir in dirs:
        total_runs += 1
        results = validate_run_dir(run_dir)
        run_ok = all(err is None for _, err in results)
        if not run_ok:
            run_errors += 1
        run_label = f"  {run_dir.name}" if hasattr(run_dir, "name") else f"  {run_dir}"
        status = "OK" if run_ok else "FAIL"
        print(f"{status}  {run_dir}")
        for fpath, err in results:
            total_files += 1
            if err:
                total_errors += 1
                fname = os.path.basename(fpath)
                print(f"      FAIL  {fname}: {err}")
            else:
                fname = os.path.basename(fpath)
                print(f"      ok    {fname}")

    print(f"\n{'='*60}")
    print(f"Runs: {total_runs}  Files checked: {total_files}  "
          f"Errors: {total_errors}  Run dirs with errors: {run_errors}")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
