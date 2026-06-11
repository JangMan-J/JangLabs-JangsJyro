#!/usr/bin/env bash
# run-slice.sh <slice> [seconds=12] — one Steam-lane tracer slice:
# FIFO-replay traces/<slice>.trace through the live synthetic pad -> Steam Input ->
# capture XI2 (output plane) + evdev (negative control / stimulus confirm).
# Requires: Steam up with the sitting's Desktop-layout bindings; pad holder alive
# (synthetic_gamepad.py --control-fifo /tmp/synthetic_pad_ctrl). Serial runs only.
set -u
SLICE="$1"; SECS="${2:-12}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"        # gamepad/
RUN="$(cd "$(dirname "$0")" && pwd)"
FIFO=/tmp/synthetic_pad_ctrl
TRACE="$RUN/traces/$SLICE.trace"
[ -p "$FIFO" ] || { echo "FATAL: pad holder FIFO missing — start synthetic_gamepad.py --control-fifo first"; exit 1; }
[ -f "$TRACE" ] || { echo "FATAL: no trace $TRACE"; exit 1; }

python3 "$ROOT/tools/xi2_capture.py" capture --types key --seconds "$SECS" \
    --jsonl "$RUN/$SLICE.xi2.jsonl" > "$RUN/$SLICE.xi2.txt" 2>&1 &
XI2=$!
python3 "$ROOT/tools/evdev_capture.py" capture --types key --seconds "$SECS" \
    --jsonl "$RUN/$SLICE.evdev.jsonl" > "$RUN/$SLICE.evdev.txt" 2>&1 &
EVD=$!
sleep 1.0
echo "[$SLICE] replaying trace into FIFO…"
cat "$TRACE" > "$FIFO"
wait "$XI2" "$EVD" 2>/dev/null
echo "[$SLICE] XI2 key events (non-raw):"
grep -E ' Key(Press|Release) ' "$RUN/$SLICE.xi2.txt" | awk '{printf "    %-12s %s\n", $2, $4}'
echo "[$SLICE] evdev KEY_ events (expect stimulus BTN_* only, no keyboard keys):"
grep -oE '(KEY|BTN)_[A-Z0-9]+' "$RUN/$SLICE.evdev.txt" | sort | uniq -c | sed 's/^/    /'
echo "[$SLICE] artifacts: $RUN/$SLICE.{xi2,evdev}.{txt,jsonl}"
