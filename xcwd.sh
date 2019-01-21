#!/bin/bash

# Returns the current working directory of the focused urxvtc window.

# Written because https://github.com/schischi/xcwd does not work for urxvtc,
# due to it being a daemon. Inspired by https://github.com/wknapik/lastcwd and
# https://gist.github.com/viking/5851049, but faster.

# We first find the window ID of the active window. Then we find the newest
# process that has the same window ID in its initial environment, and has its
# /proc/$PID/cwd set.

DIR="$(for PID in $(ps e --sort=+pid -o pid,args \
    | sed -n "s|^\s*\([0-9]\+\) .*WINDOWID=$(xdotool getactivewindow).*|\\1|p")
do
    readlink /proc/$PID/cwd
done | tail -n 1)"

[ -d "$DIR" ] && echo "$DIR" || echo "$HOME"

