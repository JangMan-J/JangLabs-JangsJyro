#!/usr/bin/env python3
"""Unit tests for compare_lanes.py.

Two test classes:
  TestComparatorUnit  — pure unit tests against synthetic normalized streams.
  TestGateB           — known-answer Gate B test: loads the real Phase-2 raw
                        captures, normalizes them, and asserts the verdict table
                        from findings/steam_lane_behavior.md.

Run: python3 -m unittest test_compare_lanes -v
"""
import json
import unittest
from pathlib import Path

import normalize_capture as nc
import compare_lanes as cl

# ---------------------------------------------------------------------------
# Paths to Phase-2 run dirs (relative to this file's location = tools/)
# ---------------------------------------------------------------------------
_TOOLS_DIR = Path(__file__).resolve().parent
_GAMEPAD_DIR = _TOOLS_DIR.parent
_JSM_RUN = _GAMEPAD_DIR / "runs" / "20260602T145517Z-phase2-jsm-quickwins"
_STEAM_RUN = _GAMEPAD_DIR / "runs" / "20260611T124018Z-phase2-steam-quickwins"
_JSM_MANIFEST = _JSM_RUN / "run-manifest.json"
_STEAM_MANIFEST = _STEAM_RUN / "run-manifest.json"

# JSM digital slice is in the phase1 run (separate from phase2 JSM).
_JSM_DIGITAL_RUN = _GAMEPAD_DIR / "runs" / "20260602T144140Z-phase1-jsm-synthetic-spike"
_JSM_DIGITAL_CAPTURE = _JSM_DIGITAL_RUN / "capture.jsonl"
_STEAM_DIGITAL_CAPTURE = _STEAM_RUN / "digital-retest.xi2.jsonl"


def _load_norm(path: Path, plane: str = "auto") -> dict:
    with open(path) as f:
        lines = f.readlines()
    return nc.normalize(lines, plane=plane)


# ---------------------------------------------------------------------------
# Unit test helpers — synthetic streams
# ---------------------------------------------------------------------------

def _mk_norm(plane, events, presses=None, rel_totals=None):
    return {
        "schema_version": "1",
        "plane": plane,
        "n_raw": len(events),
        "t0_epoch": 0.0,
        "events": events,
        "summary": {
            "presses": presses or {},
            "rel_totals": rel_totals or {},
        },
    }


def _press(kind, name, t_ms, dur_ms):
    return {"kind": kind, "name": name, "t_ms": t_ms, "dur_ms": dur_ms}


# ---------------------------------------------------------------------------
# Unit tests (synthetic streams, no file I/O)
# ---------------------------------------------------------------------------

class TestComparatorUnit(unittest.TestCase):

    # ---- digital — identity case (same key name on both sides) ----

    def test_digital_exact(self):
        # Phase-9 production case: both lanes emit the same key name
        jsm = _mk_norm("evdev", [_press("key", "SPACE", 0, 50), _press("key", "SPACE", 500, 50)])
        stm = _mk_norm("evdev", [_press("key", "SPACE", 0, 55), _press("key", "SPACE", 600, 55)])
        _, cls = cl.compare("digital", jsm, stm)
        self.assertEqual(cls["verdict"], "exact")

    def test_digital_different_counts_both_ok(self):
        # Different stimulus counts per lane (different sessions) — both structurally correct.
        jsm = _mk_norm("evdev", [_press("key", "SPACE", 0, 50)])
        stm = _mk_norm("evdev", [_press("key", "SPACE", 0, 55), _press("key", "SPACE", 600, 55),
                                  _press("key", "SPACE", 1200, 55)])
        _, cls = cl.compare("digital", jsm, stm)
        self.assertEqual(cls["verdict"], "exact")

    def test_digital_no_jsm_presses_fails(self):
        jsm = _mk_norm("evdev", [])
        stm = _mk_norm("evdev", [_press("key", "SPACE", 0, 55)])
        _, cls = cl.compare("digital", jsm, stm)
        self.assertNotEqual(cls["verdict"], "exact")

    def test_digital_extra_key_fails(self):
        # Second key in JSM stream means it's not a clean single-key binding
        jsm = _mk_norm("evdev", [_press("key", "SPACE", 0, 50), _press("key", "ENTER", 500, 50)])
        stm = _mk_norm("evdev", [_press("key", "SPACE", 0, 55)])
        _, cls = cl.compare("digital", jsm, stm)
        self.assertNotEqual(cls["verdict"], "exact")

    # ---- digital — cross-lane roles (Phase-2 characterization case) ----

    def test_digital_exact_with_roles(self):
        # JSM emits SPACE; Steam emits F9 — same mechanic, aligned by role
        jsm = _mk_norm("evdev", [_press("key", "SPACE", 0, 50)])
        stm = _mk_norm("xi2",  [_press("key", "F9",    0, 55)])
        _, cls = cl.compare("digital", jsm, stm,
                             jsm_roles={"digital": "SPACE"},
                             steam_roles={"digital": "F9"})
        self.assertEqual(cls["verdict"], "exact")

    # ---- taphold — identity case ----

    def test_taphold_exact(self):
        # Both lanes emit the same key names (Phase-9 case)
        jsm = _mk_norm("evdev", [_press("key", "A", 0, 44), _press("key", "B", 850, 299)])
        stm = _mk_norm("evdev", [_press("key", "A", 0, 67), _press("key", "B", 1000, 107)])
        _, cls = cl.compare("taphold", jsm, stm,
                             jsm_roles={"tap": "A", "hold": "B"},
                             steam_roles={"tap": "A", "hold": "B"})
        self.assertEqual(cls["verdict"], "exact")

    def test_taphold_exact_cross_lane_roles(self):
        # JSM: A (tap), B (hold); Steam: F10 (tap), F11 (hold) — role-aligned
        jsm = _mk_norm("evdev", [_press("key", "A", 0, 44), _press("key", "B", 850, 299)])
        stm = _mk_norm("xi2",  [_press("key", "F10", 0, 67), _press("key", "F11", 1000, 107)])
        _, cls = cl.compare("taphold", jsm, stm,
                             jsm_roles={"tap": "A", "hold": "B"},
                             steam_roles={"tap": "F10", "hold": "F11"})
        self.assertEqual(cls["verdict"], "exact")

    def test_taphold_wrong_key_count(self):
        # Only tap present, no hold in JSM
        jsm = _mk_norm("evdev", [_press("key", "A", 0, 44)])
        stm = _mk_norm("xi2",  [_press("key", "F10", 0, 67), _press("key", "F11", 1000, 107)])
        _, cls = cl.compare("taphold", jsm, stm,
                             jsm_roles={"tap": "A"},
                             steam_roles={"tap": "F10", "hold": "F11"})
        self.assertNotEqual(cls["verdict"], "exact")

    # ---- doublepress ----

    def test_doublepress_bounded(self):
        # JSM base role: 2 presses (1st press of pair + lone); Steam base: 1 press.
        # The delta is count-differs (base: jsm=2, steam=1) — jsm fires extra base press.
        jsm = _mk_norm("evdev", [_press("key", "B", 0, 61), _press("key", "B", 560, 59),
                                  _press("key", "X", 610, 50)])
        stm = _mk_norm("xi2",  [_press("key", "F12", 0, 100), _press("key", "F7", 200, 100)])
        delta, cls = cl.compare("doublepress", jsm, stm,
                                  jsm_roles={"base": "B", "double": "X"},
                                  steam_roles={"base": "F12", "double": "F7"})
        self.assertEqual(cls["verdict"], "bounded_approximation")
        # base role should have count-differs with jsm > steam (the extra JSM base press)
        base_delta = [e for e in delta["entries"]
                      if e["name"] == "base" and e["delta_type"] == "count-differs"
                      and e.get("jsm_value", 0) > e.get("steam_value", 0)]
        self.assertTrue(len(base_delta) > 0,
                        f"Expected count-differs on base role (jsm>steam), got: {delta['entries']}")

    def test_doublepress_equal_counts_flags_it(self):
        jsm = _mk_norm("evdev", [_press("key", "B", 0, 61), _press("key", "X", 300, 50)])
        stm = _mk_norm("xi2",  [_press("key", "F12", 0, 100), _press("key", "F7", 200, 100)])
        delta, cls = cl.compare("doublepress", jsm, stm,
                                  jsm_roles={"base": "B", "double": "X"},
                                  steam_roles={"base": "F12", "double": "F7"})
        # Both have 1 each — no jsm-only delta, but verdict should still reflect no anomaly
        # (exact here since counts match; the bounded_approximation comes from the jsm-only entry)
        self.assertEqual(len([e for e in delta["entries"] if e["delta_type"] == "jsm-only"]), 0)

    # ---- chord ----

    def test_chord_exact(self):
        jsm = _mk_norm("evdev", [_press("key", "B", 0, 119), _press("key", "G", 799, 121)])
        stm = _mk_norm("xi2",  [_press("key", "F6", 0, 100), _press("key", "F8", 800, 110)])
        _, cls = cl.compare("chord", jsm, stm,
                             jsm_roles={"base": "B", "chord": "G"},
                             steam_roles={"base": "F6", "chord": "F8"})
        self.assertEqual(cls["verdict"], "exact")

    def test_chord_member_leak_detected(self):
        # Steam has chord + base; JSM has only chord output (no base leak)
        jsm = _mk_norm("evdev", [_press("key", "G", 0, 119)])
        stm = _mk_norm("xi2",  [_press("key", "F6", 0, 100), _press("key", "F8", 800, 110)])
        _, cls = cl.compare("chord", jsm, stm,
                             jsm_roles={"chord": "G"},
                             steam_roles={"base": "F6", "chord": "F8"})
        self.assertNotEqual(cls["verdict"], "exact")

    # ---- simpress ----

    def test_simpress_degraded_steam_leaks(self):
        # JSM: Q only; Steam: Q + LSHIFT (member binding leaks after namespace fold)
        jsm = _mk_norm("evdev", [_press("key", "Q", 0, 297)])
        stm = _mk_norm("xi2",  [_press("key", "LSHIFT", 0, 350),
                                 _press("key", "Q", 100, 200)])
        delta, cls = cl.compare("simpress", jsm, stm,
                                  jsm_roles={"chord": "Q"},
                                  steam_roles={"chord": "Q", "member_l": "LSHIFT"})
        self.assertEqual(cls["verdict"], "degraded_approximation")
        steam_only = [e for e in delta["entries"] if e["delta_type"] == "steam-only"]
        self.assertTrue(len(steam_only) > 0)

    def test_simpress_jsm_sticky_state_flagged(self):
        # JSM emits Q twice (sticky state); Steam emits Q + LSHIFT
        jsm = _mk_norm("evdev", [_press("key", "Q", 0, 297), _press("key", "Q", 952, 146)])
        stm = _mk_norm("xi2",  [_press("key", "LSHIFT", 0, 350),
                                 _press("key", "Q", 100, 200)])
        delta, cls = cl.compare("simpress", jsm, stm,
                                  jsm_roles={"chord": "Q"},
                                  steam_roles={"chord": "Q", "member_l": "LSHIFT"})
        self.assertEqual(cls["verdict"], "degraded_approximation")
        # chord role: JSM has 2 presses, Steam has 1 → jsm-only count-differs
        chord_delta = [e for e in delta["entries"] if e["name"] == "chord"]
        self.assertTrue(len(chord_delta) > 0,
                        f"Expected chord delta entry for sticky state, got: {delta['entries']}")

    # ---- trigfull ----

    def test_trigfull_exact_staged(self):
        jsm = _mk_norm("evdev", [_press("mousebtn", "MOUSE_RIGHT", 0, 906),
                                  _press("key", "LSHIFT", 452, 451)])
        stm = _mk_norm("xi2",  [_press("key", "F3", 0, 900),
                                 _press("key", "F4", 400, 450)])
        _, cls = cl.compare("trigfull", jsm, stm,
                             jsm_roles={"soft": "MOUSE_RIGHT", "full": "LSHIFT"},
                             steam_roles={"soft": "F3", "full": "F4"})
        self.assertEqual(cls["verdict"], "exact")

    def test_trigfull_missing_soft_on_steam(self):
        jsm = _mk_norm("evdev", [_press("mousebtn", "MOUSE_RIGHT", 0, 906),
                                  _press("key", "LSHIFT", 452, 451)])
        stm = _mk_norm("xi2",  [_press("key", "F4", 0, 450)])  # only full
        _, cls = cl.compare("trigfull", jsm, stm,
                             jsm_roles={"soft": "MOUSE_RIGHT", "full": "LSHIFT"},
                             steam_roles={"full": "F4"})
        self.assertNotEqual(cls["verdict"], "exact")

    # ---- schema conformance ----

    def test_outputs_conform_to_schemas(self):
        from validate_artifacts import validate_delta, validate_classification, ValidationError
        jsm = _mk_norm("evdev", [_press("key", "A", 0, 44), _press("key", "B", 850, 299)])
        stm = _mk_norm("xi2",  [_press("key", "F10", 0, 67), _press("key", "F11", 1000, 107)])
        delta, cls = cl.compare("taphold", jsm, stm,
                                  jsm_roles={"tap": "A", "hold": "B"},
                                  steam_roles={"tap": "F10", "hold": "F11"})
        try:
            validate_delta(delta)
            validate_classification(cls)
        except ValidationError as e:
            self.fail(f"Schema validation failed: {e}")


# ---------------------------------------------------------------------------
# Gate B fixture table
#
# Source of truth: findings/steam_lane_behavior.md (§ Phase-2 verdict table).
# Each entry is: mechanic -> (expected_verdict, note)
#
# INVARIANT: never change the expected verdict here to make a test pass.
# A mismatch means either (a) a comparator bug in compare_lanes.py — fix that,
# or (b) a findings error — escalate to team-lead for adjudication.
# ---------------------------------------------------------------------------
_GATE_B_EXPECTED = {
    # mechanic           expected verdict         source note (findings/steam_lane_behavior.md)
    "digital":          ("exact",                 "1:1 press model — no structural delta"),
    "taphold":          ("exact",                 "same tap/hold model both lanes; threshold differs but model matches"),
    "doublepress":      ("bounded_approximation", "JSM fires base on 1st press of double pair; Steam suppresses it"),
    "chord":            ("exact",                 "modifier-held chord overrides base; modifier itself silent — both lanes"),
    "simpress":         ("degraded_approximation","Steam leaks member binding (LSHIFT); JSM sticky-state bug (Q×2)"),
    "trigfull":         ("exact",                 "staged pull: soft stays held under full — both lanes (NO_SKIP model)"),
    "stickwasd":        ("exact",                 "directional held while tilted past deadzone — both lanes"),
}
# holdtimeglobal: JSM-lane-only finding (bounded_approximation, gotcha X.2).
# Excluded from Gate B — Gate B requires both lanes present in Phase-2 data.


# ---------------------------------------------------------------------------
# Gate B: known-answer test on real Phase-2 captures
# ---------------------------------------------------------------------------

@unittest.skipUnless(
    (_JSM_RUN / "taphold.capture.jsonl").exists() and
    (_STEAM_RUN / "taphold.xi2.jsonl").exists(),
    "Phase-2 raw capture files not present — skip Gate B"
)
class TestGateB(unittest.TestCase):
    """Gate B: reproduce the Phase-2 verdict table from findings/steam_lane_behavior.md.

    INVARIANT: if a test fails, the cause is either:
      (a) a comparator bug — fix compare_lanes.py, OR
      (b) a findings error — escalate to team-lead; NEVER adjust _GATE_B_EXPECTED to pass.

    Failure messages are formatted as:
      Gate B [mechanic]: got '<actual>' expected '<expected>' | jsm=... steam=... delta=...
    so team-lead can adjudicate comparator-bug vs findings-error at a glance.
    """

    def _compare_slice(self, slice_name,
                       jsm_capture_file=None, steam_capture_file=None,
                       jsm_manifest=None, steam_manifest=None):
        jsm_file = jsm_capture_file or (_JSM_RUN / f"{slice_name}.capture.jsonl")
        stm_file = steam_capture_file or (_STEAM_RUN / f"{slice_name}.xi2.jsonl")
        jsm_mf = jsm_manifest or _JSM_MANIFEST
        stm_mf = steam_manifest or _STEAM_MANIFEST

        jsm_norm = _load_norm(jsm_file, plane="evdev")
        stm_norm = _load_norm(stm_file, plane="xi2")

        # Load roles from manifests (empty dict = identity default when no key_roles entry)
        jsm_roles = cl.roles_from_manifest(jsm_mf, slice_name, "jsm") or None
        stm_roles = cl.roles_from_manifest(stm_mf, slice_name, "steam") or None

        return cl.compare(slice_name, jsm_norm, stm_norm,
                          jsm_roles=jsm_roles, steam_roles=stm_roles,
                          jsm_run=str(jsm_mf.parent),
                          steam_run=str(stm_mf.parent))

    def _assert_verdict(self, mechanic, delta, cls):
        expected, _ = _GATE_B_EXPECTED[mechanic]
        actual = cls["verdict"]
        self.assertEqual(
            actual, expected,
            f"Gate B [{mechanic}]: got '{actual}' expected '{expected}' | "
            f"jsm={cls['jsm_summary']} steam={cls['steam_summary']} "
            f"delta={delta['entries']}"
        )

    def test_digital_exact(self):
        """digital: exact — 1:1 press model, no structural delta."""
        delta, cls = self._compare_slice(
            "digital",
            jsm_capture_file=_JSM_DIGITAL_CAPTURE,
            steam_capture_file=_STEAM_DIGITAL_CAPTURE,
            jsm_manifest=_JSM_DIGITAL_RUN / "run-manifest.json",
            steam_manifest=_STEAM_MANIFEST,
        )
        self._assert_verdict("digital", delta, cls)

    def test_taphold_exact(self):
        """taphold: exact — same tap/hold model both lanes."""
        delta, cls = self._compare_slice("taphold")
        self._assert_verdict("taphold", delta, cls)

    def test_doublepress_bounded(self):
        """doublepress: bounded_approximation — JSM fires base on 1st press; Steam suppresses."""
        delta, cls = self._compare_slice("doublepress")
        self._assert_verdict("doublepress", delta, cls)
        # Structural check: base role must have count-differs with jsm > steam
        # (the extra base press that JSM fires on the 1st press of the double pair)
        base_delta = [e for e in delta["entries"]
                      if e["name"] == "base"
                      and e["delta_type"] in ("jsm-only", "count-differs")
                      and e.get("jsm_value", 0) > e.get("steam_value", 0)]
        self.assertTrue(len(base_delta) > 0,
            f"Gate B [doublepress]: expected base-role count delta (jsm>steam) "
            f"but got delta={delta['entries']}")

    def test_chord_exact(self):
        """chord: exact — modifier-held chord overrides base, modifier itself silent."""
        delta, cls = self._compare_slice("chord")
        self._assert_verdict("chord", delta, cls)

    def test_simpress_degraded(self):
        """simpress: degraded_approximation — Steam leaks member binding; JSM sticky-state bug."""
        delta, cls = self._compare_slice("simpress")
        self._assert_verdict("simpress", delta, cls)
        # Structural check: steam-only entry for member binding leak (LSHIFT)
        steam_only = [e for e in delta["entries"] if e["delta_type"] == "steam-only"]
        self.assertTrue(len(steam_only) > 0,
            f"Gate B [simpress]: expected steam-only delta entry (member binding leak) "
            f"but got delta={delta['entries']}")
        # Structural check: count/jsm-only entry for sticky-state bug (Q×2 vs Q×1)
        sticky_delta = [e for e in delta["entries"]
                        if e["delta_type"] in ("jsm-only", "count-differs")
                        and e["name"] in ("chord", "Q")]
        self.assertTrue(len(sticky_delta) > 0,
            f"Gate B [simpress]: expected chord-role count delta (sticky-state Q×2) "
            f"but got delta={delta['entries']}")

    def test_trigfull_staged_exact(self):
        """trigfull: exact — soft stays held under full (staged pull, NO_SKIP model)."""
        delta, cls = self._compare_slice("trigfull")
        self._assert_verdict("trigfull", delta, cls)

    def test_stickwasd_exact(self):
        """stickwasd: exact — directional held while tilted past deadzone, both lanes."""
        delta, cls = self._compare_slice("stickwasd")
        self._assert_verdict("stickwasd", delta, cls)

    def test_delta_and_classification_conform_to_schemas(self):
        """All comparator outputs for Phase-2 slices must be schema-valid."""
        from validate_artifacts import validate_delta, validate_classification, ValidationError
        for slice_name in ["taphold", "doublepress", "chord", "simpress", "trigfull"]:
            with self.subTest(slice=slice_name):
                jsm_file = _JSM_RUN / f"{slice_name}.capture.jsonl"
                stm_file = _STEAM_RUN / f"{slice_name}.xi2.jsonl"
                if not jsm_file.exists() or not stm_file.exists():
                    self.skipTest(f"Capture files missing for {slice_name}")
                delta, cls = self._compare_slice(slice_name)
                try:
                    validate_delta(delta)
                    validate_classification(cls)
                except ValidationError as e:
                    self.fail(f"Gate B [{slice_name}]: schema validation failed: {e}")


if __name__ == "__main__":
    unittest.main()
