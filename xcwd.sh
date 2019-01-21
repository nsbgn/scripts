#!/bin/sh

# Returns the current working directory of the focused urxvtc window.

# Written because https://github.com/schischi/xcwd does not work for urxvtc,
# due to it being a daemon. Inspired by https://github.com/wknapik/lastcwd and
# https://gist.github.com/viking/5851049, but faster.

# We first find the window ID of the active window. Then we find the newest
# process that has the same window ID in its starting environment and has its
# /proc/$PID/cwd set. (The PWD in the ps args is only the starting directory of
# the process.)

PIDS="$(ps e --sort=+pid -o pid,args \
    | grep -e "WINDOWID=$(xdotool getactivewindow)" \
    | grep -o '^[0-9]*')"

DIR="$(for PID in $PIDS; do
    readlink "/proc/$PID/cwd"
done | tail -n 1)"

if [ -z "$DIR" ]; then
    echo "$HOME"
else
    echo "$DIR"
fi
