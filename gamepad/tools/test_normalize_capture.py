#!/usr/bin/env python3
"""Unit tests for normalize_capture.py — pure, deterministic, stdlib only (no
/dev/uinput, no JSM). Run: `python3 -m unittest test_normalize_capture -v`."""
import json
import unittest

import normalize_capture as nc


def cap(*rows):
    """rows: (t, dev, type, code, value) tuples -> jsonl lines."""
    return [json.dumps({"t": t, "dev": d, "type": ty, "code": c, "value": v})
            for (t, d, ty, c, v) in rows]


class TestCanon(unittest.TestCase):
    def test_keys(self):
        self.assertEqual(nc.canon("KEY_SPACE"), ("key", "SPACE"))
        self.assertEqual(nc.canon("KEY_LEFTSHIFT"), ("key", "LSHIFT"))  # namespace fold

    def test_mouse_buttons(self):
        self.assertEqual(nc.canon("BTN_LEFT"), ("mousebtn", "MOUSE_LEFT"))
        self.assertEqual(nc.canon("BTN_RIGHT"), ("mousebtn", "MOUSE_RIGHT"))

    def test_pad_button_passthrough(self):
        self.assertEqual(nc.canon("BTN_SOUTH"), ("button", "SOUTH"))

    def test_rel(self):
        self.assertEqual(nc.canon("REL_X"), ("rel", "MOUSE_DX"))
        self.assertEqual(nc.canon("REL_WHEEL"), ("rel", "WHEEL"))


class TestNormalize(unittest.TestCase):
    def test_press_pairing_and_duration(self):
        n = nc.normalize(cap(
            (100.0, "kbd", "KEY", "KEY_A", 1),
            (100.0, "kbd", "SYN", "SYN_REPORT", 0),
            (100.12, "kbd", "KEY", "KEY_A", 0),
        ))
        self.assertEqual(n["n_raw"], 2)  # SYN dropped
        self.assertEqual(len(n["events"]), 1)
        ev = n["events"][0]
        self.assertEqual((ev["kind"], ev["name"]), ("key", "A"))
        self.assertEqual(ev["t_ms"], 0.0)            # relative to first event
        self.assertAlmostEqual(ev["dur_ms"], 120.0, places=0)
        self.assertEqual(n["summary"]["presses"], {"A": 1})

    def test_relative_timestamps(self):
        n = nc.normalize(cap(
            (50.0, "m", "KEY", "BTN_LEFT", 1),
            (50.05, "m", "KEY", "BTN_LEFT", 0),
            (50.5, "k", "KEY", "KEY_B", 1),
            (50.6, "k", "KEY", "KEY_B", 0),
        ))
        self.assertEqual([e["t_ms"] for e in n["events"]], [0.0, 500.0])

    def test_up_only(self):
        n = nc.normalize(cap((10.0, "k", "KEY", "KEY_C", 0)))
        self.assertEqual(n["events"][0]["note"], "up-only")
        self.assertIsNone(n["events"][0]["dur_ms"])

    def test_still_held_at_end(self):
        n = nc.normalize(cap((10.0, "k", "KEY", "KEY_D", 1)))
        ev = n["events"][0]
        self.assertEqual(ev["note"], "still-held-at-end")
        self.assertIsNone(ev["dur_ms"])
        self.assertEqual(n["summary"]["presses"], {"D": 1})

    def test_rel_aggregation(self):
        n = nc.normalize(cap(
            (1.0, "m", "REL", "REL_X", 5),
            (1.0, "m", "REL", "REL_X", -2),
            (1.0, "m", "REL", "REL_WHEEL", 1),
        ))
        self.assertEqual(n["summary"]["rel_totals"], {"MOUSE_DX": 3, "WHEEL": 1})
        self.assertEqual(len(n["events"]), 3)

    def test_empty(self):
        n = nc.normalize([])
        self.assertEqual(n["n_raw"], 0)
        self.assertEqual(n["events"], [])

    def test_two_distinct_presses_counted(self):
        n = nc.normalize(cap(
            (0.0, "k", "KEY", "KEY_A", 1), (0.05, "k", "KEY", "KEY_A", 0),
            (0.5, "k", "KEY", "KEY_A", 1), (0.55, "k", "KEY", "KEY_A", 0),
        ))
        self.assertEqual(n["summary"]["presses"], {"A": 2})


def xi2_cap(*rows):
    """rows: (t, event, dev_id, dev, code, flag) -> jsonl lines."""
    return [json.dumps({"t": t, "event": ev, "dev_id": did,
                        "dev": dev, "code": code, "flag": flag})
            for (t, ev, did, dev, code, flag) in rows]


_SEAT_DEV = "xwayland-keyboard:10"
_MASTER_DEV = "Virtual core keyboard"
_SEAT_FLAG = "Xwayland-seat(XTEST/libei/phys)"
_MASTER_FLAG = "master"


class TestCanonNamespace(unittest.TestCase):
    """Canonical key namespace fold: both evdev and xi2 paths must speak one vocabulary."""

    # evdev: KEY_LEFTSHIFT -> LSHIFT (not LEFTSHIFT)
    def test_evdev_leftshift_folded(self):
        n = nc.normalize(cap(
            (1.0, "kbd", "KEY", "KEY_LEFTSHIFT", 1),
            (1.1, "kbd", "KEY", "KEY_LEFTSHIFT", 0),
        ))
        self.assertEqual(n["events"][0]["name"], "LSHIFT")
        self.assertIn("LSHIFT", n["summary"]["presses"])

    def test_evdev_rightshift_folded(self):
        n = nc.normalize(cap(
            (1.0, "kbd", "KEY", "KEY_RIGHTSHIFT", 1),
            (1.1, "kbd", "KEY", "KEY_RIGHTSHIFT", 0),
        ))
        self.assertEqual(n["events"][0]["name"], "RSHIFT")

    def test_evdev_leftctrl_folded(self):
        n = nc.normalize(cap(
            (1.0, "kbd", "KEY", "KEY_LEFTCTRL", 1),
            (1.1, "kbd", "KEY", "KEY_LEFTCTRL", 0),
        ))
        self.assertEqual(n["events"][0]["name"], "LCTRL")

    def test_evdev_leftalt_folded(self):
        n = nc.normalize(cap(
            (1.0, "kbd", "KEY", "KEY_LEFTALT", 1),
            (1.1, "kbd", "KEY", "KEY_LEFTALT", 0),
        ))
        self.assertEqual(n["events"][0]["name"], "LALT")

    # xi2: Shift_L -> LSHIFT; lowercase 'q' -> 'Q'
    def test_xi2_shift_l_folded(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "Shift_L", _SEAT_FLAG),
            (1.1, "KeyRelease", 9, _SEAT_DEV, "Shift_L", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["name"], "LSHIFT")
        self.assertIn("LSHIFT", n["summary"]["presses"])

    def test_xi2_shift_r_folded(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "Shift_R", _SEAT_FLAG),
            (1.1, "KeyRelease", 9, _SEAT_DEV, "Shift_R", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["name"], "RSHIFT")

    def test_xi2_ctrl_l_folded(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "Control_L", _SEAT_FLAG),
            (1.1, "KeyRelease", 9, _SEAT_DEV, "Control_L", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["name"], "LCTRL")

    def test_xi2_alt_l_folded(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "Alt_L", _SEAT_FLAG),
            (1.1, "KeyRelease", 9, _SEAT_DEV, "Alt_L", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["name"], "LALT")

    def test_xi2_lowercase_letter_upcased(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "q", _SEAT_FLAG),
            (1.1, "KeyRelease", 9, _SEAT_DEV, "q", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["name"], "Q")

    def test_xi2_lowercase_wasd_upcased(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "w", _SEAT_FLAG),
            (1.1, "KeyRelease", 9, _SEAT_DEV, "w", _SEAT_FLAG),
            (1.2, "KeyPress", 9, _SEAT_DEV, "a", _SEAT_FLAG),
            (1.3, "KeyRelease", 9, _SEAT_DEV, "a", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        names = [e["name"] for e in n["events"]]
        self.assertIn("W", names)
        self.assertIn("A", names)

    # F-keys and special keys must NOT be altered
    def test_xi2_fkey_passthrough(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
            (1.1, "KeyRelease", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["name"], "F9")

    # After namespace fold: evdev KEY_LEFTSHIFT and xi2 Shift_L both map to LSHIFT
    def test_both_planes_agree_on_lshift(self):
        evdev_n = nc.normalize(cap(
            (1.0, "kbd", "KEY", "KEY_LEFTSHIFT", 1),
            (1.1, "kbd", "KEY", "KEY_LEFTSHIFT", 0),
        ))
        xi2_n = nc.normalize(xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "Shift_L", _SEAT_FLAG),
            (1.1, "KeyRelease", 9, _SEAT_DEV, "Shift_L", _SEAT_FLAG),
        ))
        self.assertEqual(evdev_n["events"][0]["name"], xi2_n["events"][0]["name"])


class TestNormalizeXI2(unittest.TestCase):
    def test_plane_detected_as_xi2(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
            (1.5, "KeyRelease", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["plane"], "xi2")

    def test_press_pairing_xi2(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
            (1.5, "KeyRelease", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(len(n["events"]), 1)
        ev = n["events"][0]
        self.assertEqual(ev["kind"], "key")
        self.assertEqual(ev["name"], "F9")
        self.assertAlmostEqual(ev["dur_ms"], 500.0, places=0)
        self.assertEqual(n["summary"]["presses"], {"F9": 1})

    def test_raw_events_deduped(self):
        # Both Raw (master) and Device (xwayland) events for the same key
        lines = xi2_cap(
            (1.0, "RawKeyPress", 3, _MASTER_DEV, "F9", _MASTER_FLAG),
            (1.001, "KeyPress", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
            (1.002, "RawKeyRelease", 3, _MASTER_DEV, "F9", _MASTER_FLAG),
            (1.5, "KeyRelease", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        # n_raw includes all 4, but only 1 press event after dedup
        self.assertEqual(n["n_raw"], 4)
        self.assertEqual(len(n["events"]), 1)
        self.assertEqual(n["events"][0]["name"], "F9")

    def test_keysym_fold_l1_to_f11(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "L1", _SEAT_FLAG),
            (1.2, "KeyRelease", 9, _SEAT_DEV, "L1", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["name"], "F11")
        self.assertIn("F11", n["summary"]["presses"])

    def test_keysym_fold_l2_to_f12(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "L2", _SEAT_FLAG),
            (1.2, "KeyRelease", 9, _SEAT_DEV, "L2", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["name"], "F12")

    def test_up_only_xi2(self):
        lines = xi2_cap(
            (1.0, "KeyRelease", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["note"], "up-only")
        self.assertIsNone(n["events"][0]["dur_ms"])

    def test_still_held_xi2(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["events"][0]["note"], "still-held-at-end")

    def test_empty_xi2(self):
        n = nc.normalize([], plane="xi2")
        self.assertEqual(n["n_raw"], 0)
        self.assertEqual(n["events"], [])
        self.assertEqual(n["plane"], "xi2")

    def test_multiple_distinct_keys_xi2(self):
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
            (1.1, "KeyPress", 9, _SEAT_DEV, "F10", _SEAT_FLAG),
            (1.5, "KeyRelease", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
            (1.6, "KeyRelease", 9, _SEAT_DEV, "F10", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(n["summary"]["presses"], {"F9": 1, "F10": 1})
        self.assertEqual(len(n["events"]), 2)

    def test_schema_version_and_plane_fields_xi2(self):
        n = nc.normalize([], plane="xi2")
        self.assertEqual(n["schema_version"], "1")
        self.assertEqual(n["plane"], "xi2")

    def test_schema_version_and_plane_fields_evdev(self):
        n = nc.normalize([])
        self.assertEqual(n["schema_version"], "1")
        self.assertEqual(n["plane"], "evdev")

    def test_explicit_plane_override(self):
        # Force evdev plane even though input looks like xi2
        lines = xi2_cap(
            (1.0, "KeyPress", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
        )
        # With plane="evdev" the xi2-shaped records have no "type" or "value";
        # the evdev path should return empty (no valid evdev events)
        n = nc.normalize(lines, plane="evdev")
        self.assertEqual(n["plane"], "evdev")


class TestRawLayerTimestamps(unittest.TestCase):
    """Raw-layer timestamps must be used for t_down and dur_ms in XI2 normalization.

    Per finding (runs/20260612T053331Z-phase4-pin-batch1/result.md §P2):
    Key-layer (slave device, KeyPress/KeyRelease) events are flush-on-next-event
    artifacts — their timestamps reflect queue-flush points, not SI emission points.
    Raw-layer (master device, RawKeyPress/RawKeyRelease) timestamps are the actual
    SI emission times and must be the sole timing source.

    Regression fixture derived from p2-120ms-raw-audit.jsonl (canonical divergence capture):
      RawKeyPress  F1  t=0.000000    (SI emission, physical down)
      KeyPress     F1  t=0.035091    (key-layer flush, 35ms later)
      RawKeyRelease F1 t=0.035141    (SI emission, raw tap = pipeline latency ~34ms)
      KeyRelease   F1  t=0.193158    (key-layer flush, deferred to F3 RawKeyPress moment)
      RawKeyPress  F3  t=0.193215    (SI emission, DTT=190ms boundary)
      KeyPress     F3  t=0.227302    (key-layer flush)
      RawKeyRelease F3 t=0.227345    (SI emission)
      KeyRelease   F3  t=9.074000    (key-layer flush — capture exit artifact)

    Correct normalizer output (raw-layer wins):
      F1: t_ms=0.0,   dur_ms=35.1   (RawKeyPress→RawKeyRelease: 35ms raw tap)
      F3: t_ms=193.2, dur_ms=34.1   (RawKeyPress→RawKeyRelease: 34ms raw tap)

    Key-layer-wins output (wrong):
      F1: t_ms=35.1,  dur_ms=158.1  (KeyPress→KeyRelease: queue-flush artifact)
      F3: t_ms=227.3, dur_ms=8846.7 (KeyPress→KeyRelease: capture-exit artifact)
    """

    # Fixture timestamps scaled to t0=0 (relative); all from p2-120ms-raw-audit.jsonl
    # Original absolute timestamps: F1 RawKeyPress at 1781242883.777503
    _T0 = 1781242883.777503

    def _raw_audit_lines(self):
        """Return jsonl lines matching p2-120ms-raw-audit.jsonl."""
        rows = [
            # (t, event, dev_id, dev, code, flag)
            (self._T0 + 0.000000, "RawKeyPress",    3, _MASTER_DEV, "F1", _MASTER_FLAG),
            (self._T0 + 0.035091, "KeyPress",        6, _SEAT_DEV,   "F1", _SEAT_FLAG),
            (self._T0 + 0.035141, "RawKeyRelease",  3, _MASTER_DEV, "F1", _MASTER_FLAG),
            (self._T0 + 0.193158, "KeyRelease",      6, _SEAT_DEV,   "F1", _SEAT_FLAG),
            (self._T0 + 0.193215, "RawKeyPress",    3, _MASTER_DEV, "F3", _MASTER_FLAG),
            (self._T0 + 0.227302, "KeyPress",        6, _SEAT_DEV,   "F3", _SEAT_FLAG),
            (self._T0 + 0.227345, "RawKeyRelease",  3, _MASTER_DEV, "F3", _MASTER_FLAG),
            (self._T0 + 9.074000, "KeyRelease",      6, _SEAT_DEV,   "F3", _SEAT_FLAG),
        ]
        return xi2_cap(*rows)

    def test_f1_t_ms_uses_raw_timestamp(self):
        """F1 t_ms must be 0.0 (from RawKeyPress), not 35.1ms (from KeyPress)."""
        lines = self._raw_audit_lines()
        n = nc.normalize(lines)
        events = {ev["name"]: ev for ev in n["events"]}
        self.assertIn("F1", events, "F1 not found in normalized events")
        # Raw-layer t_ms: RawKeyPress is t0, so F1 t_ms must be 0.0
        self.assertAlmostEqual(events["F1"]["t_ms"], 0.0, delta=1.0,
            msg=f"F1 t_ms={events['F1']['t_ms']:.1f}ms — expected ~0ms (raw) not ~35ms (key-layer)")

    def test_f1_dur_ms_uses_raw_timestamps(self):
        """F1 dur_ms must be ~35ms (RawKeyPress→RawKeyRelease), not ~158ms (key-layer)."""
        lines = self._raw_audit_lines()
        n = nc.normalize(lines)
        events = {ev["name"]: ev for ev in n["events"]}
        self.assertIn("F1", events)
        dur = events["F1"]["dur_ms"]
        self.assertIsNotNone(dur, "F1 dur_ms is None — raw-layer up event not used")
        self.assertAlmostEqual(dur, 35.1, delta=5.0,
            msg=f"F1 dur_ms={dur:.1f}ms — expected ~35ms (raw tap) not ~158ms (key-layer artifact)")

    def test_f3_t_ms_uses_raw_timestamp(self):
        """F3 t_ms must be ~193ms (from RawKeyPress at DTT), not ~227ms (from KeyPress)."""
        lines = self._raw_audit_lines()
        n = nc.normalize(lines)
        events = {ev["name"]: ev for ev in n["events"]}
        self.assertIn("F3", events, "F3 not found in normalized events")
        t = events["F3"]["t_ms"]
        self.assertAlmostEqual(t, 193.2, delta=5.0,
            msg=f"F3 t_ms={t:.1f}ms — expected ~193ms (raw DTT emission) not ~227ms (key-layer flush)")

    def test_f3_dur_ms_uses_raw_timestamps(self):
        """F3 dur_ms must be ~34ms (RawKeyPress→RawKeyRelease), not ~8847ms (capture-exit artifact)."""
        lines = self._raw_audit_lines()
        n = nc.normalize(lines)
        events = {ev["name"]: ev for ev in n["events"]}
        self.assertIn("F3", events)
        dur = events["F3"]["dur_ms"]
        self.assertIsNotNone(dur, "F3 dur_ms is None")
        self.assertAlmostEqual(dur, 34.1, delta=5.0,
            msg=f"F3 dur_ms={dur:.1f}ms — expected ~34ms (raw tap) not ~8847ms (capture-exit artifact)")

    def test_raw_preferred_over_key_layer_for_t0(self):
        """t0_epoch must come from the earliest record — which is a RawKeyPress."""
        lines = self._raw_audit_lines()
        n = nc.normalize(lines)
        # t0_epoch must equal the RawKeyPress timestamp, not the first KeyPress
        self.assertAlmostEqual(n["t0_epoch"], self._T0, places=3)

    def test_key_layer_only_fallback(self):
        """When no Raw events present, key-layer events still produce a result."""
        lines = xi2_cap(
            (1.0, "KeyPress",   9, _SEAT_DEV, "F9", _SEAT_FLAG),
            (1.5, "KeyRelease", 9, _SEAT_DEV, "F9", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        self.assertEqual(len(n["events"]), 1)
        ev = n["events"][0]
        self.assertEqual(ev["name"], "F9")
        self.assertAlmostEqual(ev["t_ms"], 0.0, places=1)
        self.assertAlmostEqual(ev["dur_ms"], 500.0, delta=5.0)

    def test_raw_layer_t_ms_pin_f1_anchor(self):
        """Pin test: F1 must anchor at t_ms < 5ms (raw layer), not at ~35ms (key layer).

        This is the core oracle-pin consequence: all DTT-delta calculations
        (F3_t - F1_t ≈ DTT) require F1 to be anchored at physical-down, not at
        the key-layer flush 35ms later. With key-layer timing, the apparent DTT
        would be 193ms - 35ms = 158ms (wrong); with raw timing it is 193ms - 0ms
        = 193ms ≈ DTT=190ms (correct).
        """
        lines = self._raw_audit_lines()
        n = nc.normalize(lines)
        events = {ev["name"]: ev for ev in n["events"]}
        self.assertIn("F1", events)
        self.assertLess(events["F1"]["t_ms"], 5.0,
            msg="F1 must be anchored at physical-down (~0ms), not at key-layer flush (~35ms). "
                "DTT calculations require raw-layer timing.")


class TestZeroDurationRawPair(unittest.TestCase):
    """Zero/near-zero-duration raw pairs must be preserved, not noise-classified.

    Oracle mechanic (findings/steam_lane_behavior.md §Release_Press):
    Release_Press fires a single COMBINED down/up at the same instant — its
    expected raw signature is RawKeyPress + RawKeyRelease with identical or
    sub-millisecond-separated timestamps.  The normalizer must:

      (a) NOT drop them via the dedup window (the Device events arrive much later
          or may never arrive).
      (b) NOT classify the unmatched Raw events as noise.
      (c) Produce exactly one press record with dur_ms == 0 (or ≈0 for sub-ms).
      (d) Still handle the normal case (with Device events) — dur_ms stays
          raw-accurate (≈0), not stretched to the Device-layer gap.

    The primary failure mode (pre-fix): both Raw events hit the final
    `if ev in _XI2_RAW_EVENTS: continue` guard and are silently dropped when
    no Device counterpart has been seen — producing a false "absent" verdict.

    Test (e) covers multiple Release_Press pulses in sequence: each must be
    counted as a separate press.
    """

    def _zero_dur_lines(self, t_raw, t_key_press=None, t_key_release=None,
                        code="F1", raw_sep=0.0):
        """Build xi2_cap lines for a zero/near-zero-duration raw pair.

        raw_sep: seconds between RawKeyPress and RawKeyRelease (0 = identical).
        t_key_press / t_key_release: Device events, omit to test raw-only path.
        """
        rows = [
            (t_raw,           "RawKeyPress",   3, _MASTER_DEV, code, _MASTER_FLAG),
            (t_raw + raw_sep, "RawKeyRelease", 3, _MASTER_DEV, code, _MASTER_FLAG),
        ]
        if t_key_press is not None:
            rows.append((t_key_press,   "KeyPress",   9, _SEAT_DEV, code, _SEAT_FLAG))
        if t_key_release is not None:
            rows.append((t_key_release, "KeyRelease", 9, _SEAT_DEV, code, _SEAT_FLAG))
        # Sort by timestamp (xi2_cap helper doesn't sort)
        rows.sort(key=lambda r: r[0])
        return xi2_cap(*rows)

    # ------------------------------------------------------------------
    # (a) Identical timestamps, Device events arrive 35ms later
    # ------------------------------------------------------------------

    def test_identical_ts_with_device_events_produces_one_press(self):
        """RawKeyPress+RawKeyRelease at t=0, Device events at 35ms → one press event."""
        lines = self._zero_dur_lines(t_raw=1.0, raw_sep=0.0,
                                     t_key_press=1.035, t_key_release=1.070)
        n = nc.normalize(lines)
        events = [e for e in n["events"] if e["name"] == "F1"]
        self.assertEqual(len(events), 1,
            f"Expected 1 F1 press, got {len(events)}: {events}")

    def test_identical_ts_with_device_events_dur_ms_zero(self):
        """Zero-duration raw pair with Device events: dur_ms must be 0ms (raw-layer)."""
        lines = self._zero_dur_lines(t_raw=1.0, raw_sep=0.0,
                                     t_key_press=1.035, t_key_release=1.070)
        n = nc.normalize(lines)
        events = [e for e in n["events"] if e["name"] == "F1"]
        self.assertEqual(len(events), 1)
        self.assertIsNotNone(events[0].get("dur_ms"),
            "dur_ms must not be None — raw release timestamp must close the pair")
        self.assertAlmostEqual(events[0]["dur_ms"], 0.0, delta=1.0,
            msg=f"dur_ms={events[0]['dur_ms']}ms — expected ~0ms for zero-duration raw pair, "
                f"not the Device-layer gap (~35ms)")

    # ------------------------------------------------------------------
    # (b) Sub-ms separation (0.3ms), Device events arrive later
    # ------------------------------------------------------------------

    def test_subms_sep_with_device_events_produces_one_press(self):
        """RawKeyPress at t=0, RawKeyRelease at t=0.3ms, Device events at 35ms → one press."""
        lines = self._zero_dur_lines(t_raw=1.0, raw_sep=0.0003,
                                     t_key_press=1.035, t_key_release=1.070)
        n = nc.normalize(lines)
        events = [e for e in n["events"] if e["name"] == "F1"]
        self.assertEqual(len(events), 1,
            f"Expected 1 F1 press, got {len(events)}: {events}")

    def test_subms_sep_dur_ms_near_zero(self):
        """0.3ms raw separation → dur_ms ≈ 0.3ms (raw-accurate), not Device-layer gap."""
        lines = self._zero_dur_lines(t_raw=1.0, raw_sep=0.0003,
                                     t_key_press=1.035, t_key_release=1.070)
        n = nc.normalize(lines)
        events = [e for e in n["events"] if e["name"] == "F1"]
        self.assertEqual(len(events), 1)
        self.assertIsNotNone(events[0].get("dur_ms"))
        self.assertAlmostEqual(events[0]["dur_ms"], 0.3, delta=0.5,
            msg=f"dur_ms={events[0]['dur_ms']}ms — expected ~0.3ms for sub-ms raw pair")

    # ------------------------------------------------------------------
    # (c) Zero-duration raw pair with NO Device counterpart at all
    #     (the primary Release_Press failure mode)
    # ------------------------------------------------------------------

    def test_zero_dur_raw_only_no_device_produces_one_press(self):
        """RawKeyPress+RawKeyRelease at same instant, no Device events → must emit one press.

        This is the primary failure mode: without a Device counterpart, the
        normalizer previously classified the Raw events as noise and dropped them.
        A Release_Press that emits a combined down/up but whose Device flush never
        arrives (or arrives outside the capture window) must still be counted.
        """
        lines = self._zero_dur_lines(t_raw=1.0, raw_sep=0.0)  # no Device events
        n = nc.normalize(lines)
        events = [e for e in n["events"] if e["name"] == "F1"]
        self.assertEqual(len(events), 1,
            f"Expected 1 F1 press from raw-only zero-dur pair, got {len(events)} — "
            f"zero-duration raw pairs must not be noise-classified")

    def test_zero_dur_raw_only_dur_ms_is_zero(self):
        """Raw-only zero-duration pair: dur_ms must be 0.0, not None."""
        lines = self._zero_dur_lines(t_raw=1.0, raw_sep=0.0)
        n = nc.normalize(lines)
        events = [e for e in n["events"] if e["name"] == "F1"]
        self.assertEqual(len(events), 1)
        self.assertIsNotNone(events[0].get("dur_ms"),
            "dur_ms must not be None for a raw-only paired event")
        self.assertAlmostEqual(events[0]["dur_ms"], 0.0, delta=0.5)

    def test_zero_dur_raw_only_t_ms_is_correct(self):
        """Raw-only zero-duration pair: t_ms must be anchored at RawKeyPress timestamp."""
        # two events at t=1.0 (raw) and t=2.0 (the zero-dur pair for a different key),
        # so t0=1.0 and F2 t_ms should be 1000ms
        rows = [
            (1.0, "RawKeyPress",   3, _MASTER_DEV, "F1", _MASTER_FLAG),
            (1.0, "RawKeyRelease", 3, _MASTER_DEV, "F1", _MASTER_FLAG),
            (2.0, "RawKeyPress",   3, _MASTER_DEV, "F2", _MASTER_FLAG),
            (2.0, "RawKeyRelease", 3, _MASTER_DEV, "F2", _MASTER_FLAG),
            # Device events for F1 only (to provide a stable t0 anchor)
            (1.035, "KeyPress",   9, _SEAT_DEV, "F1", _SEAT_FLAG),
            (1.070, "KeyRelease", 9, _SEAT_DEV, "F1", _SEAT_FLAG),
        ]
        rows.sort(key=lambda r: r[0])
        lines = xi2_cap(*rows)
        n = nc.normalize(lines)
        f2_events = [e for e in n["events"] if e["name"] == "F2"]
        self.assertEqual(len(f2_events), 1,
            "F2 raw-only zero-dur pair must produce one event")
        self.assertAlmostEqual(f2_events[0]["t_ms"], 1000.0, delta=5.0,
            msg=f"F2 t_ms={f2_events[0]['t_ms']:.1f}ms — expected ~1000ms from t0")

    def test_subms_raw_only_produces_one_press(self):
        """RawKeyPress+RawKeyRelease 0.3ms apart, no Device events → one press."""
        lines = self._zero_dur_lines(t_raw=1.0, raw_sep=0.0003)
        n = nc.normalize(lines)
        events = [e for e in n["events"] if e["name"] == "F1"]
        self.assertEqual(len(events), 1,
            f"Expected 1 F1 from raw-only sub-ms pair, got {len(events)}")

    # ------------------------------------------------------------------
    # (d) Dedup window: Device event within 5ms of zero-dur raw pair
    #     Raw is in dedup set; Device event provides the pairing signal.
    #     Only one press emitted; no double-counting.
    # ------------------------------------------------------------------

    def test_zero_dur_raw_within_dedup_window_not_double_counted(self):
        """If Device event is within 5ms of zero-dur raw, exactly one press emitted."""
        # RawKeyPress at t=1.000, RawKeyRelease at t=1.000 (identical)
        # KeyPress at t=1.002 (2ms later, within 5ms dedup window)
        # KeyRelease at t=1.003
        lines = xi2_cap(
            (1.000, "RawKeyPress",   3, _MASTER_DEV, "F1", _MASTER_FLAG),
            (1.000, "RawKeyRelease", 3, _MASTER_DEV, "F1", _MASTER_FLAG),
            (1.002, "KeyPress",      9, _SEAT_DEV,   "F1", _SEAT_FLAG),
            (1.003, "KeyRelease",    9, _SEAT_DEV,   "F1", _SEAT_FLAG),
        )
        n = nc.normalize(lines)
        f1 = [e for e in n["events"] if e["name"] == "F1"]
        self.assertEqual(len(f1), 1,
            f"Expected exactly 1 F1 event (no double-count), got {len(f1)}: {f1}")

    # ------------------------------------------------------------------
    # (e) Multiple Release_Press pulses in sequence — each must be counted
    # ------------------------------------------------------------------

    def test_multiple_zero_dur_raw_pairs_all_counted(self):
        """Three Release_Press-style raw pairs in sequence → three press events."""
        rows = []
        for i in range(3):
            t = 1.0 + i * 0.5  # t=1.0, 1.5, 2.0
            rows += [
                (t,     "RawKeyPress",   3, _MASTER_DEV, "F1", _MASTER_FLAG),
                (t,     "RawKeyRelease", 3, _MASTER_DEV, "F1", _MASTER_FLAG),
                (t+0.035, "KeyPress",   9, _SEAT_DEV,   "F1", _SEAT_FLAG),
                (t+0.070, "KeyRelease", 9, _SEAT_DEV,   "F1", _SEAT_FLAG),
            ]
        rows.sort(key=lambda r: r[0])
        lines = xi2_cap(*rows)
        n = nc.normalize(lines)
        self.assertEqual(n["summary"]["presses"].get("F1", 0), 3,
            f"Expected 3 F1 presses, got {n['summary']['presses']}")

    def test_multiple_zero_dur_raw_only_all_counted(self):
        """Three raw-only Release_Press pulses (no Device events) → three press events."""
        rows = []
        for i in range(3):
            t = 1.0 + i * 0.5
            rows += [
                (t, "RawKeyPress",   3, _MASTER_DEV, "F1", _MASTER_FLAG),
                (t, "RawKeyRelease", 3, _MASTER_DEV, "F1", _MASTER_FLAG),
            ]
        rows.sort(key=lambda r: r[0])
        lines = xi2_cap(*rows)
        n = nc.normalize(lines)
        self.assertEqual(n["summary"]["presses"].get("F1", 0), 3,
            f"Expected 3 F1 presses from raw-only pairs, got {n['summary']['presses']}")


if __name__ == "__main__":
    unittest.main()
