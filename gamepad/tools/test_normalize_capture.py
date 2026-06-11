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
        self.assertEqual(nc.canon("KEY_LEFTSHIFT"), ("key", "LEFTSHIFT"))

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


if __name__ == "__main__":
    unittest.main()
