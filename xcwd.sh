#!/bin/sh

# Returns the current working directory of the focused urxvtc window (and
# perhaps other software too).

# Written because https://github.com/schischi/xcwd does not work for urxvtc,
# due to it being a daemon. Inspired by https://github.com/wknapik/lastcwd and
# https://gist.github.com/viking/5851049, but faster.

# We first find the window ID of the active window. Then we find the newest
# process that has the same window ID in its initial environment, and has its
# /proc/$PID/cwd set. Otherwise, we just return the home directory.

# This only works if the terminal didn't spawn another process in the
# background that also has a cwd and is newer than the process you are actually
# working with. To filter out at least some of these cases, we set -N --ppid 1
# (to say that the process must not be a direct child of the root process)

(echo "$HOME"
 ps e -N --ppid 1 --sort=+pid -o pid,args \
  | sed -n "s|^\s*\([0-9]\+\) .*WINDOWID=`xdotool getactivewindow`.*|\\1|p" \
  | xargs -d'\n' -I{} readlink /proc/{}/cwd 
) | tail -n 1
