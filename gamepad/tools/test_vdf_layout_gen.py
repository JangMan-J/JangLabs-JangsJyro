#!/usr/bin/env python3
"""Unit tests for vdf_layout_gen.py — pure, deterministic, stdlib only.

TDD: these tests were written BEFORE the implementation.  Run:
  python3 -m unittest test_vdf_layout_gen -v
"""
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Allow running from the tools/ directory
sys.path.insert(0, os.path.dirname(__file__))

import vdf_layout_gen as vg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(text: str):
    """Round-trip parse: return the top-level Pairs from a VDF string."""
    tokens = vg.tokenize(text)
    pairs, _ = vg.parse(tokens)
    return pairs


def _groups_by_mode(pairs):
    """Return {mode: list_of_group_pairs} from a controller_mappings Pairs."""
    root = pairs.get_first("controller_mappings")
    return {g.get_first("mode"): g for _, g in root if _ == "group"}


# ---------------------------------------------------------------------------
# Tokenizer / parser (shared with vdf_clean.py logic)
# ---------------------------------------------------------------------------

class TestTokenizer(unittest.TestCase):
    def test_simple_key_value(self):
        tokens = vg.tokenize('"a" "b"')
        self.assertEqual(tokens, [("STR", "a"), ("STR", "b")])

    def test_nested(self):
        tokens = vg.tokenize('"x" { "k" "v" }')
        self.assertIn(("OBJ_OPEN", None), tokens)
        self.assertIn(("OBJ_CLOSE", None), tokens)

    def test_roundtrip_simple(self):
        text = '"controller_mappings"\n{\n"version"\t"3"\n}\n'
        pairs = _parse(text)
        root = pairs.get_first("controller_mappings")
        self.assertEqual(root.get_first("version"), "3")


# ---------------------------------------------------------------------------
# Activator building blocks
# ---------------------------------------------------------------------------

class TestActivatorBuilder(unittest.TestCase):
    def test_full_press_activator(self):
        act = vg.make_activator("Full_Press", "F13")
        self.assertEqual(act.get_first("activator_type"), "Full_Press")
        bindings = act.get_first("bindings")
        self.assertIsNotNone(bindings)
        self.assertIn("F13", bindings.get_first("binding", ""))

    def test_long_press_activator_default_time(self):
        act = vg.make_activator("Long_Press", "F14")
        # Default long_press_time should NOT be injected (use Steam's default)
        settings = act.get_first("settings")
        if settings is not None:
            self.assertIsNone(settings.get_first("long_press_time"))

    def test_long_press_activator_explicit_time(self):
        act = vg.make_activator("Long_Press", "F14", long_press_time=603)
        settings = act.get_first("settings")
        self.assertIsNotNone(settings)
        self.assertEqual(settings.get_first("long_press_time"), "603")

    def test_double_press_activator_default_no_dtt(self):
        act = vg.make_activator("Double_Press", "F15")
        settings = act.get_first("settings")
        if settings is not None:
            self.assertIsNone(settings.get_first("double_tap_time"))

    def test_double_press_activator_explicit_dtt(self):
        act = vg.make_activator("Double_Press", "F15", double_tap_time=190)
        settings = act.get_first("settings")
        self.assertIsNotNone(settings)
        self.assertEqual(settings.get_first("double_tap_time"), "190")

    def test_interruptable_0_flag(self):
        act = vg.make_activator("Full_Press", "F13", interruptable=False)
        settings = act.get_first("settings")
        self.assertIsNotNone(settings)
        self.assertEqual(settings.get_first("interruptable"), "0")

    def test_interruptable_default_omitted(self):
        act = vg.make_activator("Full_Press", "F13")
        settings = act.get_first("settings")
        if settings is not None:
            self.assertIsNone(settings.get_first("interruptable"))

    def test_start_press_activator(self):
        act = vg.make_activator("Start_Press", "F13")
        self.assertEqual(act.get_first("activator_type"), "Start_Press")
        bindings = act.get_first("bindings")
        self.assertIsNotNone(bindings)
        self.assertIn("F13", bindings.get_first("binding", ""))

    def test_release_press_activator(self):
        act = vg.make_activator("Release_Press", "F14")
        self.assertEqual(act.get_first("activator_type"), "Release_Press")
        bindings = act.get_first("bindings")
        self.assertIsNotNone(bindings)
        self.assertIn("F14", bindings.get_first("binding", ""))


# ---------------------------------------------------------------------------
# Helpers for extracting all key bindings from a layout tree
# ---------------------------------------------------------------------------

def _collect_bindings(pairs, acc=None):
    """Walk a Pairs tree and collect all 'binding' string values."""
    if acc is None:
        acc = []
    for k, v in pairs:
        if k == "binding" and isinstance(v, str):
            acc.append(v)
        elif isinstance(v, vg.Pairs):
            _collect_bindings(v, acc)
    return acc


def _binding_keys(text):
    """Return list of key names from all binding strings in a VDF text."""
    pairs = _parse(text)
    bindings = _collect_bindings(pairs)
    keys = []
    for b in bindings:
        # binding format: "key_press F3, , " or "key_press LEFT_SHIFT, , "
        parts = b.strip().split()
        if len(parts) >= 2 and parts[0] == "key_press":
            keys.append(parts[1].rstrip(","))
    return keys


# ---------------------------------------------------------------------------
# Layout-1: Marker layout — final respec per gate review
#
# Key map (gate-review mandated; F1–F10 only; all keys unique):
#   button_y (THE test button — all four activators):
#     Start_Press   → F1
#     Release_Press → F2
#     Full_Press    → F3  (Regular; delayed to first-down + DTT)
#     Double_Press  → F4  (DISTINCT from F3; double_tap_time=190; interruptable default)
#   button_a (digital baseline / canary): Full_Press → F5
#   button_b (tap/hold):    Full_Press → F6, Long_Press → F7
#   button_x (interruptable=0 probe): Full_Press (interruptable=0) → F8, Long_Press → F9
#
# Design rationale (gate-review feedback):
#   - Start_Press/Release_Press on the test button provide in-stream reference
#     markers: pipeline latency cancels when differencing F1/F2 vs F3/F4 in
#     the same XI2 capture stream.
#   - Distinct keys per activator: F3 ≠ F4 makes Regular vs Double attribution
#     unambiguous by key identity alone (timing-inference-free).
#   - No F11/F12 (alias to L1/L2 keysyms in xinput output — Phase-2 confirmed).
#   - No F13–F16 (unproven on this stack; Phase 2 only proved F1–F12 at XI2).
#   - Key uniqueness is enforced as a generator invariant via assert_all_keys_unique().
# ---------------------------------------------------------------------------

def _get_four_buttons_inputs(groups):
    """Extract the inputs Pairs from the four_buttons group."""
    return groups["four_buttons"][0].get_first("inputs")


class TestMarkerLayout(unittest.TestCase):
    def setUp(self):
        self.text = vg.make_marker_layout(double_tap_time=190)
        self.pairs = _parse(self.text)
        root = self.pairs.get_first("controller_mappings")
        self.groups = {}
        for k, v in root:
            if k == "group":
                mode = v.get_first("mode")
                self.groups[mode] = self.groups.get(mode, [])
                self.groups[mode].append(v)
        inputs = _get_four_buttons_inputs(self.groups)
        # button_y is the test button
        self.test_btn = inputs.get_first("button_y")
        self.test_activators = self.test_btn.get_first("activators")

    def test_parses_as_valid_vdf(self):
        self.assertIsNotNone(self.pairs.get_first("controller_mappings"))

    def test_has_four_buttons_group(self):
        self.assertIn("four_buttons", self.groups)

    # --- Test button (button_y) activator checks ---

    def test_start_press_f1(self):
        """Start_Press activator → F1."""
        sp = self.test_activators.get_first("Start_Press")
        self.assertIsNotNone(sp, "Start_Press missing on test button (button_y)")
        binding = sp.get_first("bindings").get_first("binding")
        self.assertIn("F1", binding)
        # Confirm it's exactly F1, not F10/F11/...
        self.assertRegex(binding, r"\bF1\b")

    def test_release_press_f2(self):
        """Release_Press activator → F2."""
        rp = self.test_activators.get_first("Release_Press")
        self.assertIsNotNone(rp, "Release_Press missing on test button (button_y)")
        binding = rp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF2\b")

    def test_full_press_f3(self):
        """Full_Press (Regular) activator → F3."""
        fp = self.test_activators.get_first("Full_Press")
        self.assertIsNotNone(fp, "Full_Press missing on test button (button_y)")
        binding = fp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF3\b")

    def test_double_press_f4_dtt_190(self):
        """Double_Press activator → F4 (distinct from F3) with double_tap_time=190."""
        dp = self.test_activators.get_first("Double_Press")
        self.assertIsNotNone(dp, "Double_Press missing on test button (button_y)")
        binding = dp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF4\b")
        # Must NOT share key with Regular (F3 ≠ F4)
        self.assertNotIn("F3", binding,
                         "Double_Press must use a DISTINCT key from Full_Press")
        settings = dp.get_first("settings")
        self.assertIsNotNone(settings, "Double_Press settings missing (need double_tap_time)")
        self.assertEqual(settings.get_first("double_tap_time"), "190")

    def test_interruptable_NOT_set_on_test_button(self):
        """interruptable must NOT be explicitly set on the test button — Steam default."""
        for act_type in ("Start_Press", "Release_Press", "Full_Press", "Double_Press"):
            act = self.test_activators.get_first(act_type)
            if act is None:
                continue
            settings = act.get_first("settings")
            if settings is not None:
                self.assertIsNone(
                    settings.get_first("interruptable"),
                    f"{act_type}: interruptable must be left at default (not set)")

    def test_four_activator_types_on_test_button(self):
        """All four activator types must be present on the test button."""
        for act_type in ("Start_Press", "Release_Press", "Full_Press", "Double_Press"):
            self.assertIsNotNone(
                self.test_activators.get_first(act_type),
                f"Missing activator type on test button: {act_type}")

    # --- Other buttons ---

    def test_button_a_canary_f5(self):
        """button_a canary: Full_Press → F5."""
        inputs = _get_four_buttons_inputs(self.groups)
        btn = inputs.get_first("button_a")
        self.assertIsNotNone(btn, "button_a missing")
        fp = btn.get_first("activators").get_first("Full_Press")
        self.assertIsNotNone(fp, "button_a Full_Press missing")
        self.assertRegex(fp.get_first("bindings").get_first("binding"), r"\bF5\b")

    def test_button_b_taphold_f6_f7(self):
        """button_b tap/hold: Full_Press → F6, Long_Press → F7."""
        inputs = _get_four_buttons_inputs(self.groups)
        btn = inputs.get_first("button_b")
        self.assertIsNotNone(btn, "button_b missing")
        acts = btn.get_first("activators")
        fp = acts.get_first("Full_Press")
        lp = acts.get_first("Long_Press")
        self.assertIsNotNone(fp, "button_b Full_Press missing")
        self.assertIsNotNone(lp, "button_b Long_Press missing")
        self.assertRegex(fp.get_first("bindings").get_first("binding"), r"\bF6\b")
        self.assertRegex(lp.get_first("bindings").get_first("binding"), r"\bF7\b")

    def test_button_x_interruptable0_f8_f9(self):
        """button_x interruptable=0 probe: Full_Press(interruptable=0) → F8, Long_Press → F9."""
        inputs = _get_four_buttons_inputs(self.groups)
        btn = inputs.get_first("button_x")
        self.assertIsNotNone(btn, "button_x missing")
        acts = btn.get_first("activators")
        fp = acts.get_first("Full_Press")
        lp = acts.get_first("Long_Press")
        self.assertIsNotNone(fp, "button_x Full_Press missing")
        self.assertIsNotNone(lp, "button_x Long_Press missing")
        self.assertRegex(fp.get_first("bindings").get_first("binding"), r"\bF8\b")
        self.assertRegex(lp.get_first("bindings").get_first("binding"), r"\bF9\b")
        # interruptable=0 must be set on Full_Press
        settings = fp.get_first("settings")
        self.assertIsNotNone(settings, "button_x Full_Press settings missing (need interruptable=0)")
        self.assertEqual(settings.get_first("interruptable"), "0")

    # --- Key uniqueness (generator invariant) ---

    def test_all_keys_unique_in_layout(self):
        """Every (button, activator) → unique key. No two activators share a binding key."""
        keys = _binding_keys(self.text)
        # Filter out non-Fkey bindings (layer/set actions don't apply here)
        fkeys = [k for k in keys if k.startswith("F")]
        self.assertEqual(
            len(fkeys), len(set(fkeys)),
            f"Duplicate keys in marker layout: {fkeys} — "
            f"duplicates: {[k for k in set(fkeys) if fkeys.count(k) > 1]}")

    def test_no_f11_f12_in_layout(self):
        """F11 and F12 must not appear — they alias to L1/L2 keysyms in xinput output."""
        keys = _binding_keys(self.text)
        for k in keys:
            self.assertNotIn(k, ("F11", "F12"),
                             f"F11/F12 found in layout (aliases to L1/L2 in xinput): {k}")

    def test_no_high_fkeys_in_layout(self):
        """F13+ must not appear — unproven binding tokens on this stack."""
        keys = _binding_keys(self.text)
        for k in keys:
            if k.startswith("F") and k[1:].isdigit():
                n = int(k[1:])
                self.assertLessEqual(n, 10,
                                     f"{k} is an unproven binding token on this stack "
                                     f"(Phase 2 only confirmed F1–F10 at XI2)")

    def test_serializes_without_parse_error(self):
        reparsed = _parse(self.text)
        self.assertIsNotNone(reparsed.get_first("controller_mappings"))


# ---------------------------------------------------------------------------
# Layout-2: Timed remove_layer layout
# ---------------------------------------------------------------------------

class TestRemoveLayerLayout(unittest.TestCase):
    def setUp(self):
        self.text = vg.make_remove_layer_layout()
        self.pairs = _parse(self.text)
        self.root = self.pairs.get_first("controller_mappings")

    def test_parses_as_valid_vdf(self):
        self.assertIsNotNone(self.root)

    def test_has_two_presets(self):
        presets = [v for k, v in self.root if k == "preset"]
        self.assertEqual(len(presets), 2,
                         "Expected two presets: Default and a Layer")

    def test_layer_preset_has_numeric_id_and_name(self):
        """Layer preset must have a numeric id and name 'LayerA'."""
        presets = [v for k, v in self.root if k == "preset"]
        layer_preset = next((p for p in presets if p.get_first("name") == "LayerA"), None)
        self.assertIsNotNone(layer_preset, "No preset with name='LayerA' found")
        pid = layer_preset.get_first("id")
        self.assertIsNotNone(pid, "Layer preset has no id")
        self.assertTrue(pid.isdigit(), f"Layer preset id must be numeric, got {pid!r}")

    def test_action_layers_block_declares_layera(self):
        """controller_mappings must have an action_layers block listing 'LayerA'."""
        action_layers = self.root.get_first("action_layers")
        self.assertIsNotNone(action_layers, "Missing action_layers block")
        names = [k for k, _ in action_layers]
        self.assertIn("LayerA", names,
                      f"'LayerA' not in action_layers block; got {names}")

    def test_action_layers_layera_has_set_layer_flag(self):
        """LayerA entry in action_layers must have set_layer='1'."""
        action_layers = self.root.get_first("action_layers")
        layera = action_layers.get_first("LayerA")
        self.assertIsNotNone(layera, "No LayerA entry in action_layers")
        self.assertEqual(layera.get_first("set_layer"), "1")

    def test_add_layer_binding_uses_controller_action_verb(self):
        """add_layer binding must use 'controller_action add_layer <id> ...' format."""
        import re
        found = re.search(r'controller_action add_layer (\d+)', self.text)
        self.assertIsNotNone(found,
            "No 'controller_action add_layer <id>' binding found in layout")

    def test_remove_layer_binding_uses_controller_action_verb(self):
        """remove_layer binding must use 'controller_action remove_layer <id> ...' format."""
        import re
        found = re.search(r'controller_action remove_layer (\d+)', self.text)
        self.assertIsNotNone(found,
            "No 'controller_action remove_layer <id>' binding found in layout")

    def test_layer_binding_id_matches_layer_preset_id(self):
        """The numeric id in add_layer/remove_layer bindings must equal the LayerA preset id."""
        import re
        presets = [v for k, v in self.root if k == "preset"]
        layer_preset = next((p for p in presets if p.get_first("name") == "LayerA"), None)
        self.assertIsNotNone(layer_preset)
        pid = layer_preset.get_first("id")
        # Every add_layer and remove_layer binding must reference this preset id
        for op in ("add_layer", "remove_layer"):
            for m in re.finditer(rf'controller_action {op} (\d+)', self.text):
                self.assertEqual(m.group(1), pid,
                    f"controller_action {op} references id {m.group(1)!r}, "
                    f"expected LayerA preset id {pid!r}")

    def test_serializes_without_parse_error(self):
        reparsed = _parse(self.text)
        self.assertIsNotNone(reparsed.get_first("controller_mappings"))

    def test_no_high_fkeys_in_layout(self):
        """F13+ must not appear — unproven binding tokens on this stack."""
        keys = _binding_keys(self.text)
        high = [k for k in keys if k.startswith("F") and k[1:].isdigit() and int(k[1:]) >= 13]
        self.assertEqual(high, [], f"Unexpected high F-keys in remove_layer layout: {high}")

    def test_no_f11_f12_in_layout(self):
        """F11 and F12 must not appear — they alias to L1/L2 keysyms in xinput output."""
        keys = _binding_keys(self.text)
        bad = [k for k in keys if k in ("F11", "F12")]
        self.assertEqual(bad, [], f"F11/F12 present in remove_layer layout: {bad}")

    def test_all_keys_unique_in_layout(self):
        """Every (button, activator) → unique key. No two activators share a binding key."""
        keys = _binding_keys(self.text)
        fkeys = [k for k in keys if k.startswith("F") and k[1:].isdigit()]
        self.assertEqual(len(fkeys), len(set(fkeys)),
                         f"Duplicate F-keys in remove_layer layout: {fkeys}")


# ---------------------------------------------------------------------------
# Layout-3: Two-action-set swap layout
# ---------------------------------------------------------------------------

class TestActionSetSwapLayout(unittest.TestCase):
    def setUp(self):
        self.text = vg.make_action_set_swap_layout()
        self.pairs = _parse(self.text)
        self.root = self.pairs.get_first("controller_mappings")

    def test_parses_as_valid_vdf(self):
        self.assertIsNotNone(self.root)

    def test_has_two_presets(self):
        presets = [v for k, v in self.root if k == "preset"]
        self.assertGreaterEqual(len(presets), 2,
                                "Need at least two action sets")

    def test_presets_have_distinct_names(self):
        presets = [v for k, v in self.root if k == "preset"]
        names = [p.get_first("name", "") for p in presets]
        self.assertEqual(len(set(names)), len(names),
                         f"Preset names must be distinct, got {names}")

    def test_change_preset_binding_uses_controller_action_verb(self):
        """Switch binding must use 'controller_action change_preset <id> ...' format.

        NOTE: change_preset is an UNVERIFIED-HIGH-RISK hypothesis — no real-config
        evidence exists. This test pins the generator output to the candidate verb;
        it does NOT confirm Steam accepts the string. Runner must verify empirically.
        """
        import re
        found = re.search(r'controller_action change_preset (\d+)', self.text)
        self.assertIsNotNone(found,
            "No 'controller_action change_preset <id>' binding found — "
            "verb is UNVERIFIED-HIGH-RISK hypothesis")

    def test_change_preset_binding_references_known_preset_ids(self):
        """Each change_preset target id must correspond to a declared preset."""
        import re
        presets = [v for k, v in self.root if k == "preset"]
        declared_ids = {p.get_first("id") for p in presets}
        for m in re.finditer(r'controller_action change_preset (\d+)', self.text):
            ref_id = m.group(1)
            self.assertIn(ref_id, declared_ids,
                f"change_preset references id {ref_id!r} not in declared presets {declared_ids}")

    def test_serializes_without_parse_error(self):
        reparsed = _parse(self.text)
        self.assertIsNotNone(reparsed.get_first("controller_mappings"))

    def test_no_high_fkeys_in_layout(self):
        """F13+ must not appear — unproven binding tokens on this stack."""
        keys = _binding_keys(self.text)
        high = [k for k in keys if k.startswith("F") and k[1:].isdigit() and int(k[1:]) >= 13]
        self.assertEqual(high, [], f"Unexpected high F-keys in action_set_swap layout: {high}")

    def test_no_f11_f12_in_layout(self):
        """F11 and F12 must not appear — they alias to L1/L2 keysyms in xinput output."""
        keys = _binding_keys(self.text)
        bad = [k for k in keys if k in ("F11", "F12")]
        self.assertEqual(bad, [], f"F11/F12 present in action_set_swap layout: {bad}")

    def test_all_keys_unique_in_layout(self):
        """Every (button, activator) → unique key. No two activators share a binding key."""
        keys = _binding_keys(self.text)
        fkeys = [k for k in keys if k.startswith("F") and k[1:].isdigit()]
        self.assertEqual(len(fkeys), len(set(fkeys)),
                         f"Duplicate F-keys in action_set_swap layout: {fkeys}")


# ---------------------------------------------------------------------------
# Key-uniqueness generator invariant
# ---------------------------------------------------------------------------
#
# assert_all_keys_unique() must raise ValueError if called with a VDF text
# that contains duplicate F-key bindings — one test per factory function to
# confirm the invariant is wired in, not just present.  These tests are
# intentionally white-box: they synthesise a minimal collision and call the
# invariant directly (or monkey-patch emit to inject a collision), so they
# stay fast and self-contained.
# ---------------------------------------------------------------------------

class TestKeyUniquenessInvariant(unittest.TestCase):
    """assert_all_keys_unique raises on collision; passes on clean text."""

    # --- Unit tests for the invariant function itself ---

    def test_raises_on_duplicate_fkey(self):
        """A VDF snippet with two key_press F3 bindings must raise."""
        colliding = (
            '"controller_mappings"\n{\n'
            '  "group"\n  {\n'
            '    "binding"\t\t"key_press F3, , "\n'
            '    "binding"\t\t"key_press F3, , "\n'
            '  }\n'
            '}\n'
        )
        with self.assertRaises(ValueError) as ctx:
            vg.assert_all_keys_unique(colliding, "test_collision")
        self.assertIn("F3", str(ctx.exception))

    def test_passes_on_unique_fkeys(self):
        """A VDF snippet with distinct keys must not raise."""
        clean = (
            '"controller_mappings"\n{\n'
            '  "group"\n  {\n'
            '    "binding"\t\t"key_press F1, , "\n'
            '    "binding"\t\t"key_press F2, , "\n'
            '    "binding"\t\t"key_press F3, , "\n'
            '  }\n'
            '}\n'
        )
        vg.assert_all_keys_unique(clean, "test_unique")  # must not raise

    def test_ignores_non_fkey_bindings(self):
        """Non-F-key bindings (SPACE, ENTER, etc.) are not checked."""
        mixed = (
            '"controller_mappings"\n{\n'
            '  "group"\n  {\n'
            '    "binding"\t\t"key_press SPACE, , "\n'
            '    "binding"\t\t"key_press SPACE, , "\n'
            '    "binding"\t\t"key_press F1, , "\n'
            '  }\n'
            '}\n'
        )
        vg.assert_all_keys_unique(mixed, "test_non_fkey")  # must not raise

    # --- Per-factory collision tests (invariant is wired into each factory) ---
    # Strategy: patch emit() to append a duplicate binding line, then call the
    # factory. The factory calls assert_all_keys_unique on the result of emit(),
    # so it must raise before returning.

    def _make_collision_emit(self, key):
        """Return a patched emit that appends a duplicate key_press <key> line."""
        original_emit = vg.emit
        def patched_emit(pairs, indent=0):
            text = original_emit(pairs, indent)
            if indent == 0:
                # Inject a duplicate at top level to guarantee collision
                text += f'\n"binding"\t\t"key_press {key}, , "\n'
                text += f'\n"binding"\t\t"key_press {key}, , "\n'
            return text
        return patched_emit

    def test_marker_factory_raises_on_collision(self):
        """make_marker_layout must raise when emit produces a duplicate key."""
        original = vg.emit
        try:
            vg.emit = self._make_collision_emit("F3")
            with self.assertRaises(ValueError):
                vg.make_marker_layout(190)
        finally:
            vg.emit = original

    def test_remove_layer_factory_raises_on_collision(self):
        """make_remove_layer_layout must raise when emit produces a duplicate key."""
        original = vg.emit
        try:
            vg.emit = self._make_collision_emit("F1")
            with self.assertRaises(ValueError):
                vg.make_remove_layer_layout()
        finally:
            vg.emit = original

    def test_action_set_swap_factory_raises_on_collision(self):
        """make_action_set_swap_layout must raise when emit produces a duplicate key."""
        original = vg.emit
        try:
            vg.emit = self._make_collision_emit("F1")
            with self.assertRaises(ValueError):
                vg.make_action_set_swap_layout()
        finally:
            vg.emit = original


# ---------------------------------------------------------------------------
# Layout-4: Release_Press discrimination layout
# ---------------------------------------------------------------------------
#
# Purpose: discriminate between bad-token and activator-interaction hypotheses
# for Release_Press being absent from the four-activator marker_layout.
#
# button_a: Release_Press → F1 ONLY (isolated — if this fires, token is good)
# button_b: Start_Press → F2 + Release_Press → F3 (Start/Release pair — no Full/Double)
# button_x: Full_Press → F4 + Release_Press → F5 (suspected blocker pair — Full+Release)
# button_y: Double_Press (DTT=190) → F6 + Release_Press → F7 (Double+Release pair)
#
# Invariants: F1–F10 only, all keys unique, round-trip validated.
# ---------------------------------------------------------------------------

class TestReleasePressIsolatedLayout(unittest.TestCase):
    def setUp(self):
        self.text = vg.make_release_press_isolated_layout()
        self.pairs = _parse(self.text)
        root = self.pairs.get_first("controller_mappings")
        self.groups = {}
        for k, v in root:
            if k == "group":
                mode = v.get_first("mode")
                self.groups.setdefault(mode, []).append(v)

    def _inputs(self):
        """Return the inputs Pairs from the four_buttons group."""
        return self.groups["four_buttons"][0].get_first("inputs")

    # --- button_a: isolated Release_Press → F1 ---

    def test_button_a_has_only_release_press(self):
        """button_a must have ONLY Release_Press (no Full_Press, Start_Press, Double_Press)."""
        inp = self._inputs()
        btn = inp.get_first("button_a")
        self.assertIsNotNone(btn, "button_a missing")
        acts = btn.get_first("activators")
        # Must have Release_Press
        rp = acts.get_first("Release_Press")
        self.assertIsNotNone(rp, "button_a Release_Press missing")
        # Must NOT have any other activator type
        for act_type in ("Full_Press", "Long_Press", "Double_Press", "Start_Press"):
            self.assertIsNone(acts.get_first(act_type),
                f"button_a must have ONLY Release_Press; found extra activator {act_type}")

    def test_button_a_release_press_f1(self):
        """button_a Release_Press → F1."""
        inp = self._inputs()
        btn = inp.get_first("button_a")
        rp = btn.get_first("activators").get_first("Release_Press")
        binding = rp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF1\b")

    # --- button_b: Start_Press → F2 + Release_Press → F3 ---

    def test_button_b_has_start_press_and_release_press_only(self):
        """button_b must have Start_Press and Release_Press, no Full/Long/Double."""
        inp = self._inputs()
        btn = inp.get_first("button_b")
        self.assertIsNotNone(btn, "button_b missing")
        acts = btn.get_first("activators")
        self.assertIsNotNone(acts.get_first("Start_Press"),
            "button_b Start_Press missing")
        self.assertIsNotNone(acts.get_first("Release_Press"),
            "button_b Release_Press missing")
        for act_type in ("Full_Press", "Long_Press", "Double_Press"):
            self.assertIsNone(acts.get_first(act_type),
                f"button_b must have only Start/Release_Press; found {act_type}")

    def test_button_b_start_press_f2(self):
        """button_b Start_Press → F2."""
        inp = self._inputs()
        btn = inp.get_first("button_b")
        sp = btn.get_first("activators").get_first("Start_Press")
        binding = sp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF2\b")

    def test_button_b_release_press_f3(self):
        """button_b Release_Press → F3."""
        inp = self._inputs()
        btn = inp.get_first("button_b")
        rp = btn.get_first("activators").get_first("Release_Press")
        binding = rp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF3\b")

    # --- button_x: Full_Press → F4 + Release_Press → F5 ---

    def test_button_x_has_full_press_and_release_press(self):
        """button_x must have Full_Press and Release_Press (suspected blocker pair)."""
        inp = self._inputs()
        btn = inp.get_first("button_x")
        self.assertIsNotNone(btn, "button_x missing")
        acts = btn.get_first("activators")
        self.assertIsNotNone(acts.get_first("Full_Press"),
            "button_x Full_Press missing")
        self.assertIsNotNone(acts.get_first("Release_Press"),
            "button_x Release_Press missing")

    def test_button_x_full_press_f4(self):
        """button_x Full_Press → F4."""
        inp = self._inputs()
        btn = inp.get_first("button_x")
        fp = btn.get_first("activators").get_first("Full_Press")
        binding = fp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF4\b")

    def test_button_x_release_press_f5(self):
        """button_x Release_Press → F5."""
        inp = self._inputs()
        btn = inp.get_first("button_x")
        rp = btn.get_first("activators").get_first("Release_Press")
        binding = rp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF5\b")

    # --- button_y: Double_Press (DTT=190) → F6 + Release_Press → F7 ---

    def test_button_y_has_double_press_and_release_press(self):
        """button_y must have Double_Press and Release_Press."""
        inp = self._inputs()
        btn = inp.get_first("button_y")
        self.assertIsNotNone(btn, "button_y missing")
        acts = btn.get_first("activators")
        self.assertIsNotNone(acts.get_first("Double_Press"),
            "button_y Double_Press missing")
        self.assertIsNotNone(acts.get_first("Release_Press"),
            "button_y Release_Press missing")

    def test_button_y_double_press_f6_dtt_190(self):
        """button_y Double_Press → F6 with double_tap_time=190."""
        inp = self._inputs()
        btn = inp.get_first("button_y")
        dp = btn.get_first("activators").get_first("Double_Press")
        binding = dp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF6\b")
        settings = dp.get_first("settings")
        self.assertIsNotNone(settings, "Double_Press settings missing (need double_tap_time)")
        self.assertEqual(settings.get_first("double_tap_time"), "190")

    def test_button_y_release_press_f7(self):
        """button_y Release_Press → F7."""
        inp = self._inputs()
        btn = inp.get_first("button_y")
        rp = btn.get_first("activators").get_first("Release_Press")
        binding = rp.get_first("bindings").get_first("binding")
        self.assertRegex(binding, r"\bF7\b")

    # --- Layout-wide invariants ---

    def test_all_keys_unique(self):
        """Every (button, activator) → unique key. F1–F7 must each appear exactly once."""
        keys = _binding_keys(self.text)
        fkeys = [k for k in keys if k.startswith("F") and k[1:].isdigit()]
        self.assertEqual(len(fkeys), len(set(fkeys)),
            f"Duplicate F-keys in release_press_isolated layout: {fkeys}")

    def test_no_f11_f12(self):
        """F11/F12 must not appear — alias to L1/L2 in xinput."""
        keys = _binding_keys(self.text)
        bad = [k for k in keys if k in ("F11", "F12")]
        self.assertEqual(bad, [], f"F11/F12 present in layout: {bad}")

    def test_no_high_fkeys(self):
        """F13+ must not appear — unproven on this stack."""
        keys = _binding_keys(self.text)
        high = [k for k in keys if k.startswith("F") and k[1:].isdigit() and int(k[1:]) >= 13]
        self.assertEqual(high, [], f"Unexpected high F-keys: {high}")

    def test_round_trip(self):
        """Layout must survive parse→emit→reparse."""
        reparsed = _parse(self.text)
        self.assertIsNotNone(reparsed.get_first("controller_mappings"))

    def test_collision_invariant_wired(self):
        """Factory must raise ValueError when emit produces a duplicate key."""
        original = vg.emit
        try:
            # Inject a collision using the same helper pattern as Task #2 tests
            orig_emit = vg.emit
            def _patched(pairs, indent=0):
                text = orig_emit(pairs, indent)
                if indent == 0:
                    text += '\n"binding"\t\t"key_press F1, , "\n'
                    text += '\n"binding"\t\t"key_press F1, , "\n'
                return text
            vg.emit = _patched
            with self.assertRaises(ValueError):
                vg.make_release_press_isolated_layout()
        finally:
            vg.emit = original


# ---------------------------------------------------------------------------
# Activator slot-order preservation (prerequisite for permutation layouts)
# ---------------------------------------------------------------------------

def _activator_slot_order(text: str, button_name: str) -> list:
    """Return the list of activator_type names in slot order for a given button.

    Searches for the button's activators block in the emitted VDF text by:
    1. Finding the button_name key
    2. Extracting the activators sub-block
    3. Collecting activator_type values in textual order

    Returns a list of activator type strings in their slot order.
    """
    import re
    # Find all activator_type values in the full text under the named button.
    # Strategy: locate the button block by name, then extract activator_type values.
    # We use the Pairs tree for this (order-preserving) rather than regex.
    pairs = _parse(text)
    root = pairs.get_first("controller_mappings")
    # Search all groups for the button
    for k, v in root:
        if k != "group":
            continue
        inputs = v.get_first("inputs")
        if inputs is None:
            continue
        btn = inputs.get_first(button_name)
        if btn is None:
            continue
        activators = btn.get_first("activators")
        if activators is None:
            return []
        # Keys of the activators Pairs are the slot names (e.g. "Start_Press")
        return [act_key for act_key, _ in activators]
    return []


class TestActivatorSlotOrderPreservation(unittest.TestCase):
    """Slot order in the emitted VDF text must match the spec order.

    Prerequisite for the permutation layouts: if the parser/emitter does not
    preserve activator block order, the permutation layouts cannot represent
    distinct slot orderings — that would be a blocking defect.
    """

    def test_emit_preserves_activator_slot_order(self):
        """Activator slots emitted in construction order (R, S, L)."""
        btn = vg._button_input([
            ("Release_Press", vg.make_activator("Release_Press", "F1")),
            ("Start_Press",   vg.make_activator("Start_Press",   "F2")),
            ("Long_Press",    vg.make_activator("Long_Press",    "F3")),
        ])
        text = vg.emit(btn)
        import re
        order = re.findall(r'"activator_type"\s+"(\w+)"', text)
        self.assertEqual(order, ["Release_Press", "Start_Press", "Long_Press"])

    def test_roundtrip_preserves_activator_slot_order(self):
        """Slot order must survive parse → emit → reparse unchanged."""
        btn = vg._button_input([
            ("Release_Press", vg.make_activator("Release_Press", "F1")),
            ("Start_Press",   vg.make_activator("Start_Press",   "F2")),
            ("Long_Press",    vg.make_activator("Long_Press",    "F3")),
        ])
        text = vg.emit(btn)
        # Round-trip via tokenize/parse/emit
        tokens = vg.tokenize(text)
        pairs, _ = vg.parse(tokens)
        text2 = vg.emit(pairs)
        import re
        order1 = re.findall(r'"activator_type"\s+"(\w+)"', text)
        order2 = re.findall(r'"activator_type"\s+"(\w+)"', text2)
        self.assertEqual(order1, order2,
            f"Slot order changed through round-trip: {order1} → {order2}")

    def test_different_orders_produce_different_text(self):
        """Two buttons with swapped slot order must differ in the emitted text position."""
        btn_srl = vg._button_input([
            ("Start_Press",   vg.make_activator("Start_Press",   "F1")),
            ("Release_Press", vg.make_activator("Release_Press", "F2")),
            ("Long_Press",    vg.make_activator("Long_Press",    "F3")),
        ])
        btn_rsl = vg._button_input([
            ("Release_Press", vg.make_activator("Release_Press", "F2")),
            ("Start_Press",   vg.make_activator("Start_Press",   "F1")),
            ("Long_Press",    vg.make_activator("Long_Press",    "F3")),
        ])
        text_srl = vg.emit(btn_srl)
        text_rsl = vg.emit(btn_rsl)
        import re
        order_srl = re.findall(r'"activator_type"\s+"(\w+)"', text_srl)
        order_rsl = re.findall(r'"activator_type"\s+"(\w+)"', text_rsl)
        self.assertNotEqual(order_srl, order_rsl,
            "Different slot orderings must produce different textual block order")
        self.assertEqual(order_srl, ["Start_Press", "Release_Press", "Long_Press"])
        self.assertEqual(order_rsl, ["Release_Press", "Start_Press", "Long_Press"])


# ---------------------------------------------------------------------------
# Layouts 5–10: Activator slot-order permutation layouts
# ---------------------------------------------------------------------------
#
# Context (findings/steam_lane_behavior.md §Order-dependent edge-activator loss):
# Edge-fired activators (Start_Press, Release_Press) are eaten or fire incorrectly
# as a function of their SLOT ORDER when a state-bound activator (Long_Press,
# Double_Press) shares the button.
#
# GUI-observed (user, 2026-06-12):
#   (S, R, L): Start never fires; Release fires early
#   (R, S, L): all three fire  ← the slot-order fix
#
# Lab correlation: our marker button (S, R, F, D) → Start fires / Release eaten.
#
# Purpose: systematic order-permutation matrix across {S,R,L}, {S,R,D}, and the
# 4-activator case to map the eat-pattern precisely.
#
# Set A (Long as state-bound): all 6 orderings of {Start, Release, Long}
#   Layout A1: P1=(S,R,L) P2=(S,L,R) P3=(R,S,L)  + canary
#   Layout A2: P4=(R,L,S) P5=(L,S,R) P6=(L,R,S)  + canary
#
# Set B (Double as state-bound, DTT=190): all 6 orderings of {Start, Release, Double}
#   Layout B1: P1=(S,R,D) P2=(S,D,R) P3=(R,S,D)  + canary
#   Layout B2: P4=(R,D,S) P5=(D,S,R) P6=(D,R,S)  + canary
#
# Set C (4-activator variants):
#   Layout C1: PC1=(S,R,F,D)[committed,known-eat-R] PC2=(R,S,F,D)[reverse-edge]
#   Layout C2: PC3=(F,D,S,R)[Full-first-A]          PC4=(F,S,D,R)[Full-first-B]
#
# F-key assignment (F1–F10 only; 3 activators × 3 per permutation button):
#   Each layout: button_a→F1-F3, button_b→F4-F6, button_x→F7-F9, button_y→F10 canary
#   Within each button, keys assigned by activator type role:
#     Set A/B: Start→Fn, Release→Fn+1, Long/Double→Fn+2 (regardless of slot order)
#     Set C: Start→Fn, Release→Fn+1, Full→Fn+2, Double→Fn+3 (2 buttons per layout)
#
# Bug predictions (from finding):
#   P3=(R,S,L): all fire (GUI-verified)
#   P1=(S,R,L): Start never fires; Release fires early (GUI-verified)
#   All others: UNKNOWN — that is the point of this matrix.
# ---------------------------------------------------------------------------

# Slot-order names for documentation
_A_PERMS = [
    ("P1", ("Start_Press", "Release_Press", "Long_Press")),
    ("P2", ("Start_Press", "Long_Press",    "Release_Press")),
    ("P3", ("Release_Press", "Start_Press", "Long_Press")),
    ("P4", ("Release_Press", "Long_Press",  "Start_Press")),
    ("P5", ("Long_Press",    "Start_Press", "Release_Press")),
    ("P6", ("Long_Press",    "Release_Press", "Start_Press")),
]

_B_PERMS = [
    ("P1", ("Start_Press",  "Release_Press", "Double_Press")),
    ("P2", ("Start_Press",  "Double_Press",  "Release_Press")),
    ("P3", ("Release_Press","Start_Press",   "Double_Press")),
    ("P4", ("Release_Press","Double_Press",  "Start_Press")),
    ("P5", ("Double_Press", "Start_Press",   "Release_Press")),
    ("P6", ("Double_Press", "Release_Press", "Start_Press")),
]

_C_PERMS = [
    ("PC1", ("Start_Press", "Release_Press", "Full_Press",   "Double_Press")),  # committed, known-eat-R
    ("PC2", ("Release_Press","Start_Press",  "Full_Press",   "Double_Press")),  # reverse-edge
    ("PC3", ("Full_Press",   "Double_Press", "Start_Press",  "Release_Press")), # Full-first-A
    ("PC4", ("Full_Press",   "Start_Press",  "Double_Press", "Release_Press")), # Full-first-B
]


def _check_slot_order_layout(tc, factory_fn, layout_name,
                              perms_on_buttons,
                              canary_button=None, dtt=None):
    """Shared verifier for all slot-order permutation layouts.

    perms_on_buttons: list of (button_name, perm_name, slot_order_tuple, fkey_map)
      where fkey_map = {activator_type: Fkey_string}
    canary_button: (button_name, fkey) if present
    """
    kwargs = {} if dtt is None else {"double_tap_time": dtt}
    text = factory_fn(**kwargs)

    # 1. Round-trip
    reparsed = _parse(text)
    tc.assertIsNotNone(reparsed.get_first("controller_mappings"),
        f"{layout_name}: round-trip lost controller_mappings")

    # 2. Slot order assertions
    for btn_name, perm_name, slot_order, fkey_map in perms_on_buttons:
        actual_order = _activator_slot_order(text, btn_name)
        tc.assertEqual(list(slot_order), actual_order,
            f"{layout_name}/{btn_name} ({perm_name}): "
            f"expected slot order {list(slot_order)}, got {actual_order}")

    # 3. F-key binding assertions
    for btn_name, perm_name, slot_order, fkey_map in perms_on_buttons:
        pairs = _parse(text)
        root = pairs.get_first("controller_mappings")
        for k, v in root:
            if k != "group":
                continue
            inputs = v.get_first("inputs")
            if inputs is None:
                continue
            btn = inputs.get_first(btn_name)
            if btn is None:
                continue
            activators = btn.get_first("activators")
            for act_type, expected_fkey in fkey_map.items():
                act = activators.get_first(act_type)
                tc.assertIsNotNone(act,
                    f"{layout_name}/{btn_name}: activator {act_type} missing")
                binding = act.get_first("bindings").get_first("binding")
                tc.assertRegex(binding, rf'\b{expected_fkey}\b',
                    f"{layout_name}/{btn_name}/{act_type}: "
                    f"expected {expected_fkey}, got {binding!r}")

    # 4. F-key uniqueness
    fkeys = [k for k in _binding_keys(text) if k.startswith("F") and k[1:].isdigit()]
    tc.assertEqual(len(fkeys), len(set(fkeys)),
        f"{layout_name}: duplicate F-keys {fkeys}")

    # 5. No F11/F12/F13+
    for k in fkeys:
        if k in ("F11", "F12"):
            tc.fail(f"{layout_name}: {k} present (xinput alias)")
        n = int(k[1:])
        tc.assertLessEqual(n, 10, f"{layout_name}: {k} is unproven on this stack")

    # 6. Canary
    if canary_button:
        btn_name, fkey = canary_button
        actual_order = _activator_slot_order(text, btn_name)
        tc.assertGreater(len(actual_order), 0,
            f"{layout_name}: canary {btn_name} missing")


class TestSlotOrderPrerequisite(unittest.TestCase):
    """Slot order is representable and round-trip-stable (blocking check)."""

    def test_slot_order_preserved_in_full_layout_context(self):
        """Activator slot order must survive a full layout round-trip (controller_mappings root)."""
        # Build a minimal layout text with a known slot order
        btn = vg._button_input([
            ("Release_Press", vg.make_activator("Release_Press", "F1")),
            ("Start_Press",   vg.make_activator("Start_Press",   "F2")),
        ])
        four_buttons_group = vg._p(
            ("id", "6"), ("mode", "four_buttons"),
            ("name", ""), ("description", ""),
            ("inputs", vg._p(("button_a", btn))),
        )
        switches_group = vg._p(
            ("id", "0"), ("mode", "switches"),
            ("name", ""), ("description", ""),
            ("inputs", vg.Pairs()),
        )
        cm = vg.Pairs(vg._controller_mappings_header())
        cm.append(("group", switches_group))
        cm.append(("group", four_buttons_group))
        cm.append(vg._preset("0", "Default", vg._p(("0", "switch active"), ("6", "button_diamond active"))))
        cm.append(("settings", vg.Pairs()))
        root_pairs = vg._p(("controller_mappings", cm))
        text = vg.emit(root_pairs)

        # Round-trip
        tokens = vg.tokenize(text)
        pairs, _ = vg.parse(tokens)
        text2 = vg.emit(pairs)

        import re
        order1 = re.findall(r'"activator_type"\s+"(\w+)"', text)
        order2 = re.findall(r'"activator_type"\s+"(\w+)"', text2)
        self.assertEqual(order1, ["Release_Press", "Start_Press"],
            f"Pre-round-trip order wrong: {order1}")
        self.assertEqual(order1, order2,
            f"Slot order changed through full-layout round-trip: {order1} → {order2}")


class TestSlotOrderSetA1(unittest.TestCase):
    """Set A, Layout 1: Long state-bound, permutations P1=(S,R,L), P2=(S,L,R), P3=(R,S,L)."""

    # F-key map: Start→Fn, Release→Fn+1, Long→Fn+2 per button block
    _PERMS = [
        ("button_a", "P1", ("Start_Press",   "Release_Press", "Long_Press"),
         {"Start_Press": "F1", "Release_Press": "F2", "Long_Press": "F3"}),
        ("button_b", "P2", ("Start_Press",   "Long_Press",    "Release_Press"),
         {"Start_Press": "F4", "Release_Press": "F5", "Long_Press": "F6"}),
        ("button_x", "P3", ("Release_Press", "Start_Press",   "Long_Press"),
         {"Start_Press": "F7", "Release_Press": "F8", "Long_Press": "F9"}),
    ]
    _CANARY = ("button_y", "F10")

    def test_all_permutations_and_invariants(self):
        _check_slot_order_layout(self, vg.make_slot_order_set_a1_layout,
                                 "slot_order_set_a1",
                                 self._PERMS, self._CANARY)

    def test_p1_slot_order(self):
        text = vg.make_slot_order_set_a1_layout()
        self.assertEqual(_activator_slot_order(text, "button_a"),
                         ["Start_Press", "Release_Press", "Long_Press"],
                         "P1=(S,R,L): button_a slot order wrong")

    def test_p2_slot_order(self):
        text = vg.make_slot_order_set_a1_layout()
        self.assertEqual(_activator_slot_order(text, "button_b"),
                         ["Start_Press", "Long_Press", "Release_Press"],
                         "P2=(S,L,R): button_b slot order wrong")

    def test_p3_slot_order_gui_verified(self):
        """P3=(R,S,L) is the GUI-verified 'all three fire' ordering."""
        text = vg.make_slot_order_set_a1_layout()
        self.assertEqual(_activator_slot_order(text, "button_x"),
                         ["Release_Press", "Start_Press", "Long_Press"],
                         "P3=(R,S,L): button_x slot order wrong")


class TestSlotOrderSetA2(unittest.TestCase):
    """Set A, Layout 2: Long state-bound, permutations P4=(R,L,S), P5=(L,S,R), P6=(L,R,S)."""

    _PERMS = [
        ("button_a", "P4", ("Release_Press", "Long_Press",    "Start_Press"),
         {"Start_Press": "F1", "Release_Press": "F2", "Long_Press": "F3"}),
        ("button_b", "P5", ("Long_Press",    "Start_Press",   "Release_Press"),
         {"Start_Press": "F4", "Release_Press": "F5", "Long_Press": "F6"}),
        ("button_x", "P6", ("Long_Press",    "Release_Press", "Start_Press"),
         {"Start_Press": "F7", "Release_Press": "F8", "Long_Press": "F9"}),
    ]
    _CANARY = ("button_y", "F10")

    def test_all_permutations_and_invariants(self):
        _check_slot_order_layout(self, vg.make_slot_order_set_a2_layout,
                                 "slot_order_set_a2",
                                 self._PERMS, self._CANARY)

    def test_p4_slot_order(self):
        text = vg.make_slot_order_set_a2_layout()
        self.assertEqual(_activator_slot_order(text, "button_a"),
                         ["Release_Press", "Long_Press", "Start_Press"])

    def test_p5_slot_order(self):
        text = vg.make_slot_order_set_a2_layout()
        self.assertEqual(_activator_slot_order(text, "button_b"),
                         ["Long_Press", "Start_Press", "Release_Press"])

    def test_p6_slot_order(self):
        text = vg.make_slot_order_set_a2_layout()
        self.assertEqual(_activator_slot_order(text, "button_x"),
                         ["Long_Press", "Release_Press", "Start_Press"])


class TestSlotOrderSetA_Coverage(unittest.TestCase):
    """All 6 Long-state-bound permutations appear exactly once across A1+A2."""

    def test_all_six_long_permutations_covered(self):
        """Every ordering of {Start, Release, Long} appears exactly once across A1 + A2."""
        import itertools
        all_expected = set(itertools.permutations(
            ("Start_Press", "Release_Press", "Long_Press")))
        seen = set()
        for factory, buttons in [
            (vg.make_slot_order_set_a1_layout, ["button_a", "button_b", "button_x"]),
            (vg.make_slot_order_set_a2_layout, ["button_a", "button_b", "button_x"]),
        ]:
            text = factory()
            for btn in buttons:
                order = tuple(_activator_slot_order(text, btn))
                self.assertNotIn(order, seen,
                    f"Duplicate permutation {order} in layout")
                seen.add(order)
        self.assertEqual(seen, all_expected,
            f"Not all 6 permutations covered.\nMissing: {all_expected - seen}\nExtra: {seen - all_expected}")


class TestSlotOrderSetB1(unittest.TestCase):
    """Set B, Layout 1: Double state-bound (DTT=190), P1=(S,R,D), P2=(S,D,R), P3=(R,S,D)."""

    _PERMS = [
        ("button_a", "P1", ("Start_Press",   "Release_Press", "Double_Press"),
         {"Start_Press": "F1", "Release_Press": "F2", "Double_Press": "F3"}),
        ("button_b", "P2", ("Start_Press",   "Double_Press",  "Release_Press"),
         {"Start_Press": "F4", "Release_Press": "F5", "Double_Press": "F6"}),
        ("button_x", "P3", ("Release_Press", "Start_Press",   "Double_Press"),
         {"Start_Press": "F7", "Release_Press": "F8", "Double_Press": "F9"}),
    ]
    _CANARY = ("button_y", "F10")

    def test_all_permutations_and_invariants(self):
        _check_slot_order_layout(self, vg.make_slot_order_set_b1_layout,
                                 "slot_order_set_b1",
                                 self._PERMS, self._CANARY, dtt=190)

    def test_p1_slot_order(self):
        text = vg.make_slot_order_set_b1_layout(double_tap_time=190)
        self.assertEqual(_activator_slot_order(text, "button_a"),
                         ["Start_Press", "Release_Press", "Double_Press"])

    def test_p3_slot_order(self):
        text = vg.make_slot_order_set_b1_layout(double_tap_time=190)
        self.assertEqual(_activator_slot_order(text, "button_x"),
                         ["Release_Press", "Start_Press", "Double_Press"])

    def test_dtt_190_on_all_double_press_activators(self):
        """Every Double_Press activator must have double_tap_time=190."""
        pairs = _parse(vg.make_slot_order_set_b1_layout(double_tap_time=190))
        root = pairs.get_first("controller_mappings")
        for k, v in root:
            if k != "group":
                continue
            inputs = v.get_first("inputs")
            if inputs is None:
                continue
            for btn_name in ("button_a", "button_b", "button_x"):
                btn = inputs.get_first(btn_name)
                if btn is None:
                    continue
                acts = btn.get_first("activators")
                dp = acts.get_first("Double_Press")
                if dp is None:
                    continue
                settings = dp.get_first("settings")
                self.assertIsNotNone(settings,
                    f"{btn_name} Double_Press missing settings (need double_tap_time)")
                self.assertEqual(settings.get_first("double_tap_time"), "190")


class TestSlotOrderSetB2(unittest.TestCase):
    """Set B, Layout 2: Double state-bound, P4=(R,D,S), P5=(D,S,R), P6=(D,R,S)."""

    _PERMS = [
        ("button_a", "P4", ("Release_Press", "Double_Press",  "Start_Press"),
         {"Start_Press": "F1", "Release_Press": "F2", "Double_Press": "F3"}),
        ("button_b", "P5", ("Double_Press",  "Start_Press",   "Release_Press"),
         {"Start_Press": "F4", "Release_Press": "F5", "Double_Press": "F6"}),
        ("button_x", "P6", ("Double_Press",  "Release_Press", "Start_Press"),
         {"Start_Press": "F7", "Release_Press": "F8", "Double_Press": "F9"}),
    ]
    _CANARY = ("button_y", "F10")

    def test_all_permutations_and_invariants(self):
        _check_slot_order_layout(self, vg.make_slot_order_set_b2_layout,
                                 "slot_order_set_b2",
                                 self._PERMS, self._CANARY, dtt=190)

    def test_p4_slot_order(self):
        text = vg.make_slot_order_set_b2_layout(double_tap_time=190)
        self.assertEqual(_activator_slot_order(text, "button_a"),
                         ["Release_Press", "Double_Press", "Start_Press"])

    def test_p5_slot_order(self):
        text = vg.make_slot_order_set_b2_layout(double_tap_time=190)
        self.assertEqual(_activator_slot_order(text, "button_b"),
                         ["Double_Press", "Start_Press", "Release_Press"])

    def test_p6_slot_order(self):
        text = vg.make_slot_order_set_b2_layout(double_tap_time=190)
        self.assertEqual(_activator_slot_order(text, "button_x"),
                         ["Double_Press", "Release_Press", "Start_Press"])


class TestSlotOrderSetB_Coverage(unittest.TestCase):
    """All 6 Double-state-bound permutations appear exactly once across B1+B2."""

    def test_all_six_double_permutations_covered(self):
        import itertools
        all_expected = set(itertools.permutations(
            ("Start_Press", "Release_Press", "Double_Press")))
        seen = set()
        for factory, buttons in [
            (vg.make_slot_order_set_b1_layout, ["button_a", "button_b", "button_x"]),
            (vg.make_slot_order_set_b2_layout, ["button_a", "button_b", "button_x"]),
        ]:
            text = factory(double_tap_time=190)
            for btn in buttons:
                order = tuple(_activator_slot_order(text, btn))
                self.assertNotIn(order, seen,
                    f"Duplicate permutation {order}")
                seen.add(order)
        self.assertEqual(seen, all_expected,
            f"Not all 6 Double permutations covered.\n"
            f"Missing: {all_expected - seen}")


class TestSlotOrderSetC1(unittest.TestCase):
    """Set C, Layout 1: 4-activator variants PC1=(S,R,F,D) [committed] and PC2=(R,S,F,D) [reverse-edge]."""

    _PERMS = [
        ("button_a", "PC1",
         ("Start_Press", "Release_Press", "Full_Press", "Double_Press"),
         {"Start_Press": "F1", "Release_Press": "F2", "Full_Press": "F3", "Double_Press": "F4"}),
        ("button_b", "PC2",
         ("Release_Press", "Start_Press", "Full_Press", "Double_Press"),
         {"Start_Press": "F5", "Release_Press": "F6", "Full_Press": "F7", "Double_Press": "F8"}),
    ]

    def test_all_permutations_and_invariants(self):
        _check_slot_order_layout(self, vg.make_slot_order_set_c1_layout,
                                 "slot_order_set_c1",
                                 self._PERMS, dtt=190)

    def test_pc1_slot_order_matches_committed_marker(self):
        """PC1 must match the committed marker_layout.vdf slot order (S,R,F,D)."""
        text = vg.make_slot_order_set_c1_layout(double_tap_time=190)
        self.assertEqual(_activator_slot_order(text, "button_a"),
                         ["Start_Press", "Release_Press", "Full_Press", "Double_Press"],
                         "PC1 must match committed marker button order (known: eats Release)")

    def test_pc2_slot_order_reverse_edge(self):
        """PC2=(R,S,F,D) is the reverse-edge variant."""
        text = vg.make_slot_order_set_c1_layout(double_tap_time=190)
        self.assertEqual(_activator_slot_order(text, "button_b"),
                         ["Release_Press", "Start_Press", "Full_Press", "Double_Press"])

    def test_dtt_190_on_double_press(self):
        pairs = _parse(vg.make_slot_order_set_c1_layout(double_tap_time=190))
        root = pairs.get_first("controller_mappings")
        for k, v in root:
            if k != "group":
                continue
            inputs = v.get_first("inputs")
            if inputs is None:
                continue
            for btn_name in ("button_a", "button_b"):
                btn = inputs.get_first(btn_name)
                if btn is None:
                    continue
                dp = btn.get_first("activators").get_first("Double_Press")
                if dp is None:
                    continue
                settings = dp.get_first("settings")
                self.assertIsNotNone(settings)
                self.assertEqual(settings.get_first("double_tap_time"), "190")


class TestSlotOrderSetC2(unittest.TestCase):
    """Set C, Layout 2: Full-first variants PC3=(F,D,S,R) and PC4=(F,S,D,R)."""

    _PERMS = [
        ("button_a", "PC3",
         ("Full_Press", "Double_Press", "Start_Press", "Release_Press"),
         {"Start_Press": "F1", "Release_Press": "F2", "Full_Press": "F3", "Double_Press": "F4"}),
        ("button_b", "PC4",
         ("Full_Press", "Start_Press", "Double_Press", "Release_Press"),
         {"Start_Press": "F5", "Release_Press": "F6", "Full_Press": "F7", "Double_Press": "F8"}),
    ]

    def test_all_permutations_and_invariants(self):
        _check_slot_order_layout(self, vg.make_slot_order_set_c2_layout,
                                 "slot_order_set_c2",
                                 self._PERMS, dtt=190)

    def test_pc3_full_first_slot_order(self):
        text = vg.make_slot_order_set_c2_layout(double_tap_time=190)
        self.assertEqual(_activator_slot_order(text, "button_a"),
                         ["Full_Press", "Double_Press", "Start_Press", "Release_Press"])

    def test_pc4_full_first_b_slot_order(self):
        text = vg.make_slot_order_set_c2_layout(double_tap_time=190)
        self.assertEqual(_activator_slot_order(text, "button_b"),
                         ["Full_Press", "Start_Press", "Double_Press", "Release_Press"])


class TestSlotOrderSetC_Coverage(unittest.TestCase):
    """All 4 Set-C permutations appear exactly once across C1+C2."""

    def test_all_c_permutations_covered(self):
        expected = {
            ("Start_Press",   "Release_Press", "Full_Press",   "Double_Press"),  # PC1
            ("Release_Press", "Start_Press",   "Full_Press",   "Double_Press"),  # PC2
            ("Full_Press",    "Double_Press",  "Start_Press",  "Release_Press"), # PC3
            ("Full_Press",    "Start_Press",   "Double_Press", "Release_Press"), # PC4
        }
        seen = set()
        for factory, buttons in [
            (vg.make_slot_order_set_c1_layout, ["button_a", "button_b"]),
            (vg.make_slot_order_set_c2_layout, ["button_a", "button_b"]),
        ]:
            text = factory(double_tap_time=190)
            for btn in buttons:
                order = tuple(_activator_slot_order(text, btn))
                self.assertNotIn(order, seen, f"Duplicate C permutation: {order}")
                seen.add(order)
        self.assertEqual(seen, expected,
            f"C permutation coverage mismatch.\nMissing: {expected - seen}")


# ---------------------------------------------------------------------------
# Serializer
# ---------------------------------------------------------------------------

class TestSerializer(unittest.TestCase):
    def test_emit_roundtrip(self):
        """Parse the reference vdf and serialize — must reparse cleanly."""
        ref = Path(__file__).parent.parent / "reference" / "desktop-layout-phase2-reference.vdf"
        text = ref.read_text()
        tokens = vg.tokenize(text)
        pairs, _ = vg.parse(tokens)
        out = vg.emit(pairs)
        reparsed = _parse(out)
        root = reparsed.get_first("controller_mappings")
        self.assertIsNotNone(root)
        self.assertEqual(root.get_first("version"), "3")

    def test_emit_indentation(self):
        """Nested objects should indent with tabs."""
        pairs = vg.Pairs([("root", vg.Pairs([("k", "v")]))])
        out = vg.emit(pairs)
        self.assertIn("\t", out)


# ---------------------------------------------------------------------------
# parse-validate round-trip guard (the contract the task description requires)
# ---------------------------------------------------------------------------

class TestRoundTripOnGeneratedLayouts(unittest.TestCase):
    """All generated layouts must survive a parse→emit→reparse cycle."""

    def _check(self, text, label):
        pairs = _parse(text)
        self.assertIsNotNone(pairs.get_first("controller_mappings"),
                             f"{label}: no controller_mappings root after parse")
        out = vg.emit(pairs)
        reparsed = _parse(out)
        self.assertIsNotNone(reparsed.get_first("controller_mappings"),
                             f"{label}: no controller_mappings root after re-emit")

    def test_marker_layout(self):
        self._check(vg.make_marker_layout(190), "marker_layout")

    def test_remove_layer_layout(self):
        self._check(vg.make_remove_layer_layout(), "remove_layer_layout")

    def test_action_set_swap_layout(self):
        self._check(vg.make_action_set_swap_layout(), "action_set_swap_layout")
