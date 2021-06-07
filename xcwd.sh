#!/bin/sh

# Hacky wrapper around xcwd to work with urxvtc. First tries to draw from the
# window title, then uses xcwd. Only works when your window titles are set up
# like mine (see dotfiles).

# Written because https://github.com/schischi/xcwd does not work for urxvtc,
# due to it being a daemon. Inspired by https://github.com/wknapik/lastcwd and
# https://gist.github.com/viking/5851049, but faster. See git history for the
# previous, also imperfect way using window IDs.

CWD="$(xdotool getactivewindow getwindowname \
    | tr -s ' ' | cut -d' ' -f2 | sed "s|^~|$HOME|g")"
if [ -f "${CWD}" ]; then
    dirname "${CWD}"
elif [ -d "${CWD}" ]; then
    echo "${CWD}"
else
    xcwd
fi

