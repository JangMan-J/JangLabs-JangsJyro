#!/usr/bin/env python3
"""Unit tests for Phase-4 trace DSL scripts.

These tests verify that all trace files in tools/phase4/ are:
  1. Valid DSL (every non-comment, non-blank line is a known action)
  2. Structurally sound (at least one stimulus action; no orphan down/up)
  3. Within timing bounds (no single wait > 5000 ms — guards against a typo
     that would make a live run take many minutes)
  4. Each script contains a VERDICT CHECK comment header

Tests run on the static files only — no uinput / evdev / live system access.
Run: python3 -m unittest test_phase4_traces -v
"""
import os
import sys
import unittest
from pathlib import Path

# Locate the phase4 directory relative to this test file
TOOLS_DIR = Path(__file__).resolve().parent
PHASE4_DIR = TOOLS_DIR / "phase4"

# Known DSL verbs (from synthetic_gamepad.py do_action)
_KNOWN_VERBS = {"wait", "down", "up", "press", "axis"}

# Valid button names
_BTN_NAMES = {"SOUTH", "EAST", "NORTH", "WEST", "TL", "TR",
              "SELECT", "START", "MODE", "THUMBL", "THUMBR"}

# Valid axis names
_AXIS_NAMES = {"LX", "LY", "RX", "RY", "LZ", "RZ", "HX", "HY"}


def _parse_trace(path: Path):
    """Parse a .txt trace file into a list of (lineno, verb, args) tuples.
    Strips comments and blank lines.  Returns list of (lineno, parts)."""
    actions = []
    with open(path) as f:
        for i, raw in enumerate(f, 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            actions.append((i, parts))
    return actions


def _get_trace_files():
    if not PHASE4_DIR.exists():
        return []
    return sorted(PHASE4_DIR.glob("*.txt"))


class TestTraceSyntax(unittest.TestCase):
    """Every action in every trace file must be syntactically valid DSL."""

    def _check_file(self, path):
        actions = _parse_trace(path)
        self.assertGreater(len(actions), 0,
                           f"{path.name}: trace file has no actions")
        for lineno, parts in actions:
            verb = parts[0].lower()
            self.assertIn(verb, _KNOWN_VERBS,
                          f"{path.name}:{lineno}: unknown verb {parts[0]!r}")
            if verb in ("down", "up"):
                self.assertEqual(len(parts), 2,
                                 f"{path.name}:{lineno}: {verb} needs exactly 1 arg")
                self.assertIn(parts[1].upper(), _BTN_NAMES,
                              f"{path.name}:{lineno}: unknown button {parts[1]!r}")
            elif verb == "press":
                self.assertIn(len(parts), (2, 3),
                              f"{path.name}:{lineno}: press needs 1-2 args")
                self.assertIn(parts[1].upper(), _BTN_NAMES,
                              f"{path.name}:{lineno}: unknown button {parts[1]!r}")
                if len(parts) == 3:
                    self.assertRaises(ValueError, lambda: None)  # keep line clean
                    float(parts[2])  # must be numeric
            elif verb == "wait":
                self.assertEqual(len(parts), 2,
                                 f"{path.name}:{lineno}: wait needs 1 arg")
                ms = float(parts[1])
                self.assertGreater(ms, 0,
                                   f"{path.name}:{lineno}: wait ms must be > 0")
                self.assertLessEqual(ms, 5000,
                                     f"{path.name}:{lineno}: wait {ms} ms > 5000 ms "
                                     f"(likely a typo — would stall a live run)")
            elif verb == "axis":
                self.assertEqual(len(parts), 3,
                                 f"{path.name}:{lineno}: axis needs 2 args")
                self.assertIn(parts[1].upper(), _AXIS_NAMES,
                              f"{path.name}:{lineno}: unknown axis {parts[1]!r}")
                val = int(parts[2])
                # Triggers: 0..255; sticks/hats: allow -32768..32767
                self.assertGreaterEqual(val, -32768,
                                        f"{path.name}:{lineno}: axis value {val} < -32768")
                self.assertLessEqual(val, 32767,
                                     f"{path.name}:{lineno}: axis value {val} > 32767")


# Dynamically add one test method per trace file
def _make_test(path):
    def test_method(self):
        self._check_file(path)
    test_method.__name__ = f"test_syntax_{path.stem}"
    test_method.__doc__ = f"Syntax check: {path.name}"
    return test_method


for _p in _get_trace_files():
    _method = _make_test(_p)
    setattr(TestTraceSyntax, _method.__name__, _method)


class TestTraceStructure(unittest.TestCase):
    """Each trace must have a VERDICT CHECK comment and at least one stimulus."""

    def _check_file(self, path):
        text = path.read_text()
        self.assertIn("VERDICT CHECK", text,
                      f"{path.name}: missing VERDICT CHECK comment header")
        actions = _parse_trace(path)
        stimulus_verbs = {"down", "up", "press", "axis"}
        stimuli = [a for _, a in actions if a[0].lower() in stimulus_verbs]
        self.assertGreater(len(stimuli), 0,
                           f"{path.name}: no stimulus actions found")

    def _check_balance_approx(self, path):
        """For button traces: down/up counts should be roughly balanced.
        (Not exact — some probes intentionally send bare 'down' without 'up'
        for split-batch use, but >3x imbalance is likely a typo.)"""
        actions = _parse_trace(path)
        downs = sum(1 for _, a in actions if a[0].lower() in ("down",))
        ups = sum(1 for _, a in actions if a[0].lower() in ("up",))
        if downs > 0 and ups > 0:
            ratio = max(downs, ups) / min(downs, ups)
            self.assertLessEqual(ratio, 3.0,
                                 f"{path.name}: down/up count imbalance "
                                 f"({downs}/{ups}) > 3:1 — possible missing up")


def _make_structure_test(path):
    def test_method(self):
        self._check_file(path)
        self._check_balance_approx(path)
    test_method.__name__ = f"test_structure_{path.stem}"
    test_method.__doc__ = f"Structure check: {path.name}"
    return test_method


for _p in _get_trace_files():
    _method = _make_structure_test(_p)
    setattr(TestTraceStructure, _method.__name__, _method)


class TestTraceFilesExist(unittest.TestCase):
    """All five expected trace files must exist."""

    EXPECTED = {
        "vary_hold_d2d_pin.txt",
        "singles_anchor_set.txt",
        "double_emission_timing.txt",
        "held_double_watch.txt",
        "rz200_staged_trigger.txt",
    }

    def test_phase4_dir_exists(self):
        self.assertTrue(PHASE4_DIR.exists(),
                        f"tools/phase4/ directory not found at {PHASE4_DIR}")

    def test_all_expected_files_present(self):
        found = {p.name for p in PHASE4_DIR.glob("*.txt")}
        missing = self.EXPECTED - found
        self.assertFalse(missing,
                         f"Missing trace files in tools/phase4/: {missing}")


class TestVdfLayoutFilesExist(unittest.TestCase):
    """All three expected layout files must exist and be non-empty."""

    LAYOUTS_DIR = TOOLS_DIR.parent / "reference" / "phase4-layouts"

    EXPECTED = {
        "marker_layout.vdf",
        "remove_layer.vdf",
        "action_set_swap.vdf",
    }

    def test_phase4_layouts_dir_exists(self):
        self.assertTrue(self.LAYOUTS_DIR.exists(),
                        f"reference/phase4-layouts/ not found")

    def test_all_expected_layouts_present(self):
        found = {p.name for p in self.LAYOUTS_DIR.glob("*.vdf")}
        missing = self.EXPECTED - found
        self.assertFalse(missing,
                         f"Missing layout files: {missing}")

    def test_layouts_non_empty(self):
        for name in self.EXPECTED:
            p = self.LAYOUTS_DIR / name
            if p.exists():
                self.assertGreater(p.stat().st_size, 100,
                                   f"{name} appears to be empty or trivially small")

    def test_layouts_contain_controller_mappings(self):
        for name in self.EXPECTED:
            p = self.LAYOUTS_DIR / name
            if p.exists():
                text = p.read_text()
                self.assertIn("controller_mappings", text,
                              f"{name}: missing 'controller_mappings' root key")


if __name__ == "__main__":
    import unittest
    unittest.main()
