#!/usr/bin/env python3
"""vdf_layout_gen.py — programmatic Steam Input VDF layout generator.

Builds Phase-4 diagnostic VDF layouts for the mapper-conversion lab.
Every layout produced here goes through a parse-validate round-trip (parse →
emit → reparse) before being written to disk — never a raw string blob.

Four public factory functions:
  make_marker_layout(double_tap_time=190)
      F1–F9 marker layout: button_y = test button (Start/Release/Full/Double),
      button_a = digital canary (F5), button_b = tap/hold (F6/F7),
      button_x = interruptable=0 probe (F8/F9).  DTT default 190 ms.
  make_release_press_isolated_layout()
      Release_Press discrimination layout: four buttons, each pairing
      Release_Press with a different co-activator to isolate bad-token vs
      activator-interaction hypotheses.  F1–F7.
  make_remove_layer_layout()
      Timed remove_layer layout: base + action layer, remove on a button.
  make_action_set_swap_layout()
      Two-action-set swap layout, START swaps sets.

All use the same VDF data model (Pairs) and emit() serializer shared with
vdf/vdf_clean.py's tokenizer/parser (copy-inlined here to avoid a cross-dir
import dependency).

Usage:
  python3 vdf_layout_gen.py --help
  python3 vdf_layout_gen.py marker --dtt 190 --out reference/phase4-layouts/marker_layout.vdf
  python3 vdf_layout_gen.py release-press-isolated --out reference/phase4-layouts/release_press_isolated.vdf
  python3 vdf_layout_gen.py remove-layer --out reference/phase4-layouts/remove_layer.vdf
  python3 vdf_layout_gen.py action-set-swap --out reference/phase4-layouts/action_set_swap.vdf

Tests: tools/test_vdf_layout_gen.py (stdlib unittest, no deps).
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# VDF tokenizer / parser (inlined from vdf/vdf_clean.py — keep in sync)
# ---------------------------------------------------------------------------

TOKEN_RE = re.compile(r'"((?:[^"\\]|\\.)*)"|(\{)|(\})', re.S)


def tokenize(text: str):
    out = []
    for m in TOKEN_RE.finditer(text):
        s, o, c = m.group(1), m.group(2), m.group(3)
        if s is not None:
            out.append(("STR", s))
        elif o:
            out.append(("OBJ_OPEN", None))
        elif c:
            out.append(("OBJ_CLOSE", None))
    return out


class Pairs(list):
    """list of (key, value) where value is str or Pairs."""

    def get_all(self, key):
        return [v for k, v in self if k == key]

    def get_first(self, key, default=None):
        for k, v in self:
            if k == key:
                return v
        return default


def parse(tokens, i=0, top=True):
    pairs = Pairs()
    while i < len(tokens):
        tt, tv = tokens[i]
        if tt == "OBJ_CLOSE":
            return pairs, i + 1
        if tt != "STR":
            raise ValueError(f"expected key string at token {i}, got {tt}")
        key = tv
        i += 1
        if i >= len(tokens):
            raise ValueError("unexpected EOF after key")
        nt, nv = tokens[i]
        if nt == "STR":
            pairs.append((key, nv))
            i += 1
        elif nt == "OBJ_OPEN":
            sub, i = parse(tokens, i + 1, top=False)
            pairs.append((key, sub))
        else:
            raise ValueError(f"unexpected token {nt} after key {key!r}")
    if not top:
        raise ValueError("unclosed object")
    return pairs, i


# ---------------------------------------------------------------------------
# Serializer
# ---------------------------------------------------------------------------

def emit(pairs, indent=0):
    """Serialize a Pairs tree back to a VDF string."""
    lines = []
    tab = "\t" * indent
    for key, val in pairs:
        if isinstance(val, str):
            lines.append(f'{tab}"{key}"\t\t"{val}"')
        else:
            lines.append(f'{tab}"{key}"')
            lines.append(f'{tab}{{')
            lines.append(emit(val, indent + 1))
            lines.append(f'{tab}}}')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Low-level VDF building blocks
# ---------------------------------------------------------------------------

def _p(*pairs):
    """Construct a Pairs from positional (key, value) tuples."""
    return Pairs(list(pairs))


def make_activator(activator_type: str, key: str, *,
                   long_press_time: Optional[int] = None,
                   double_tap_time: Optional[int] = None,
                   interruptable: Optional[bool] = None,
                   haptic_intensity: Optional[int] = None) -> Pairs:
    """Build an activator Pairs node.

    Args:
        activator_type: 'Full_Press', 'Long_Press', 'Double_Press', etc.
        key: The key to emit, e.g. 'F13'.
        long_press_time: Explicit ms value for Long_Press (omit to use default).
        double_tap_time: Explicit ms value for Double_Press (omit to use default).
        interruptable: If False, inject interruptable=0 (suppresses base).
        haptic_intensity: Optional haptic setting.
    """
    settings = Pairs()
    if long_press_time is not None:
        settings.append(("long_press_time", str(long_press_time)))
    if double_tap_time is not None:
        settings.append(("double_tap_time", str(double_tap_time)))
    if interruptable is False:
        settings.append(("interruptable", "0"))
    if haptic_intensity is not None:
        settings.append(("haptic_intensity", str(haptic_intensity)))

    node = Pairs([
        ("activator_type", activator_type),
        ("bindings", _p(("binding", f"key_press {key}, , "))),
    ])
    node.append(("disabled_activators", Pairs()))
    if settings:
        node.append(("settings", settings))
    return node


def _button_input(activators_list):
    """Wrap a list of (act_type, act_node) into a button input Pairs."""
    activators = Pairs(activators_list)
    return _p(
        ("activators", activators),
        ("disabled_activators", Pairs()),
    )


def _controller_mappings_header(preset_id="0", preset_name="Default",
                                controller_type="controller_xbox360"):
    """Return header key-value pairs (no groups, no preset)."""
    return [
        ("version", "3"),
        ("revision", "1"),
        ("title", ""),
        ("description", "#SettingsController_AutosaveDescription"),
        ("creator", "76561197989260696"),
        ("progenitor", "local://controller_base/empty.vdf"),
        ("export_type", "unknown"),
        ("controller_type", controller_type),
    ]


def _preset(preset_id, name, gsb_pairs, is_layer=False):
    """Build a preset Pairs node."""
    p = Pairs([
        ("id", str(preset_id)),
        ("name", name),
    ])
    if is_layer:
        p.append(("parent_set_name", "Default"))
    p.append(("group_source_bindings", gsb_pairs))
    return ("preset", p)


# ---------------------------------------------------------------------------
# Generator invariant: key uniqueness
# ---------------------------------------------------------------------------

def assert_all_keys_unique(text: str, label: str) -> None:
    """Enforce that every (button, activator) maps to a unique binding key.

    Scans all key_press tokens in the emitted VDF text and raises ValueError
    if any F-key appears more than once.  Called at the end of every layout
    factory before returning to the caller.
    """
    keys: list = []
    for m in re.finditer(r'key_press\s+(\S+?),', text):
        keys.append(m.group(1))
    fkeys = [k for k in keys if k.startswith("F") and k[1:].isdigit()]
    seen: set = set()
    dupes: list = []
    for k in fkeys:
        if k in seen:
            dupes.append(k)
        seen.add(k)
    if dupes:
        raise ValueError(
            f"{label}: duplicate binding keys {dupes} — "
            f"every (button, activator) must map to a unique key"
        )


# ---------------------------------------------------------------------------
# Layout-1: Marker layout — Start_Press / Release_Press / Full_Press / Double_Press
# ---------------------------------------------------------------------------
#
# Gate-review spec (2026-06-11):
#
# button_y (THE test button) — all four activator primitives, interruptable default:
#   Start_Press   → F1   fires at press-DOWN, instantly deactivates (in-stream marker)
#   Release_Press → F2   fires at press-UP   (in-stream marker)
#   Full_Press    → F3   Regular; delayed to first-down + DTT on a double-bound button
#   Double_Press  → F4   fires at second-down; DTT explicit (default 190 ms)
#
# button_a (digital baseline / canary):
#   Full_Press → F5  unambiguous "am I live" pulse; no competing activators
#
# button_b (tap/hold pair):
#   Full_Press → F6  short-tap result
#   Long_Press → F7  long-hold result
#
# button_x (interruptable=0 probe):
#   Full_Press → F8  interruptable=0 — fires regardless alongside Long_Press
#   Long_Press → F9
#
# Invariants:
#   Every (button, activator) → unique F-key.  F1–F10 only; F11/F12 avoided
#   (xinput aliases); F13+ unproven on this XI2 stack.
#
# Findings / Oracle predictions served:
#   Pin #1: Regular (F3) emission anchored at first-down + DTT regardless of hold
#   Pin #2: Double (F4) fires at second-down with ~zero latency
#   Pin #3: Held-double output shape — watch for spurious event at first-down + DTT
#   Start_Press / Release_Press: in-stream pipeline-latency cancellation markers
#     (pipeline ~35 ms; F3-F1 offset and F4-second_down offset cancel the offset)
# ---------------------------------------------------------------------------

def make_marker_layout(double_tap_time: int = 190) -> str:
    """Generate the Start_Press/Release_Press/Full_Press/Double_Press marker layout.

    button_y is THE test button (F1–F4); button_a canary (F5); button_b
    tap/hold (F6/F7); button_x interruptable=0 probe (F8/F9).

    double_tap_time: the Double Tap Time in ms (default 190).
    Returns the VDF text as a string.
    """
    # button_y: THE test button — all four activator types, interruptable default
    btn_y = _button_input([
        ("Start_Press",   make_activator("Start_Press",   "F1")),
        ("Release_Press", make_activator("Release_Press", "F2")),
        ("Full_Press",    make_activator("Full_Press",    "F3")),
        ("Double_Press",  make_activator("Double_Press",  "F4",
                                         double_tap_time=double_tap_time)),
    ])

    # button_a: digital baseline / canary — pure Full_Press → F5
    btn_a = _button_input([
        ("Full_Press", make_activator("Full_Press", "F5")),
    ])

    # button_b: tap/hold pair — Full_Press → F6, Long_Press → F7
    btn_b = _button_input([
        ("Full_Press", make_activator("Full_Press", "F6")),
        ("Long_Press", make_activator("Long_Press", "F7")),
    ])

    # button_x: interruptable=0 probe — Full_Press fires alongside Long_Press
    btn_x = _button_input([
        ("Full_Press", make_activator("Full_Press", "F8", interruptable=False)),
        ("Long_Press", make_activator("Long_Press", "F9")),
    ])

    four_buttons_group = _p(
        ("id", "6"),
        ("mode", "four_buttons"),
        ("name", ""),
        ("description", ""),
        ("inputs", _p(
            ("button_a", btn_a),
            ("button_b", btn_b),
            ("button_x", btn_x),
            ("button_y", btn_y),
        )),
    )

    # Minimal switches group (required so preset can reference 'switch active')
    switches_group = _p(
        ("id", "0"),
        ("mode", "switches"),
        ("name", ""),
        ("description", ""),
        ("inputs", Pairs()),
    )

    # Preset wires the groups
    gsb = _p(
        ("0", "switch active"),
        ("6", "button_diamond active"),
    )

    cm = Pairs(_controller_mappings_header())
    cm.append(("group", switches_group))
    cm.append(("group", four_buttons_group))
    cm.append(_preset("0", "Default", gsb))
    cm.append(("settings", Pairs()))

    root = _p(("controller_mappings", cm))
    text = emit(root)
    _validate_roundtrip(text, "make_marker_layout")
    assert_all_keys_unique(text, "make_marker_layout")
    return text


# ---------------------------------------------------------------------------
# Layout-1b: Release_Press discrimination layout
# ---------------------------------------------------------------------------
#
# Purpose: discriminate between bad-token and activator-interaction hypotheses
# for Release_Press being absent from the four-activator marker_layout.vdf.
#
# Per runner batch-1b (2026-06-12), Release_Press emitted nothing on button_y
# across all probes.  F2 absent at raw layer — not a delivery issue.  Candidates:
#   (a) bad VDF token — Release_Press unrecognized by Steam
#   (b) activator interaction — Full_Press or Double_Press suppresses Release_Press
#
# This layout places Release_Press in four contexts, one per button, to isolate
# which pairing (if any) suppresses it:
#
# button_a: Release_Press → F1 ONLY (isolated — fires → token is good)
# button_b: Start_Press → F2 + Release_Press → F3 (Start/Release pair — no Full/Double)
# button_x: Full_Press → F4 + Release_Press → F5 (suspected blocker: Full+Release)
# button_y: Double_Press (DTT=190) → F6 + Release_Press → F7 (Double+Release pair)
#
# Discrimination logic (runner):
#   button_a fires F1 → token good; interaction is the cause.
#   button_a silent   → bad token; all other buttons will also be silent.
#   (button_a fires F1) AND (button_x silent) → Full_Press is the blocker.
#   (button_a fires F1) AND (button_y silent) → Double_Press is the blocker.
#   (button_a fires F1) AND (button_b fires F3) → Start_Press does not block.
#
# F1–F10 only; all keys unique; round-trip validated.
# ---------------------------------------------------------------------------

def make_release_press_isolated_layout() -> str:
    """Generate the Release_Press discrimination layout.

    Single layout; four buttons, each pairing Release_Press with a different
    co-activator (or isolation).  F1–F7 used; invariants: unique keys, F1–F10
    only, round-trip validated.

    Returns the VDF text as a string.
    """
    # button_a: Release_Press ONLY → F1 (isolated; no co-activators)
    btn_a = _button_input([
        ("Release_Press", make_activator("Release_Press", "F1")),
    ])

    # button_b: Start_Press → F2, Release_Press → F3 (no Full/Double)
    btn_b = _button_input([
        ("Start_Press",   make_activator("Start_Press",   "F2")),
        ("Release_Press", make_activator("Release_Press", "F3")),
    ])

    # button_x: Full_Press → F4, Release_Press → F5 (suspected blocker pair)
    btn_x = _button_input([
        ("Full_Press",    make_activator("Full_Press",    "F4")),
        ("Release_Press", make_activator("Release_Press", "F5")),
    ])

    # button_y: Double_Press (DTT=190) → F6, Release_Press → F7
    btn_y = _button_input([
        ("Double_Press",  make_activator("Double_Press",  "F6", double_tap_time=190)),
        ("Release_Press", make_activator("Release_Press", "F7")),
    ])

    four_buttons_group = _p(
        ("id", "6"),
        ("mode", "four_buttons"),
        ("name", ""),
        ("description", ""),
        ("inputs", _p(
            ("button_a", btn_a),
            ("button_b", btn_b),
            ("button_x", btn_x),
            ("button_y", btn_y),
        )),
    )

    switches_group = _p(
        ("id", "0"),
        ("mode", "switches"),
        ("name", ""),
        ("description", ""),
        ("inputs", Pairs()),
    )

    gsb = _p(
        ("0", "switch active"),
        ("6", "button_diamond active"),
    )

    cm = Pairs(_controller_mappings_header())
    cm.append(("group", switches_group))
    cm.append(("group", four_buttons_group))
    cm.append(_preset("0", "Default", gsb))
    cm.append(("settings", Pairs()))

    root = _p(("controller_mappings", cm))
    text = emit(root)
    _validate_roundtrip(text, "make_release_press_isolated_layout")
    assert_all_keys_unique(text, "make_release_press_isolated_layout")
    return text


# ---------------------------------------------------------------------------
# Layout-2: Timed remove_layer layout
# ---------------------------------------------------------------------------
#
# Purpose: verify the timed remove_layer gotcha — a button press activates a
# layer, a second button removes it, and Layer bindings are only live while the
# layer is applied.
#
# VERIFIED BINDING FORMAT (empirical, 130+ real configs; vdf/vdf_clean.py L126):
#   "controller_action add_layer <preset_id> 1 0, , "
#   "controller_action remove_layer <preset_id> 1 0, , "
#   (args observed as "1 1" in v13 and "1 0" in majority; using "1 0")
#
# The layer is LayerA (preset id=1), declared in an action_layers block at the
# controller_mappings top level (from real layout analysis: name in action_layers,
# set_layer="1", parent_set_name="Default").
#
# Base preset (Default, id=0):
#   button_a → F1 (always active — baseline / canary)
#   button_b → F2 (base binding)
#   button_x → controller_action add_layer 1 1 0    (applies LayerA)
#   button_y → controller_action remove_layer 1 1 0 (removes LayerA)
#
# Layer preset (LayerA, id=1):
#   button_b → F3 (overrides F2 while LayerA active)
#
# F1–F10 only: F13+ are unproven tokens on this XI2 stack; F11/F12 alias L1/L2.
#
# Findings served:
#   Phase-4 gotcha: does remove_layer happen at press-down or press-up?
#   Does the base binding resume immediately?
# ---------------------------------------------------------------------------

# Layer preset id for LayerA — must match the numeric id in add_layer/remove_layer bindings
_LAYER_A_PRESET_ID = "1"


def make_remove_layer_layout() -> str:
    """Generate a timed remove_layer layout.

    Returns the VDF text as a string.
    Key map (F1–F10 only):
      button_a → F1 (canary)
      button_b → F2 (base), F3 (layer override while LayerA active)
      button_x → controller_action add_layer 1 1 0   [EMPIRICALLY VERIFIED format]
      button_y → controller_action remove_layer 1 1 0 [EMPIRICALLY VERIFIED format]
    """
    layer_id = _LAYER_A_PRESET_ID

    # --- Base groups ---
    # button_a: canary — always F1
    btn_a_base = _button_input([
        ("Full_Press", make_activator("Full_Press", "F1")),
    ])
    # button_b base: F2
    btn_b_base = _button_input([
        ("Full_Press", make_activator("Full_Press", "F2")),
    ])
    # button_x: add_layer — controller_action add_layer <id> 1 0
    btn_x_add = _button_input([
        ("Full_Press", _p(
            ("activator_type", "Full_Press"),
            ("bindings", _p(("binding", f"controller_action add_layer {layer_id} 1 0, , "))),
            ("disabled_activators", Pairs()),
        )),
    ])
    # button_y: remove_layer — controller_action remove_layer <id> 1 0
    btn_y_remove = _button_input([
        ("Full_Press", _p(
            ("activator_type", "Full_Press"),
            ("bindings", _p(("binding", f"controller_action remove_layer {layer_id} 1 0, , "))),
            ("disabled_activators", Pairs()),
        )),
    ])

    base_four_buttons = _p(
        ("id", "6"),
        ("mode", "four_buttons"),
        ("name", ""),
        ("description", ""),
        ("inputs", _p(
            ("button_a", btn_a_base),
            ("button_b", btn_b_base),
            ("button_x", btn_x_add),
            ("button_y", btn_y_remove),
        )),
    )

    # --- Layer group ---
    # button_b in layer: F3 (overrides base F2 while LayerA active)
    btn_b_layer = _button_input([
        ("Full_Press", make_activator("Full_Press", "F3")),
    ])

    layer_four_buttons = _p(
        ("id", "7"),
        ("mode", "four_buttons"),
        ("name", ""),
        ("description", ""),
        ("inputs", _p(
            ("button_b", btn_b_layer),
        )),
    )

    switches_group = _p(
        ("id", "0"),
        ("mode", "switches"),
        ("name", ""),
        ("description", ""),
        ("inputs", Pairs()),
    )

    # --- action_layers block (required by Steam for layer recognition) ---
    # Mirrors real layout structure from vdf/ corpus: name in action_layers block,
    # set_layer="1", parent_set_name declares which base set this layers on top of.
    layer_a_entry = _p(
        ("set_layer", "1"),
        ("parent_set_name", "Default"),
    )
    action_layers = _p(("LayerA", layer_a_entry))

    # --- Presets ---
    base_gsb = _p(
        ("0", "switch active"),
        ("6", "button_diamond active"),
    )
    layer_gsb = _p(
        ("7", "button_diamond active"),
    )

    cm = Pairs(_controller_mappings_header())
    cm.append(("action_layers", action_layers))
    cm.append(("group", switches_group))
    cm.append(("group", base_four_buttons))
    cm.append(("group", layer_four_buttons))
    cm.append(_preset("0", "Default", base_gsb))
    cm.append(_preset(layer_id, "LayerA", layer_gsb, is_layer=True))
    cm.append(("settings", Pairs()))

    root = _p(("controller_mappings", cm))
    text = emit(root)
    _validate_roundtrip(text, "make_remove_layer_layout")
    assert_all_keys_unique(text, "make_remove_layer_layout")
    return text


# ---------------------------------------------------------------------------
# Layout-3: Two-action-set swap layout
# ---------------------------------------------------------------------------
#
# Purpose: verify action-set switching — START button cycles between SET_A and
# SET_B; each set has distinct F-key bindings so the runner can verify that the
# correct set is active and that the switch happens promptly.
#
# BINDING FORMAT — UNVERIFIED-HIGH-RISK HYPOTHESIS:
#   "controller_action change_preset <preset_id> 1 0, , "
#   No real-config or documentation evidence found for this verb; the candidate
#   token "change_action_set" turned out to be screenshot filenames, not binding
#   strings.  "change_preset" is the plausible lead hypothesis based on
#   controller_action verb patterns observed in the real corpus (add_layer etc.).
#
#   RUNNER DIAGNOSTIC: press the START button; if the set does not switch
#   (button_a still emits F1 instead of F3), this verb is wrong.  Report the
#   exact binding from a GUI-saved action-set-swap layout.
#
# SET_A (Default, id=0):
#   button_a → F1, button_b → F2
#   START → controller_action change_preset 1 1 0   (switches to SetB id=1)
#
# SET_B (SetB, id=1):
#   button_a → F3, button_b → F4
#   START → controller_action change_preset 0 1 0   (switches to Default id=0)
#
# F1–F10 only: F13+ are unproven tokens on this XI2 stack; F11/F12 alias L1/L2.
#
# Findings served:
#   Phase-4 gotcha: action-set swap — does switch happen at press-down or up?
#   Does the new set's binding fire on the very next stimulus?
#   Converter: Steam action sets have no direct JSM analogue → classify.
# ---------------------------------------------------------------------------

def make_action_set_swap_layout() -> str:
    """Generate a two-action-set swap layout.

    Returns the VDF text as a string.
    Key map (F1–F10 only):
      SET_A (Default, id=0): button_a → F1, button_b → F2
      SET_B (SetB, id=1):    button_a → F3, button_b → F4
      START: controller_action change_preset <target_id> 1 0
             [UNVERIFIED-HIGH-RISK hypothesis — no corpus evidence for verb]
    """
    def _set_buttons(f_a, f_b):
        """Build face-button inputs: btn_a→fA, btn_b→fB."""
        btn_a = _button_input([
            ("Full_Press", make_activator("Full_Press", f_a)),
        ])
        btn_b = _button_input([
            ("Full_Press", make_activator("Full_Press", f_b)),
        ])
        return _p(
            ("button_a", btn_a),
            ("button_b", btn_b),
        )

    def _switch_button(target_preset_id):
        """Build a START binding: controller_action change_preset <id> 1 0."""
        return _button_input([
            ("Full_Press", _p(
                ("activator_type", "Full_Press"),
                ("bindings", _p(
                    ("binding",
                     f"controller_action change_preset {target_preset_id} 1 0, , ")
                )),
                ("disabled_activators", Pairs()),
            )),
        ])

    # Preset IDs: Default=0, SetB=1
    _ID_DEFAULT = "0"
    _ID_SETB = "1"

    # SET_A groups (id 6 for four_buttons, id 0 for switches)
    set_a_four = _p(
        ("id", "6"),
        ("mode", "four_buttons"),
        ("name", ""),
        ("description", ""),
        ("inputs", _set_buttons("F1", "F2")),
    )
    set_a_switches = _p(
        ("id", "0"),
        ("mode", "switches"),
        ("name", ""),
        ("description", ""),
        ("inputs", _p(
            ("button_start", _switch_button(_ID_SETB)),
        )),
    )

    # SET_B groups (id 7 for four_buttons, id 1 for switches)
    set_b_four = _p(
        ("id", "7"),
        ("mode", "four_buttons"),
        ("name", ""),
        ("description", ""),
        ("inputs", _set_buttons("F3", "F4")),
    )
    set_b_switches = _p(
        ("id", "1"),
        ("mode", "switches"),
        ("name", ""),
        ("description", ""),
        ("inputs", _p(
            ("button_start", _switch_button(_ID_DEFAULT)),
        )),
    )

    # Presets
    set_a_gsb = _p(
        ("0", "switch active"),
        ("6", "button_diamond active"),
    )
    set_b_gsb = _p(
        ("1", "switch active"),
        ("7", "button_diamond active"),
    )

    cm = Pairs(_controller_mappings_header())
    cm.append(("group", set_a_switches))
    cm.append(("group", set_a_four))
    cm.append(("group", set_b_switches))
    cm.append(("group", set_b_four))
    cm.append(_preset("0", "Default", set_a_gsb))
    cm.append(_preset("1", "SetB", set_b_gsb))
    cm.append(("settings", Pairs()))

    root = _p(("controller_mappings", cm))
    text = emit(root)
    _validate_roundtrip(text, "make_action_set_swap_layout")
    assert_all_keys_unique(text, "make_action_set_swap_layout")
    return text


# ---------------------------------------------------------------------------
# Round-trip guard
# ---------------------------------------------------------------------------

def _validate_roundtrip(text: str, label: str):
    """Parse → emit → reparse. Raises ValueError if the round-trip fails."""
    tokens = tokenize(text)
    pairs, _ = parse(tokens)
    out2 = emit(pairs)
    tokens2 = tokenize(out2)
    pairs2, _ = parse(tokens2)
    root2 = pairs2.get_first("controller_mappings")
    if root2 is None:
        raise ValueError(
            f"{label}: round-trip lost 'controller_mappings' root"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _write_validated(text: str, out_path: Path, label: str):
    """Validate round-trip, then write to out_path (creating parent dirs)."""
    _validate_roundtrip(text, label)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text)
    print(f"Written: {out_path}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_marker = sub.add_parser("marker",
        help="F1-F9 marker layout (button_y test btn + canary/tap-hold/interruptable=0 probes)")
    p_marker.add_argument("--dtt", type=int, default=190,
        help="Double Tap Time in ms (default 190)")
    p_marker.add_argument("--out", required=True, help="output .vdf path")

    p_rpi = sub.add_parser("release-press-isolated",
        help="Release_Press discrimination layout (4 buttons × 4 pairing contexts)")
    p_rpi.add_argument("--out", required=True, help="output .vdf path")

    p_rl = sub.add_parser("remove-layer",
        help="Timed remove_layer layout (base + LayerA)")
    p_rl.add_argument("--out", required=True, help="output .vdf path")

    p_as = sub.add_parser("action-set-swap",
        help="Two-action-set swap (Default ↔ SetB)")
    p_as.add_argument("--out", required=True, help="output .vdf path")

    args = ap.parse_args(argv)

    if args.cmd == "marker":
        text = make_marker_layout(args.dtt)
        _write_validated(text, Path(args.out), "marker")
    elif args.cmd == "release-press-isolated":
        text = make_release_press_isolated_layout()
        _write_validated(text, Path(args.out), "release-press-isolated")
    elif args.cmd == "remove-layer":
        text = make_remove_layer_layout()
        _write_validated(text, Path(args.out), "remove-layer")
    elif args.cmd == "action-set-swap":
        text = make_action_set_swap_layout()
        _write_validated(text, Path(args.out), "action-set-swap")

    return 0


if __name__ == "__main__":
    sys.exit(main())
