#!/usr/bin/env python3
"""Unit tests for validate_artifacts.py — pure, deterministic, stdlib only.
Run: python3 -m unittest test_validate_artifacts -v"""
import json
import os
import tempfile
import unittest
from pathlib import Path

import validate_artifacts as va


# ---------------------------------------------------------------------------
# Minimal valid fixture factories
# ---------------------------------------------------------------------------

def _manifest(overrides=None):
    m = {
        "schema_version": "1",
        "run_id": "20260602T145517Z-phase2-jsm-quickwins",
        "date": "2026-06-02",
        "phase": "phase2-jsm",
        "host": "CachyOS/Wayland/KDE/NVIDIA",
        "jsm_commit": "68dcb97",
        "steam_client": None,
        "lanes": ["jsm"],
        "slices": [
            {
                "slice": "taphold",
                "verdict": "exact",
                "jsm_capture": "taphold.capture.jsonl",
                "steam_capture": None,
                "injector_log": "taphold.injector.log",
                "notes": None,
            }
        ],
        "notes": None,
    }
    if overrides:
        m.update(overrides)
    return m


def _norm_stream(overrides=None):
    s = {
        "schema_version": "1",
        "plane": "evdev",
        "n_raw": 4,
        "t0_epoch": 1780412148.7545,
        "events": [
            {"kind": "key", "name": "A", "t_ms": 0.0, "dur_ms": 44.1}
        ],
        "summary": {"presses": {"A": 1}, "rel_totals": {}},
    }
    if overrides:
        s.update(overrides)
    return s


def _classification(overrides=None):
    c = {
        "schema_version": "1",
        "mechanic": "taphold",
        "verdict": "exact",
        "loss_text": None,
        "jsm_summary": None,
        "steam_summary": None,
        "evidence_refs": ["runs/foo/taphold.capture.jsonl"],
        "notes": None,
    }
    if overrides:
        c.update(overrides)
    return c


def _delta(overrides=None):
    d = {
        "schema_version": "1",
        "mechanic": "doublepress",
        "jsm_run": "runs/20260602T145517Z-phase2-jsm-quickwins",
        "steam_run": "runs/20260611T124018Z-phase2-steam-quickwins",
        "entries": [
            {
                "kind": "key",
                "name": "B",
                "delta_type": "jsm-only",
                "jsm_value": 1,
                "steam_value": 0,
                "note": "JSM fires base on first press of double pair",
            }
        ],
    }
    if overrides:
        d.update(overrides)
    return d


def _kb_note(overrides=None):
    n = {
        "schema_version": "1",
        "id": "taphold-jsm-150ms",
        "date": "2026-06-02",
        "source": "trace",
        "mechanic": "taphold",
        "lane": "jsm",
        "text": "HOLD_PRESS_TIME default 150ms confirmed by trace.",
        "evidence_refs": [],
        "promoted": False,
    }
    if overrides:
        n.update(overrides)
    return n


# ---------------------------------------------------------------------------
# run-manifest tests
# ---------------------------------------------------------------------------

class TestRunManifest(unittest.TestCase):
    def _ok(self, **kw):
        va.validate_run_manifest(_manifest(kw))

    def _fail(self, **kw):
        with self.assertRaises(va.ValidationError):
            va.validate_run_manifest(_manifest(kw))

    def test_valid_minimal(self):
        self._ok()

    def test_wrong_schema_version(self):
        self._fail(schema_version="2")

    def test_missing_run_id(self):
        m = _manifest()
        del m["run_id"]
        with self.assertRaises(va.ValidationError):
            va.validate_run_manifest(m)

    def test_bad_run_id_pattern(self):
        self._fail(run_id="not-a-timestamp-slug")

    def test_bad_date_pattern(self):
        self._fail(date="06-02-2026")

    def test_empty_lanes(self):
        self._fail(lanes=[])

    def test_bad_lane_value(self):
        self._fail(lanes=["xboxlane"])

    def test_bad_verdict_in_slice(self):
        m = _manifest()
        m["slices"][0]["verdict"] = "WRONG"
        with self.assertRaises(va.ValidationError):
            va.validate_run_manifest(m)

    def test_null_verdict_ok(self):
        m = _manifest()
        m["slices"][0]["verdict"] = None
        va.validate_run_manifest(m)

    def test_blocked_verdict_ok(self):
        m = _manifest()
        m["slices"][0]["verdict"] = "blocked"
        va.validate_run_manifest(m)

    def test_multiple_lanes(self):
        self._ok(lanes=["jsm", "steam"])

    def test_empty_slices_ok(self):
        self._ok(slices=[])


# ---------------------------------------------------------------------------
# normalized-stream tests
# ---------------------------------------------------------------------------

class TestNormalizedStream(unittest.TestCase):
    def test_valid(self):
        va.validate_normalized_stream(_norm_stream())

    def test_wrong_schema_version(self):
        with self.assertRaises(va.ValidationError):
            va.validate_normalized_stream(_norm_stream({"schema_version": "0"}))

    def test_bad_plane(self):
        with self.assertRaises(va.ValidationError):
            va.validate_normalized_stream(_norm_stream({"plane": "xtest"}))

    def test_xi2_plane_ok(self):
        va.validate_normalized_stream(_norm_stream({"plane": "xi2"}))

    def test_bad_event_kind(self):
        s = _norm_stream()
        s["events"][0]["kind"] = "gamepad"
        with self.assertRaises(va.ValidationError):
            va.validate_normalized_stream(s)

    def test_valid_note(self):
        s = _norm_stream()
        s["events"][0]["note"] = "still-held-at-end"
        va.validate_normalized_stream(s)

    def test_bad_note(self):
        s = _norm_stream()
        s["events"][0]["note"] = "unknown-note"
        with self.assertRaises(va.ValidationError):
            va.validate_normalized_stream(s)

    def test_empty_events_ok(self):
        va.validate_normalized_stream(_norm_stream({"n_raw": 0, "events": []}))


# ---------------------------------------------------------------------------
# classification tests
# ---------------------------------------------------------------------------

class TestClassification(unittest.TestCase):
    def test_valid(self):
        va.validate_classification(_classification())

    def test_bad_verdict(self):
        with self.assertRaises(va.ValidationError):
            va.validate_classification(_classification({"verdict": "kinda-ok"}))

    def test_all_valid_verdicts(self):
        for v in ["exact", "bounded_approximation", "degraded_approximation",
                  "unsupported_omitted", "requires_user_choice"]:
            va.validate_classification(_classification({"verdict": v}))

    def test_missing_evidence_refs(self):
        c = _classification()
        del c["evidence_refs"]
        with self.assertRaises(va.ValidationError):
            va.validate_classification(c)


# ---------------------------------------------------------------------------
# delta tests
# ---------------------------------------------------------------------------

class TestDelta(unittest.TestCase):
    def test_valid(self):
        va.validate_delta(_delta())

    def test_bad_delta_type(self):
        d = _delta()
        d["entries"][0]["delta_type"] = "wrong"
        with self.assertRaises(va.ValidationError):
            va.validate_delta(d)

    def test_empty_entries_ok(self):
        va.validate_delta(_delta({"entries": []}))


# ---------------------------------------------------------------------------
# kb-note tests
# ---------------------------------------------------------------------------

class TestKbNote(unittest.TestCase):
    def test_valid(self):
        va.validate_kb_note(_kb_note())

    def test_bad_source(self):
        with self.assertRaises(va.ValidationError):
            va.validate_kb_note(_kb_note({"source": "hearsay"}))

    def test_bad_lane(self):
        with self.assertRaises(va.ValidationError):
            va.validate_kb_note(_kb_note({"lane": "windows"}))

    def test_bad_date(self):
        with self.assertRaises(va.ValidationError):
            va.validate_kb_note(_kb_note({"date": "June 2 2026"}))


# ---------------------------------------------------------------------------
# validate_run_dir integration tests (using tempfile)
# ---------------------------------------------------------------------------

class TestValidateRunDir(unittest.TestCase):
    def _make_run(self, manifest, extra_files=None):
        """Create a temp run dir with run-manifest.json + optional extra files."""
        d = tempfile.mkdtemp(prefix="jsmlab-test-run-")
        with open(os.path.join(d, "run-manifest.json"), "w") as f:
            json.dump(manifest, f)
        if extra_files:
            for name, data in extra_files.items():
                with open(os.path.join(d, name), "w") as f:
                    json.dump(data, f)
        return d

    def test_valid_run_dir_passes(self):
        d = self._make_run(_manifest())
        results = va.validate_run_dir(d)
        errors = [(p, e) for p, e in results if e]
        self.assertEqual(errors, [], f"Unexpected errors: {errors}")

    def test_missing_manifest_fails(self):
        d = tempfile.mkdtemp(prefix="jsmlab-test-run-")
        results = va.validate_run_dir(d)
        self.assertTrue(any(e for _, e in results))

    def test_invalid_manifest_fails(self):
        bad = _manifest({"schema_version": "99"})
        d = self._make_run(bad)
        results = va.validate_run_dir(d)
        self.assertTrue(any(e for _, e in results))

    def test_valid_normalized_stream_detected(self):
        d = self._make_run(_manifest(),
                           extra_files={"taphold.normalized.json": _norm_stream()})
        results = va.validate_run_dir(d)
        errors = [(p, e) for p, e in results if e]
        self.assertEqual(errors, [])

    def test_invalid_normalized_stream_caught(self):
        bad = _norm_stream({"plane": "bad"})
        d = self._make_run(_manifest(),
                           extra_files={"taphold.normalized.json": bad})
        results = va.validate_run_dir(d)
        self.assertTrue(any(e for _, e in results))

    def test_valid_classification_detected(self):
        d = self._make_run(_manifest(),
                           extra_files={"taphold.classification.json": _classification()})
        results = va.validate_run_dir(d)
        errors = [(p, e) for p, e in results if e]
        self.assertEqual(errors, [])

    def test_valid_delta_detected(self):
        d = self._make_run(_manifest(),
                           extra_files={"taphold.delta.json": _delta()})
        results = va.validate_run_dir(d)
        errors = [(p, e) for p, e in results if e]
        self.assertEqual(errors, [])

    def test_unknown_json_files_ignored(self):
        d = self._make_run(_manifest(),
                           extra_files={"some-other-data.json": {"foo": "bar"}})
        results = va.validate_run_dir(d)
        names = [os.path.basename(p) for p, _ in results]
        self.assertNotIn("some-other-data.json", names)


if __name__ == "__main__":
    unittest.main()
