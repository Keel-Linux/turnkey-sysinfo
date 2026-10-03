"""The welcome line of contrib/motd: libsysinfo.welcome.

What a login on a Keel appliance reads first. The line names the machine
as the kernel names it and the distribution as /etc/keel_version says it,
with /etc/turnkey_version as the fallback; neither file says TurnKey to
the operator. pybuild runs this file at package build time, so it needs
nothing of turnkey-version (lsb_release is the caller's business).
"""

from pathlib import Path

import pytest

from libsysinfo import welcome

DISTRO = "Debian 13/Trixie"


# reading the identity file


def test_the_keel_file_is_read_first(tmp_path: Path) -> None:
    keel = tmp_path / "keel_version"
    turnkey = tmp_path / "turnkey_version"
    keel.write_text("keel-web-19.0-trixie-amd64\n")
    turnkey.write_text("turnkey-web-19.0-trixie-amd64\n")

    assert welcome.read_version((str(keel), str(turnkey))) == \
        "keel-web-19.0-trixie-amd64"


def test_the_turnkey_file_is_the_fallback(tmp_path: Path) -> None:
    turnkey = tmp_path / "turnkey_version"
    turnkey.write_text("turnkey-core-19.0-trixie-amd64\n")

    paths = (str(tmp_path / "keel_version"), str(turnkey))
    assert welcome.read_version(paths) == "turnkey-core-19.0-trixie-amd64"


def test_an_empty_keel_file_falls_back_too(tmp_path: Path) -> None:
    keel = tmp_path / "keel_version"
    turnkey = tmp_path / "turnkey_version"
    keel.write_text("\n")
    turnkey.write_text("turnkey-core-19.0-trixie-amd64\n")

    assert welcome.read_version((str(keel), str(turnkey))) == \
        "turnkey-core-19.0-trixie-amd64"


def test_no_file_is_an_empty_version(tmp_path: Path) -> None:
    paths = (str(tmp_path / "keel_version"), str(tmp_path / "turnkey_version"))

    assert welcome.read_version(paths) == ""


def test_the_default_paths_are_the_two_identity_files() -> None:
    assert welcome.VERSION_FILES == ("/etc/keel_version", "/etc/turnkey_version")


# the release of an identity string


@pytest.mark.parametrize(
    ("version", "release"),
    [
        ("keel-web-19.0-trixie-amd64", "19.0"),
        ("turnkey-core-19.0-trixie-amd64", "19.0"),
        ("keel-nginx-php-fastcgi-19.0-trixie-amd64", "19.0"),
        ("keel-core-19.0rc1-trixie-arm64", "19.0rc1"),
    ],
)
def test_the_release_is_the_version_field(version: str, release: str) -> None:
    assert welcome.release_of(version) == release


@pytest.mark.parametrize("version", ["", "core", "web-19.0", "keel-web-19.0"])
def test_a_string_without_four_fields_has_no_release(version: str) -> None:
    assert welcome.release_of(version) == ""


# the distribution line


def test_release_and_distribution() -> None:
    assert welcome.fmt_sysversion("19.0", DISTRO) == \
        f"Keel Linux 19.0 ({DISTRO})"


def test_a_distribution_alone_when_no_identity_file_is_readable() -> None:
    assert welcome.fmt_sysversion("", DISTRO) == DISTRO


def test_a_release_alone_when_lsb_release_says_nothing() -> None:
    assert welcome.fmt_sysversion("19.0", "") == "Keel Linux 19.0"


def test_neither_is_unknown_as_upstream_had_it() -> None:
    assert welcome.fmt_sysversion("", "") == "Unknown"


# the whole line


def test_the_welcome_line() -> None:
    line = welcome.fmt_welcome("keel-web1", f"Keel Linux 19.0 ({DISTRO})")

    assert line == "Welcome to keel-web1, Keel Linux 19.0 (Debian 13/Trixie)"


def test_the_hostname_is_printed_as_the_machine_has_it() -> None:
    # upstream ran str.capitalize() on it, which made keel-web1 Keel-web1
    # and WEB Web; the name is the operator's and is not retouched
    assert welcome.fmt_welcome("keel-web1", "") == "Welcome to keel-web1"
    assert welcome.fmt_welcome("Keel-Web1", "") == "Welcome to Keel-Web1"


def test_no_version_is_the_welcome_alone() -> None:
    assert welcome.fmt_welcome("web", "") == "Welcome to web"


def test_nothing_the_line_says_names_turnkey() -> None:
    for release in ("19.0", ""):
        for distro in (DISTRO, ""):
            line = welcome.fmt_welcome("web", welcome.fmt_sysversion(release, distro))
            assert "turnkey" not in line.lower()
