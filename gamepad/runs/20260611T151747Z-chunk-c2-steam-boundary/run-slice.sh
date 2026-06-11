#!/usr/bin/env bash
# run-slice.sh <slice> [seconds=16] — Steam-lane boundary tracer slice (Chunk C2).
# Requires: nested env up (steam-virtual-env.sh), pad holder alive at FIFO /tmp/synthetic_pad_ctrl,
# DISPLAY set to nested Xwayland (cat /tmp/jsmlab_display).
# Captures XI2 (Steam output plane) + evdev (negative control). Serial runs only.
set -u
SLICE="$1"; SECS="${2:-16}"
ROOT=/home/jangmanj/JangLabs/jangsjyro/gamepad
RUN="$ROOT/runs/20260611T151747Z-chunk-c2-steam-boundary"
FIFO=/tmp/synthetic_pad_ctrl
TRACE="$RUN/traces/$SLICE.trace"
DISP="$(cat /tmp/jsmlab_display 2>/dev/null || echo ':1')"

[ -p "$FIFO" ] || { echo "FATAL: pad holder FIFO missing — start synthetic_gamepad.py --control-fifo first"; exit 1; }
[ -f "$TRACE" ] || { echo "FATAL: no trace $TRACE"; exit 1; }

echo "[$SLICE] starting XI2+evdev capture ($SECS s) on DISPLAY=$DISP"
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
echo "[$SLICE] evdev KEY_ events (stimulus only — no keyboard keys expected):"
grep -oE '(KEY|BTN)_[A-Z0-9]+' "$RUN/$SLICE.evdev.txt" | sort | uniq -c | sed 's/^/    /'
echo "[$SLICE] done — artifacts: $RUN/$SLICE.{xi2,evdev}.{txt,jsonl}"
