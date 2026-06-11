#!/usr/bin/env bash
# steam-virtual-env.sh — stand up the SEAT-FREE Steam lane (verified 2026-06-11):
# nested headless KWin (--virtual, own Xwayland) -> Steam inside it -> ready for the
# pad holder + captures. The user's desktop seat receives NOTHING (Steam Input output
# lands on the nested Xwayland seat only) and user typing cannot contaminate captures.
# Same KWin+Xwayland stack as the real session, so plane findings transfer.
#
# After it prints the display: start the pad holder, then observe with
#   DISPLAY=$(cat /tmp/jsmlab_display) python3 tools/xi2_capture.py capture ...
# Tear down: steam -shutdown; kill the kwin_wayland pid it prints.
set -u
SOCK=wayland-jsmlab
if pgrep -x steam >/dev/null; then
  echo "Steam is already running (desktop instance?). 'steam -shutdown' first."; exit 1
fi
BEFORE=$(ls /tmp/.X11-unix)
kwin_wayland --virtual --socket="$SOCK" --xwayland --no-lockscreen &>/tmp/kwin-jsmlab.log &
KWIN=$!
sleep 4
NEWX=$(comm -13 <(echo "$BEFORE") <(ls /tmp/.X11-unix) | head -1 | sed 's/^X/:/')
[ -n "$NEWX" ] || { echo "FATAL: no new X display appeared (see /tmp/kwin-jsmlab.log)"; kill "$KWIN" 2>/dev/null; exit 1; }
echo "$NEWX" > /tmp/jsmlab_display
echo "nested kwin pid=$KWIN  X=$NEWX  wayland=$SOCK"
DISPLAY="$NEWX" WAYLAND_DISPLAY="$SOCK" setsid steam &>/tmp/steam-virtual-launch.log </dev/null &
echo "Steam launching on $NEWX (log: /tmp/steam-virtual-launch.log; ~30s to settle)."
echo "Canary before trusting anything: digital slice, observer on DISPLAY=$NEWX."
