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
from os.path import expanduser, realpath, ismount, dirname, basename, join

from itertools import groupby
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


def ensure_mounted(path, mounts):
    """
    Make sure that the remote path is on a known mounted disk.
    """
    mount = next((mp for mp in mounts if path.startswith(mp.get('dir'))), None)
    if mount is None:
        raise Exception("No known mountpoint for path {}".format(path))

    if not ismount(mount.get('dir')):
        pmount(mount.get('dir'),
               '/dev/disk/by-uuid/{}'.format(mount.get('uuid')),
               keyfile=mount.get('keyfile'))


def rsync(sync, dry_run=True, fat32=True, delete_before=False):
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

    command.extend((join(sync.local, f) for f in sync.files))
    command.append(sync.remote)

    logging.warning(" ".join(command))
    subprocess.run(command, check=True)


def group_sync_pairs(sync_pairs):
    """
    Group synchronisation pairs such that pairs with the same remote directory
    and in which the basename is the same in both local and remote.
    """

    return groupby(sorted(sync_pairs, key=SyncPair.remote), SyncPair.remote)


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


def sync_pairs(mapping, prefixes):
    """
    Find all local-remote directory pairs that are relevant given the prefixes.

    @param mapping: A dictionary mapping local directories to one or more
        remote directories.
    @param prefixes: A generator of string prefixes.
    """

    prefixes = [norm(path) for path in prefixes]

    for local_obj, remote_obj in mapping.items():

        if type(remote_obj) != list:
            remote_obj = [remote_obj]

        local = [norm(path) for path in expand_braces(local_obj)]
        remote = [norm(path) for expr in remote_obj for path in expand_braces(expr)]

        # for now
        for l in local:
            if l.endswith("/"):
                raise Exception("Local must not be the content of a directory")
        for r in remote:
            if not r.endswith("/"):
                raise Exception("Remote must be a directory in which the "
                                "local directory will be placed")

        for l in local:
            for r in remote:
                if any(r.startswith(p) for p in prefixes):
                    yield SyncPair(dirname(l)+"/", r, basename(l))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Mount and synchronise directories based on YAML "
                    "configuration"
    )

    parser.add_argument('--config', default='~/scrapbook/bak.yaml',
                        help="configuration file")

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

    syncs = list(sync_pairs(config.get('sync', {}), args.prefixes))

    if not args.push:
        syncs = list(SyncPair.swap, syncs)

    pairs = groupby(sorted(syncs, key=SyncPair.remote), SyncPair.remote)

    for remote, sync in pairs:
        for s in sync:
            if args.push:
                s.rsync()

#    for sync in syncs:
#        ensure_mounted(sync.remote, mounts)
#        rsync(sync)

