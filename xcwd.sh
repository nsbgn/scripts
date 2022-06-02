#!/bin/sh
# Returns the current working directory of the focused terminal window. Only
# for X11. Works for urxvtc and takes into account foreground process.
# Inspired by:
# - https://github.com/wknapik/lastcwd
# - https://gist.github.com/viking/5851049

readlink /proc/$(ps e -o tpgid=,tty=,args= \
    | awk -F' ' '$2~/pts/ && /WINDOWID='$(xdotool getactivewindow)'/ {print $1}' \
    | head -n1)/cwd || echo $HOME

# readlink /proc/$(xdotool getactivewindow getwindowpid)/cwd || echo $HOME
