Scripts
===============================================================================

Here you will find nifty scripts I wrote to make my life easier. 

Most of them are pretty messy and only intended for personal use, but I did 
try to make them small and easy to change, so have a look around and do with 
them as you please. I'm fond of using 
[dmenu](http://tools.suckless.org/dmenu/) / 
[rofi](https://github.com/DaveDavenport/rofi) and 
[jq](https://stedolan.github.io/jq/), because they make quick DIY scripts 
easy.

Currently, the repository contains the following tools:

- [dmenu-mpv](dmenu-mpv): An interface to [mpv](https://mpv.io/), as a plain 
  music player that simply offers a shuffled list of full albums to play.
- [dmenu-pass](dmenu-pass): An interface to 
  [pass](http://www.zx2c4.com/projects/password-store/), as a password 
  manager.
- [dmenu-cheatsheet](dmenu-cheatsheet): Quick reminders of keyboard shortcuts 
  and commands.
- [xcwd.sh](xcwd.sh): an alternative to 
  [xcwd](https://github.com/schischi/xcwd), 
  [lastcwd](https://github.com/wknapik/lastcwd) and
  [i3-shell](https://gist.github.com/viking/5851049#file-i3-shell-sh) that 
  returns the working directory of the currently active terminal window.
- [toggle-pointer](toggle-pointer): A script to disable and re-enable the 
  mouse pointer.
- [download-article](download-article) downloads an internet article to a 
  Markdown file.
- [thesaurus](thesaurus): Presents a list of related words.
- [crsync](crsync): A script to keep my files synchronised across my devices 
  (ereader, music player, external harddisk, etcetera), by running 
  [rsync](https://rsync.samba.org/) on a YAML configuration.
- [block](block): Easily blocking websites through `/etc/hosts`.
- [printer](printer): Print PDFs as double-sided booklets on cheap printers 
  without automatic double-sided printing.
- [scanner](scanner): The command I use for making quick scans. Photographs 
  are automatically separated, cropped, and de-rotated, whereas documents are 
  made black-and-white and heavily compressed.
- [diffpic](diffpic): A quick script to identify and delete duplicate or 
  visually similar images using 
  [findimagedupes](http://www.jhnc.org/findimagedupes/) and 
  [sxiv](https://github.com/muennich/sxiv).


### Notices

- `keyboard-config` has been reworked into [thumbledore](https://github.com/slakkenhuis/thumbledore)
