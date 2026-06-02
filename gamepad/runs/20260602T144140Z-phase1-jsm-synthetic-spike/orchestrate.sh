#!/usr/bin/env bash
# Phase 1 tracer-bullet orchestration: synthetic uinput gamepad -> JSM -> evdev.
# Deterministic, run-and-observe on one live system (serial by design, plan §11).
#
#   t=0   create synthetic Xbox360 pad (injector bg, warmup 10s, repeat 2, linger 8s)
#   t=1   start JSM (pad already present at SDL enumeration)
#   t=3   feed smoke.config + RECONNECT_CONTROLLERS via the command FIFO
#   t=4   snapshot device list (confirm JSM output devices + the synthetic pad)
#   t=5   grab-capture JSM's JoyShockMapper_KEYBOARD/_MOUSE output (18s window)
#   t=10  injector fires SOUTH press + right-trigger ramp (x2) INSIDE the window
#   t~24  injector self-exits; stop capture + JSM
set -u
ROOT=/home/jangmanj/JangLabs/jangsjyro
RUN="$ROOT/gamepad/runs/20260602T144140Z-phase1-jsm-synthetic-spike"
JSM="$ROOT/build-linux/JoyShockMapper/JoyShockMapper"
TOOLS="$ROOT/gamepad/tools"
FIFO=/tmp/jsm_command_fifo

cleanup() {
  [ -n "${CAP_PID:-}" ] && kill "$CAP_PID" 2>/dev/null
  [ -n "${JSM_PID:-}" ] && kill -TERM "$JSM_PID" 2>/dev/null
  [ -n "${INJ_PID:-}" ] && kill "$INJ_PID" 2>/dev/null
  wait 2>/dev/null
}
trap cleanup EXIT

# clean slate
pkill -x JoyShockMapper 2>/dev/null; sleep 0.3; rm -f "$FIFO"

echo "[orch] t0 create synthetic pad"
python3 "$TOOLS/synthetic_gamepad.py" --warmup 10 --linger 8 --repeat 2 \
    --log "$RUN/injector.log" > "$RUN/injector.stdout" 2>&1 &
INJ_PID=$!
sleep 1.0

echo "[orch] t1 start JSM"
stdbuf -oL -eL "$JSM" > "$RUN/jsm.stdout.log" 2>"$RUN/jsm.stderr.log" &
JSM_PID=$!
sleep 2.0

echo "[orch] t3 feed config + RECONNECT_CONTROLLERS via FIFO"
if [ -p "$FIFO" ]; then
  cat "$RUN/smoke.config" > "$FIFO"
  sleep 0.3
  echo "RECONNECT_CONTROLLERS" > "$FIFO"
else
  echo "[orch] WARN: FIFO $FIFO not present yet"
fi
sleep 1.0

echo "[orch] t4 device-list snapshot"
python3 "$TOOLS/evdev_capture.py" list > "$RUN/devices.txt" 2>&1

echo "[orch] t5 start grab-capture of JSM output (18s)"
python3 "$TOOLS/evdev_capture.py" capture \
    --name JoyShockMapper --grab-name JoyShockMapper \
    --types key,rel,syn --seconds 18 \
    --jsonl "$RUN/capture.jsonl" > "$RUN/capture.txt" 2>&1 &
CAP_PID=$!

echo "[orch] waiting for injector to finish its sequence + linger…"
wait "$INJ_PID"; INJ_PID=
echo "[orch] injector done; letting capture window close"
wait "$CAP_PID"; CAP_PID=

echo "[orch] stopping JSM"
kill -TERM "$JSM_PID" 2>/dev/null; wait "$JSM_PID" 2>/dev/null; JSM_PID=
echo "[orch] done"
