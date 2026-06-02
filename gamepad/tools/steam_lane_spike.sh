#!/usr/bin/env bash
# steam_lane_spike.sh — guided Steam-Input-lane spike (the Steam half of Phase 1,
# building on Phase 0b). Automates everything EXCEPT the Steam Input GUI binding,
# which only you can do. Run it with Steam up. It answers two questions:
#   (1) Does Steam Input recognize a *synthetic* uinput gamepad at all?
#   (2) With a button bound to F9, is Steam Input's output at the XI2/Wayland seat
#       (Phase 0b finding) and NOT at evdev?
#
# Pipeline: synthetic_gamepad.py (--control-fifo holder, live on-cue injection) +
# xi2_capture.py (XI2 plane) + evdev_capture.py (evdev plane, negative control).
# Prereqs verified 2026-06-02: /dev/uinput rw; xinput present; DISPLAY set.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"          # gamepad/
TOOLS="$ROOT/tools"
RUN="$ROOT/runs/$(date -u +%Y%m%dT%H%M%SZ)-steam-lane-spike"
CTRL=/tmp/synthetic_pad_ctrl
mkdir -p "$RUN"

HOLDER= XI2= EVD=
cleanup() {
  [ -n "$XI2" ] && kill "$XI2" 2>/dev/null
  [ -n "$EVD" ] && kill "$EVD" 2>/dev/null
  [ -n "$HOLDER" ] && { echo quit > "$CTRL" 2>/dev/null; sleep 0.3; kill "$HOLDER" 2>/dev/null; }
  wait 2>/dev/null
  rm -f "$CTRL"
}
trap cleanup EXIT
echo "== Steam-lane spike == artifacts -> $RUN"

# Phase 0: is Steam up?
if pgrep -x steam >/dev/null; then echo "[0] Steam: running"; else
  echo "[0] WARNING: Steam is NOT running. Launch Steam (Beta + experimental SteamRT3 per Phase 0b) first, then re-run."
fi
for f in ~/.steam/steam/logs/controller.log ~/.local/share/Steam/logs/controller.log; do
  [ -f "$f" ] && CLOG="$f"; done
echo "[0] controller.log: ${CLOG:-none found}"

# Phase 1: create the synthetic pad (stays alive via the control FIFO)
echo "[1] creating synthetic Xbox-360 pad (held alive for binding)…"
rm -f "$CTRL"
python3 "$TOOLS/synthetic_gamepad.py" --control-fifo "$CTRL" --warmup 0 \
    --log "$RUN/holder.log" > "$RUN/holder.out" 2>&1 &
HOLDER=$!
sleep 1.2
python3 "$TOOLS/evdev_capture.py" list 2>/dev/null | grep -i 'X-Box' | tee "$RUN/pad-on-evdev.txt" | sed 's/^/    evdev: /'
[ -n "${CLOG:-}" ] && { echo "    --- last controller.log lines mentioning a pad ---"; grep -iE 'x-box|360|045e|gamepad|added|controller' "$CLOG" | tail -5 | sed 's/^/    /'; }

cat <<'EOF'

[1] >>> ACTION (you, in the Steam GUI): <<<
    a. Steam → Settings → Controller. Confirm "Microsoft X-Box 360 pad" appears.
       - If it does NOT appear, Steam does not see synthetic uinput pads → the
         Steam lane needs a uhid device instead. Note that and Ctrl-C here.
    b. Enable Steam Input for it (Desktop config is fine).
    c. Bind its **A / South** button to keyboard **F9** (Desktop layout or a test layout).
    Press ENTER here once F9 is bound to the pad's South button…
EOF
read -r _

# Phase 2: observe both planes while injecting the bound button
echo "[2] capturing XI2 + evdev for 14s; injecting South x11…"
python3 "$TOOLS/xi2_capture.py" capture --types key --seconds 14 --jsonl "$RUN/xi2.jsonl" > "$RUN/xi2.txt" 2>&1 &
XI2=$!
python3 "$TOOLS/evdev_capture.py" capture --types key --seconds 14 --jsonl "$RUN/evdev.jsonl" > "$RUN/evdev.txt" 2>&1 &
EVD=$!
sleep 1.0
for i in $(seq 1 11); do echo "press SOUTH 120" > "$CTRL"; sleep 0.45; done
wait "$XI2" 2>/dev/null; XI2=
wait "$EVD" 2>/dev/null; EVD=

# Phase 3: verdict
echo "[3] RESULT:"
X=$(grep -ciE 'F9|keycode 75|\<75\>' "$RUN/xi2.txt" 2>/dev/null || echo 0)
E=$(grep -ciE 'KEY_F9' "$RUN/evdev.txt" 2>/dev/null || echo 0)
echo "    F9 events at XI2/seat : $X   (expect ~11 if Steam Input emits there — Phase 0b)"
echo "    KEY_F9 at evdev       : $E   (expect 0 — Steam output is NOT at evdev on Wayland)"
echo "    -> If XI2>0 & evdev=0: Steam-lane plane confirmed for SYNTHETIC input (Phase 0b generalizes)."
echo "    -> If XI2=0 & evdev=0: Steam didn't emit — re-check the binding / that the pad was recognized."
echo "    Write a result.md in $RUN summarizing (record Steam Beta/RT3 + recognition yes/no)."
