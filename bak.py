#!/usr/bin/env python3
"""
A wrapper around `rsync` that automatically mounts and unmounts required
directories. Intended for myself, but it may be useful. Requires `pmount` and
`rsync` in your $PATH.

For example, the YAML configuration (default location: ~/.config/bak.yaml):

    mount:
        - dir: /media/toshiba
          uuid: 18a3c1b4
          keyfile: ~/.keyfile.bin
          default: true
        - dir: /media/sandisk
          uuid: 60f417bd
    sync:
        ~/{projects,documents}:
            - /media/sandisk/
            - /media/toshiba/archive/
        /media/data/photos: /media/sandisk/pictures

Then, calling `bak --push /media/sandisk` would push local changes to just
those remote directories that start with /media/sandisk, before ensuring that
/media/sandisk is mounted. To find out the UUID of a disk, run `blkid`.
"""

import subprocess
import re
import yaml
import logging
import argparse
from os.path import expanduser, realpath, ismount, join, split

from collections import defaultdict
from itertools import product
# from pathlib import Path


class SyncPair:
    def __init__(self, local, remote, *files):
        self.local = local
        self.remote = remote
        self.files = files

    def remote(self):
        return self.remote

    def local(self):
        for f in self.files:
            yield join(self.local, f)


def norm(path):
    return realpath(expanduser(path)) + ("/" if path.endswith("/") else "")


def pmount(path, device, keyfile=None, mount=True):
    """
    Mount directories as a user. Wrapper for the `pmount` tool.
    """
    command = ["pmount" if mount else "pumount"]
    if keyfile:
        command.extend(("-p", expanduser(keyfile)))
    command.append(device)
    command.append(path)
    subprocess.run(command, check=True)


def relevant_mounts(paths, mounts):
    """
    """

    result = dict()
    for path in paths:
        result.update({
            m.get('dir'): m for m in mounts if path.startswith(m.get('dir'))
        })
    return result.values()


def mount_all(mounts, mount=True):
    """
    Make sure that the given mounts are mounted.
    """
    for mount in mounts:
        if not ismount(mount.get('dir')):
            pmount(mount.get('dir'),
                   '/dev/disk/by-uuid/{}'.format(mount.get('uuid')),
                   keyfile=mount.get('keyfile'),
                   mount=mount)


def rsync(sources, dest, dry_run=True, fat32=False, delete_before=False):
    command = ['rsync', '--progress']

    if dry_run:
        command.append('--dry-run')

    if fat32:
        command.extend((
            '--recursive',
            '--links',
            '--times',
            '--devices',
            '--specials',
            '--size-only',
            '--modify-window=1'))
    else:
        command.append('--archive')

    command.append('--delete')

    if delete_before:
        command.append('--delete-before')

    command.extend((
        '--filter=dir-merge,- .gitignore',
        '--exclude=lost+found',
        '--exclude=.Trash-1000'))

    command.extend(sources)
    command.append(dest)

    logging.warning(" ".join(command))
    subprocess.run(command, check=True)


def expand_braces(s, pattern=re.compile(r'.*(\{.+?[^\\]\})')):
    """
    Shell-style expansion of braces, that is: "a{b,c}" becomes "ab", "ac"
    """

    result = []
    match = pattern.search(s)
    if match is not None:
        sub = match.group(1)
        opening = s.find(sub)
        closing = opening + len(sub) - 1
        if sub.find(',') != -1:
            result.extend((
                a
                for p in sub.strip('{}').split(',')
                for a in expand_braces(s[:opening] + p + s[closing+1:])
            ))
        else:
            result.extend(
               expand_braces(s[:opening] + sub.replace('}', '\\}') +
                             s[closing+1:]))
    else:
        result.append(s.replace('\\}', '}'))

    return result


def group_syncs(syncs):
    """
    Group 3-tuples, such that those with the same destination directory end up
    in the same tuple.

    @param syncs: 3-tuples
    @returns: iterator of tuples, containing a destination directory and a list
        of source files
    """

    d = defaultdict(list)
    for src_dir, fn, dest_dir in syncs:
        d[norm(dest_dir)].append(join(src_dir, fn))
    return d.items()


def filter_syncs(syncs, prefixes):
    """
    Filter 3-tuples such that only those with relevant prefixes on the remote
    directory are kept.

    @param prefixes: A generator of string prefixes.
    """

    return filter(
        lambda s: any(s[2].startswith(norm(p)) for p in prefixes),
        syncs)


def extract_syncs(mapping):
    """
    Find all 3-tuples of local directory, filename and remote directory
    represented by the mapping.

    @param mapping: A dictionary mapping files to to one or more remote
        directories.
    @returns: tuple of local directory, target basename, and remote directory
    """

    for local_repr, remote_reprs in mapping.items():

        if type(remote_reprs) != list:
            remote_reprs = [remote_reprs]

        local_paths = expand_braces(local_repr)

        remote_dirs = [
            path
            for remote_repr in remote_reprs
            for path in expand_braces(remote_repr)
        ]

        for local_path, remote_dir in product(local_paths, remote_dirs):

            # For now, to keep things easy
            if local_path.endswith("/"):
                raise Exception("Local must not be the content of a directory")
            if not remote_dir.endswith("/"):
                raise Exception("Remote must be a directory in which the "
                                "local directory will be placed")

            local_dir, fn = split(local_path)
            yield join(norm(local_dir), ""), fn, join(norm(remote_dir), "")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Mount and synchronise directories based on YAML "
                    "configuration"
    )

    parser.add_argument('--config', default='~/scrapbook/bak.yaml',
                        help="configuration file")

    parser.add_argument(
        '-m', '--automount', action='store_true',
        default=False, help="automatically (un)mount devices")

    push = parser.add_mutually_exclusive_group(required=True)
    push.add_argument('-o', '--push', action='store_true',
                      help="push changes to remote")
    push.add_argument('-i', '--pull', action='store_false',
                      help="pull changes from remote")

    parser.add_argument(
        'prefixes',
        nargs='*',
        help="prefixes of remote directories to be synced")

    args = parser.parse_args()

    with open(expanduser(args.config), 'r') as f:
        config = yaml.safe_load(f)

    mounts = config.get('mount', [])
    if not args.prefixes:
        logging.info("No prefixes given, picking defaults")
        args.prefixes = [
            mount.get('dir') for mount in mounts if mount.get('default')]

    syncs = extract_syncs(config.get('sync'))
    syncs = filter_syncs(syncs, args.prefixes)

    # Figure out what needs to be mounted
    needed_mounts = relevant_mounts((r[2] for r in syncs), mounts)
    to_be_mounted = list(filter(lambda x: not ismount(x.get('dir')), needed_mounts))

    if args.automount:
        mount_all(to_be_mounted)
    elif len(to_be_mounted) != 0:
        for m in to_be_mounted:
            logging.error("{} is not mounted".format(m.get('dir')))

    if not args.push:
        syncs = map(reversed, syncs)

    for dest, sources in group_syncs(syncs):
        logging.warning("rsync {} {}".format(sources, dest))

    if args.automount:
        mount_all(to_be_mounted, False)

        # for s in sync:
        #    if args.push:
        #        s.rsync()

#    for sync in syncs:
#        ensure_mounted(sync.remote, mounts)
#        rsync(sync)

