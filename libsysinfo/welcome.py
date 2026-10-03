# Copyright (c) 2026 Keel Linux maintainers <admin@keellinux.org>
#
# This file is part of turnkey-sysinfo
#
# turnkey-sysinfo is open source software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
"""The welcome line of contrib/motd, the first thing a login reads.

"Welcome to <hostname>, Keel Linux <release> (<distribution>)". The release
is the version field of the identity file, /etc/keel_version first and
/etc/turnkey_version as the fallback (common, decision 0014): the same
grammar, <prefix>-<app>-<version>-<codename>-<arch>, with an app name that
may carry hyphens. The hostname is printed as the machine has it.

Upstream took the line from sysversion.fmt_sysversion, which names
TurnKey GNU/Linux; the fork of turnkey-version leaves that wording alone,
so this package composes its own. Nothing here runs a command: the
distribution string is the caller's, from sysversion.fmt_base_distribution.
"""

DISTRIBUTION = "Keel Linux"
VERSION_FILES = ("/etc/keel_version", "/etc/turnkey_version")
IDENTITY_FIELDS = 4  # <prefix>-<app> <version> <codename> <arch>


def read_version(paths: tuple[str, ...] = VERSION_FILES) -> str:
    """The first non-empty identity string among paths, or ''."""
    for path in paths:
        try:
            with open(path) as fob:
                version = fob.read().strip()
        except OSError:
            continue
        if version:
            return version
    return ""


def release_of(version: str) -> str:
    """The version field of an identity string: keel-web-19.0-trixie-amd64
    gives 19.0, whatever the prefix and however many hyphens the app has.
    A string without the four fields gives ''."""
    fields = version.rsplit("-", IDENTITY_FIELDS - 1)
    if len(fields) != IDENTITY_FIELDS:
        return ""
    return fields[1]


def fmt_sysversion(release: str, distribution: str) -> str:
    """"Keel Linux 19.0 (Debian 13/Trixie)", with the parts that are known:
    the distribution alone without a release, the release alone without a
    distribution, "Unknown" with neither, as upstream had it."""
    parts = []
    if release:
        parts.append(f"{DISTRIBUTION} {release}")
    if distribution:
        parts.append(distribution)
    if len(parts) == 2:  # noqa: PLR2004
        return f"{parts[0]} ({parts[1]})"
    if parts:
        return parts[0]
    return "Unknown"


def fmt_welcome(hostname: str, sysversion: str) -> str:
    """"Welcome to <hostname>, <sysversion>"; the hostname is not retouched."""
    welcome = f"Welcome to {hostname}"
    if sysversion:
        welcome += ", " + sysversion
    return welcome
