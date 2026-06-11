#!/usr/bin/env bash
# run-slice.sh <slice> — one JSM-lane boundary tracer slice (Chunk C1).
# Reads configs/<slice>.cfg + traces/<slice>.trace; writes <slice>.{capture.txt,
# capture.jsonl,injector.log,jsm.stdout.log,jsm.stderr.log}. Serial run-and-observe.
set -u
SLICE="$1"
ROOT=/home/jangmanj/JangLabs/jangsjyro
RUN="$ROOT/gamepad/runs/20260611T150936Z-chunk-c1-jsm-boundary"
JSM="$ROOT/build-linux/JoyShockMapper/JoyShockMapper"
TOOLS="$ROOT/gamepad/tools"
FIFO=/tmp/jsm_command_fifo
CFG="$RUN/configs/$SLICE.cfg"
TRACE="$RUN/traces/$SLICE.trace"

cleanup() {
  [ -n "${CAP_PID:-}" ] && kill "$CAP_PID" 2>/dev/null
  [ -n "${JSM_PID:-}" ] && kill -TERM "$JSM_PID" 2>/dev/null
  [ -n "${INJ_PID:-}" ] && kill "$INJ_PID" 2>/dev/null
  wait 2>/dev/null
}
trap cleanup EXIT

pkill -x JoyShockMapper 2>/dev/null; sleep 0.3; rm -f "$FIFO"
echo "[$SLICE] create synthetic pad + replay trace"
python3 "$TOOLS/synthetic_gamepad.py" --trace "$TRACE" --warmup 9 --linger 4 \
    --log "$RUN/$SLICE.injector.log" > /dev/null 2>&1 &
INJ_PID=$!
sleep 1.0
echo "[$SLICE] start JSM"
stdbuf -oL -eL "$JSM" > "$RUN/$SLICE.jsm.stdout.log" 2>"$RUN/$SLICE.jsm.stderr.log" &
JSM_PID=$!
sleep 2.5
echo "[$SLICE] feed config + RECONNECT_CONTROLLERS"
if [ -p "$FIFO" ]; then cat "$CFG" > "$FIFO"; sleep 0.3; echo "RECONNECT_CONTROLLERS" > "$FIFO"; fi
sleep 1.0
echo "[$SLICE] grab-capture JSM output (30s)"
python3 "$TOOLS/evdev_capture.py" capture --name JoyShockMapper --grab-name JoyShockMapper \
    --types key,rel,syn --seconds 30 --jsonl "$RUN/$SLICE.capture.jsonl" \
    > "$RUN/$SLICE.capture.txt" 2>&1 &
CAP_PID=$!
wait "$INJ_PID"; INJ_PID=
wait "$CAP_PID"; CAP_PID=
kill -TERM "$JSM_PID" 2>/dev/null; wait "$JSM_PID" 2>/dev/null; JSM_PID=
echo "[$SLICE] done"
