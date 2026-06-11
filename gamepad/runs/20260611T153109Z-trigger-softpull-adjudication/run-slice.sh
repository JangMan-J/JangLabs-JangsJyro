#!/usr/bin/env bash
# run-slice.sh <slice> [seconds=14] — Steam-lane trigger adjudication slices.
# Requires: nested env up (steam-virtual-env.sh), pad holder at /tmp/synthetic_pad_ctrl,
# DISPLAY set to nested Xwayland (cat /tmp/jsmlab_display).
set -u
SLICE="$1"; SECS="${2:-14}"
ROOT=/home/jangmanj/JangLabs/jangsjyro/gamepad
RUN="$ROOT/runs/20260611T153109Z-trigger-softpull-adjudication"
FIFO=/tmp/synthetic_pad_ctrl
TRACE="$RUN/traces/$SLICE.trace"
DISP="$(cat /tmp/jsmlab_display 2>/dev/null || echo ':1')"

[ -p "$FIFO" ] || { echo "FATAL: pad holder FIFO missing"; exit 1; }
[ -f "$TRACE" ] || { echo "FATAL: no trace $TRACE"; exit 1; }

echo "[$SLICE] capturing XI2+evdev ($SECS s) on DISPLAY=$DISP"
DISPLAY="$DISP" python3 "$ROOT/tools/xi2_capture.py" capture --types key --seconds "$SECS" \
    --jsonl "$RUN/$SLICE.xi2.jsonl" > "$RUN/$SLICE.xi2.txt" 2>&1 &
XI2=$!
python3 "$ROOT/tools/evdev_capture.py" capture --types key --seconds "$SECS" \
    --jsonl "$RUN/$SLICE.evdev.jsonl" > "$RUN/$SLICE.evdev.txt" 2>&1 &
EVD=$!
sleep 1.0
echo "[$SLICE] replaying trace into pad FIFO…"
cat "$TRACE" > "$FIFO"
wait "$XI2" "$EVD" 2>/dev/null
echo "[$SLICE] XI2 key events (non-raw):"
grep -E ' Key(Press|Release) ' "$RUN/$SLICE.xi2.txt" | awk '{printf "    %-12s %s\n", $2, $4}'
echo "[$SLICE] done"
